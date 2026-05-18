import customtkinter as ctk
import threading
import subprocess
import os
import speech_recognition as sr

ORANGE = "#ff7b00"
BG = "#05080d"
PANEL = "#0b1118"
GREEN = "#00ff99"
CYAN = "#00eaff"
VOCE = "Luca"

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("1200x750")
app.title("JARVIS AI")
app.configure(fg_color=BG)

def parla(testo):
    subprocess.Popen(["say", "-v", VOCE, testo])

def log(testo):
    terminale.insert("end", testo + "\n")
    terminale.see("end")

def chiedi_ai(domanda):
    prompt = f"Rispondi sempre in italiano, breve e chiaro. Domanda: {domanda}"
    result = subprocess.run(
        ["ollama", "run", "llama3", prompt],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def rispondi(testo):
    if testo.strip() == "":
        return

    log("Roberto: " + testo)
    comando = testo.lower()

    if "ciao" in comando:
        risposta = "Ciao Roberto, sono online."

    elif "chi sei" in comando:
        risposta = "Sono Jarvis, il tuo assistente personale."

    elif "apri youtube" in comando:
        os.system("open https://youtube.com")
        risposta = "Apro YouTube."

    elif "apri google" in comando:
        os.system("open https://google.com")
        risposta = "Apro Google."

    else:
        log("Jarvis: Sto pensando...")
        risposta = chiedi_ai(testo)

    log("Jarvis: " + risposta)
    log("")
    parla(risposta)

def invia():
    testo = entry.get()
    entry.delete(0, "end")
    threading.Thread(target=rispondi, args=(testo,), daemon=True).start()

def ascolta():
    def lavoro():
        recognizer = sr.Recognizer()

        try:
            log("Jarvis: Ti ascolto...")

            with sr.Microphone(device_index=0) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)

            testo = recognizer.recognize_google(audio, language="it-IT")
            log("Microfono: " + testo)
            rispondi(testo)

        except Exception as e:
            log("Errore microfono: " + str(e))

    threading.Thread(target=lavoro, daemon=True).start()

title = ctk.CTkLabel(
    app,
    text="JARVIS AI",
    font=("Arial", 42, "bold"),
    text_color=ORANGE
)
title.pack(pady=25)

status = ctk.CTkLabel(
    app,
    text="ONLINE • Sistema operativo",
    font=("Arial", 18, "bold"),
    text_color=GREEN
)
status.pack(pady=5)

terminale = ctk.CTkTextbox(
    app,
    width=1000,
    height=450,
    fg_color=PANEL,
    text_color="white",
    font=("Menlo", 15),
    border_color=ORANGE,
    border_width=2
)
terminale.pack(pady=25)

bottom = ctk.CTkFrame(app, fg_color=BG)
bottom.pack(pady=10)

entry = ctk.CTkEntry(
    bottom,
    width=700,
    height=55,
    placeholder_text="Scrivi un comando...",
    font=("Arial", 18)
)
entry.grid(row=0, column=0, padx=10)
entry.bind("<Return>", lambda event: invia())

btn_mic = ctk.CTkButton(
    bottom,
    text="🎤",
    width=80,
    height=55,
    fg_color=ORANGE,
    text_color="black",
    font=("Arial", 24),
    command=ascolta
)
btn_mic.grid(row=0, column=1, padx=10)

btn_send = ctk.CTkButton(
    bottom,
    text="INVIA",
    width=160,
    height=55,
    fg_color=ORANGE,
    text_color="black",
    font=("Arial", 18, "bold"),
    command=invia
)
btn_send.grid(row=0, column=2, padx=10)

log("Jarvis online.")
log("Scrivi 'ciao' e premi INVIA.")
log("")

app.mainloop()