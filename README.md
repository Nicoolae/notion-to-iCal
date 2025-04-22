# 🗓️ Notion to iCalendar

Questo progetto permette di **esportare automaticamente eventi da uno o più database Notion** e convertirli in un **file `.ics` compatibile con Apple Calendar, Google Calendar, Outlook**, ecc.

## 🚀 Funzionalità

- Connessione a database Notion tramite API
- Pulizia e normalizzazione dei dati
- Generazione di un calendario `.ics` dinamico
- Hosting tramite Flask + Render o Docker
- Feed aggiornabile in tempo reale da client calendario

---

## 🧱 Requisiti

- Python 3.8+
- Un'integrazione Notion attiva (con token)
- Flask
- Docker (opzionale)
- Un account GitHub (per il deploy su Render)

---

## ⚙️ Setup locale

1. **Clona il repository**
   ```bash
   git clone https://github.com/Nicoolae/notion-to-iCal.git
   cd notion-to-iCal
   ```

2. **Crea un file `.env` nella root del progetto**
   ```env
   NOTION_TOKEN=secret_xxx
   DATABASE_ID_SCADENZE=xxx
   DATABASE_ID_CORSI=xxx
   ```

3. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Avvia il server Flask**
   ```bash
   flask run
   ```

5. Accedi a `http://localhost:5000/scadenze.ics` per vedere il feed iCal

---

## 🐳 Uso con Docker (opzionale)

1. Costruisci l'immagine:
   ```bash
   docker build -t notion-to-ical .
   ```

2. Avvia il container:
   ```bash
   docker run -p 5000:5000 --env-file .env notion-to-ical
   ```

---

## ☁️ Deploy su Render

1. Crea un repo su GitHub e pusha il progetto.
2. Vai su [Render](https://render.com), crea un nuovo **Web Service**.
3. Configura:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `flask run --host=0.0.0.0 --port=$PORT`
4. Aggiungi le variabili d’ambiente (`.env`) dalla dashboard di Render.
5. Ottieni il tuo URL pubblico (es. `https://notion-to-ical.onrender.com/scadenze.ics`).

---

## 📅 Importazione in Apple Calendar

1. Apri Apple Calendar → `File > Nuovo calendario in abbonamento...`
2. Inserisci l’URL `.ics` generato (es: `https://.../scadenze.ics`)
3. Imposta la frequenza di aggiornamento (es. ogni ora)

---

## 📌 Tecnologie usate

- 🐍 Python
- 🌐 Flask
- 🗃️ Notion API
- 📅 icalendar (libreria)
- ☁️ Render
- 🐳 Docker

---

## 🛡️ Note sulla sicurezza

Ricorda di **non caricare mai il file `.env` su GitHub**: contiene credenziali private.  
Il file `.gitignore` già esclude `.env` di default.

---

## 📬 Contatti

Creato da [@Nicoolae](https://github.com/Nicoolae) – se ti è stato utile, lascia una ⭐!
