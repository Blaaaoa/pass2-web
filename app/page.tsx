// pages/index.js
'use client';

import { useState } from 'react';
import { runCode } from './api/route';

export default function Home() {
  const [inputContent, setInputContent] = useState('');
  const [result, setResult] = useState(null);

  const handleRunCode = async () => {
    const result = await runCode(inputContent);
    setResult(result);
  };

  return (
    <div>
      <h1>Run Your Code</h1>
      <textarea
        rows={10}
        cols={50}
        value={inputContent}
        onChange={(e) => setInputContent(e.target.value)}
      />
      <button onClick={handleRunCode}>Run Code</button>
      {result && (
        <div>
          <h2>Result:</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
