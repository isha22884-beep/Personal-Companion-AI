import tkinter as tk
import threading
import pyaudio
import numpy as np
import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import datetime
import smtplib
import struct
import pvporcupine
import math
import wikipedia

# TTS Engine Setup
engine = pyttsx3.init()
engine.setProperty('rate', 170)

EMAIL = "your_email@gmail.com"
PASSWORD = "your_app_password"

running = True
lang_mode = "english"

def speak(text):
    print("Ai:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            # Listen actively
            audio = r.listen(source, timeout=5, phrase_time_limit=5)

        return r.recognize_google(audio).lower()
    except Exception as e:
        print(f"Listen error: {e}")
        return ""

def choose_language():
    global lang_mode
    speak("Choose language: Hinglish, Hindi or English")
    cmd = listen()
    if "hinglish" in cmd:
        lang_mode = "hinglish"
        speak("Hinglish mode activated")
    elif "hindi" in cmd:
        lang_mode = "hindi"
        speak("Hindi mode activated")
    elif "english" in cmd:
        lang_mode = "english"
        speak("English mode activated")
    else:
        speak("Defaulting to English mode")
        lang_mode = "english"

def say(hindi, english, hinglish):
    if lang_mode == "hindi":
        speak(hindi)
    elif lang_mode == "hinglish":
        speak(hinglish)
    else:
        speak(english)

def send_email(to, content):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, to, content)
    server.quit()

def wake_word():
    # Note: Ensure you have a custom .ppn file for "Sarthi" or use default like "computer"
    try:
        porcupine = pvporcupine.create(
            access_key="AIzaSyCLNJ4j1WRlvK_tevlwDxUF5f4newUArgU",
            keywords=["computer"] # Using 'computer' as fallback if 'Sarthi' custom model isn't found
        )
    except Exception as e:
        print(f"Porcupine Init Error: {e}")
        return False

    pa = pyaudio.PyAudio()
    stream = pa.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)

    print("Listening for wake word...")
    while running:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        if porcupine.process(pcm) >= 0:
            say("जी बोलिए", "Yes, I am listening", "Haan bolo")

            # CRITICAL FIX: Close the stream to free up the mic for speech_recognition
            stream.stop_stream()
            stream.close()
            pa.terminate()
            porcupine.delete()
            return True

def execute(command):
    global running

    if "open youtube" in command:
        webbrowser.open("https://youtube.com")
        say("यूट्यूब खोल रहा हूँ", "Opening YouTube", "YouTube khol raha hoon")

    elif "search" in command:
        webbrowser.open("https://google.com/search?q=" + command.replace("search", ""))
        say("सर्च कर रहा हूँ", "Searching", "Search kar raha hoon")

    elif "wikipedia" in command:
        say("विकिपीडिया पर खोज रहा हूँ", "Searching Wikipedia", "Wikipedia par search kar raha hoon")
        try:
            result = wikipedia.summary(command.replace("wikipedia", ""), sentences=2)
            speak(result)
        except:
            say("कोई परिणाम नहीं मिला", "No result found", "Koi result nahi mila")

    elif "send email" in command:
        say("ईमेल बताओ", "Tell email", "Email bolo")
        to = listen().replace(" ", "")
        if to:
            say("मैसेज बताओ", "Tell message", "Message bolo")
            msg = listen()
            try:
                send_email(to, msg)
                say("ईमेल भेज दिया", "Email sent", "Email bhej diya")
            except:
                say("फेल हो गया", "Failed to send email", "Email fail ho gaya")

    elif "time" in command:
        t = datetime.datetime.now().strftime("%H:%M")
        say(f"समय है {t}", f"Time is {t}", f"Time hai {t}")

    elif "shutdown computer" in command:
        os.system("shutdown /s /t 1")

    elif "terminate sarth" in command:
        say("सार्थ बंद हो रहा है", "Sarth shutting down", "Sarth band ho raha hai")
        running = False
        root.destroy()

def assistant():
    choose_language()
    say("सार्थ शुरू हो गया", "Sarth online", "Sarth start ho gaya")
    while running:
        try:
            triggered = wake_word()
            if triggered:
                print("Listening for command...")
                cmd = listen()
                print(f"Command received: {cmd}")
                if cmd:
                    execute(cmd)
        except Exception as e:
            # CRITICAL FIX: Don't exit(0) here, just print and continue running
            print(f"Assistant loop error occurred: {e}")
            continue

def start():
    threading.Thread(target=assistant, daemon=True).start()

# --- GUI and Animation ---
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-transparentcolor", "black")
root.configure(bg="black")
root.geometry("400x400+1000+200")

canvas = tk.Canvas(root, width=400, height=400, bg="black", highlightthickness=0)
canvas.pack()

# Using a dummy value for amplitude so we don't lock the mic globally
angle = 0
def animate():
    global angle
    canvas.delete("all")

    # Replaced mic reading with a sine wave animation to prevent mic blocking
    amp = 1.2 + 0.5 * math.sin(angle * 2)

    cx, cy = 200, 200
    r_base = 70
    pts = []

    for i in range(100):
        a = (i / 100) * 2 * math.pi
        r = r_base + amp * 30 * math.sin(i * 3 + angle)
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        pts.append((x, y))

    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i+1) % len(pts)]
        canvas.create_line(x1, y1, x2, y2, fill="cyan", width=2)

    canvas.create_text(cx, cy, text="Ai", fill="cyan", font=("Arial", 14, "bold"))

    angle += 0.2

    if running:
        root.after(40, animate)

root.bind("<Escape>", lambda e: root.destroy())

start()
animate()

root.mainloop()