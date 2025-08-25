"use strict";
/**
 * GitHub API Rate Limit Monitor and Cache Manager
 * Provides real-time monitoring and intelligent caching
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.rateLimitManager = exports.GitHubRateLimitManager = void 0;
class GitHubRateLimitManager {
    static instance;
    rateLimitStatus = null;
    lastCheck = 0;
    checkInterval = 60000; // 1 minute
    cacheHits = 0;
    cacheMisses = 0;
    static getInstance() {
        if (!GitHubRateLimitManager.instance) {
            GitHubRateLimitManager.instance = new GitHubRateLimitManager();
        }
        return GitHubRateLimitManager.instance;
    }
    /**
     * Check if we can make a request safely
     */
    canMakeRequest(type = 'core', requiredRemaining = 50) {
        if (!this.rateLimitStatus)
            return true; // First request
        const limit = this.rateLimitStatus[type];
        return limit.remaining >= requiredRemaining;
    }
    /**
     * Get time until rate limit resets
     */
    getTimeToReset(type = 'core') {
        if (!this.rateLimitStatus)
            return 0;
        const resetTime = this.rateLimitStatus[type].reset * 1000;
        return Math.max(0, resetTime - Date.now());
    }
    /**
     * Update rate limit status
     */
    updateRateLimit(status) {
        this.rateLimitStatus = status;
        this.lastCheck = Date.now();
    }
    /**
     * Get current rate limit status
     */
    getCurrentStatus() {
        return this.rateLimitStatus;
    }
    /**
     * Check if rate limit data is stale
     */
    isStatusStale() {
        return Date.now() - this.lastCheck > this.checkInterval;
    }
    /**
     * Record cache hit
     */
    recordCacheHit() {
        this.cacheHits++;
    }
    /**
     * Record cache miss
     */
    recordCacheMiss() {
        this.cacheMisses++;
    }
    /**
     * Get cache metrics
     */
    getCacheMetrics() {
        const total = this.cacheHits + this.cacheMisses;
        return {
            totalEntries: total,
            hitRate: total > 0 ? this.cacheHits / total : 0,
            memoryUsage: process.memoryUsage().heapUsed,
            topKeys: [], // Would be populated by cache implementation
        };
    }
    /**
     * Smart delay based on rate limit status
     */
    async smartDelay(type = 'core') {
        if (!this.canMakeRequest(type)) {
            const delay = this.getTimeToReset(type);
            if (delay > 0) {
                console.log(`⏳ Rate limit hit for ${type}. Waiting ${Math.ceil(delay / 1000)}s...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    /**
     * Get recommendations for optimizing API usage
     */
    getOptimizationRecommendations() {
        const recommendations = [];
        const status = this.rateLimitStatus;
        if (!status)
            return recommendations;
        // Check core API usage
        if (status.core.remaining < status.core.limit * 0.2) {
            recommendations.push('🔴 Core API usage is high (>80%). Consider caching responses longer.');
        }
        // Check GraphQL usage
        if (status.graphql.remaining < status.graphql.limit * 0.3) {
            recommendations.push('🟡 GraphQL API usage is elevated. Batch queries where possible.');
        }
        // Check search API
        if (status.search.remaining < status.search.limit * 0.5) {
            recommendations.push('🟠 Search API usage is high. Cache search results aggressively.');
        }
        // Cache performance
        const metrics = this.getCacheMetrics();
        if (metrics.hitRate < 0.6) {
            recommendations.push('📊 Cache hit rate is low (<60%). Review caching strategy.');
        }
        return recommendations;
    }
    /**
     * Format status for display
     */
    formatStatus() {
        if (!this.rateLimitStatus)
            return 'Rate limit status unknown';
        const { core, graphql, search } = this.rateLimitStatus;
        const metrics = this.getCacheMetrics();
        return `
📊 GitHub API Rate Limits:
├── 🔧 Core API: ${core.remaining}/${core.limit} (${Math.round(core.remaining / core.limit * 100)}%)
├── 🔍 GraphQL: ${graphql.remaining}/${graphql.limit} (${Math.round(graphql.remaining / graphql.limit * 100)}%)
├── 🔎 Search: ${search.remaining}/${search.limit} (${Math.round(search.remaining / search.limit * 100)}%)
└── 💾 Cache Hit Rate: ${Math.round(metrics.hitRate * 100)}%

⏰ Next Reset:
├── Core: ${new Date(core.reset * 1000).toLocaleTimeString()}
├── GraphQL: ${new Date(graphql.reset * 1000).toLocaleTimeString()}
└── Search: ${new Date(search.reset * 1000).toLocaleTimeString()}
`;
    }
}
exports.GitHubRateLimitManager = GitHubRateLimitManager;
// Export singleton
exports.rateLimitManager = GitHubRateLimitManager.getInstance();
//# sourceMappingURL=rate-limit-manager.js.map