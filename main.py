import requests
import json
import mimetypes
import subprocess
import os
from urllib.parse import urlparse

"""_summary_
this file has three parts:
1. read in a local video/ video
2. convert it to text
3. call the LLM model to generate a response that make sense
4. seperate it by paragraphs and then call the LLM model to generate a summary
5. make the summary and the response into a json file
5. save the json file in mongodb
"""


def check_local_file_exists(url):
    return os.path.exists(url)


def video_to_audio(url,output_format="mp3"):
    #检查视频文件是否存在
    if not check_local_file_exists(url):
        print('given url does not exist')
        return
    



    # 定义ffmpeg的路径和参数
    ffmpeg_path = "ffmpeg.exe"

    # 从URL中提取文件名
    file_name_with_ext = os.path.basename(url)
    file_name, _ = os.path.splitext(file_name_with_ext)

    # 构建输出文件名
    output_file = f"audio_files/{file_name}.{output_format}"


    # 检查音频文件是否存在
    if check_local_file_exists(output_file):
        print(f"output file already exists: {output_file}")
        return


    # 构建ffmpeg命令
    ffmpeg_command = [
        "ffmpeg",
        "-i", url,
        "-vn",
        "-acodec", "libmp3lame",
        output_file
    ]

    # 运行ffmpeg命令
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"File converted successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

video_to_audio(r"C:\Users\skyliu\Documents\GitHub\Handbook\video_files\【哲学性】你我是否还囿于“自我提升”中？【Sisyphus 55】.mp4")

def video_to_text(url):

    

    #检查文件是否存在
    input_file_path = None
    if not check_local_file_exists(url):
        return
        print(f"{parsed_url} not exists,try downloading audio in media files folder")
        input_file_path = download_video(url)
    else :
        input_file_path = url

    #生成文本
    output_file_path = f"{file_name}"
    ffmpeg_command = [ffmpeg_path, "-i", input_file_path, output_file_path]

def download_video(url): 
    """
    Downloads a video from a given URL.
    
    Args:
        url (str): The URL of the video.
        
    Returns:
        str: The path to the downloaded video file.
    """
    pass

def voice_to_text(file_path):
    """
    Uploads a media file and retrieves the text transcription.
    
    Args:
        file_path (str): The path to the media file (e.g., 'audio.wav').
        
    Returns:
        dict: A dictionary containing the response data.
    """
    url = "http://192.168.2.124:7777/api/v0/openai/whisper/transcribe"
    headers = {}
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"
    files = files=[
   ('media_file',('extracted_audio.wav',open('extracted_audio.wav','rb'),'audio/wav'))
]
    payload={}
    
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"code": 100001, "data": None, "msg": "Failed to convert media file to text."}

response = voice_to_text("extracted_audio.wav")

def call_llm(self, prompt, temperature=0.2, top_p=0.3, is_stream=False):
    url = 'http://192.168.2.95:10010/api/llm/internlm2/decision'

    data = {"model": "internlm2-chat-20B",
            "prompt": prompt,
            "stream": is_stream,
            "temperature": temperature,
            "top_p": top_p
            }

    with requests.post(url, json=data, stream=is_stream) as response:
        if response.status_code == 200:
            final_response = ''
            if data["stream"]:
                for chunk in response.iter_content(chunk_size=None):
                    message = chunk
                    llm_response = message.decode('utf-8')
                    if llm_response != "[DONE]":
                        temp = json.loads(llm_response)['data']
                    final_response += temp
            else:
                response_data = response.json()
                final_response = response_data.encode('utf-8').decode('unicode_escape')
            return final_response
        else:
            print('Failed to retrieve data:', response.status_code)

