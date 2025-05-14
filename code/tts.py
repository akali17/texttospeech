from gtts import gTTS

def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    return tts
