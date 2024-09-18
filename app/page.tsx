"use client";

import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [srccode, setSrcCode] = useState('');
  const [optab, setOptab] = useState('');

  interface ResultType {
    intermediate_file: string[];
    symtab: Record<string, any>;
    program_size: number;
  }

  const [result, setResult] = useState<ResultType | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    try {
      // Convert srccode to array (split by newlines) and optab to an object
      const srcCodeArray = srccode.split('\n').map(line => line.trim()).filter(Boolean);
      const optabObject = optab.split('\n').reduce<Record<string, string>>((acc, line) => {
        const [opcode, machineCode] = line.split(/\s+/); // Split by space or tab
        if (opcode && machineCode) {
          acc[opcode.trim()] = machineCode.trim();
        }
        return acc;
      }, {});

      const payload = {
        srccode: srcCodeArray,
        optab: optabObject
      };

      const response = await axios.post('http://127.0.0.1:5000/', payload);
      setResult(response.data);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to process the input. Please check your data.');
      setResult(null);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-white">Welcome to Blaaa's Pass1 Processor</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="srccode" className="block text-lg font-semibold mb-2 text-white">Source Code (one instruction per line):</label>
          <textarea
            id="srccode"
            value={srccode}
            onChange={(e) => setSrcCode(e.target.value)}
            rows={10}
            className="w-full p-3 border border-black rounded-lg shadow-sm text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder={`e.g.\nLABEL START 1000\nLABEL1 LDA ALPHA\nSTA BETA`}
            required
          />
        </div>

        <div>
          <label htmlFor="optab" className="block text-lg font-semibold mb-2 text-black">Opcode Table (opcode machine_code):</label>
          <textarea
            id="optab"
            value={optab}
            onChange={(e) => setOptab(e.target.value)}
            rows={5}
            className="w-full p-3 border border-black rounded-lg shadow-sm text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder={`e.g.\nLDA 00\nSTA 0C\nADD 18`}
            required
          />
        </div>

        <button 
          type="submit" 
          className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Submit
        </button>
      </form>

      {error && (
        <p className="mt-6 text-red-600 font-medium">{error}</p>
      )}

      {result && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4 text-black">Result</h2>
          
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-2 text-black">Intermediate File:</h3>
            <pre className="p-4 bg-gray-100 border border-black rounded-lg overflow-x-auto text-black">
              {result.intermediate_file.join('\n')}
            </pre>
          </div>

          <div>
            <h3 className="text-xl font-semibold mb-2 text-black">Symbol Table:</h3>
            <pre className="p-4 bg-gray-100 border border-black rounded-lg overflow-x-auto text-black">
              {JSON.stringify(result.symtab, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
