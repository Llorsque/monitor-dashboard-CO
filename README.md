
# Monitoring Dashboard — Clubs & Klanten (Streamlit)

Een lichtgewicht **Streamlit** dashboard om de voortgang van onze afdeling te monitoren.
We **uploaden 2 Excel-bestanden** (*.xlsx): **Nulmeting** en **Actueel**. Het dashboard:

- Filtert **alle persoonsgegevens** automatisch uit de monitoring (blijven wél zichtbaar op *Klantenkaart*).
- Toont **alleen aantallen en percentages** (geen tabellen/grafieken).
- Bevat een **Klantenkaart** (zoek op klant/club) en een **Vergelijker** (2 clubs naast elkaar).
- Heeft een **Advanced**-pagina om eigen parameters/KPI's te kiezen.
- Toont **huidige datum/tijd** en detecteert de **peildata** van nulmeting/actueel.

## Snel starten (lokaal)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Excel-stramien (aanbevolen kolommen)

- Clubnaam → `name` *(verplicht)*
- Sport → `sport`
- Gemeente → `municipality`
- Sportsbond/Federatie → `federation`
- Straat + Huisnummer → `street`
- Postcode → `postal_code`
- Plaats → `city`
- Contactpersoon → `contact_person` *(PII)*
- E-mail → `email` *(PII)*
- Telefoonnummer → `phone` *(PII)*
- Functie → `role` *(PII)*
- Eigen kantine (Ja/Nee) → `has_canteen`
- Aantal leden → `members_count`
- Aantal vrijwilligers → `volunteers_count`
- Contributie → `membership_fee`
- Peildatum/Stand per/Datum → `snapshot_date` *(optioneel)*

> Synoniemen worden automatisch herkend (bijv. *vereniging*, *organisatie*, *kantine*, *leden*, *vrijwilligers*, *peildatum*).

## Privacy
Persoonsgegevens (PII) worden **niet** meegenomen in de monitoring en de vergelijker. Op de **Klantenkaart** worden ze wél getoond zodat je volledig inzicht in de club/klant hebt.

## Optimalisatie-ideeën
- Schema-validatie bij upload (pydantic) en een aanpasbare `column_map.json`.
- Presets opslaan op de **Advanced**-pagina.
- (Later) Export van resultaten en KPI's als CSV of PDF.


---

## Validatie
Bij upload wordt het bestand gecontroleerd op:
- verplichte kolom: `name`
- aanbevolen kolommen: `sport`, `municipality`, `has_canteen`, `members_count`, `volunteers_count`, `snapshot_date`
- typechecks (numeric/boolean) en dubbele namen
Fouten en waarschuwingen zie je direct in de zijbalk.

## KPI-configuratie
In `config/kpis.json` beheer je KPI's zonder code. Types: 
- `count_rows`, `sum`, `mean`, `pct_true`, `count_new_names` (vergelijking t.o.v. nulmeting).
De waarden verschijnen automatisch op de Dashboard-pagina met deltas wanneer een nulmeting is geladen.
