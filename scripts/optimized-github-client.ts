/**
 * Optimized GitHub API Client with Caching and GraphQL
 * Implements efficient data fetching and rate limit management
 */

import { Octokit } from '@octokit/rest';
import { GraphqlResponseError } from '@octokit/graphql';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: number;
  used: number;
}

interface BatchOperation {
  id: string;
  operation: 'query' | 'mutation';
  query: string;
  variables?: Record<string, any>;
}

export class OptimizedGitHubClient {
  private octokit: Octokit;
  private cache = new Map<string, CacheEntry<any>>();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes
  private batchQueue: BatchOperation[] = [];
  private batchTimeout: NodeJS.Timeout | null = null;
  private readonly BATCH_SIZE = 5;
  private readonly BATCH_DELAY = 100; // ms

  constructor(token: string) {
    this.octokit = new Octokit({
      auth: token,
      userAgent: 'Oatie-AI-Assistant/1.0',
    });
  }

  /**
   * Get cached data or fetch if not cached/expired
   */
  private getCached<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;
    
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return entry.data;
  }

  /**
   * Set cache entry with TTL
   */
  private setCache<T>(key: string, data: T, ttl = this.defaultTTL): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  /**
   * Check current rate limit status
   */
  async checkRateLimit(): Promise<RateLimitInfo> {
    const cacheKey = 'rate-limit';
    const cached = this.getCached<RateLimitInfo>(cacheKey);
    if (cached) return cached;

    try {
      const response = await this.octokit.rest.rateLimit.get();
      const rateLimit = {
        limit: response.data.rate.limit,
        remaining: response.data.rate.remaining,
        reset: response.data.rate.reset,
        used: response.data.rate.used,
      };
      
      // Cache for 1 minute
      this.setCache(cacheKey, rateLimit, 60 * 1000);
      return rateLimit;
    } catch (error) {
      console.error('Failed to check rate limit:', error);
      throw error;
    }
  }

  /**
   * GraphQL query with caching
   */
  async graphqlQuery<T>(query: string, variables: Record<string, any> = {}, ttl = this.defaultTTL): Promise<T> {
    const cacheKey = `graphql:${query}:${JSON.stringify(variables)}`;
    const cached = this.getCached<T>(cacheKey);
    if (cached) return cached;

    try {
      const result = await this.octokit.graphql<T>(query, variables);
      this.setCache(cacheKey, result, ttl);
      return result;
    } catch (error) {
      if (error instanceof GraphqlResponseError) {
        console.error('GraphQL Error:', error.message);
        console.error('Query:', query);
        console.error('Variables:', variables);
      }
      throw error;
    }
  }

  /**
   * Get pull request with caching
   */
  async getPullRequest(owner: string, repo: string, pullNumber: number) {
    const cacheKey = `pr:${owner}/${repo}/${pullNumber}`;
    const cached = this.getCached(cacheKey);
    if (cached) return cached;

    const query = `
      query GetPullRequest($owner: String!, $repo: String!, $number: Int!) {
        repository(owner: $owner, name: $repo) {
          pullRequest(number: $number) {
            id
            number
            title
            body
            state
            draft
            mergeable
            createdAt
            updatedAt
            additions
            deletions
            changedFiles
            author {
              login
            }
            baseRefName
            headRefName
            commits(last: 1) {
              nodes {
                commit {
                  oid
                  message
                }
              }
            }
            files(first: 100) {
              nodes {
                path
                additions
                deletions
                changeType
              }
            }
            reviews(last: 10) {
              nodes {
                id
                state
                body
                author {
                  login
                }
                createdAt
              }
            }
          }
        }
      }
    `;

    const variables = { owner, repo, number: pullNumber };
    const result = await this.graphqlQuery(query, variables);
    return result;
  }

  /**
   * Get multiple pull requests efficiently
   */
  async getPullRequests(owner: string, repo: string, first = 20, states: string[] = ['OPEN']) {
    const cacheKey = `prs:${owner}/${repo}:${first}:${states.join(',')}`;
    const cached = this.getCached(cacheKey);
    if (cached) return cached;

    const query = `
      query GetPullRequests($owner: String!, $repo: String!, $first: Int!, $states: [PullRequestState!]) {
        repository(owner: $owner, name: $repo) {
          pullRequests(first: $first, states: $states, orderBy: {field: UPDATED_AT, direction: DESC}) {
            nodes {
              id
              number
              title
              state
              draft
              mergeable
              createdAt
              updatedAt
              additions
              deletions
              changedFiles
              author {
                login
              }
              baseRefName
              headRefName
              labels(first: 10) {
                nodes {
                  name
                  color
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
      }
    `;

    const variables = { owner, repo, first, states };
    const result = await this.graphqlQuery(query, variables, 2 * 60 * 1000); // 2 minute cache
    return result;
  }

  /**
   * Add operation to batch queue
   */
  private addToBatch(operation: BatchOperation): Promise<any> {
    return new Promise((resolve, reject) => {
      this.batchQueue.push({
        ...operation,
        resolve,
        reject,
      } as any);

      // Process batch if it's full or after delay
      if (this.batchQueue.length >= this.BATCH_SIZE) {
        this.processBatch();
      } else if (!this.batchTimeout) {
        this.batchTimeout = setTimeout(() => {
          this.processBatch();
        }, this.BATCH_DELAY);
      }
    });
  }

  /**
   * Process batch operations
   */
  private async processBatch(): Promise<void> {
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    if (this.batchQueue.length === 0) return;

    const batch = this.batchQueue.splice(0, this.BATCH_SIZE);
    
    try {
      // For GraphQL, we can batch multiple queries in one request
      const queries = batch.map((op, index) => `
        query${index}: ${op.query.replace('query', '').trim()}
      `).join('\n');

      const batchQuery = `query BatchQuery {
        ${queries}
      }`;

      const variables = batch.reduce((acc, op, index) => {
        Object.keys(op.variables || {}).forEach(key => {
          acc[`${key}${index}`] = op.variables![key];
        });
        return acc;
      }, {} as Record<string, any>);

      const result = await this.octokit.graphql(batchQuery, variables);
      
      // Resolve individual promises
      batch.forEach((op: any, index) => {
        op.resolve(result[`query${index}`]);
      });
    } catch (error) {
      // Reject all promises in batch
      batch.forEach((op: any) => {
        op.reject(error);
      });
    }
  }

  /**
   * Batch create/update operations
   */
  async batchOperations(operations: BatchOperation[]): Promise<any[]> {
    const promises = operations.map(op => this.addToBatch(op));
    return Promise.all(promises);
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get cache stats
   */
  getCacheStats(): { size: number; entries: string[] } {
    return {
      size: this.cache.size,
      entries: Array.from(this.cache.keys()),
    };
  }

  /**
   * Wait for rate limit reset if needed
   */
  async waitForRateLimit(minimumRemaining = 100): Promise<void> {
    const rateLimit = await this.checkRateLimit();
    
    if (rateLimit.remaining < minimumRemaining) {
      const resetTime = rateLimit.reset * 1000; // Convert to milliseconds
      const waitTime = resetTime - Date.now();
      
      if (waitTime > 0) {
        console.log(`Rate limit low (${rateLimit.remaining}/${rateLimit.limit}). Waiting ${Math.ceil(waitTime / 1000)}s for reset...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }
  }
}

// Export singleton instance
export const optimizedGitHub = new OptimizedGitHubClient(
  process.env.GITHUB_TOKEN || ''
);

// Usage examples
export const GitHubOperations = {
  /**
   * Get PR with automatic caching and error handling
   */
  async getPR(owner: string, repo: string, prNumber: number) {
    await optimizedGitHub.waitForRateLimit();
    return optimizedGitHub.getPullRequest(owner, repo, prNumber);
  },

  /**
   * Get multiple PRs efficiently
   */
  async getAllPRs(owner: string, repo: string) {
    await optimizedGitHub.waitForRateLimit();
    return optimizedGitHub.getPullRequests(owner, repo, 50);
  },

  /**
   * Batch review multiple PRs
   */
  async batchReviewPRs(reviews: Array<{owner: string, repo: string, prNumber: number, body: string}>) {
    const operations = reviews.map(review => ({
      id: `review-${review.prNumber}`,
      operation: 'mutation' as const,
      query: `
        mutation ReviewPR($prId: ID!, $body: String!) {
          addPullRequestReview(input: {
            pullRequestId: $prId
            body: $body
            event: APPROVE
          }) {
            pullRequestReview {
              id
            }
          }
        }
      `,
      variables: {
        prId: `pr-${review.prNumber}`, // Would need to resolve PR ID
        body: review.body,
      },
    }));

    return optimizedGitHub.batchOperations(operations);
  },
};
