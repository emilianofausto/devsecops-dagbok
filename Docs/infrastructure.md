# Infrastruktur och Deployment

Det här dokumentet förklarar hur appen är uppsatt för databas, deployment och kodsäkerhet.

## 1. Databas i Produktionen (Neon)
När appen körs i produktion används **Neon**, en serverless PostgreSQL-databas.
- **Fördelar:** Det är gratis (Free Tier) och väldigt lätt att använda. Neon ger en "Connection String" som enkelt kan klistras in som en miljövariabel (secret) i hostning-tjänsten (som Render).
- **Nackdelar:** På gratisversionen finns det begränsningar. Den största nackdelen är "Scale-to-zero", vilket betyder att databasen pausar sig själv om den är inaktiv i 5 minuter. När den ska vakna upp igen vid första användningen, kan det ta lite tid (ibland nästan 1 minut) för att starta. För gratisplanen är det max 1 projekt och 0.5 GB lagring.

*(Under enhetstestning i GitHub Actions används istället en lokal MySQL-databas, så vi rör inte produktionsdatabasen när vi testar koden).*

## 2. CI/CD och Hosting (Render)
Appen hostas på **Render**, via deras Free Tier.
- **CI/CD Pipeline:** När ny kod pushas till main-branchen och går igenom alla tester i GitHub Actions (Continuous Integration), byggs en Docker-image. 
- **Deployment:** Render hämtar sedan och kör den image vi byggt.
- **Miljövariabler:** Inne i Render har jag lagt till hemligheter (secrets), och en av dessa är kopplingssträngen (connection string) till Neon-databasen. På det sättet kan backend prata med rätt databas utan att lösenordet finns i koden.

## 3. Säkerhet i GitHub (Branch Protection)
För att jobba säkert (DevSecOps) har jag skyddat `main`-branchen i GitHub. Några av reglerna jag har satt upp är:
- **Ingen direkt push:** Det går inte att pusha kod direkt till main. Man måste skapa en ny branch och göra en Pull Request (PR).
- **Krav på Code Review:** Minst en person (eller automatisk kontroll) måste godkänna koden innan den slås ihop (merge).
- **Status Checks:** Alla våra automatiserade Newman-tester och säkerhetstester måste passera grönt innan man kan mergea in i main. 

Dessa metoder förhindrar att dålig eller skadlig kod råkar hamna i produktion.
