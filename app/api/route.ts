// utils/api.js

export async function runCode(inputFileContent: string) {
    try {
      const response = await fetch('http://127.0.0.1:5000/', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input_file_content: inputFileContent }),
      });
  
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
  
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error:', error);
      return { error: (error as any).message };
    }
  }
  