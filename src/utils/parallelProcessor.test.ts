import { describe, it, expect } from 'vitest';
import { OracleParallelProcessor } from '../utils/parallelProcessor';

describe('OracleParallelProcessor', () => {
  it('creates processor instance with default concurrency', () => {
    const processor = new OracleParallelProcessor();
    expect(processor).toBeDefined();
    
    const status = processor.getStatus();
    expect(status).toHaveProperty('queueSize');
    expect(status).toHaveProperty('activeJobs');
    expect(status).toHaveProperty('completedJobs');
  });

  it('adds tasks to queue', () => {
    const processor = new OracleParallelProcessor();
    
    const taskId = processor.addTask({
      type: 'query',
      payload: { query: 'SELECT * FROM test' },
      priority: 'medium',
      maxRetries: 3,
    });
    
    expect(taskId).toBeDefined();
    expect(typeof taskId).toBe('string');
    
    const status = processor.getStatus();
    expect(status.queueSize).toBe(1);
  });
});