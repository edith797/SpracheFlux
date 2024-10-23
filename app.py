import os
import speech_recognition as sr
from flask import Flask, render_template, request, jsonify
from googletrans import Translator
from pydub import AudioSegment

app = Flask(__name__)

# Initialize Google Translator
translator = Translator()

def translate_text(text, src_lang, target_lang):
    translation = translator.translate(text, src=src_lang, dest=target_lang)
    return translation.text

def live_speech_to_text_translation(src_lang, target_lang):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for speech...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language=src_lang)
        translation = translate_text(text, src_lang, target_lang)
        return text, translation
    except Exception as e:
        return None, str(e)

def upload_and_translate_audio(file_path, src_lang, target_lang):
    audio = AudioSegment.from_file(file_path)
    audio.export("temp.wav", format="wav")  # Convert to WAV for recognition

    recognizer = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language=src_lang)
            translation = translate_text(text, src_lang, target_lang)
            return text, translation
        except Exception as e:
            return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live_translate', methods=['POST'])
def live_translate():
    src_lang = request.form['src_lang']
    target_lang = request.form['target_lang']
    original, translation = live_speech_to_text_translation(src_lang, target_lang)
    return jsonify({'original': original, 'translation': translation})

@app.route('/upload_translate', methods=['POST'])
def upload_translate():
    file = request.files['audio_file']
    src_lang = request.form['src_lang']
    target_lang = request.form['target_lang']
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    original, translation = upload_and_translate_audio(file_path, src_lang, target_lang)
    return jsonify({'original': original, 'translation': translation})

@app.route('/text_translate', methods=['POST'])
def text_translate():
    src_lang = request.form['src_lang']
    target_lang = request.form['target_lang']
    text = request.form['text']
    translation = translate_text(text, src_lang, target_lang)
    return jsonify({'translation': translation})

if __name__ == "__main__":
    app.run(debug=True)
