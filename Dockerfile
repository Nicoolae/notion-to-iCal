# Usa un'immagine base di Python
FROM python:3.14.0a7-slim

# Imposta la directory di lavoro dentro il container
WORKDIR /app

# Copia i file necessari nella directory di lavoro
COPY . /app

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Imposta la variabile d'ambiente per Flask
# Imposta quale è lo script principale che deve eseguire flask, dove si trovano le rotte
ENV FLASK_APP=app.py
# Indirizzo IP su cui flask ascolta per le richieste, di default 127.0.0.1(localhost)
# In deploy poi 0.0.0.0(tutti)
ENV FLASK_RUN_HOST=0.0.0.0

# Espone la porta 5000 per Flask
EXPOSE 5000

# Comando per avviare l'app Flask
# In Docker, la riga CMD ["flask", "run"] è quella che avvia effettivamente l’applicazione Flask quando il container viene eseguito. 
# Questo comando dice al container di eseguire Flask in modalità “sviluppo” (usando flask run), che avvia il server web sulla porta 5000.
# Nota: Questo comando avvia il server web di Flask in modalità di sviluppo, che è utile per il test e lo sviluppo locale. 
# Quando l’app è pronta per la produzione, dovresti usare un server web più robusto, come Gunicorn o uWSGI, 
# per gestire le richieste in modo più efficiente.
CMD ["flask", "run"]