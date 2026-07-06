# Kalendarz poza biurem — Streamlit

Prosta aplikacja Streamlit do zaznaczania dni poza biurem.

## Co robi aplikacja

- przed wejściem wymaga hasła: `dexflex67`,
- pozwala wybrać osobę: Dagmara, Szymon, Michał, Darek, Julka,
- pozwala wybrać własny kolor na kalendarzu,
- pokazuje miesięczny kalendarz,
- blokuje dzień, jeśli już zaznaczyła go inna osoba,
- pozwala odznaczyć dzień tylko osobie, która go zaznaczyła,
- zapisuje dane w lokalnej bazie SQLite `out_of_office.db`.

## Uruchomienie lokalnie

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Hasło

Domyślne hasło to:

```text
dexflex67
```

Możesz je zmienić przez zmienną środowiskową `APP_PASSWORD`:

```bash
APP_PASSWORD="nowe-haslo" streamlit run app.py
```

Na Windows PowerShell:

```powershell
$env:APP_PASSWORD="nowe-haslo"
streamlit run app.py
```

## Wdrożenie

Możesz wrzucić projekt na GitHub i podpiąć go pod Streamlit Community Cloud. Ważne: przy wdrożeniu na środowisku, które restartuje aplikację lub nie trzyma plików na stałe, lokalna baza SQLite może zostać wyczyszczona po restarcie. Do prostego użytku zespołowego w jednej instancji działa dobrze; przy większym wdrożeniu warto podmienić SQLite na zewnętrzną bazę.
