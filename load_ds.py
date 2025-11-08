import json
from pytubefix import YouTube

def load_json(fp,filter="label:Medical Instructional",limit = 10):
    parsed_data = []
    cnt = 0 
    key, val = filter.split(':')[0],filter.split(':')[1]
    with open(fp,'r') as fin:
        data = json.load(fin)
        for entry in data: 
            if limit and cnt >= limit:
                break 
            if entry[key] == val:
                parsed_data.append(entry)
            cnt +=1 
    return parsed_data

def download_video(video_meta,dataset_path,fname):
    url = video_meta['video_link']
    yt = YouTube(url)
    try: 
        stream = yt.streams.first()
        if stream:
            # Download the video to the specified path
            print(f"Downloading '{yt.title}' to '{dataset_path}'...")
            stream.download(output_path=dataset_path,
                            filename=fname)
            print("Download complete!")
        else:
            print("No suitable stream found for download.")
    except:
        print(f"failed to download {url}")

if __name__ == "__main__":  
    meta = load_json('data/test.json')
    download_video(meta,"data")

