import requests
import json
import mimetypes
import subprocess
import os
import re
import time
# from urllib.parse import urlparse
# import shutil

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


def video_to_audio(url,output_format="mp3") -> str:
    #检查视频文件是否存在
    if not check_local_file_exists(url):
        print('given url does not exist')
        return None
    
    # 从URL中提取文件名
    file_name_with_ext = os.path.basename(url)
    file_name, _ = os.path.splitext(file_name_with_ext)

    # 构建输出文件名
    output_file = f"audio_files/{file_name}.{output_format}"


    # 检查音频文件是否存在
    if check_local_file_exists(output_file):
        print(f"output file already exists: {output_file}")
        return output_file


    # 构建ffmpeg命令
    ffmpeg_command = [
        "ffmpeg",
        "-i", url,
        "-vn",
        "-acodec", "libmp3lame",
        output_file
    ]

    # 运行ffmpeg命令
    print(f"Converting file to audio: {url}")
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"File converted successfully: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
    return None


def download_video(url): 
    """
    Downloads a video from a given URL.
    
    Args:
        url (str): The URL of the video.
        
    Returns:
        str: The path to the downloaded video file.
    """
    pass


def voice_to_text(file_path) -> str:
    """
    Uploads a media file and retrieves the text transcription.
    
    Args:
        file_path (str): The path to the media file (e.g., 'audio.wav').
        
    Returns:
        dict: A dictionary containing the response data.
    """
    url = "http://192.168.2.124:7777/api/v0/openai/whisper/transcribe"
    # file_path = os.path.join('C:/Users/skyliu/Documents/GitHub/Handbook', file_path)
    #检查音频文件是否存在
    if not check_local_file_exists(file_path):
        print('given url does not exist')
        return None
    

    # 从URL中提取文件名
    file_name_with_ext = os.path.basename(file_path)
    file_name, _ = os.path.splitext(file_name_with_ext)

    # 将JSON数据保存到文件
    output_file = f"C:/Users/skyliu/Documents/GitHub/Handbook/text_output_files/{file_name}.json"

    #检查输出文件是否存在
    if check_local_file_exists(output_file):
        print(f'{output_file} already exists')
        return output_file
    
    print(f"Converting audio to text: {url}")
    headers = {}
    content_type, _ = mimetypes.guess_type(file_path)
    response = None
    if not content_type:
        content_type = "application/octet-stream"
    # files=[('media_file',(file_path, open(file_path,'rb'), content_type))]
    with open (file_path, 'rb') as file:
        if not file:
            print('file not found')
            return None
        

        files = {'media_file': (file_name, file, content_type)}
        payload={}
        
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
    


    if response.status_code == 200:
        data = response.json()   
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Response saved to {output_file}")
            return output_file

    else:
        print({"code": 100001, "data": None, "msg": "Failed to convert media file to text."})
        return None


# def move_file_to_done(url):
#     try:
#         # Ensure the source file exists
#         if not os.path.exists(source_path):
#             raise FileNotFoundError(f"The source file at {source_path} does not exist.")
        
#         # Ensure the destination directory exists, create if it doesn't
#         os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
#         # Move the file
#         shutil.move(source_path, destination_path)
#         print(f"File moved from {source_path} to {destination_path}")

#     except FileNotFoundError as e:
#         print(e)
#     except Exception as e:
#         print(f"An error occurred: {e}")

