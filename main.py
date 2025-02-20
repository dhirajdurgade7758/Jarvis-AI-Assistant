import speech_recognition as sr
import webbrowser
import pyttsx3
from musicLibrary import music
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os

# Initialize recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def old_speak(text):
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()

# def speak(text):
#     tts = gTTS(text)
#     tts.save('temp.mp3')
#     # Initialize pygame mixer
#     pygame.mixer.init()

#     # Load the MP3 file
#     pygame.mixer.music.load("temp.mp3")  # Replace with your actual MP3 file path

#     # Play the MP3 file
#     pygame.mixer.music.play()

#     # Keep the program running so the music doesn't stop immediately
#     while pygame.mixer.music.get_busy():
#         continue  # Wait until the music finishes playing
#     pygame.mixer.music.unload()
#     os.remove("temp.mp3")

def speak(text):
    """Speak text using a male voice at medium speed"""
    engine = pyttsx3.init()

    # Set voice to male (change index if necessary)
    voices = engine.getProperty('voices')
    for voice in voices:
        if "male" in voice.name.lower():  # Try finding a male voice
            engine.setProperty('voice', voice.id)
            break  # Stop after finding a male voice

    # Set speech rate (default is ~200, reducing makes it slower)
    engine.setProperty('rate', 150)  # Adjust to your preference

    # Speak the text
    engine.say(text)
    engine.runAndWait()



def aiProcess(command):
    client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general task like alexa and google cloud. give short responces"},
            {
                "role": "user",
                "content": command
            }
        ]
    )

    return (completion.choices[0].message.content);


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
        song_name = command.replace("play", "").strip()  # Get full song name
        song_library = {key.lower(): value for key, value in music.items()}  # Case-insensitive match

        if song_name.lower() in song_library:
            link = song_library[song_name.lower()]
            speak(f"Playing {song_name}")
            webbrowser.open(link)
        else:
            # Suggest available songs
            available_songs = ", ".join(music.keys())
            speak(f"Sorry, I couldn't find that song. Try one of these: {available_songs}")

    elif "news" in command.lower():

        API_KEY = os.getenv("NEWS_API_KEY")
        URL = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"

        try:
            response = requests.get(URL)
            data = response.json()

            if data["status"] == "ok":
                articles = data["articles"]
                print("Top Headlines:\n")
                speak("Top headlines")
                for i, article in enumerate(articles[:5], 1):  # Limit to top 5 headlines
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

if __name__ == '__main__':
    speak("Initializing Jarvis...")
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for wake word 'Jarvis'...")

        while True:
            try:
                # Listen for wake word
                audio = recognizer.listen(source)
                word = recognizer.recognize_google(audio).lower()

                if word == "jarvis":
                    speak("Yes?")
                    print("Jarvis activated...")

                    # Listen for the actual command
                    audio = recognizer.listen(source)
                    command = recognizer.recognize_google(audio)
                    processCommand(command)

            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError:
                print("Could not request results. Check internet connection.")

            except KeyboardInterrupt:
                speak("Shutting down...")
                break

