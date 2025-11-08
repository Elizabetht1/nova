import requests
import json

if __name__ == "__main__":
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer <TOKEN>",
        # "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        # "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    data=json.dumps({
        "model": "google/gemini-2.5-flash-preview-09-2025", # Optional
        "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Output the key frames"
                },
                # {
                #     "type": "input_video",
                #     "video_url": {
                #       "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                #     }
                # }
                {"type": "input_video",
                "video_url" : {"url": "https://www.youtube.com/watch?v=6SmLo1Td5zY"}}
            ]
        }
        ]
    })
    )
    print(response.json())

