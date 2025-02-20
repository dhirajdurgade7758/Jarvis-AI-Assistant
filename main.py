import speech_recognition as sr
import webbrowser
import pyttsx3
from musicLibrary import music
import requests
from openai import OpenAI
import os

# Initialize recognizer and text-to-speech engine
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300  # Lower to make it more sensitive
recognizer.pause_threshold = 0.5  # Reduce pause detection time
engine = pyttsx3.init()

def speak(text):
    """Speak text more slowly with a male voice"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    for voice in voices:
        if "male" in voice.name.lower():  # Try to find a male voice
            engine.setProperty('voice', voice.id)
            break

    engine.setProperty('rate', 130)  # Slower speech speed
    engine.say(text)
    engine.runAndWait()

def aiProcess(command):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a virtual assistant named Jarvis, skilled in general tasks. Give short responses."},
            {"role": "user", "content": command}
        ]
    )

    return completion.choices[0].message.content

def processCommand(command):
    """Process recognized commands"""
    command = command.lower()
    print(f"Command received: {command}")

    if "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif "search" in command:
        query = command.replace("search", "").strip()
        speak(f"Searching for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    elif command.startswith("play"):
        song_name = command.replace("play", "").strip()
        song_library = {key.lower(): value for key, value in music.items()}

        if song_name.lower() in song_library:
            link = song_library[song_name.lower()]
            speak(f"Playing {song_name}")
            webbrowser.open(link)
        else:
            available_songs = ", ".join(music.keys())
            speak(f"Sorry, I couldn't find that song. Try one of these: {available_songs}")

    elif "news" in command:
        API_KEY = os.getenv("NEWS_API_KEY")
        URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"

        try:
            response = requests.get(URL)
            data = response.json()

            if data["status"] == "ok":
                articles = data["articles"]
                speak("Top headlines are:")
                for i, article in enumerate(articles[:5], 1):
                    print(f"{i}. {article['title']}")
                    speak(f"{i}. {article['title']}")
                    print(f"   {article['url']}\n")
            else:
                print("Error fetching news:", data["message"])
        except Exception as e:
            print("Failed to fetch news:", e)

    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
        exit()
    else:
        ans = aiProcess(command)
        speak(ans)

def listen_for_wake_word():
    """Continuously listen for 'Jarvis' and execute commands"""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening for wake word 'Jarvis'...")

        while True:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                word = recognizer.recognize_google(audio).lower()

                if "jarvis" in word:
                    speak("Yes?")
                    print("Jarvis activated...")

                    # Listen for command
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = recognizer.recognize_google(audio)
                    processCommand(command)

            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError:
                print("Could not request results. Check internet connection.")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == '__main__':
    speak("Initializing Jarvis...")
    listen_for_wake_word()
