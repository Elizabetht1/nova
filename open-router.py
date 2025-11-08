import requests
import json

if __name__ == "__main__":
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer <YOUR API KEY>",
        # "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        # "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    data=json.dumps({
        "model": "openai/gpt-4o", # Optional
        "messages": [
        {
            "role": "user",
            "content": "What is the meaning of life?"
        }
        ]
    })
    )
    print(response.json())

