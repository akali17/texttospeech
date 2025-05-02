from googletrans import Translator

def translate_text(text, dest_lang='en'):
    try:
        translator = Translator()
        translated = translator.translate(text, dest=dest_lang)
        return translated.text
    except Exception as e:
        return f"Lỗi khi dịch: {str(e)}"

