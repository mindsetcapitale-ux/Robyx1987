import customtkinter as ctk
import threading
import subprocess
import os
import speech_recognition as sr

ORANGE = "#ff7b00"
CYAN = "#00eaff"
GREEN = "#00ff99"
BG = "#05080d"
PANEL = "#0b1118"
PANEL2 = "#101722"
VOCE = "Luca"

ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.geometry("1300x780")
app.title("JARVIS AI - Stable Core")
app.configure(fg_color=BG)

def parla(testo):
    subprocess.Popen(["say", "-v", VOCE, testo])

def log(testo):
    terminale.insert("end", testo + "\n")
    terminale.see("end")

def chiedi_ai(domanda):
    prompt = f"""
    Rispondi sempre in italiano.
    Sei Jarvis, assistente personale di Roberto.
    Rispondi breve, chiaro e pratico.

    Domanda: {domanda}
    """

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

    elif "apri chatgpt" in comando:
        os.system("open https://chatgpt.com")
        risposta = "Apro ChatGPT."

    else:
        status.configure(text="STATO: ELABORAZIONE", text_color=ORANGE)
        log("Jarvis: Sto pensando...")
        risposta = chiedi_ai(testo)

    log("Jarvis: " + risposta)
    log("")
    status.configure(text="STATO: ONLINE", text_color=GREEN)
    parla(risposta)

def invia():
    testo = entry.get()
    entry.delete(0, "end")
    threading.Thread(target=rispondi, args=(testo,), daemon=True).start()

def ascolta():
    def lavoro():
        recognizer = sr.Recognizer()

        try:
            status.configure(text="STATO: ASCOLTO", text_color=CYAN)
            log("Jarvis: Ti ascolto...")

            with sr.Microphone(device_index=0) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)

            testo = recognizer.recognize_google(audio, language="it-IT")
            log("Microfono: " + testo)
            rispondi(testo)

        except Exception as e:
            log("Errore microfono: " + str(e))
            status.configure(text="STATO: ONLINE", text_color=GREEN)

    threading.Thread(target=lavoro, daemon=True).start()

# SIDEBAR

sidebar = ctk.CTkFrame(app, width=230, fg_color="#070b10", corner_radius=0)
sidebar.pack(side="left", fill="y")

ctk.CTkLabel(
    sidebar,
    text="JARVIS",
    font=("Arial", 38, "bold"),
    text_color=ORANGE
).pack(pady=(35, 0), padx=22, anchor="w")

ctk.CTkLabel(
    sidebar,
    text="AI CORE SYSTEM",
    font=("Arial", 13),
    text_color="#aaaaaa"
).pack(pady=(0, 30), padx=22, anchor="w")

for item in ["DASHBOARD", "VOCE", "MICROFONO", "AGENTI", "MEMORIA", "CRYPTO"]:
    ctk.CTkButton(
        sidebar,
        text=item,
        height=44,
        fg_color=PANEL2,
        hover_color=ORANGE,
        corner_radius=12,
        anchor="w",
        font=("Arial", 14, "bold")
    ).pack(fill="x", padx=18, pady=7)

# MAIN

main = ctk.CTkFrame(app, fg_color=BG)
main.pack(side="left", fill="both", expand=True)

top = ctk.CTkFrame(main, fg_color=BG)
top.pack(fill="x", padx=22, pady=18)

ctk.CTkLabel(
    top,
    text="JARVIS OPERATIVE DASHBOARD",
    font=("Arial", 30, "bold"),
    text_color="white"
).pack(anchor="w")

status = ctk.CTkLabel(
    top,
    text="STATO: ONLINE",
    font=("Arial", 17, "bold"),
    text_color=GREEN
)
status.pack(anchor="w", pady=(4, 0))

cards = ctk.CTkFrame(main, fg_color=BG)
cards.pack(fill="x", padx=22, pady=(0, 12))

def card(titolo, valore, colore):
    box = ctk.CTkFrame(cards, width=210, height=82, fg_color=PANEL, corner_radius=16)
    box.pack(side="left", padx=(0, 14))
    box.pack_propagate(False)

    ctk.CTkLabel(
        box,
        text=titolo,
        font=("Arial", 12),
        text_color="#999999"
    ).pack(anchor="w", padx=16, pady=(12, 0))

    ctk.CTkLabel(
        box,
        text=valore,
        font=("Arial", 24, "bold"),
        text_color=colore
    ).pack(anchor="w", padx=16)

card("VOICE", "LUCA", ORANGE)
card("MIC", "READY", CYAN)
card("AI", "OLLAMA", GREEN)
card("MODE", "LOCAL", ORANGE)

core = ctk.CTkFrame(main, fg_color=PANEL, corner_radius=18)
core.pack(fill="both", expand=True, padx=22, pady=10)

ctk.CTkLabel(
    core,
    text="TERMINALE JARVIS",
    font=("Arial", 18, "bold"),
    text_color=ORANGE
).pack(anchor="w", padx=20, pady=(18, 8))

terminale = ctk.CTkTextbox(
    core,
    fg_color="#070b10",
    text_color="white",
    font=("Menlo", 15),
    border_width=1,
    border_color="#1b2b3b"
)
terminale.pack(fill="both", expand=True, padx=20, pady=(0, 20))

bottom = ctk.CTkFrame(main, fg_color=BG)
bottom.pack(fill="x", padx=22, pady=(0, 20))

entry = ctk.CTkEntry(
    bottom,
    width=720,
    height=58,
    placeholder_text="Scrivi un comando...",
    font=("Arial", 18),
    fg_color="#070b10",
    border_color="#1b2b3b"
)
entry.pack(side="left", padx=(0, 12))
entry.bind("<Return>", lambda event: invia())

ctk.CTkButton(
    bottom,
    text="🎤",
    width=80,
    height=58,
    fg_color=ORANGE,
    hover_color="#ff9900",
    text_color="black",
    font=("Arial", 26),
    command=ascolta
).pack(side="left", padx=8)

ctk.CTkButton(
    bottom,
    text="INVIA",
    width=170,
    height=58,
    fg_color=ORANGE,
    hover_color="#ff9900",
    text_color="black",
    font=("Arial", 18, "bold"),
    command=invia
).pack(side="left", padx=8)

log("Jarvis online.")
log("Sistema stabile caricato.")
log("Microfono e voce pronti.")
log("")

app.mainloop()