"use strict";
/**
 * Optimized GitHub API Client with Caching and GraphQL
 * Implements efficient data fetching and rate limit management
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.GitHubOperations = exports.optimizedGitHub = exports.OptimizedGitHubClient = void 0;
const rest_1 = require("@octokit/rest");
const graphql_1 = require("@octokit/graphql");
class OptimizedGitHubClient {
    octokit;
    cache = new Map();
    defaultTTL = 5 * 60 * 1000; // 5 minutes
    batchQueue = [];
    batchTimeout = null;
    BATCH_SIZE = 5;
    BATCH_DELAY = 100; // ms
    constructor(token) {
        this.octokit = new rest_1.Octokit({
            auth: token,
            userAgent: 'Oatie-AI-Assistant/1.0',
        });
    }
    /**
     * Get cached data or fetch if not cached/expired
     */
    getCached(key) {
        const entry = this.cache.get(key);
        if (!entry)
            return null;
        if (Date.now() - entry.timestamp > entry.ttl) {
            this.cache.delete(key);
            return null;
        }
        return entry.data;
    }
    /**
     * Set cache entry with TTL
     */
    setCache(key, data, ttl = this.defaultTTL) {
        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl,
        });
    }
    /**
     * Check current rate limit status
     */
    async checkRateLimit() {
        const cacheKey = 'rate-limit';
        const cached = this.getCached(cacheKey);
        if (cached)
            return cached;
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
        }
        catch (error) {
            console.error('Failed to check rate limit:', error);
            throw error;
        }
    }
    /**
     * GraphQL query with caching
     */
    async graphqlQuery(query, variables = {}, ttl = this.defaultTTL) {
        const cacheKey = `graphql:${query}:${JSON.stringify(variables)}`;
        const cached = this.getCached(cacheKey);
        if (cached)
            return cached;
        try {
            const result = await this.octokit.graphql(query, variables);
            this.setCache(cacheKey, result, ttl);
            return result;
        }
        catch (error) {
            if (error instanceof graphql_1.GraphqlResponseError) {
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
    async getPullRequest(owner, repo, pullNumber) {
        const cacheKey = `pr:${owner}/${repo}/${pullNumber}`;
        const cached = this.getCached(cacheKey);
        if (cached)
            return cached;
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
    async getPullRequests(owner, repo, first = 20, states = ['OPEN']) {
        const cacheKey = `prs:${owner}/${repo}:${first}:${states.join(',')}`;
        const cached = this.getCached(cacheKey);
        if (cached)
            return cached;
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
    addToBatch(operation) {
        return new Promise((resolve, reject) => {
            this.batchQueue.push({
                ...operation,
                resolve,
                reject,
            });
            // Process batch if it's full or after delay
            if (this.batchQueue.length >= this.BATCH_SIZE) {
                this.processBatch();
            }
            else if (!this.batchTimeout) {
                this.batchTimeout = setTimeout(() => {
                    this.processBatch();
                }, this.BATCH_DELAY);
            }
        });
    }
    /**
     * Process batch operations
     */
    async processBatch() {
        if (this.batchTimeout) {
            clearTimeout(this.batchTimeout);
            this.batchTimeout = null;
        }
        if (this.batchQueue.length === 0)
            return;
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
                    acc[`${key}${index}`] = op.variables[key];
                });
                return acc;
            }, {});
            const result = await this.octokit.graphql(batchQuery, variables);
            // Resolve individual promises
            batch.forEach((op, index) => {
                op.resolve(result[`query${index}`]);
            });
        }
        catch (error) {
            // Reject all promises in batch
            batch.forEach((op) => {
                op.reject(error);
            });
        }
    }
    /**
     * Batch create/update operations
     */
    async batchOperations(operations) {
        const promises = operations.map(op => this.addToBatch(op));
        return Promise.all(promises);
    }
    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
    }
    /**
     * Get cache stats
     */
    getCacheStats() {
        return {
            size: this.cache.size,
            entries: Array.from(this.cache.keys()),
        };
    }
    /**
     * Wait for rate limit reset if needed
     */
    async waitForRateLimit(minimumRemaining = 100) {
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
exports.OptimizedGitHubClient = OptimizedGitHubClient;
// Export singleton instance
exports.optimizedGitHub = new OptimizedGitHubClient(process.env.GITHUB_TOKEN || '');
// Usage examples
exports.GitHubOperations = {
    /**
     * Get PR with automatic caching and error handling
     */
    async getPR(owner, repo, prNumber) {
        await exports.optimizedGitHub.waitForRateLimit();
        return exports.optimizedGitHub.getPullRequest(owner, repo, prNumber);
    },
    /**
     * Get multiple PRs efficiently
     */
    async getAllPRs(owner, repo) {
        await exports.optimizedGitHub.waitForRateLimit();
        return exports.optimizedGitHub.getPullRequests(owner, repo, 50);
    },
    /**
     * Batch review multiple PRs
     */
    async batchReviewPRs(reviews) {
        const operations = reviews.map(review => ({
            id: `review-${review.prNumber}`,
            operation: 'mutation',
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
        return exports.optimizedGitHub.batchOperations(operations);
    },
};
//# sourceMappingURL=optimized-github-client.js.map