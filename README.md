# SNS-CSV-naar-Excel-gecategoriseerd
Zet de SNS-export van een bankrekening om naar een Excel en CSV gecategoriseerd en overbodige tabellen eruit gehaald voor eenvoudige verwerking om inzicht te krijgen in de financiën. Verder verwerking moet in Excel. 

Voor de categorisering wordt gekeken naar een losse CSV waar de categorieën in zitten. 

De code is specifiek voor de SNS. Maar de kolommen op regel 7 zijn aan te passen voor iedere andere bank. Let op kolommen moeten unieke namen bevatten.

Benodigde software/plug-ins
* Python, pandas en openpyxl om het script de draaien
* Visual code studio om het script af te trappen

Wat doet het script:
* Voegt de (sub)categorieën toe zoals gedefinieerd in een losse CSV (Financien - Categorie indeling - voorbeeld.csv) op basis van het kenmerkenveld in de CSV van de bank export
* Voegt de maand van de transactie toe op basis van transactie datum
* Voegt toe of het een "Af" of "Toe" transactie is
* Maakt een export naar CSV en Excel met de codering _datum export_datum eerste transactie_datum laatste transactie
