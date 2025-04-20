import tkinter as tk
from threading import Thread
import os
import time
import requests

# === CONFIGURAZIONE ===
CARTELLA_WATCH = "/Users/leonardo/Desktop/DomandeSottomesse"
TOKEN_BOT = "7743436623:AAHZwH_l20jG-G2YXqWpLCmiBgzDa0kn-Vo"
CHAT_ID = "194936543"

import os
import time
import hashlib
import requests
from threading import Thread

import os
import time
import hashlib
import requests
from threading import Thread

# Funzione per calcolare l'hash del file
def calcola_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

class Monitor(Thread):
    def __init__(self, folder, token, chat_id):
        super().__init__()
        self.folder = folder
        self.token = token
        self.chat_id = chat_id
        self.running = False
        self.visti = set(os.listdir(folder))  # File già visti
        self.files_inviati = {}  # Dizionario per memorizzare gli hash dei file inviati
        self.files_inviati_list = []  # Lista per raccogliere i file inviati durante la sessione

    def run(self):
        self.running = True
        while self.running:
            time.sleep(5)  # Attende 5 secondi tra i cicli
            attuali = set(os.listdir(self.folder))  # Legge i file correnti nella cartella
            nuovi = attuali - self.visti  # Trova i nuovi file

            for file in nuovi:
                if file.lower().endswith(".pdf"):  # Solo i file PDF
                    file_path = os.path.join(self.folder, file)
                    file_hash = calcola_hash(file_path)  # Calcola l'hash del file
                    
                    # Verifica se il file è stato modificato (confronto degli hash)
                    if file not in self.files_inviati or self.files_inviati[file] != file_hash:
                        if file in self.files_inviati:  # Il file è stato già inviato, ma è stato aggiornato
                            self.invia_notifica(file, aggiornato=True)
                        else:
                            self.invia_notifica(file, aggiornato=False)  # Prima volta che inviamo il file
                        self.files_inviati[file] = file_hash  # Memorizza l'hash del file inviato
                        self.files_inviati_list.append(file)  # Aggiungi il nome del file alla lista
                        print(f"📤 Notifica e PDF inviati per: {file}")
            
            self.visti = attuali  # Aggiorna i file visti

    def stop(self):
        self.running = False
        self.invia_recap()  # Invia il recap al gruppo Telegram quando l'ascolto viene interrotto

    def invia_notifica(self, nome_file, aggiornato=False):
        if aggiornato:
            messaggio = f"⚠️ ATTENZIONE: Il file inviato precedentemente è stato aggiornato. Ecco la nuova versione: {nome_file}"
        else:
            messaggio = f"✅ Domanda inviata: {nome_file}"  # Messaggio di notifica
        
        file_path = os.path.join(self.folder, nome_file)  # Percorso completo del file

        # URL per inviare il documento tramite Telegram
        url = f"https://api.telegram.org/bot{self.token}/sendDocument"
        
        try:
            # Invio del PDF come documento tramite Telegram
            with open(file_path, 'rb') as file:
                requests.post(url, data={"chat_id": self.chat_id, "caption": messaggio}, files={"document": file})
            print(f"📤 PDF {nome_file} inviato con successo!")
        except Exception as e:
            print(f"Errore durante invio PDF su Telegram: {e}")

    def invia_recap(self):
        # Creiamo il messaggio di recap con tutte le aggiunte della sessione
        recap_message = "📋 Recap delle domande inviate:\n\n"
        if not self.files_inviati_list:
            recap_message += "Non ci sono domande inviate nella sessione.\n"
        else:
            for file in self.files_inviati_list:
                recap_message += f"✅ {file}\n"
        
        # Invia il recap a tutti nel gruppo Telegram
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            requests.post(url, data={"chat_id": self.chat_id, "text": recap_message})
            print("📤 Recap inviato con successo!")
        except Exception as e:
            print(f"Errore durante invio recap su Telegram: {e}")


# === GUI ===
def avvia():
    global monitor
    monitor = Monitor(CARTELLA_WATCH, TOKEN_BOT, CHAT_ID)
    monitor.start()
    stato_label.config(text="🟢 Monitoraggio attivo")

def ferma():
    if monitor:
        monitor.stop()
        stato_label.config(text="🔴 Monitoraggio fermato")

# Finestra
finestra = tk.Tk()
finestra.title("Notifiche Domanda")
finestra.geometry("300x150")

tk.Button(finestra, text="Avvia Monitoraggio", command=avvia).pack(pady=10)
tk.Button(finestra, text="Ferma Monitoraggio", command=ferma).pack(pady=10)
stato_label = tk.Label(finestra, text="🔴 Inattivo")
stato_label.pack(pady=10)

monitor = None
finestra.mainloop()