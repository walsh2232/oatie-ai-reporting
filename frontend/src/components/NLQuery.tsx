import { useState } from 'react';
import axios from 'axios';

export function NLQuery() {
  const [schemaName, setSchemaName] = useState('HCM');
  const [request, setRequest] = useState('Show me all people');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setError(null);
    try {
      const resp = await axios.post('http://localhost:8000/sql/generate', { 
        schema_name: schemaName, 
        request 
      });
      setResult(resp.data);
    } catch (e: any) {
      setError(e.message);
    }
  }

  return (
    <div className="component-container">
      <h2>Natural Language to SQL</h2>
      <div className="form-group">
        <label htmlFor="nl-schema-input">Schema:</label>
        <input
          id="nl-schema-input"
          type="text"
          value={schemaName}
          onChange={e => setSchemaName(e.target.value)}
          placeholder="e.g., HCM, FIN"
        />
      </div>
      <div className="form-group">
        <label htmlFor="nl-request-input">Request:</label>
        <textarea
          id="nl-request-input"
          rows={4}
          cols={60}
          value={request}
          onChange={e => setRequest(e.target.value)}
          placeholder="Describe what you want in natural language..."
        />
      </div>
      <button className="submit-button" onClick={submit}>Generate SQL</button>
      {error && <div className="error-message">{error}</div>}
      {result && (
        <div className="result-container">
          <h3>Generated SQL</h3>
          <pre className="result-display">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
