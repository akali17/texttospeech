from gtts import gTTS

def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    return tts


### file_utils.py
from PyQt5.QtWidgets import QFileDialog

def save_text_file(text):
    path, _ = QFileDialog.getSaveFileName(None, "Lưu văn bản", "output.txt", "Text Files (*.txt)")
    if path:
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)


def save_audio_file(tts_obj):
    path, _ = QFileDialog.getSaveFileName(None, "Lưu âm thanh", "output.mp3", "MP3 Files (*.mp3)")
    if path:
        tts_obj.save(path)
