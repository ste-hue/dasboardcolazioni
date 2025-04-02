import pandas as pd
import numpy as np
from datetime import datetime

# Carica i dati delle colazioni giornaliere
df_colazioni = pd.read_csv('colazionigiornalierecount2024.csv')
df_colazioni.columns = df_colazioni.columns.str.strip()
df_colazioni['data'] = pd.to_datetime(df_colazioni['data'], format='%d/%m/%Y %H.%M.%S')
df_colazioni['mese'] = df_colazioni['data'].dt.month

# Carica i dati dei prodotti dal file Excel
def carica_dati_mensili(file_excel, mese):
    try:
        # Salta le prime 3 righe che contengono l'intestazione
        df = pd.read_excel(file_excel, sheet_name=mese, skiprows=3)
        # Rimuovi righe con tutti NA
        df = df.dropna(how='all')
        return df
    except Exception as e:
        print(f"Errore nel caricamento del foglio {mese}: {e}")
        return None

# Mappa numeri mesi a nomi
nomi_mesi = {
    4: 'Aprile',
    5: 'Maggio',
    6: 'Giugno',
    7: 'Luglio',
    8: 'Agosto',
    9: 'Settembre',
    10: 'Ottobre'
}

# Calcola statistiche per ogni mese
risultati_mensili = []
risultati_prodotti = []

for num_mese, nome_mese in nomi_mesi.items():
    # Filtra i dati delle colazioni per il mese corrente
    dati_mese = df_colazioni[df_colazioni['mese'] == num_mese]
    colazioni_totali = dati_mese['CONSUMO REALE COLAZIONI'].sum()
    giorni_con_dati = len(dati_mese)
    
    # Carica i dati dei prodotti per il mese
    df_prodotti = carica_dati_mensili('breakfast_dashboard.xlsx', nome_mese)
    
    if df_prodotti is not None:
        # Calcola i costi per ogni prodotto
        for _, prodotto in df_prodotti.iterrows():
            if pd.notna(prodotto['Articolo']) and pd.notna(prodotto['Coefficiente']):
                consumo_totale = prodotto['Coefficiente'] * colazioni_totali
                costo_unitario = prodotto.get('Costo Unitario', 0)  # Aggiungi il nome corretto della colonna
                costo_totale_prodotto = consumo_totale * costo_unitario
                
                risultati_prodotti.append({
                    'Mese': nome_mese,
                    'Categoria': prodotto.get('Categoria', ''),
                    'Articolo': prodotto['Articolo'],
                    'UDM': prodotto.get('UDM', ''),
                    'Coefficiente': prodotto['Coefficiente'],
                    'Consumo_Totale': consumo_totale,
                    'Costo_Unitario': costo_unitario,
                    'Costo_Totale_Prodotto': costo_totale_prodotto
                })

# Crea DataFrame con i risultati
df_risultati_prodotti = pd.DataFrame(risultati_prodotti)

# Raggruppa per mese e categoria
df_summary = df_risultati_prodotti.groupby(['Mese', 'Categoria']).agg({
    'Costo_Totale_Prodotto': 'sum',
    'Consumo_Totale': 'sum'
}).reset_index()

# Formatta i numeri per una migliore leggibilità
pd.set_option('display.float_format', lambda x: '{:.2f}'.format(x))

# Stampa i risultati
print("\nAnalisi costi per categoria e mese:")
print(df_summary.to_string(index=False))

# Stampa dettaglio prodotti
print("\nDettaglio prodotti:")
print(df_risultati_prodotti.sort_values(['Mese', 'Categoria', 'Articolo']).to_string(index=False))

# Salva i risultati in CSV
df_risultati_prodotti.to_csv('analisi_costi_prodotti.csv', index=False)
df_summary.to_csv('analisi_costi_categorie.csv', index=False)
print("\nFile di analisi creati con successo!") 