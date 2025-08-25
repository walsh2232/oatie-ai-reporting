/**
 * Optimized GitHub API Client with Caching and GraphQL
 * Implements efficient data fetching and rate limit management
 */
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
export declare class OptimizedGitHubClient {
    private octokit;
    private cache;
    private defaultTTL;
    private batchQueue;
    private batchTimeout;
    private readonly BATCH_SIZE;
    private readonly BATCH_DELAY;
    constructor(token: string);
    /**
     * Get cached data or fetch if not cached/expired
     */
    private getCached;
    /**
     * Set cache entry with TTL
     */
    private setCache;
    /**
     * Check current rate limit status
     */
    checkRateLimit(): Promise<RateLimitInfo>;
    /**
     * GraphQL query with caching
     */
    graphqlQuery<T>(query: string, variables?: Record<string, any>, ttl?: number): Promise<T>;
    /**
     * Get pull request with caching
     */
    getPullRequest(owner: string, repo: string, pullNumber: number): Promise<unknown>;
    /**
     * Get multiple pull requests efficiently
     */
    getPullRequests(owner: string, repo: string, first?: number, states?: string[]): Promise<unknown>;
    /**
     * Add operation to batch queue
     */
    private addToBatch;
    /**
     * Process batch operations
     */
    private processBatch;
    /**
     * Batch create/update operations
     */
    batchOperations(operations: BatchOperation[]): Promise<any[]>;
    /**
     * Clear cache
     */
    clearCache(): void;
    /**
     * Get cache stats
     */
    getCacheStats(): {
        size: number;
        entries: string[];
    };
    /**
     * Wait for rate limit reset if needed
     */
    waitForRateLimit(minimumRemaining?: number): Promise<void>;
}
export declare const optimizedGitHub: OptimizedGitHubClient;
export declare const GitHubOperations: {
    /**
     * Get PR with automatic caching and error handling
     */
    getPR(owner: string, repo: string, prNumber: number): Promise<unknown>;
    /**
     * Get multiple PRs efficiently
     */
    getAllPRs(owner: string, repo: string): Promise<unknown>;
    /**
     * Batch review multiple PRs
     */
    batchReviewPRs(reviews: Array<{
        owner: string;
        repo: string;
        prNumber: number;
        body: string;
    }>): Promise<any[]>;
};
export {};
//# sourceMappingURL=optimized-github-client.d.ts.map