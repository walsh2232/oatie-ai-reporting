import { useState } from 'react';
import axios from 'axios';

export function ValidateSQL() {
  const [schemaName, setSchemaName] = useState('HCM');
  const [sql, setSql] = useState('SELECT * FROM PER_ALL_PEOPLE_F');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setError(null);
    try {
      const resp = await axios.post('http://localhost:8000/sql/validate', { 
        schema_name: schemaName, 
        sql 
      });
      setResult(resp.data);
    } catch (e: any) {
      setError(e.message);
    }
  }

  return (
    <div className="component-container">
      <h2>SQL Validation</h2>
      <div className="form-group">
        <label htmlFor="schema-input">Schema:</label>
        <input
          id="schema-input"
          type="text"
          value={schemaName}
          onChange={e => setSchemaName(e.target.value)}
          placeholder="e.g., HCM, FIN"
        />
      </div>
      <div className="form-group">
        <label htmlFor="sql-input">SQL Query:</label>
        <textarea
          id="sql-input"
          rows={4}
          cols={60}
          value={sql}
          onChange={e => setSql(e.target.value)}
          placeholder="Enter your SQL query here..."
        />
      </div>
      <button className="submit-button" onClick={submit}>Validate</button>
      {error && <div className="error-message">{error}</div>}
      {result && (
        <div className="result-container">
          <h3>Validation Result</h3>
          <pre className="result-display">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
