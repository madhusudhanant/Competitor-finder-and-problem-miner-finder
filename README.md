# venv activate
.\venv\Scripts\Activate.ps1

# task 12 run commend
python ai/extract_problems.py --output ai/extracted_problems.txt


# fastapi server
uvicorn src.your_ai_service.api.main:app --reload
http://127.0.0.1:8000/docs


# check endpoint
POST /api/v1/problems/mine

{
  "competitor_name": "Notion",
  "platforms": ["reddit"],
  "max_posts": 50,
  "include_comments": false
}

# for restarting your fast api server
echo "Restart your FastAPI server by pressing Ctrl+C in the uvicorn terminal, then run: python main.py"