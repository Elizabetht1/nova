import modal

import pathlib
import shutil
import subprocess

# from load_ds import load_json


image = (
    modal.Image.debian_slim(python_version="3.13")
    .uv_pip_install("pytubefix")
)

volume = modal.Volume.from_name("nova-volume")
app = modal.App("example-get-started")


@app.function(
    volumes={"/mnt/": volume},
    image=image,
    timeout=60,  # 1 minute,
    # ephemeral_disk= 10,  # 10 MBs
)
def download_ds(videos_meta) -> None:
    import json
    from pytubefix import YouTube

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
    

    tmp_path = pathlib.Path("/tmp/nova/")
    vol_path = pathlib.Path("/mnt/nova/")
    vol_path.mkdir(exist_ok=True)

    for video_meta in videos_meta:
        fname = video_meta['video_id']
        download_video(video_meta,tmp_path,fname=fname)
        shutil.copy(tmp_path / f"{fname}.mp4", vol_path)

    # subprocess.run(f"tree -L 3 {vol_path}", shell=True, check=True)
    print("Dataset is loaded ✅")



@app.function()
def square(x):
    print("This code is running on a remote worker!")
    return x**2


def load_json(fp,filter="label:Medical Instructional",limit = 10):
    import json
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

@app.local_entrypoint()
def main():
    print("the square is", square.remote(42))
    download_ds.remote(load_json('data/train.json'))

    