import requests

url = "http://192.168.2.124:7777/api/v0/openai/whisper/transcribe"

payload={}
files=[
   ('media_file',('extracted_audio.wav',open('extracted_audio.wav','rb'),'audio/wav'))
]
headers = {
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)
