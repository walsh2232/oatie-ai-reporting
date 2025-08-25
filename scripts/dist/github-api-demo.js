#!/usr/bin/env node
"use strict";
/**
 * GitHub API Demo - Showcase optimized API usage
 * Demonstrates caching, GraphQL, and rate limit management
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.demonstrateOptimizations = demonstrateOptimizations;
exports.showGitHubAppBenefits = showGitHubAppBenefits;
const optimized_github_client_js_1 = require("./optimized-github-client.js");
const rate_limit_manager_js_1 = require("./rate-limit-manager.js");
async function demonstrateOptimizations() {
    console.log('🚀 GitHub API Optimization Demo\n');
    try {
        // 1. Check initial rate limit
        console.log('1️⃣ Checking rate limit status...');
        const rateLimit = await optimized_github_client_js_1.optimizedGitHub.checkRateLimit();
        console.log(`   Rate Limit: ${rateLimit.remaining}/${rateLimit.limit} remaining`);
        console.log(`   Resets at: ${new Date(rateLimit.reset * 1000).toLocaleTimeString()}\n`);
        // 2. Demonstrate caching with repeated requests
        console.log('2️⃣ Testing cache efficiency...');
        const startTime = Date.now();
        // First request (cache miss)
        console.log('   Making first request (cache miss)...');
        const pr1 = await optimized_github_client_js_1.GitHubOperations.getPR('walsh2232', 'oatie-ai-reporting', 4);
        const firstTime = Date.now() - startTime;
        // Second request (cache hit)
        console.log('   Making second request (should be cached)...');
        const cacheStartTime = Date.now();
        const pr2 = await optimized_github_client_js_1.GitHubOperations.getPR('walsh2232', 'oatie-ai-reporting', 4);
        const cacheTime = Date.now() - cacheStartTime;
        console.log(`   First request: ${firstTime}ms`);
        console.log(`   Cached request: ${cacheTime}ms`);
        console.log(`   Speed improvement: ${Math.round((firstTime - cacheTime) / firstTime * 100)}%\n`);
        // 3. Demonstrate GraphQL efficiency
        console.log('3️⃣ Testing GraphQL batch queries...');
        const batchStartTime = Date.now();
        const allPRs = await optimized_github_client_js_1.GitHubOperations.getAllPRs('walsh2232', 'oatie-ai-reporting');
        const batchTime = Date.now() - batchStartTime;
        console.log(`   Retrieved ${allPRs.repository?.pullRequests?.nodes?.length || 0} PRs in ${batchTime}ms`);
        console.log(`   Using single GraphQL query instead of ${allPRs.repository?.pullRequests?.nodes?.length || 0} REST calls\n`);
        // 4. Show cache statistics
        console.log('4️⃣ Cache statistics...');
        const cacheStats = optimized_github_client_js_1.optimizedGitHub.getCacheStats();
        console.log(`   Cache entries: ${cacheStats.size}`);
        console.log(`   Cached keys: ${cacheStats.entries.slice(0, 3).join(', ')}${cacheStats.entries.length > 3 ? '...' : ''}\n`);
        // 5. Rate limit recommendations
        console.log('5️⃣ Optimization recommendations...');
        const recommendations = rate_limit_manager_js_1.rateLimitManager.getOptimizationRecommendations();
        if (recommendations.length > 0) {
            recommendations.forEach(rec => console.log(`   ${rec}`));
        }
        else {
            console.log('   ✅ API usage is optimized!');
        }
        console.log('\n📊 Final rate limit status:');
        const finalRateLimit = await optimized_github_client_js_1.optimizedGitHub.checkRateLimit();
        console.log(rate_limit_manager_js_1.rateLimitManager.formatStatus());
    }
    catch (error) {
        console.error('❌ Demo failed:', error);
    }
}
async function showGitHubAppBenefits() {
    console.log('\n🏢 GitHub App vs Personal Token Comparison:');
    console.log('┌─────────────────────┬──────────────────┬─────────────────┐');
    console.log('│ Feature             │ Personal Token   │ GitHub App      │');
    console.log('├─────────────────────┼──────────────────┼─────────────────┤');
    console.log('│ Rate Limit          │ 5,000/hour       │ 15,000/hour     │');
    console.log('│ Security            │ User scope       │ Granular perms  │');
    console.log('│ Organization Access │ User-dependent   │ App-specific    │');
    console.log('│ Audit Trail         │ User actions     │ App actions     │');
    console.log('│ Token Rotation      │ Manual           │ Automatic       │');
    console.log('└─────────────────────┴──────────────────┴─────────────────┘');
}
// Run demo if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    demonstrateOptimizations()
        .then(() => showGitHubAppBenefits())
        .catch(console.error);
}
//# sourceMappingURL=github-api-demo.js.map