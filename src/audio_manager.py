import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

class AudioManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def text_to_speech(self, text: str) -> str:
        """Generates MP3 from text and returns path."""
        try:
            tts = gTTS(text=text, lang='en') # Or 'de' based on language
            # Create a unique temp file
            fd, path = tempfile.mkstemp(suffix='.mp3')
            os.close(fd)
            tts.save(path)
            return path
        except Exception as e:
            print(f"TTS Error: {e}")
            return None

    def speech_to_text(self, audio_source) -> str:
        """Transcribes audio from a file path or file-like object."""
        try:
            # sr.AudioFile supports file paths or file-like objects (wav/aiff/flac)
            with sr.AudioFile(audio_source) as source:
                # Adjust for ambient noise if needed, but for direct input might not be necessary
                # self.recognizer.adjust_for_ambient_noise(source)
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results; {e}"
        except Exception as e:
            return f"Transcription error: {str(e)}"
