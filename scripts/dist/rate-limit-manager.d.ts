/**
 * GitHub API Rate Limit Monitor and Cache Manager
 * Provides real-time monitoring and intelligent caching
 */
export interface RateLimitStatus {
    core: {
        limit: number;
        remaining: number;
        reset: number;
        used: number;
        resource: string;
    };
    graphql: {
        limit: number;
        remaining: number;
        reset: number;
        used: number;
        resource: string;
    };
    search: {
        limit: number;
        remaining: number;
        reset: number;
        used: number;
        resource: string;
    };
}
export interface CacheMetrics {
    totalEntries: number;
    hitRate: number;
    memoryUsage: number;
    topKeys: string[];
}
export declare class GitHubRateLimitManager {
    private static instance;
    private rateLimitStatus;
    private lastCheck;
    private checkInterval;
    private cacheHits;
    private cacheMisses;
    static getInstance(): GitHubRateLimitManager;
    /**
     * Check if we can make a request safely
     */
    canMakeRequest(type?: 'core' | 'graphql' | 'search', requiredRemaining?: number): boolean;
    /**
     * Get time until rate limit resets
     */
    getTimeToReset(type?: 'core' | 'graphql' | 'search'): number;
    /**
     * Update rate limit status
     */
    updateRateLimit(status: RateLimitStatus): void;
    /**
     * Get current rate limit status
     */
    getCurrentStatus(): RateLimitStatus | null;
    /**
     * Check if rate limit data is stale
     */
    isStatusStale(): boolean;
    /**
     * Record cache hit
     */
    recordCacheHit(): void;
    /**
     * Record cache miss
     */
    recordCacheMiss(): void;
    /**
     * Get cache metrics
     */
    getCacheMetrics(): CacheMetrics;
    /**
     * Smart delay based on rate limit status
     */
    smartDelay(type?: 'core' | 'graphql' | 'search'): Promise<void>;
    /**
     * Get recommendations for optimizing API usage
     */
    getOptimizationRecommendations(): string[];
    /**
     * Format status for display
     */
    formatStatus(): string;
}
export declare const rateLimitManager: GitHubRateLimitManager;
//# sourceMappingURL=rate-limit-manager.d.ts.map