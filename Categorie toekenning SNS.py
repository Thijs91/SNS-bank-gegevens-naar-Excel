import pandas as pd
import re
import os
from datetime import datetime

# Definieer kolomnamen voor csv_bank. Deze zijn specifiek voor de SNS. Aan te passen voor iedere andere bank. Let op kolommen moeten unike namen bevatten.
kolomnamen_csv_bank = [
    "Datum_1", "Eigen rekening", "Tegen rekening", "Ontvanger", "Column5", "Column6", 
    "Column7", "Valuta_1", "Saldo", "Valuta_2", "Bedrag", "Datum_2", "Datum_3", 
    "Column14", "BIC", "Column16", "Column17", "Omschrijving", "Column19"
]

# Bestandslocaties. r' zorgt er voor dat je het path van de bestandslocatie zo kan plakken en niet de \ hoeft om te zetten naar /
csv_indeling_path = r'C:\OneDrive\Huis\Financien\Financien - Categorie indeling - voorbeeld.csv' # Locatie waar de csv met categorie indelingen staan
csv_bank_path = r'C:\OneDrive\Huis\Financien\transactie-historie_gemeenschappelijk.csv' # Locatie waar de csv met bank transacties staan
export_dir = r'C:\OneDrive\Huis\Financien' # Locatie waar de export moet komen

# Controleer of de CSV-bestanden bestaan
if not os.path.exists(csv_indeling_path):
    raise FileNotFoundError(f"Het bestand '{csv_indeling_path}' is niet gevonden.")
if not os.path.exists(csv_bank_path):
    raise FileNotFoundError(f"Het bestand '{csv_bank_path}' is niet gevonden.")

# Inlezen van csv_indeling
csv_indeling = pd.read_csv(csv_indeling_path, sep=';', header=0)

# Inlezen van csv_bank
csv_bank = pd.read_csv(csv_bank_path, sep=';', names=kolomnamen_csv_bank)

# Vervang komma door punt in de 'Bedrag' kolom en converteer naar numerieke waarden
csv_bank['Bedrag'] = csv_bank['Bedrag'].str.replace(',', '.', regex=False)  # Vervang komma door punt
csv_bank['Bedrag'] = pd.to_numeric(csv_bank['Bedrag'], errors='coerce')  # Zet om naar numerieke waarden, ongeldige waarden worden NaN

# Vervang komma door punt in de 'Saldo' kolom en converteer naar numerieke waarden
csv_bank['Saldo'] = csv_bank['Saldo'].str.replace(',', '.', regex=False)  # Vervang komma door punt
csv_bank['Saldo'] = pd.to_numeric(csv_bank['Saldo'], errors='coerce')  # Zet om naar numerieke waarden, ongeldige waarden worden NaN

# Converteer de 'Datum_1' kolom naar datetime formaat
csv_bank['Datum_1'] = pd.to_datetime(csv_bank['Datum_1'], format='%d-%m-%Y', errors='coerce') # Converteer naar datetime, zet ongeldige datums naar NaT

# Nieuwe kolommen toevoegen
csv_bank['Type_Bedrag'] = ''  # Nieuwe kolom 'Type_Bedrag' toevoegen
csv_bank['Categorie'] = ''  # Nieuwe kolom 'Categorie' toevoegen
csv_bank['Sub Categorie'] = ''  # Nieuwe kolom 'Categorie' toevoegen

# Toewijzen van categorieën op basis van zoektermen in omschrijving
for index_bank, row_bank in csv_bank.iterrows():
    omschrijving_bank = str(row_bank['Omschrijving'])
    categorie_gevonden = False
    
    for omschrijving_indeling, categorie, sub_categorie in zip(csv_indeling['Omschrijving'], csv_indeling['Categorie'], csv_indeling['Sub Categorie']):
        if pd.notna(omschrijving_bank) and pd.notna(omschrijving_indeling):
            if re.search(rf'\b{re.escape(omschrijving_indeling)}\b', omschrijving_bank, re.IGNORECASE):
                csv_bank.at[index_bank, 'Categorie'] = categorie
                csv_bank.at[index_bank, 'Sub Categorie'] = sub_categorie
                categorie_gevonden = True
                break
    
    if not categorie_gevonden:
        csv_bank.at[index_bank, 'Categorie'] = "Categorie niet gevonden"
    
    # Bepaal of het een "toe" of "af" bedrag is en vul de nieuwe kolom 'Type_Bedrag'
    if pd.notna(row_bank['Bedrag']):
        if row_bank['Bedrag'] > 0:
            csv_bank.at[index_bank, 'Type_Bedrag'] = 'Toe'
        elif row_bank['Bedrag'] < 0:
            csv_bank.at[index_bank, 'Type_Bedrag'] = 'Af'

# Voeg een kolom toe voor de maand (jaar-maand)
csv_bank['Maand'] = csv_bank['Datum_1'].dt.to_period('M')

# Bepaal de eerste en laatste datum uit 'Datum_1'
eerste_datum = csv_bank['Datum_1'].min()  # Eerste datum
laatste_datum = csv_bank['Datum_1'].max()  # Laatste datum

# Converteer de 'Datum_1' kolom van datetime formaat naar date
csv_bank['Datum_1'] = pd.to_datetime(csv_bank['Datum_1'], format='%d-%m-%Y', errors='coerce').dt.date # Converteer van datetime naar date, zet ongeldige datums naar NaT

# Definieer datums
huidige_datum = datetime.now().strftime("%Y%m%d")
eerste_datum = eerste_datum.strftime("%Y%m%d")
laatste_datum = laatste_datum.strftime("%Y%m%d")
print(f"De datum van vandaag is: '{huidige_datum}'. De eerste datum in het CSV bestand is: '{eerste_datum}'. De laatste datum in het CSV bestand is: '{laatste_datum}'.")

# Specificeer de gewenste kolomvolgorde
kolommen_export = ['Maand', 'Datum_1', 'Eigen rekening', 'Tegen rekening', 'Ontvanger', 
                   'Valuta_1', 'Saldo', 'Bedrag', 'Omschrijving', 'Type_Bedrag', 'Categorie', 'Sub Categorie']

# Beperk de DataFrame tot de gewenste kolommen
csv_bank_export = csv_bank[kolommen_export]

# Wijzig de kolomnaam 'Datum_1' naar 'Datum'
csv_bank_export.rename(columns={'Datum_1': 'Datum'}, inplace=True)

# Wijzig de kolomnaam 'Valuta_1' naar 'Valuta'
csv_bank_export.rename(columns={'Valuta_1': 'Valuta'}, inplace=True)

# Exporteer naar bestand met datumstempel
export_path_csv = os.path.join(export_dir, f'csv_bank_met_categorieen_{huidige_datum}_{eerste_datum}_{laatste_datum}.csv')
export_path_excel = os.path.join(export_dir, f'csv_bank_met_categorieen_{huidige_datum}_{eerste_datum}_{laatste_datum}.xlsx')

# Zorg ervoor dat de directory bestaat
os.makedirs(export_dir, exist_ok=True)

# Exporteer naar CSV-bestand met gespecificeerde separator (puntkomma)
csv_bank_export.to_csv(export_path_csv, sep=';', index=False)

# Exporteer naar Excel-bestand
csv_bank_export.to_excel(export_path_excel, index=False, engine='openpyxl')

# Print de locaties van de geëxporteerde bestanden
print(f"De nieuwe csv_bank met categorieën is opgeslagen op: '{export_path_csv}'")
print(f"De nieuwe csv_bank met categorieën is opgeslagen op: '{export_path_excel}'")
