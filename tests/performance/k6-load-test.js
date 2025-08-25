import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
export const errorRate = new Rate('errors');
export const responseTime = new Trend('response_time');

// Test configuration
export const options = {
  stages: [
    // Ramp-up
    { duration: '2m', target: 100 }, // Ramp up to 100 users over 2 minutes
    { duration: '2m', target: 500 }, // Ramp up to 500 users over 2 minutes
    { duration: '1m', target: 1000 }, // Ramp up to 1000 users over 1 minute
    
    // Sustained load
    { duration: '5m', target: 1000 }, // Maintain 1000 users for 5 minutes
    
    // Ramp-down
    { duration: '2m', target: 0 }, // Ramp down to 0 users over 2 minutes
  ],
  thresholds: {
    // Performance requirements from enterprise deployment guide
    http_req_duration: ['p(95)<5000', 'p(90)<2000'], // 95% of requests under 5s, 90% under 2s
    http_req_failed: ['rate<0.01'], // Error rate under 1%
    http_reqs: ['rate>100'], // Minimum 100 RPS throughput
  },
};

// Base URL - can be overridden via environment variable
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Test scenarios matching the Python performance test
const scenarios = [
  { name: 'health_check', endpoint: '/health', weight: 0.2 },
  { name: 'auth_login', endpoint: '/api/v1/auth/login', weight: 0.3, method: 'POST' },
  { name: 'list_reports', endpoint: '/api/v1/reports', weight: 0.8 },
  { name: 'query_execution', endpoint: '/api/v1/queries/execute', weight: 0.8, method: 'POST' },
  { name: 'user_profile', endpoint: '/api/v1/users/profile', weight: 0.5 },
  { name: 'list_templates', endpoint: '/api/v1/templates', weight: 0.8 },
  { name: 'query_history', endpoint: '/api/v1/queries/history', weight: 0.6 },
];

// Authentication token (mock)
let authToken = '';

export function setup() {
  // Perform login to get auth token
  const loginPayload = JSON.stringify({
    username: 'test_user',
    password: 'test_password'
  });
  
  const loginResponse = http.post(`${BASE_URL}/api/v1/auth/login`, loginPayload, {
    headers: { 'Content-Type': 'application/json' },
  });
  
  if (loginResponse.status === 200) {
    const loginData = JSON.parse(loginResponse.body);
    authToken = loginData.access_token || 'mock_token';
  }
  
  return { authToken };
}

export default function (data) {
  // Random scenario selection based on weights
  const scenario = selectScenario();
  
  const headers = {
    'Authorization': `Bearer ${data.authToken || 'mock_token'}`,
    'Content-Type': 'application/json',
    'User-Agent': 'K6-LoadTest/1.0',
  };
  
  let response;
  
  if (scenario.method === 'POST') {
    const payload = generatePayload(scenario.name);
    response = http.post(`${BASE_URL}${scenario.endpoint}`, payload, { headers });
  } else {
    response = http.get(`${BASE_URL}${scenario.endpoint}`, { headers });
  }
  
  // Record custom metrics
  responseTime.add(response.timings.duration);
  errorRate.add(response.status >= 400);
  
  // Check response
  const checkResult = check(response, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
    'response time < 2000ms': (r) => r.timings.duration < 2000,
    'response time < 5000ms': (r) => r.timings.duration < 5000,
    'has body': (r) => r.body && r.body.length > 0,
  });
  
  if (!checkResult) {
    console.error(`Failed check for ${scenario.name}: Status ${response.status}, Duration: ${response.timings.duration}ms`);
  }
  
  // Think time - realistic user behavior
  sleep(Math.random() * 2 + 1); // Random sleep between 1-3 seconds
}

function selectScenario() {
  // Weighted random selection
  const totalWeight = scenarios.reduce((sum, s) => sum + s.weight, 0);
  let random = Math.random() * totalWeight;
  
  for (const scenario of scenarios) {
    random -= scenario.weight;
    if (random <= 0) {
      return scenario;
    }
  }
  
  return scenarios[0]; // Fallback
}

function generatePayload(scenarioName) {
  switch (scenarioName) {
    case 'auth_login':
      return JSON.stringify({
        username: `test_user_${Math.floor(Math.random() * 1000)}`,
        password: 'test_password'
      });
      
    case 'query_execution':
      return JSON.stringify({
        sql: `SELECT * FROM sales_data WHERE region = '${getRandomRegion()}' LIMIT 100`,
        parameters: {},
        use_cache: Math.random() > 0.3
      });
      
    default:
      return '{}';
  }
}

function getRandomRegion() {
  const regions = ['North', 'South', 'East', 'West', 'Central'];
  return regions[Math.floor(Math.random() * regions.length)];
}

export function teardown(data) {
  // Cleanup after test
  console.log('Load test completed');
}