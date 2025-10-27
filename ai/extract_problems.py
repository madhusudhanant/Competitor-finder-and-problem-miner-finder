#!/usr/bin/env python3
"""
Problem Extraction Script

This script reads a local text file containing user reviews and uses Google Gemini
to extract problem statements from the content.

Usage:
    python ai/extract_problems.py [--file path/to/reviews.txt]

Environment Variables:
    GEMINI_API_KEY: Your Google Gemini API key
"""

import os
import argparse
import json
from typing import List, Dict, Optional
from pathlib import Path
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Robustly load .env from the root directory
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'    
    load_dotenv(dotenv_path=env_path)
except Exception as e:
    print(f"[dotenv] Warning: {e}", file=sys.stderr)

# Import for Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Error: Google Gemini library not installed.")
    print("Install with: pip install google-generativeai")
    exit(1)


class ProblemExtractor:
    """Main class for extracting problems from text using Google Gemini."""
    
    def __init__(self):
        """Initialize the problem extractor with Gemini."""
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Set up the Gemini client."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        # Try both possible model names for compatibility
        try:
            self.client = genai.GenerativeModel('models/gemini-2.5-flash')
        except Exception as e:
            print("[Gemini] models/gemini-2.5-flash not found, trying gemini-pro...", file=sys.stderr)
            self.client = genai.GenerativeModel('gemini-pro')
        print("✓ Gemini client initialized")
    
    def _create_prompt(self, text_content: str) -> str:
        """Create a well-engineered prompt for problem extraction."""
        prompt = f"""
You are an expert analyst specializing in extracting user problems and pain points from text reviews and feedback.

Your task is to analyze the following user reviews and extract distinct problem statements. For each problem:
1. Identify the core issue the user is experiencing
2. Categorize the type of problem (e.g., Technical, UI/UX, Performance, Support, etc.)
3. Assess the severity level (High, Medium, Low)
4. Provide a clear, concise problem statement

Text to analyze:
---
{text_content}
---
Please return your analysis in the following JSON format:
{{
    "problems": [
        {{
            "problem_statement": "Clear description of the specific problem",
            "category": "Type of problem",
            "severity": "High/Medium/Low",
            "affected_feature": "Specific feature or area affected",
            "user_impact": "How this affects the user experience"
        }}
    ],
    "summary": {{
        "total_problems": "Number of distinct problems found",
        "most_common_category": "Category with most issues",
        "overall_sentiment": "Overall user sentiment analysis"
    }}
}}

Focus on extracting actionable, specific problems rather than general complaints. Combine similar issues into single problem statements where appropriate.
"""
        return prompt
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API to extract problems."""
        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RATE_LIMIT_EXCEEDED" in error_msg:
                raise Exception(f"Gemini API quota exceeded. Please check your quota limits or try again later.\nDetails: {error_msg}")
            elif "403" in error_msg or "PERMISSION_DENIED" in error_msg:
                raise Exception(f"Gemini API permission denied. Please check your API key permissions.\nDetails: {error_msg}")
            else:
                raise Exception(f"Gemini API call failed: {error_msg}")
    
    def extract_problems(self, text_content: str) -> Dict:
        """Extract problems from the given text content using Gemini."""
        print("Extracting problems using Gemini...")
        
        prompt = self._create_prompt(text_content)
        
        # Call Gemini API
        raw_response = self._call_gemini(prompt)
        
        # Parse the JSON response
        try:
            # Clean the response in case it has markdown formatting
            clean_response = raw_response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            problems_data = json.loads(clean_response.strip())
            return problems_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {str(e)}")
            print(f"Raw response: {raw_response}")
            return {"problems": [], "summary": {"total_problems": 0, "error": "JSON parsing failed"}}


def read_text_file(file_path: str) -> str:
    """Read content from a text file."""
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        
        if not content:
            raise ValueError("File is empty")
        
        print(f"✓ Successfully read {len(content)} characters from {file_path}")
        return content
    
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {str(e)}")


def print_problems(problems_data: Dict, file=None):
    """Print the extracted problems in a formatted way. Optionally write to a file."""
    output = []
    output.append("\n" + "="*60)
    output.append("EXTRACTED PROBLEMS")
    output.append("="*60)
    
    if not problems_data.get("problems"):
        output.append("No problems were extracted from the text.")
        result = "\n".join(output)
        print(result)
        if file:
            file.write(result + "\n")
        return
    
    problems = problems_data["problems"]
    
    for i, problem in enumerate(problems, 1):
        output.append(f"\nProblem #{i}")
        output.append(f"   Statement: {problem.get('problem_statement', 'N/A')}")
        output.append(f"   Category:  {problem.get('category', 'N/A')}")
        output.append(f"   Severity:  {problem.get('severity', 'N/A')}")
        output.append(f"   Feature:   {problem.get('affected_feature', 'N/A')}")
        output.append(f"   Impact:    {problem.get('user_impact', 'N/A')}")
    
    # Print summary
    summary = problems_data.get("summary", {})
    output.append(f"\nSUMMARY")
    output.append(f"   Total Problems: {summary.get('total_problems', len(problems))}")
    output.append(f"   Most Common Category: {summary.get('most_common_category', 'N/A')}")
    output.append(f"   Overall Sentiment: {summary.get('overall_sentiment', 'N/A')}")
    output.append("="*60)
    result = "\n".join(output)
    print(result)
    if file:
        file.write(result + "\n")


def main():
    """Main function to orchestrate the problem extraction process."""
    parser = argparse.ArgumentParser(description="Extract problems from user reviews using Gemini")
    parser.add_argument(
        "--file", 
        default="ai/sample_reviews.txt",
        help="Path to the text file containing user reviews (default: ai/sample_reviews.txt)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to save the extracted problems (default: None)"
    )
    
    args = parser.parse_args()
    
    try:
        print("Starting Problem Mining Process...")
        print(f"File: {args.file}")
        print("Provider: GEMINI")
        
        # Read the input file
        text_content = read_text_file(args.file)
        
        # Initialize the problem extractor
        extractor = ProblemExtractor()
        
        # Extract problems
        problems_data = extractor.extract_problems(text_content)
        
        # Save results as JSON if output is specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(problems_data, f, indent=4)
        print_problems(problems_data)
        
        print("\nProblem extraction completed successfully!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting:")
        print("   1. Make sure your GEMINI_API_KEY is set as an environment variable")
        print("   2. Check that the input file exists and is readable")
        print("   3. Verify you have google-generativeai installed")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())