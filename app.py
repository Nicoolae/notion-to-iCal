from flask import Flask, Response, jsonify
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

NOTION_TOKEN = os.getenv("INTEGRATION_SECRET")

# Impostiamo l'header di autorizzazione per l'API di Notion
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
}

# Gets the data from a notion - db
def get_db_data(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    # Fa la richiesta HTTP usando la libreria python per prendere i dati
    # La fa in POST, perchè Notion supporta solo il post per interrogare il DB
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        # Trasforma la risposta in dizionario PY e ritorno il valore con chiave results.
        return response.json()["results"]
    else:
        print(f"Errore {response.status_code}: {response.text}")
        return []

# Gets the events in scadenze database from Notion
def get_notion_scadenze():
    DATABASE_ID = os.getenv("SCADENZE_DATABASE_ID")
    # Prende i dati dal DB, usando le API
    results = get_db_data(DATABASE_ID)
    return results    

# Gets the events in courses database from Notion
def get_notion_courses():
    DATABASE_ID = os.getenv("COURSES_DATABASE_ID")
    # Prende i dati dal DB, usando le API
    results = get_db_data(DATABASE_ID)
    return results

# Gets the study sessions from the Notion db
def get_notion_study_sessions():
    DATABASE_ID = os.getenv("STUDY_SESSION_DATABASE_ID")
    # Prende i dati dal DB, usando le API
    results = get_db_data(DATABASE_ID)
    return results

# Create a dictionary with course_id and [course_code] + course_name
def clean_courses_data(courses):
    clean_data = {}
    for course in courses:
        props = course["properties"]
        clean_data[course["id"]] = "[" + props["Course Code"]["rich_text"][0]["plain_text"] + "] " + props["Name"]["title"][0]["plain_text"] 
    return clean_data;

# Clean the API data, filtering only useful information and merging with other DBs informations
def clean_scadenze_data():
    # Prendiamo le scadenze
    deadlines = get_notion_scadenze()
    # Le scadenze sono relative a certi corsi, che indica una relazione nel database
    # Dobbiamo quindi recuperare i corsi e poi associarli, per avere il nome
    courses = get_notion_courses()
    courses_clean = clean_courses_data(courses)
    # Dobbiamo ora filtrare solo le proprietà che ci interessano e aggiungere il relativo corso
    clean_deadlines = []
    for deadline in deadlines:
        props = deadline["properties"]
        clean_deadlines.append({
            "Name": props["Name"]["title"][0]["plain_text"] if props["Name"]["title"] else "Senza titolo",
            "URL": deadline.get("url", ""),
            "Date": {
                "start": props["Due Date"]["date"]["start"] if props["Due Date"]["date"] else None,
                "end": props["Due Date"]["date"]["end"] if props["Due Date"]["date"] else None
            },
            "Status": props["Status"]["status"]["name"] if props["Status"]["status"] else "Sconosciuto",
            "Courses": [courses_clean.get(c["id"], "NA") for c in props["Courses"]["relation"]]
        })

    return clean_deadlines

# Creates a .ics calendar from notion db scadenze
@app.route("/scadenze.ics")
def serve_scadenze_calendar():
    # 1. Pulisci i dati con clean_scadenze_data()
    # 2. Crea un oggetto Calendar()
    # 3. Per ogni scadenza:
    #     - crea un Event()
    #     - aggiungi title, start, end
    #     - aggiungi una descrizione se vuoi (es. nome corso)
    #     - aggiungilo al calendario
    # 4. Serializza il calendario in formato ICS
    # 5. Restituiscilo come risposta Flask con `mimetype="text/calendar"`
    
    deadlines = clean_scadenze_data()

    cal = Calendar()

    for d in deadlines:
        event = Event()
        
        # Nome
        event.add("summary", (d["Name"] + " - " + d["Courses"][0]))

        start_date = d["Date"]["start"]
        end_date = d["Date"]["end"]

        if not start_date:
            continue  # salta l'evento se manca la data di inizio

        # La T in ISO format verifica che ci sia l'ora
        if "T" not in start_date:
            # Evento per tutto il giorno
            # .date() converte a un oggetto di tipo Date (non Datetime) per avere l'evento per tutto il giorno
            event.add("dtstart", datetime.fromisoformat(start_date).date())
            event.add("dtend", datetime.fromisoformat(end_date).date() if end_date else datetime.fromisoformat(start_date).date() + timedelta(days=1))
        else:
            # Evento con orario specifico
            event.add("dtstart", datetime.fromisoformat(start_date))
            event.add("dtend", datetime.fromisoformat(end_date) if end_date else datetime.fromisoformat(start_date))
        
        # Descrizione
        desc = f"Corsi: {', '.join(d['Courses'])}"
        if d['Status']:
            desc += f"\nStato: {d['Status']}"
        event.add("description", desc)

        # URL -  Notion
        event.add("url", d["URL"])

        # Location
        event.add("location", "Via Torino 155 30170 Mestre, Venezia Italia")

        cal.add_component(event)
    
    # Ritorna una HTTP response in formato .ics
    return Response(cal.to_ical(), mimetype="text/calendar")

# Clean the API data(-> study sessions info), filtering only
# useful information and merging with other DBs informations
def cleans_study_sessions_data():
    # Prendiamo le sessioni di studio così come sono("dirty")
    study_sessions = get_notion_study_sessions()
    # Le sessioni di studio sono relative a certi corsi, che indica una relazione nel database
    # Dobbiamo quindi recuperare i corsi e poi associarli, per avere il nome
    courses = get_notion_courses()
    courses_clean = clean_courses_data(courses)
    # Dobbiamo ora filtrare solo le proprietà che ci interessano e aggiungere il relativo corso
    clean_sessions = []
    for s in study_sessions:
        props = s["properties"]
        clean_sessions.append({
            "Name": props["Task name"]["title"][0]["plain_text"] if props["Task name"]["title"] else "Senza titolo",
            "URL": s.get("url", ""),
            "Date": {
                "start": props["Due date"]["date"]["start"] if props["Due date"]["date"] else None,
                "end": props["Due date"]["date"]["end"] if props["Due date"]["date"] else None
            },
            "Status": props["Status"]["status"]["name"] if props["Status"]["status"] else "Sconosciuto",
            "Courses": [courses_clean.get(c["id"], "NA") for c in props["Course"]["relation"]]
        })

    return clean_sessions;

# Creates a .ics calendar from notion db study sessions to have them in Apple Calendar
@app.route("/study-sessions.ics")
def serve_study_sessions_calendar():
    # First, we get the clean data, using another function
    # Then we create a new Calendar object
    # For every study session:
    # - creates a new Event
    # - add the study sessions data
    # serialize the calendar in .ics format
    # return the response at the request as a calendar
    study_sessions = cleans_study_sessions_data()

    cal = Calendar()

    for s in study_sessions:
        event = Event()
        
        # Nome
        event.add("summary", ("("+ s["Status"] + ") " + s["Name"] + " - " + s["Courses"][0]))

        start_date = s["Date"]["start"]
        end_date = s["Date"]["end"]

        if not start_date:
            continue  # salta l'evento se manca la data di inizio

        # La T in ISO format verifica che ci sia l'ora
        if "T" not in start_date:
            # Evento per tutto il giorno
            # .date() converte a un oggetto di tipo Date (non Datetime) per avere l'evento per tutto il giorno
            event.add("dtstart", datetime.fromisoformat(start_date).date())
            event.add("dtend", datetime.fromisoformat(end_date).date() if end_date else datetime.fromisoformat(start_date).date() + timedelta(days=1))
        else:
            # Evento con orario specifico
            event.add("dtstart", datetime.fromisoformat(start_date))
            event.add("dtend", datetime.fromisoformat(end_date) if end_date else datetime.fromisoformat(start_date))
        
        # Descrizione
        desc = f"Corsi: {', '.join(s['Courses'])}"
        if s['Status']:
            desc += f"\nStato: {s['Status']}"
        event.add("description", desc)

        # URL -  Notion
        event.add("url", s["URL"])

        cal.add_component(event)
    
    # Ritorna una HTTP response in formato .ics
    return Response(cal.to_ical(), mimetype="text/calendar")

if __name__ == "__main__":
    app.run()