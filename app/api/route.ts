// app/api/route.ts
import { NextRequest, NextResponse } from 'next/server';

// Define the structure of the request body
interface RequestBody {
    code: string; // Assuming the code is a string
}

// Define the response structure
interface ResponseResult {
    intermediate_file: string[];
    symtab: Record<string, string | number>; // Assuming symtab can have string or number values
    object_code: string[];
}

// Define the POST request handler
export async function POST(req: NextRequest) {
    try {
        // Parse the request body
        const body: RequestBody = await req.json();
        const inputFileContent = body.code;

        // Call your runCode function
        const result = await runCode(inputFileContent);

        // Check if the result is an error
        if ('error' in result) {
            return NextResponse.json(result, { status: 500 }); // Return error response
        }

        // Return the successful result in the response
        return NextResponse.json(result as ResponseResult, { status: 200 });
    } catch (error) {
        // Handle any errors and return an error response
        return NextResponse.json({ error: (error as Error).message }, { status: 500 });
    }
}

// The runCode function that interacts with your Python backend
async function runCode(inputFileContent: string): Promise<ResponseResult | { error: string }> {
    try {
        const response = await fetch('http://127.0.0.1:5000/run-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: inputFileContent,
            }),
        });

        // Handle response errors
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Parse the result from the Python server
        const result: ResponseResult = await response.json();
        console.log('Response from server:', result);
        return result;
    } catch (error) {
        console.error('Error:', error);
        return { error: (error as Error).message }; // Return error as an object
    }
}
