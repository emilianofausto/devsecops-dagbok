# DevSecOps Projekt: Digital Dagbok

Detta är ett fullstack-projekt skapat av Emiliano som en del av inlämningsuppgiften given av NBI Handelsakademin (Kurs: DevSecOps VT26). 

Applikationen är en digital dagbok (Dagbok) som låter användare skapa, visa, uppdatera och ta bort dagboksanteckningar (CRUD-funktionalitet). Varje anteckning innehåller ett unikt ID, en titel, ett textinnehåll, en kategori samt en tidstämpel, vilket uppfyller de tekniska kraven för datastruktur och validering.

---

## Automatiserad API-testning med Newman

Projektet innehåller en Postman-kollektion med 7 integrerade tester som verifierar API:ets endpoints, HTTP-statuskoder och indatavalidering. Följ stegen nedan för att köra testerna lokalt via Postmans CLI-verktyg (Newman).

### Förutsättningar
1. Se till att din lokala FastAPI-backend körs på port 8000:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
2. Öppna en ny terminal i projektets rotmapp.
Installera Newman globalt (om det inte redan är installerat):
    ```bash
    npm install -g newman
    ```
3. Exekvera testkollektionen:
    ```bash
    newman run backend/tests/api_collection.json
    ```
4. Förväntat resultat
    När kommandot körs kommer Newman att skicka anrop till din igångvarande backend och validera svaren i realtid. Du bör se en tabell i terminalen som sammanfattar testkörningen:
        7 förfrågningar körs sekventiellt (Skapa giltig anteckning, Valideringstest för felaktig indata, Hämta alla, Hämta specifik, Hantering av 404, Uppdatera anteckning, samt Radera anteckning).
Tabellen visar en kolumn märkt "failed" som ska stå på 0.

---------

## Extra manuell testning med CURL

Om du vill göra extra tester utan Postman eller Newman, du kan använda `curl` i terminalen. Det här är bra för att se att alla endpoints och databasen fungerar som det ska. 

Tänk på att starta backend först (`uvicorn app.main:app --port 8000`). Open en annan terminal och kör dessa kommandon:

### 1. Skapa en ny anteckning (POST)
Det här kommandot skickar data för att göra en ny dagboksanteckning.
```bash
curl -X POST [http://127.0.0.1:8000/api/entries](http://127.0.0.1:8000/api/entries) \
     -H "Content-Type: application/json" \
     -d '{"title": "Testa med Curl", "content": "Det här är en manuell test", "category": "DevSecOps"}'
```
*Du ska få ett svar tillbaka som visar ett `id` nummer (till exempel `"id": 1`).*

### 2. Hämta alla anteckningar (GET)
Det här hämtar listan med alla anteckningar som finns i databasen.
```bash
curl -X GET [http://127.0.0.1:8000/api/entries](http://127.0.0.1:8000/api/entries)
```

### 3. Hämta en specifik anteckning (GET med ID)
Här du kan hämta bara en anteckning. Byt ut siffran `1` i slutet om ditt id är något annat.
```bash
curl -X GET [http://127.0.0.1:8000/api/entries/1](http://127.0.0.1:8000/api/entries/1)
```

### 4. Uppdatera en anteckning (PUT)
Det här ändrar titeln på anteckningen med id 1.
```bash
curl -X PUT [http://127.0.0.1:8000/api/entries/1](http://127.0.0.1:8000/api/entries/1) \
     -H "Content-Type: application/json" \
     -d '{"title": "Ny titel via Curl"}'
```

### 5. Radera en anteckning (DELETE)
Det här tar bort anteckningen helt från databasen.
```bash
curl -X DELETE [http://127.0.0.1:8000/api/entries/1](http://127.0.0.1:8000/api/entries/1)
```
*Om du kör GET efter det här, anteckningen ska inte finnas kvar.*

### 6. Testa input validering (Felhantering)
För att testa VG-kravet om validering, vi skickar tomma fält. Backend ska stoppa detta.
```bash
curl -X POST [http://127.0.0.1:8000/api/entries](http://127.0.0.1:8000/api/entries) \
     -H "Content-Type: application/json" \
     -d '{"title": "", "content": "", "category": ""}'
```
*Här du ska få ett felmeddelande med statuskod `422 Unprocessable Entity` eftersom titeln och innehållet får inte vara tomma.*

# FRONTEND
## Hur man startar och kör frontend

Eftersom projektet har separat frontend och backend, du behöver inte installera Flask eller något stort verktyg. Frontend är bara vanliga HTML, CSS och JavaScript-filer som pratar med ditt API.

Följ dessa enkla steg för att starta hemsidan lokalt:

### 1. Starta backend först
Se till att din FastAPI-backend fortfarande körs i sin egen terminal på port 8000:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. Starta en server för frontend
Öppna en **ny** terminal (stäng inte av backend) och gå till mappen där frontend-filerna finns:
```bash
cd frontend/src
```

Nu kör det här kommandot för att starta Pythons inbyggda server:
```bash
python3 -m http.server 3000
```

### 3. Öppna i webbläsaren
När servern är igång, öppna din webbläsare och gå till den här adressen:
```
http://localhost:3000
```

### Vad du kan testa i appen:
* **Hämta data:** Sidan laddar automatiskt gamla anteckningar från din SQLite-databas.
* **Skapa (POST):** Skriv en titel, kategori och innehåll i formuläret och tryck på "Spara". Det visas direkt på listan.
* **Radera (DELETE):** Klicka på "Radera" på ett inlägg. Appen frågar dig först om du är säker (VG-krav för UX).
* **Felhantering (VG-krav):** Om du stänger av din backend och försöker spara, du kommer se ett rött felmeddelande på skärmen att servern är offline.

# DATABASE

## Hur man kollar i databasen lokalt (SQLite)

Appen sparar alla dina dagbokinlägg i en lokal fil som heter `dagbok.db`. Den här filen skapas automatiskt i mappen `backend` när du startar servern för första gången. 

För att titta på tabellerna och se all data som finns sparat enkelt, du kan använda ett gratis program som heter **SQLiteStudio (AKA Letos)** eller något annat verktyg för SQLite.

Följ dessa steg för att se din data:

### 1. Öppna databasen i SQLiteStudio (Letos)
1. Ladda ner och starta **SQLiteStudio** (Letos) på din dator.
2. Klicka på menyn längst upp: **Database** -> **Add a database**.
3. Under "File", klicka på den lilla gula mappen för att leta efter filen.
4. Gå till din projektmapp och välj filen som heter `dagbok.db` (den ligger i `backend/dagbok.db`). Klicka på OK.

### 2. Titta på tabellen och din data
1. I listan till vänster, dubbelklicka på databasen.
2. Expandera mappen **Tables** och dubbelklicka på tabellen **diary_entries** (det här är tabellen där dina inlägg sparas).
3. Uppe till höger ser du olika flikar. Klicka på fliken **Data**.

Nu du kommer se en tabell med kolumner för `id`, `title`, `content`, `category` och `created_at`. 

*Tips! Det här är jättebra när du testar appen. Om du klickar på "Radera" i din frontend, du kan trycka på refresh i SQLiteStudio (Letos) för att se direkt att raden försvinner från databasen.*