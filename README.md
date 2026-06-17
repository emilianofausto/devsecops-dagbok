# DevSecOps Projekt: Digital Dagbok

Det här är ett fullstack-projekt skapat av Emiliano för inlämningsuppgiften på NBI Handelsakademin (Kurs: DevSecOps VT26). 

Appen är en digital dagbok. Den låter användare skapa, titta på, uppdatera och ta bort dagboksanteckningar (CRUD-funktioner). Varje anteckning har ett unikt ID, titel, text, kategori och tid.

---

## API Dokumentation

Om du vill se exakt hur API:et fungerar och vilka parametrar som behövs, du kan kolla i mappen `Docs`. Jag har skapat två filer:
* `Docs/api_documentation.md` (Markdown)
* `Docs/api_documentation.html` (Öppna i webbläsaren)

---

## Infrastruktur och Deployment

Appen hostas på **Render** (Free Tier) med en **Neon PostgreSQL**-databas för produktion. För att läsa mer om hur databasen, CI/CD-pipelinen och GitHub-säkerheten (Branch Protection) är uppsatta, se dokumenten här:
* `Docs/infrastructure.md`
* `Docs/infrastructure.html`

---

## Automatisk API-testning med Newman

Projektet har en Postman-kollektion med 7 tester. De kollar att API:et fungerar bra. Gör så här för att köra testerna lokalt med Newman.

### Vad du behöver först
1. Se till att din FastAPI-backend är igång på port 8000:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
2. Öppna en ny terminal. Installera Newman om du inte har det:
    ```bash
    npm install -g newman
    ```
3. Kör testkollektionen:
    ```bash
    newman run backend/tests/api_collection.json
    ```
4. Förväntat resultat
    När du kör kommandot, Newman testar din backend. Du ska se en tabell i terminalen. Kolumnen som heter "failed" ska visa 0.

---

## E2E-testning med Playwright

För frontend har jag också skrivit end-to-end tester med Playwright. De finns i `frontend/tests/e2e.spec.js`. De testar att knappar och UI fungerar som en riktig användare.
Du kan köra dem med konfigurationen i `playwright.config.js`.

---

## Manuell testning med CURL

Om du vill testa utan Postman eller Newman, du kan använda `curl`. Starta backend först och öppna en ny terminal.

### 1. Skapa en ny anteckning (POST)
```bash
curl -X POST http://127.0.0.1:8000/api/entries \
     -H "Content-Type: application/json" \
     -d '{"title": "Testa med Curl", "content": "Det här är en manuell test", "category": "DevSecOps"}'
```

### 2. Hämta alla anteckningar (GET)
```bash
curl -X GET http://127.0.0.1:8000/api/entries
```

### 3. Hämta en specifik anteckning (GET med ID)
```bash
curl -X GET http://127.0.0.1:8000/api/entries/1
```

### 4. Uppdatera en anteckning (PUT)
```bash
curl -X PUT http://127.0.0.1:8000/api/entries/1 \
     -H "Content-Type: application/json" \
     -d '{"title": "Ny titel via Curl"}'
```

### 5. Radera en anteckning (DELETE)
```bash
curl -X DELETE http://127.0.0.1:8000/api/entries/1 
```

### 6. Testa felhantering
Om vi skickar tomma fält ska backend stoppa det (VG-krav).
```bash
curl -X POST http://127.0.0.1:8000/api/entries \
     -H "Content-Type: application/json" \
     -d '{"title": "", "content": "", "category": ""}'
```
*Du ska få ett felmeddelande med kod 422.*

---

# FRONTEND

## Hur man kör frontend

Frontend är vanliga HTML, CSS och JavaScript-filer i `frontend/src`. 

### 1. Starta backend först
Din FastAPI-backend måste köra på port 8000.

### 2. Starta webbserver för frontend
Öppna en **ny** terminal och gå till frontend-mappen:
```bash
cd frontend/src
```
Kör det här kommandot för att starta servern:
```bash
python3 -m http.server 3000
```

### 3. Öppna i webbläsaren
Gå till den här adressen i din webbläsare:
`http://localhost:3000`

---

# DATABAS OCH DOCKER

## Kika i databasen (SQLite)
Appen sparar allt i en fil som heter `dagbok.db` i mappen `backend`. Du kan använda programmet **SQLiteStudio (Letos)** för att titta på din data och se att rader raderas när du testar delete-funktionen.

## Dockerfile
Det finns också en `Dockerfile` i projektet om du behöver bygga och köra appen i en container-miljö.

---

## Hur jag skyddade main-branchen

Jag har lagt till Branch Protection Rules på GitHub för `main`-branchen (DevSecOps metoder):

* **Stoppat direkt push:** Man kan inte pusha direkt till main.
* **Krav på Pull Request (PR):** Man måste göra en ny branch först och skapa en PR.
* **Krav på tester:** Newman/Playwright testerna måste vara gröna innan man kan slå ihop (merge) koden.
* **Ingen Force Push:** Helt blockerat.
* **Ingen radering:** Det går inte att ta bort `main`-branchen.
