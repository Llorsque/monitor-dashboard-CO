
# Monitoring Dashboard — Static (GitHub Pages)

Dit is een **pure front-end** versie (HTML/CSS/JS) van het monitoringsdashboard. Je kunt dit project
**rechtstreeks vanaf GitHub Pages** draaien — dus zonder Python backend.

## Features
- Upload **Nulmeting** en **Actueel** (XLSX/CSV) in de browser (geen server nodig).
- **PII automatisch gefilterd** in monitoring en vergelijker (wél zichtbaar op Klantenkaart).
- **Alleen aantallen & percentages** (geen tabellen/grafieken).
- **Klantenkaart**, **Vergelijker**, **Advanced** (filters, groepeer, KPI).
- **Peildatum-detectie** + handmatige override in zijbalk.
- **Branding**: #212945 / #52E8E8.

## Runnen via GitHub Pages
1. Maak (of gebruik) je repo en upload de volledige inhoud van deze map (index.html, assets/, js/, data/).
2. Ga naar **Settings → Pages → Build and deployment**:
   - **Source:** Deploy from a branch
   - **Branch:** `main` (of jouw branch) / **root**
   - Save.
3. Wacht tot GitHub de site bouwt. Je krijgt een URL zoals `https://<user>.github.io/<repo>/`.

> Let op: we gebruiken de **SheetJS** CDN om XLSX te lezen. Zorg dat je device internet heeft voor de CDN.

## Bestandsindeling
```
index.html
assets/style.css
js/data.js
js/logic.js
js/app.js
data/sample_nulmeting.xlsx
data/sample_actueel.xlsx
```

## Privacy
- Alles gebeurt **client-side** in jouw browser: bestanden worden *niet* geüpload naar een server.
- PII-kolommen (`Contactpersoon`, `E-mail`, `Telefoonnummer`, `Functie`) komen **niet** in monitoring/vergelijker voor.

## Excel-verwachting (synoniemen herkend)
- Clubnaam → `name`
- Gemeente → `municipality`
- Sport → `sport`
- Sportsbond/Federatie → `federation`
- Adres/straat + nr → `street`
- Postcode → `postal_code`
- Plaats → `city`
- Contactpersoon/E-mail/Telefoon/Functie → PII (alleen op Klantenkaart)
- Eigen kantine (Ja/Nee) → `has_canteen`
- Aantal leden → `members_count`
- Aantal vrijwilligers → `volunteers_count`
- Contributie → `membership_fee`
- Peildatum/Datum → `snapshot_date` (optioneel)

## Optimalisatie-ideeën
- De CDN van SheetJS lokaal bundelen (voor offline/airgapped gebruik).
- Presets en exports (TXT/PDF) toevoegen — kan volledig client-side.
- URL-parameters voor vooraf ingestelde filters/KPI’s.
