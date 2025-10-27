"""
AI Service for problem extraction and content analysis using Google Gemini.
"""
import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from ..config import settings


class ProblemExtractor:
    """Extract problems from text using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize the problem extractor.
        
        Args:
            api_key: Google Gemini API key (optional, will use settings if not provided)
            model_name: Gemini model name to use (optional, will use default if not provided)
        """
        self.client = None
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._setup_client()
    
    def _setup_client(self):
        """Set up the Gemini client."""
        if not GEMINI_AVAILABLE:
            raise RuntimeError(
                "google-generativeai is not installed. "
                "Install with: pip install google-generativeai"
            )
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured. Set it in .env or pass it to the constructor.")
        
        try:
            genai.configure(api_key=self.api_key)
            
            # Try different model names for compatibility
            try:
                self.client = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini client initialized with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize {self.model_name}, trying fallback models...")
                # Try fallback models
                for fallback in ['models/gemini-1.5-flash', 'gemini-pro']:
                    try:
                        self.client = genai.GenerativeModel(fallback)
                        logger.info(f"Gemini client initialized with fallback model: {fallback}")
                        break
                    except Exception:
                        continue
                
                if not self.client:
                    raise Exception(f"Could not initialize any Gemini model. Original error: {e}")
        
        except Exception as e:
            logger.error(f"Failed to setup Gemini client: {e}")
            raise
    
    def _create_prompt(self, text_content: str, extraction_type: str = "problems") -> str:
        """
        Create a prompt for content extraction.
        
        Args:
            text_content: The text to analyze
            extraction_type: Type of extraction (problems, sentiment, features, etc.)
        
        Returns:
            Formatted prompt string
        """
        if extraction_type == "problems":
            return f"""
You are an expert analyst specializing in extracting user problems and pain points from text reviews and feedback.

Your task is to analyze the following user reviews and extract distinct problem statements. For each problem:
1. Identify the core issue the user is experiencing
2. Categorize the type of problem (e.g., Technical, UI/UX, Performance, Support, Pricing, Features, Integration, etc.)
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
        "overall_sentiment": "Overall user sentiment analysis (Positive/Negative/Neutral)"
    }}
}}

Focus on extracting actionable, specific problems rather than general complaints. Combine similar issues into single problem statements where appropriate.
"""
        elif extraction_type == "sentiment":
            return f"""
Analyze the sentiment of the following user-generated content and provide a detailed sentiment analysis.

Text to analyze:
---
{text_content}
---

Return your analysis in JSON format:
{{
    "overall_sentiment": "Positive/Negative/Neutral/Mixed",
    "sentiment_score": 0.0,
    "positive_aspects": [],
    "negative_aspects": [],
    "emotional_tone": "Description of the emotional tone"
}}
"""
        else:
            return f"""
Analyze the following text and extract key insights:

{text_content}

Provide a structured analysis in JSON format.
"""
    
    def _call_gemini(self, prompt: str) -> str:
        """
        Call Gemini API.
        
        Args:
            prompt: The prompt to send to Gemini
        
        Returns:
            Raw response text from Gemini
        
        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RATE_LIMIT_EXCEEDED" in error_msg:
                logger.error(f"Gemini API quota exceeded: {error_msg}")
                raise Exception(f"Gemini API quota exceeded. Please check your quota limits or try again later.")
            elif "403" in error_msg or "PERMISSION_DENIED" in error_msg:
                logger.error(f"Gemini API permission denied: {error_msg}")
                raise Exception(f"Gemini API permission denied. Please check your API key permissions.")
            else:
                logger.error(f"Gemini API call failed: {error_msg}")
                raise Exception(f"Gemini API call failed: {error_msg}")
    
    def _parse_json_response(self, raw_response: str) -> Dict:
        """
        Parse JSON response from Gemini, handling markdown code blocks.
        
        Args:
            raw_response: Raw response string from Gemini
        
        Returns:
            Parsed JSON as dictionary
        """
        try:
            clean_response = raw_response.strip()
            
            # Remove markdown code fences if present
            if clean_response.startswith("```"):
                lines = clean_response.split('\n')
                # Remove first line (```json or ```)
                lines = lines[1:]
                # Remove last line if it's closing fence
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                clean_response = '\n'.join(lines)
            
            # Parse JSON
            parsed_data = json.loads(clean_response.strip())
            return parsed_data
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {raw_response}")
            return {
                "problems": [],
                "summary": {
                    "total_problems": 0,
                    "error": f"JSON parsing failed: {str(e)}"
                }
            }
    
    def extract_problems(self, text_content: str) -> Dict:
        """
        Extract problems from text content.
        
        Args:
            text_content: The text to analyze
        
        Returns:
            Dictionary containing extracted problems and summary
        """
        try:
            logger.info("Extracting problems using Gemini...")
            
            if not text_content or not text_content.strip():
                logger.warning("Empty text content provided")
                return {
                    "problems": [],
                    "summary": {
                        "total_problems": 0,
                        "error": "Empty text content"
                    }
                }
            
            # Create prompt
            prompt = self._create_prompt(text_content, extraction_type="problems")
            
            # Call Gemini API
            raw_response = self._call_gemini(prompt)
            
            # Parse response
            problems_data = self._parse_json_response(raw_response)
            
            logger.info(f"Successfully extracted {len(problems_data.get('problems', []))} problems")
            return problems_data
        
        except Exception as e:
            logger.error(f"Error in extract_problems: {e}")
            raise
    
    def analyze_sentiment(self, text_content: str) -> Dict:
        """
        Analyze sentiment of text content.
        
        Args:
            text_content: The text to analyze
        
        Returns:
            Dictionary containing sentiment analysis
        """
        try:
            logger.info("Analyzing sentiment using Gemini...")
            
            prompt = self._create_prompt(text_content, extraction_type="sentiment")
            raw_response = self._call_gemini(prompt)
            sentiment_data = self._parse_json_response(raw_response)
            
            return sentiment_data
        
        except Exception as e:
            logger.error(f"Error in analyze_sentiment: {e}")
            raise
    
    def batch_extract_problems(self, text_list: List[str]) -> List[Dict]:
        """
        Extract problems from multiple text sources.
        
        Args:
            text_list: List of text strings to analyze
        
        Returns:
            List of problem extraction results
        """
        results = []
        for i, text in enumerate(text_list):
            try:
                logger.info(f"Processing text {i+1}/{len(text_list)}")
                result = self.extract_problems(text)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing text {i+1}: {e}")
                results.append({
                    "problems": [],
                    "summary": {"total_problems": 0, "error": str(e)}
                })
        
        return results


def format_problems_output(problems_data: Dict) -> str:
    """
    Format extracted problems for display.
    
    Args:
        problems_data: Dictionary containing extracted problems
    
    Returns:
        Formatted string representation
    """
    output = []
    output.append("\n" + "="*60)
    output.append("EXTRACTED PROBLEMS")
    output.append("="*60)
    
    if not problems_data.get("problems"):
        output.append("No problems were extracted from the text.")
        if "error" in problems_data.get("summary", {}):
            output.append(f"Error: {problems_data['summary']['error']}")
        return "\n".join(output)
    
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
    
    return "\n".join(output)