def call_llm(user_prompt, conversation_id = '7392518350112456711'):
    #send chat
    url = f'https://api.coze.com/v3/chat?conversation_id={conversation_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': "Bearer pat_IM2daM17zmIfuBq9LEfrd6FBsBEV2jOkFb2tyb6w8TihBTiuaHcvIIP1eAhJWnqt"
    }
    data = {
        "bot_id": "7392503554168422408",
        "user_id": "7389475480333942800",
        "stream": False,
        "auto_save_history":True,
        "additional_messages":[
            {
                "role":"user",
                "content":f"{user_prompt}",
                "content_type":"text"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    while data['code'] != 0:
        time.sleep(5)
        print(data)
        response = requests.post(url, headers=headers, json=data)
        data = response.json()
    chat_id = data['data']['id']
    while True:
        url = f'https://api.coze.com/v3/chat/retrieve?chat_id={chat_id}&conversation_id={conversation_id}'
        response = requests.get(url, headers=headers)
        if not response.json()['data']['status'] == 'completed':
            time.sleep(5)
            continue

        url = f"https://api.coze.com/v3/chat/message/list?chat_id={chat_id}&conversation_id={conversation_id}"
        response = requests.get(url, headers=headers)
        data = response.json()
        for message in data['data']:
            if message['type'] == 'answer':
                return message['content']
        return None

def split_string_with_overlap(input_string, max_length=7000, overlap=1000):
    # Split the input string into words
    words = input_string.split()
    total_words = len(words)
    
    # Check if the total number of words is greater than 8000
    if total_words <= 8000:
        return [input_string]
    
    # Initialize the list to hold the segments
    segments = []
    
    # Split the words into segments with overlap
    start = 0
    while start < total_words:
        end = min(start + max_length, total_words)
        segment = ' '.join(words[start:end])
        segments.append(segment)
        start += (max_length - overlap)
    
    return segments

def call_llm2(pre_prompt = '', user_prompt='hello there',system_prompt = "give json file", is_stream = False,temperature=0.2, top_p=0.3):
    url = 'http://192.168.2.95:10000/api/llm/internlm2-chat-20b/generation'
    # url = 'http://192.168.2.143:10000/api/llm/deepseek_v2-lite/generation'


    # list_of_prompts = split_string_with_overlap(user_prompt)
    # return_list = []
    # for each_prompt in list_of_prompts:
    data = {"model": "deepseek_v2-lite",
            "messages": [{"role":"system","content": system_prompt},{"role":"user","content": pre_prompt+user_prompt}],
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
                final_response = response_data
            return final_response
            # return_list.append(final_response)
        else:
            print('Failed to retrieve data:', response.status_code)
            # return []
# return return_list


def get_absolute_paths(folder_path):
    try:
        # Ensure the folder exists
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"The folder at {folder_path} does not exist.")
        
        # List all files and directories in the folder
        items = os.listdir(folder_path)
        
        # Get absolute paths of all files
        absolute_paths = [os.path.abspath(os.path.join(folder_path, item)) for item in items if os.path.isfile(os.path.join(folder_path, item))]
        
        return absolute_paths
    
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")

def text_to_handbook(json_input_url):
    #检查音频文件是否存在
    if not check_local_file_exists(json_input_url):
        print('given url does not exist')
        return None
    

    # 从URL中提取文件名
    file_name_with_ext = os.path.basename(json_input_url)
    file_name, _ = os.path.splitext(file_name_with_ext)

    # 将JSON数据保存到文件
    output_file = f"C:/Users/skyliu/Documents/GitHub/Handbook/handbook_files/{file_name}.json"


    #检查输出文件是否存在
    if check_local_file_exists(output_file):
        print(f'{output_file} already exists')
        return output_file
    

    prompt_handbook = """Given text input wrapped by <>.
      The text input might contain typos, duplicates, other kinds of errors. Do the following:
      1. Add punctuations if it absent, clean it up, split the content to paragraph
      2. for each paragraph, summary the paragraph context into Knowledge Point for around 30 words
      3. Translate the output to English. Transform the paragraph context and Knowledge Point into json format like:  
      {     "Title": "title",    
      "Content": [        
        {             "Knowledge Point": Knowledge Point 1,           
            "Text": "paragraph content1"         }, {             
            "Knowledge Point": Knowledge Point 2,             "Text": "paragraph content2"         }, }  

            text input : <>"""
    
    
    """Given text input wrapped by <>.
      The text input might contain typos, duplicates, other kinds of errors. Do the following:
      1. Add punctuations if it absent, clean it up, split the content to paragraph
            text input : <>"""
    print(f"Converting text to handbook: {json_input_url}")
    try:
        # Ensure the file exists
        with open(json_input_url, 'r', encoding='utf-8') as file:
            # Read the file content as a string
            json_string = file.read()
            data = call_llm2(prompt_handbook, json_string)
            if data is None:
                return None
            json_match = re.search(r'```json\n(.*?)\n```', data, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
                with open(output_file, 'w', encoding='utf-8') as f:
                    data = json.loads(json_content)
                    # if "Title" in data:
                    #     data["Title"] = file_name
                    list_tmp = list()
                    list_tmp.append(data)
                    json.dump(list_tmp, f, ensure_ascii=False, indent=4)
                    print(f"Response saved to {output_file}")
                    return output_file
            

    
    except FileNotFoundError as e:
        print(f"The file at {json_input_url} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

# text_to_handbook(r"C:\Users\skyliu\Documents\GitHub\Handbook\text_output_files\Embracing the Simple Life ｜ Tao Te Ching Chapter 80.json")

def text_to_knowledge_point(json_input_url):
    #检查音频文件是否存在
    if not check_local_file_exists(json_input_url):
        print('given url does not exist')
        return None
    

    # 从URL中提取文件名
    file_name_with_ext = os.path.basename(json_input_url)
    file_name, _ = os.path.splitext(file_name_with_ext)

    # 将JSON数据保存到文件
    output_file = f"C:/Users/skyliu/Documents/GitHub/Handbook/knowledge_base_files/{file_name}.json"

    #检查输出文件是否存在
    if check_local_file_exists(output_file):
        print(f'{output_file} already exists')
        return output_file
    

    prompt_knowledge_point = """
Given text input wrapped by <>.
      The text input might contain typos, duplicates, other kinds of errors. Do the following:
      1. Add punctuations if it absent, reduce duplicates, remove personal introduction and translate to English if not. 
      2.give me 3 key ideas
      3.for each key point, answer this question in 150 to 300 words in instructional tone:  how can I make a good content for my post
      4. reformat each key point to : Title, Keywords, Content like:  
    [{
        Title: knowledge idea 1,
        Keywords: [keyword1, keyword2],
        Content:content1,
    },
        {
        Title: knowledge idea 2,
        Keywords: [keyword1, keyword2],
        Content:content2,
    },]
5. warp results from 4 and return a json list and return this json list

text input : <>
    """
    # """
    # Based on the json file below, 
    #     1. figure out what category or topic the article is about, give me a list of keywords, make sure the topic is related to the article
    #     2. give me at most 300 english words concise advice and reason behind, don't make it up
    #     3. give me in json format like:
    #     {
    #     "Title": "the_title",
    #     "Keywords": [keyword1, keyword2],
    #     "Content": "advices"
    #     }
    #     input json: 
    #     """    
    
    print(f"Converting text to knowledge point: {json_input_url}")

    try:
        # Ensure the file exists
        with open(json_input_url, 'r', encoding='utf-8') as file:
            # Read the file content as a string
            json_string = file.read()
            data = call_llm(prompt_knowledge_point + json_string)
            if data is None:
                return None
            # json_match = re.search(r'```json\n(.*?)\n```', data, re.DOTALL)
            # if json_match:
            #     data = json_match.group(1)
            with open(output_file, 'w', encoding='utf-8') as f:
                data = json.loads(data)
                # if "Title" in data:
                #     data["Title"] = file_name
                data = data['key_ideas']
                # list_tmp = list()
                # list_tmp.append(data)
                json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"Response saved to {output_file}")
                return output_file
            

    
    except FileNotFoundError as e:
        print(f"The file at {json_input_url} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")



if __name__ == "__main__":
    paths = get_absolute_paths(r"C:\Users\skyliu\Documents\GitHub\Handbook\audio_files")
    # (r"D:\vt-dlp\vt-dlp downloads")
    for path in paths:
        # audio_path = video_to_audio(path)
        # if audio_path == None:
        #     continue
        done = voice_to_text(path)
        
        if done is not None:
            # handbook_text_url = text_to_handbook(done)
            text_to_knowledge_point(done)
