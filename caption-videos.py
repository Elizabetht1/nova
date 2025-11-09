import requests
import json

from load_ds import load_json

SYSTEM_PROMPT = """
Follow these directions. 
"""

def load_raw_ds(dsfp):
    raw_data = load_json(dsfp,filter="level_1_category_labels:SURGERY",limit=20)
    
    KEY_FRAME_LIMIT = 5
    CAPTION_LEN_LIMIT = 100

    video_captions = []
    for video_meta in raw_data:
        print("="*40 + "\n")
        # 1) prompt for key frames 
        prompt = f""" 
        Identify Key Frames by timestamp in the provided video.
         A key frame should be unique, as in, different from other key frames.
         A key frame should also be representative, as in, representative of a larger group of frames wihtin the video.

         Identify {KEY_FRAME_LIMIT} key frames.
        """

        key_frames = run_query(prompt,video_meta['video_link'])

        # 2) attend to those key frames 
        key_frame_analysis = f"""
        An Oracle has supplied a list of key frames in the video. 

        Caption those key frames as if writing the pseudo code of an algorithim to perform the task the video displays. 

        Captions shall focus on a description of the actions performed in the video.

        Captions shall describe tools and implements. 

        Each key point should appear on a seperate line, and each line must have the following format: 
        <key frame minute>:<key frame second> | <key frame caption>

        Use at most {CAPTION_LEN_LIMIT} words. 

        Key frames: 

        {key_frames}
        """

        status, captions = run_query(key_frame_analysis,video_meta['video_link'])
        if status:
            try:
                raw_captions = captions['choices'][0]['message']['content']
                
                for raw_caption in raw_captions.split("\n"):
                    status, res = parse_raw_caption(raw_caption)
                    if status:
                        ts,txt = res 
                        video_captions.append((ts,txt,video_meta['video_link'],video_meta['video_id']))
            except:
                breakpoint()
                print("[WARNING] generation failed.")
                print(captions)
    return video_captions
    
    

def parse_raw_caption(raw_key_frame):
    try:
        timestamp, text = raw_key_frame.split("|")[0],raw_key_frame.split("|")[1]
        timestamp = timestamp.strip() # remove training whitespace
        text = text.strip()
        return True, (timestamp, text)
    except:
        return False, () 


def run_query(prompt,video_url):
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
        # "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        # "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    data=json.dumps({
        "model": "google/gemini-2.5-flash-preview-09-2025", # Optional
        "messages": [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT + prompt
                },
                {"type": "input_video",
                    "video_url" : {"url": video_url}}
            ]
        }
        ]
    })
    )
    try:
        return True, response.json()
    except:
        return False, None

import cv2
import os
from pytubefix import YouTube
from pathlib import Path

def extract_key_frame(video_url, minute, second, outfp) -> None:
    """
    Extract a frame from a YouTube video at the specified timestamp.
    
    Args:
        video_url: YouTube video URL
        minute: Minute timestamp
        second: Second timestamp
        outfp: Output filepath (should end in .mp4, but will save as .jpg)
    """
    # Download video to temporary location
    yt = YouTube(video_url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    
    # Create temporary directory if it doesn't exist
    temp_dir = Path("temp_downloads")
    temp_dir.mkdir(exist_ok=True)
    
    print(f"Downloading video: {yt.title}")
    temp_video_path = stream.download(output_path=str(temp_dir))
    
    try:
        # Open video with OpenCV
        cap = cv2.VideoCapture(temp_video_path)
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        # Calculate target frame number
        target_time = minute * 60 + second
        # breakpoint()
        if target_time > duration:
            raise ValueError(f"Timestamp {minute}:{second} exceeds video duration of {duration:.2f} seconds")
        
        target_frame = int(target_time * fps)
        
        # Set frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        
        # Read the frame
        ret, frame = cap.read()
        
        if not ret:
            print("[WARNING] Failed to extract frame from video \n")
        else:
            # Save frame as image (change extension to .jpg if outfp ends with .mp4)
            output_path = outfp.replace('.mp4', '.jpg') if outfp.endswith('.mp4') else outfp
            cv2.imwrite(output_path, frame)
            
            print(f"Frame extracted and saved to: {output_path}")
            
        # Release video capture
        cap.release()
        
    finally:
        # Clean up temporary video file
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
            print(f"Cleaned up temporary file: {temp_video_path}")


if __name__ == "__main__":
    from datetime import datetime
    DS_PATH = 'captioned_data'
    captions = load_raw_ds(dsfp="data/Med-Instr-Hierarchical/test.json")
   
    for caption in captions:
        ts,txt,url,id = caption 
        id = id + str(datetime.now().microsecond)
        min,sec = int(ts.split(':')[0]),int(ts.split(':')[1])
        extract_key_frame(url, minute=min, second=sec, outfp=f"{DS_PATH}/{id}.mp4")
        with open(f"{DS_PATH}/{id}_caption.txt",'w') as fout:
            fout.write("[trigger] " + txt)

