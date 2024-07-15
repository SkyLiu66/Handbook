import requests
import json
import mimetypes
import subprocess

"""_summary_
this file has three parts:
1. read in a local video/ video
2. convert it to text
3. call the LLM model to generate a response that make sense
4. seperate it by paragraphs and then call the LLM model to generate a summary
5. make the summary and the response into a json file
5. save the json file in mongodb
"""

def media_to_text(file_path):
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

response = media_to_text("extracted_audio.wav")

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

