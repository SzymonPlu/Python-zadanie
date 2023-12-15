import requests
import pandas as pd
from datetime import datetime, timedelta
import os


# Funkcja do pobierania danych walutowych
def pobierz_dane_walutowe(waluta):
    dzisiaj = datetime.now()
    data_startu = dzisiaj - timedelta(days=90)
    url = f"https://api.nbp.pl/api/exchangerates/rates/A/{waluta}/{data_startu.strftime('%Y-%m-%d')}/{dzisiaj.strftime('%Y-%m-%d')}/"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data['rates'])
    df['effectiveDate'] = pd.to_datetime(df['effectiveDate'])
    df.set_index('effectiveDate', inplace=True)
    return df['mid']

# Funkcja do analizy danych walutowych
def analiza_danych(df, pary):
    for para in pary:
        print(f"Analiza dla {para}:")
        print(f"  Średnia: {df[para].mean()}")
        print(f"  Mediana: {df[para].median()}")
        print(f"  Minimum: {df[para].min()}")
        print(f"  Maksimum: {df[para].max()}")

try:
    # Pobieranie danych
    eur_pln = pobierz_dane_walutowe('EUR')
    usd_pln = pobierz_dane_walutowe('USD')
    chf_pln = pobierz_dane_walutowe('CHF')

    # Łączenie danych i obliczanie dodatkowych kursów
    df = pd.concat([eur_pln, usd_pln, chf_pln], axis=1)
    df.columns = ['EUR/PLN', 'USD/PLN', 'CHF/PLN']
    df['EUR/USD'] = df['EUR/PLN'] / df['USD/PLN']
    df['CHF/USD'] = df['CHF/PLN'] / df['USD/PLN']

    # Sprawdzenie, czy plik "all_currency_data.csv" już istnieje
    if os.path.exists("all_currency_data.csv"):
        df_stary = pd.read_csv("all_currency_data.csv", index_col=0)
        df_stary.index = pd.to_datetime(df_stary.index)
        df = pd.concat([df_stary, df[~df.index.isin(df_stary.index)]])

    # Zapis całych danych do pliku CSV na pulpicie
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    df.to_csv(os.path.join(desktop, "all_currency_data.csv"), index=True)

    # Wybór danych przez użytkownika
    wybrane_pary = input("Podaj interesujące Cię pary walutowe (np. EUR/PLN, USD/PLN): ").split(", ")
    df_wybrane = df[wybrane_pary]

    # Analiza wybranych danych
    analiza_danych(df, wybrane_pary)

    # Zapis wybranych danych do innego pliku CSV na pulpicie
    df_wybrane.to_csv(os.path.join(desktop, "selected_currency_data.csv"), index=True)

    # Komunikat dla użytkownika
    print("Dane dla wybranych par walutowych zostały zapisane!")

except requests.exceptions.RequestException as e:
    print(f"Błąd połączenia z API NBP: {e}")
except KeyError as e:
    print(f"Błąd: Wybrana para walutowa nie istnieje. Szczegóły: {e}")
except Exception as e:
    print(f"Wystąpił nieoczekiwany błąd: {e}")
