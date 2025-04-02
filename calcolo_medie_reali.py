import pandas as pd
from datetime import datetime

# Carica i dati delle colazioni giornaliere
df = pd.read_csv('colazionigiornalierecount2024.csv')

# Pulisci i nomi delle colonne
df.columns = df.columns.str.strip()

df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y %H.%M.%S')
df['mese'] = df['data'].dt.month

# Dati dei costi mensili
costi_mensili = {
    4: 8883.02,    # Aprile
    5: 15004.04,   # Maggio
    6: 18966.23,   # Giugno
    7: 22540.99,   # Luglio
    8: 21773.70,   # Agosto
    9: 19710.02,   # Settembre
    10: 13749.44   # Ottobre
}

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

# Calcola le statistiche mensili
risultati = []
for mese in sorted(df['mese'].unique()):
    dati_mese = df[df['mese'] == mese]
    
    # Calcola totali e medie
    colazioni_totali = dati_mese['CONSUMO REALE COLAZIONI'].sum()
    giorni_con_dati = len(dati_mese)
    costo_totale = costi_mensili.get(mese, 0)
    
    # Calcola medie
    media_colazioni_giorno = colazioni_totali / giorni_con_dati
    costo_medio_colazione = costo_totale / colazioni_totali if colazioni_totali > 0 else 0
    costo_medio_giorno = costo_totale / giorni_con_dati
    
    risultati.append({
        'Mese': nomi_mesi.get(mese, str(mese)),
        'Giorni_Rilevati': giorni_con_dati,
        'Colazioni_Totali': colazioni_totali,
        'Media_Colazioni_Giorno': media_colazioni_giorno,
        'Costo_Totale': costo_totale,
        'Costo_Medio_Colazione': costo_medio_colazione,
        'Costo_Medio_Giorno': costo_medio_giorno
    })

# Crea DataFrame con i risultati
df_risultati = pd.DataFrame(risultati)

# Formatta i numeri per una migliore leggibilità
pd.set_option('display.float_format', lambda x: '{:.2f}'.format(x))

# Stampa i risultati
print("\nAnalisi dettagliata per mese:")
print(df_risultati.to_string(index=False))

# Salva i risultati in CSV
df_risultati.to_csv('analisi_medie_reali.csv', index=False)
print("\nFile analisi_medie_reali.csv creato con successo!")