import pytest
import main
import os


def test_audio_to_text():
    response = main.voice_to_text("extracted_audio.wav")
    if "code" in response:
        assert response["code"] == 100001
        assert response["msg"] == "Failed to convert media file to text."
        return
    
    print(response.text)

if __name__ == "__main__":
    pytest.main(['-vs', 'test.py'])