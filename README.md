# DevSecOps Projekt: Digital Dagbok

Det här är min fullstack projekt för kursen. Applikation är en digital dagbok för skriva anteckningar. Man kan att skapa, läsa, uppdatera och radera (CRUD). Varje anteckning har id, titel, text, kategori och tid.

## API Dokumentation
Om du vill se hur API fungerar, du kan kolla i mappen `Docs`. Jag har skapat två filer:
* `Docs/api_documentation.md`
* `Docs/api_documentation.html`

## Infrastruktur
Applikation är hostas på Render med databas Neon PostgreSQL för produktion. Du kan läsa mer om infrastruktur i `Docs/infrastructure.md`.

## Hur startar projektet (LOKALT)
Innan jag hade två server, men nu backend serverar frontend direkt. **Du behöver inte starta port 3000 för frontend.**
1. Öppna terminal i `backend` mapp.
2. Köra den här kommando:
```bash
   uvicorn app.main:app --reload --port 8000
```
3. Öppna webläsare i http://localhost:8000. Nu frontend och backend jobbar tillsammans.

## Hur man testar API (cURL)
Applikation använda Auth0 för säkerhet. Du måste att ha en Token för använda API endpoints. Först du måste logga in på sidan för få din <DIN_TOKEN>.

### Hämta alla anteckningar (GET)
```Bash
curl -X GET [http://127.0.0.1:8000/api/entries](http://127.0.0.1:8000/api/entries) \
     -H "Authorization: Bearer <DIN_TOKEN>"
```

### Skapa ny anteckning (POST)
```Bash
curl -X POST [http://127.0.0.1:8000/api/entries](http://127.0.0.1:8000/api/entries) \
     -H "Authorization: Bearer <DIN_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"title": "Min test", "content": "Detta är ett test", "category": "Skola"}'
```

### Uppdatera anteckning (PUT)
```Bash
curl -X PUT [http://127.0.0.1:8000/api/entries/1](http://127.0.0.1:8000/api/entries/1) \
     -H "Authorization: Bearer <DIN_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"title": "Uppdaterad test", "content": "Ny text", "category": "Skola"}'
```

### Ta bort anteckning (DELETE)
```Bash
curl -X DELETE [http://127.0.0.1:8000/api/entries/1](http://127.0.0.1:8000/api/entries/1) \
     -H "Authorization: Bearer <DIN_TOKEN>"
```

## Automatisk API-testning med Newman
Projektet har en Postman-kollektion med tester. De kollar att API fungerar. Backend måste vara igång på port 8000 för att köra Newman lokalt.

## Databas och Docker
Appen sparar data i en fil som heter `dagbok.db` lokalt för test. Det finns också Dockerfile i projektet om man vill bygga container.