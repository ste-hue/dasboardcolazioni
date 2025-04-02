import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import math

# Configurazione del tema
st.set_page_config(
    page_title="Dashboard Colazioni",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definizione del tema personalizzato
st.markdown("""
    <style>
    /* Colori principali */
    :root {
        --primary-color: #dcb87b;
        --secondary-color: #f4e4bc;
        --accent-color: #e6a756;
        --background-color: #1a1a1a;
        --text-color: #ffffff;
    }
    
    /* Stile generale */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Stile titoli */
    .stTitle {
        color: var(--primary-color);
    }
    
    /* Stile metriche */
    .stMetric {
        background-color: rgba(220, 184, 123, 0.1);
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    
    /* Stile tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(220, 184, 123, 0.1);
        border-radius: 5px;
        padding: 10px 20px;
        color: var(--primary-color);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: var(--background-color);
    }
    
    /* Stile bottoni */
    .stButton button {
        background-color: var(--primary-color);
        color: var(--background-color);
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
    }
    
    .stButton button:hover {
        background-color: var(--accent-color);
    }
    
    /* Stile dataframe */
    .dataframe {
        background-color: rgba(220, 184, 123, 0.05);
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Stile selectbox */
    .stSelectbox select {
        background-color: rgba(220, 184, 123, 0.1);
        color: var(--text-color);
        border: 1px solid var(--primary-color);
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Costanti per i file
DASHBOARD_FILE = "breakfast_dashboard.xlsx"
CONSUMI_FILE = "unified_consumi_data.csv"
COLATIONI_FILE = "colazionigiornalierecount2024.csv"
MAX_PAX_GIORNALIERI = 194  # Numero massimo di colazioni giornaliere

# Dizionario dei nomi dei mesi
NOMI_MESI = {
    4: 'Aprile',
    5: 'Maggio',
    6: 'Giugno',
    7: 'Luglio',
    8: 'Agosto',
    9: 'Settembre',
    10: 'Ottobre'
}

# Dizionario dei costi mensili
COSTI_MENSILI = {
    'Aprile': 8883.02,
    'Maggio': 15004.04,
    'Giugno': 18966.23,
    'Luglio': 22540.99,
    'Agosto': 21773.70,
    'Settembre': 19710.02,
    'Ottobre': 13749.44
}

# Colazioni mensili reali (basate sui dati effettivi)
COLATIONI_MENSILI = {
    'Aprile': 1279,
    'Maggio': 3459,
    'Giugno': 4896,
    'Luglio': 5199,
    'Agosto': 5159,
    'Settembre': 4337,
    'Ottobre': 3202
}

# Caricamento dati
@st.cache_data
def carica_dati():
    """Carica i dati dai file"""
    dati = {}
    
    # Carica il file dashboard se esiste
    if os.path.exists(DASHBOARD_FILE):
        try:
            # Carica coefficienti di ogni mese
            for numero_mese, nome_mese in NOMI_MESI.items():
                try:
                    df = pd.read_excel(DASHBOARD_FILE, sheet_name=nome_mese, skiprows=3)
                    # Converti i coefficienti in valori numerici
                    if 'Coefficiente' in df.columns:
                        df['Coefficiente'] = pd.to_numeric(df['Coefficiente'], errors='coerce')
                    dati[nome_mese] = df
                except Exception as e:
                    st.warning(f"Impossibile caricare il foglio {nome_mese}: {e}")
            
            # Carica coefficienti combinati
            try:
                df_coeff = pd.read_excel(DASHBOARD_FILE, sheet_name='Coefficienti Mensili')
                dati['coefficienti'] = df_coeff
            except Exception as e:
                print(f"Impossibile caricare il foglio Coefficienti Mensili: {e}")
            
            # Carica dati dei costi dai consumi
            if os.path.exists(CONSUMI_FILE):
                try:
                    df_consumi = pd.read_csv(CONSUMI_FILE)
                    # Pulisci il nome delle colonne
                    df_consumi.columns = df_consumi.columns.str.strip()
                    dati['consumi'] = df_consumi
                except Exception as e:
                    st.warning(f"Impossibile caricare il file consumi: {e}")
                
        except Exception as e:
            st.error(f"Errore nel caricamento del file dashboard: {e}")
    
    return dati

# Cerca costi e dettagli di un prodotto
def trova_informazioni_prodotto(df_consumi, articolo):
    """Cerca le informazioni di costo per un prodotto nel dataset dei consumi"""
    if df_consumi is None or articolo is None:
        return None
    
    # Pulizia del nome articolo per migliorare la corrispondenza
    articolo_pulito = str(articolo).strip().upper()
    
    # Cerca corrispondenza esatta
    match = df_consumi[df_consumi['Articolo'].str.strip().str.upper() == articolo_pulito]
    
    if match.empty:
        # Cerca corrispondenza parziale
        match = df_consumi[df_consumi['Articolo'].str.contains(articolo_pulito, case=False, na=False)]
    
    if not match.empty:
        # Prendi il primo match
        info = match.iloc[0]
        return {
            'costo_medio': info.get('Euro Medio', 0),
            'uma': info.get('U.M.A.', ''),
            'umc': info.get('U.M.C.', ''),
            'coeff_conv': info.get('Coeff Conv', 1),
            'classe': info.get('Classe', '')
        }
    
    return None

# Applicazione principale
def main():
    # Titolo dell'app
    st.title("🍳 Dashboard Colazioni")
    
    # Carica i dati
    dati = carica_dati()
    if not dati:
        st.warning("Nessun dato disponibile. Verifica che i file Excel siano presenti.")
        st.stop()
    
    # Filtra mesi disponibili
    mesi_disponibili = [m for m in NOMI_MESI.values() if m in dati]
    
    # Layout principale a tab
    tab1, tab2, tab3 = st.tabs(["📈 Dettaglio Mensile", "🔄 Confronto Mesi", "📝 Pianificazione Ordini"])
    
    # Tab 1: Dettaglio Mensile
    with tab1:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Selezione del mese
            mese_selezionato = st.selectbox("Seleziona Mese", mesi_disponibili, key="tab1_mese")
            
            # Mostra dati mensili
            st.subheader(f"Dati {mese_selezionato} 2024")
            st.metric("Colazioni Servite", f"{COLATIONI_MENSILI.get(mese_selezionato, 0):,}")
            st.metric("Costo Totale", f"{COSTI_MENSILI.get(mese_selezionato, 0):,.2f} €")
            
            if mese_selezionato in COLATIONI_MENSILI and COLATIONI_MENSILI[mese_selezionato] > 0:
                costo_medio = COSTI_MENSILI.get(mese_selezionato, 0) / COLATIONI_MENSILI[mese_selezionato]
                st.metric("Costo Medio per Colazione", f"{costo_medio:.2f} €")
        
        with col2:
            # Carica e mostra dati delle colazioni reali
            try:
                df_colazioni = pd.read_csv('colazionigiornalierecount2024.csv')
                # Pulisci i nomi delle colonne rimuovendo spazi extra
                df_colazioni.columns = df_colazioni.columns.str.strip()
                # Converti la data nel formato corretto
                df_colazioni['data'] = pd.to_datetime(df_colazioni['data'], format='%d/%m/%Y %H.%M.%S')
                df_colazioni['mese'] = df_colazioni['data'].dt.month
                
                # Filtra per il mese selezionato
                mese_numero = [k for k, v in NOMI_MESI.items() if v == mese_selezionato][0]
                df_mese_colazioni = df_colazioni[df_colazioni['mese'] == mese_numero]
                
                if not df_mese_colazioni.empty:
                    colazioni_totali = df_mese_colazioni['CONSUMO REALE COLAZIONI'].sum()
                    
                    # Mostra metriche di confronto
                    col2a, col2b = st.columns(2)
                    with col2a:
                        st.metric("Colazioni Reali", f"{colazioni_totali:,.0f}")
                    with col2b:
                        st.metric("Differenza vs Target", f"{colazioni_totali - COLATIONI_MENSILI.get(mese_selezionato, 0):+,.0f}")
                    
                    # Grafico di confronto giornaliero
                    st.subheader("Confronto Giornaliero")
                    fig = go.Figure()
                    
                    # Aggiungi linea delle colazioni target
                    fig.add_trace(go.Scatter(
                        x=df_mese_colazioni['data'],
                        y=[COLATIONI_MENSILI.get(mese_selezionato, 0)/len(df_mese_colazioni)] * len(df_mese_colazioni),
                        name='Target Giornaliero',
                        line=dict(color='#dcb87b', dash='dash')
                    ))
                    
                    # Aggiungi linea delle colazioni reali
                    fig.add_trace(go.Scatter(
                        x=df_mese_colazioni['data'],
                        y=df_mese_colazioni['CONSUMO REALE COLAZIONI'],
                        name='Colazioni Reali',
                        line=dict(color='#e6a756')
                    ))
                    
                    fig.update_layout(
                        title=f'Confronto Target vs Colazioni Reali - {mese_selezionato}',
                        xaxis_title='Data',
                        yaxis_title='Numero Colazioni',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tabella dettaglio giornaliero
                    st.subheader("Dettaglio Giornaliero")
                    df_dettaglio = df_mese_colazioni[['data', 'CONSUMO REALE COLAZIONI']].copy()
                    df_dettaglio['data'] = df_dettaglio['data'].dt.strftime('%d/%m/%Y')
                    df_dettaglio.columns = ['Data', 'Colazioni Reali']
                    st.dataframe(
                        df_dettaglio.style.format({'Colazioni Reali': '{:,.0f}'}),
                        use_container_width=True,
                        height=200
                    )
            except Exception as e:
                st.warning(f"Impossibile caricare i dati delle colazioni reali: {e}")
            
            if mese_selezionato in dati:
                df_mese = dati[mese_selezionato].copy()
                
                # Filtra prodotti con coefficiente > 0
                df_mese_filtrato = df_mese[df_mese['Coefficiente'] > 0].copy()
                
                if not df_mese_filtrato.empty:
                    # Calcola consumo totale
                    colazioni = COLATIONI_MENSILI.get(mese_selezionato, 0)
                    df_mese_filtrato['Consumo Totale'] = df_mese_filtrato['Coefficiente'] * colazioni
                    
                    # Mostra tabella
                    st.subheader(f"Consumi Prodotti - {mese_selezionato}")
                    st.dataframe(
                        df_mese_filtrato[['Categoria', 'Articolo', 'UDM', 'Coefficiente', 'Consumo Totale']].style.format({
                            'Coefficiente': '{:.5f}',
                            'Consumo Totale': '{:.2f}'
                        }),
                        use_container_width=True,
                        height=400
                    )
                    
                    # Download CSV
                    csv = df_mese_filtrato.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Scarica dati come CSV",
                        csv,
                        f"storico_colazioni_{mese_selezionato}_2024.csv",
                        "text/csv",
                        key='download-mensile'
                    )
                    
                    # Grafico distribuzione categorie
                    st.subheader(f"Distribuzione Categorie - {mese_selezionato}")
                    
                    # Assicurati che Categoria non sia vuota
                    df_categorie = df_mese_filtrato.dropna(subset=['Categoria'])
                    if not df_categorie.empty:
                        df_categorie = df_categorie.groupby('Categoria')['Consumo Totale'].sum().reset_index()
                        df_categorie = df_categorie.sort_values('Consumo Totale', ascending=False)
                        
                        fig = px.pie(
                            df_categorie, 
                            values='Consumo Totale', 
                            names='Categoria',
                            title=f'Consumo per Categoria - {mese_selezionato}'
                        )
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Confronto Mesi
    with tab2:
        st.subheader("Confronto tra Mesi")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Selezione dei mesi da confrontare
            mesi_confronto = st.multiselect(
                "Seleziona mesi da confrontare",
                options=mesi_disponibili,
                default=mesi_disponibili[:2] if len(mesi_disponibili) >= 2 else mesi_disponibili
            )
        
        with col2:
            # Selezione della categoria da confrontare
            categorie_disponibili = set()
            for mese in mesi_confronto:
                if mese in dati:
                    df_mese = dati[mese]
                    categorie_mese = df_mese['Categoria'].dropna().unique()
                    categorie_disponibili.update(categorie_mese)
            
            categoria_selezionata = st.selectbox(
                "Seleziona categoria da confrontare",
                options=sorted(list(categorie_disponibili)) if categorie_disponibili else [""]
            )
        
        # Crea dataframe di confronto
        if mesi_confronto and categoria_selezionata:
            dati_confronto = []
            
            for mese in mesi_confronto:
                if mese in dati:
                    df_mese = dati[mese].copy()
                    df_categoria = df_mese[df_mese['Categoria'] == categoria_selezionata].copy()
                    
                    if not df_categoria.empty:
                        presenze = COLATIONI_MENSILI.get(mese, 0)
                        df_categoria['Consumo Totale'] = df_categoria['Coefficiente'] * presenze
                        
                        # Per ogni prodotto nella categoria
                        for _, row in df_categoria.iterrows():
                            if pd.notna(row['Articolo']) and pd.notna(row['Coefficiente']):
                                dati_confronto.append({
                                    'Mese': mese,
                                    'Prodotto': row['Articolo'],
                                    'Coefficiente': row['Coefficiente'],
                                    'Consumo Totale': row['Consumo Totale']
                                })
            
            if dati_confronto:
                df_confronto = pd.DataFrame(dati_confronto)
                
                # Mostra tabella di confronto
                st.subheader(f"Confronto Consumi - {categoria_selezionata}")
                st.dataframe(
                    df_confronto.pivot(index='Prodotto', columns='Mese', values='Consumo Totale').style.format('{:.2f}'),
                    use_container_width=True
                )
                
                # Grafico confronto consumi
                fig = px.bar(
                    df_confronto,
                    x='Prodotto',
                    y='Consumo Totale',
                    color='Mese',
                    title=f'Confronto Consumi per Mese - {categoria_selezionata}',
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Download confronto
                csv_confronto = df_confronto.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Scarica confronto come CSV",
                    csv_confronto,
                    f"confronto_{categoria_selezionata}.csv",
                    "text/csv",
                    key='download-confronto'
                )
    
    # Tab 3: Pianificazione Ordini
    with tab3:
        st.subheader("Pianificazione Ordini")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Selezione del mese di riferimento
            mese_riferimento = st.selectbox("Mese di riferimento", mesi_disponibili, key="tab3_mese")
            
            # Input diretto del numero di colazioni
            num_colazioni = st.number_input(
                "Numero di colazioni da preparare", 
                min_value=1, 
                value=100,
                step=10
            )
            
            # Buffer
            buffer_percentuale = st.slider(
                "Buffer (%)", 
                min_value=0, 
                max_value=50, 
                value=10,
                step=5
            )
        
        with col2:
            # Esclusione categorie
            categorie_disponibili = []
            if mese_riferimento in dati:
                df_mese = dati[mese_riferimento]
                categorie_disponibili = df_mese['Categoria'].dropna().unique().tolist()
            
            escludere_prodotti = st.multiselect(
                "Escludere categorie",
                options=categorie_disponibili
            )
            
            # Opzione per includere giacenze
            include_giacenze = st.checkbox("Considera giacenze attuali")
        
        # Calcolo quantità
        if mese_riferimento in dati:
            df_mese = dati[mese_riferimento].copy()
            
            # Calcola numero giorni necessari in base al massimo giornaliero
            giorni_necessari = math.ceil(num_colazioni / MAX_PAX_GIORNALIERI)
            colazioni_giornaliere = round(num_colazioni / giorni_necessari, 2)
            
            # Mostra info su distribuzione colazioni
            st.info(f"Per {num_colazioni} colazioni servono almeno {giorni_necessari} giorni (massimo {MAX_PAX_GIORNALIERI} pax/giorno).\n"
                   f"Media giornaliera stimata: {colazioni_giornaliere} colazioni/giorno.")
            
            # Filtra prodotti
            mask = df_mese['Coefficiente'] > 0
            if escludere_prodotti:
                mask = mask & (~df_mese['Categoria'].isin(escludere_prodotti))
            
            df_mese_filtrato = df_mese[mask].copy()
            
            # Ottieni dati sui costi dai dati di consumo
            df_consumi = dati.get('consumi', None)
            
            if not df_mese_filtrato.empty:
                # Calcola consumo previsto
                df_mese_filtrato['Consumo Previsto'] = df_mese_filtrato['Coefficiente'] * num_colazioni
                
                # Arricchisci con dati di costo
                if df_consumi is not None:
                    # Prepara un mapping di prodotti
                    mapping_prodotti = {}
                    for _, row in df_consumi.iterrows():
                        desc = row['Descrizione']
                        if pd.notna(desc):
                            mapping_prodotti[desc] = {
                                'costo_medio': row['Euro Medio'],
                                'uma': row['U.M.A.'],
                                'umc': row['U.M.C.'],
                                'coeff_conv': row['Coeff Conv']
                            }
                    
                    # Aggiungi colonne per il costo
                    df_mese_filtrato['Costo Unitario'] = 0.0
                    df_mese_filtrato['U.M.A.'] = ''
                    df_mese_filtrato['U.M.C.'] = ''
                    df_mese_filtrato['Costo Totale Previsto'] = 0.0
                    
                    # Cerca corrispondenza tra prodotti e dati di costo
                    for idx, row in df_mese_filtrato.iterrows():
                        prodotto = row['Articolo']
                        for key, info in mapping_prodotti.items():
                            if pd.notna(prodotto) and pd.notna(key) and (prodotto.upper() in key.upper() or key.upper() in prodotto.upper()):
                                df_mese_filtrato.at[idx, 'Costo Unitario'] = info['costo_medio']
                                df_mese_filtrato.at[idx, 'U.M.A.'] = info['uma']
                                df_mese_filtrato.at[idx, 'U.M.C.'] = info['umc']
                                df_mese_filtrato.at[idx, 'Costo Totale Previsto'] = info['costo_medio'] * row['Consumo Previsto'] / info['coeff_conv']
                                break
                
                # Applica buffer
                if buffer_percentuale > 0:
                    fattore_buffer = 1 + (buffer_percentuale / 100)
                    df_mese_filtrato['Quantità con Buffer'] = df_mese_filtrato['Consumo Previsto'] * fattore_buffer
                else:
                    df_mese_filtrato['Quantità con Buffer'] = df_mese_filtrato['Consumo Previsto']
                
                # Aggiorna costo totale con buffer
                if 'Costo Unitario' in df_mese_filtrato.columns:
                    df_mese_filtrato['Costo Totale con Buffer'] = df_mese_filtrato['Quantità con Buffer'] * df_mese_filtrato['Costo Unitario']
                
                # Arrotonda quantità
                df_mese_filtrato['Quantità con Buffer'] = df_mese_filtrato.apply(
                    lambda row: round(row['Quantità con Buffer']) 
                    if pd.notna(row.get('UDM')) and row['UDM'] in ['pz', 'kg', 'g', 'conf'] 
                    else round(row['Quantità con Buffer'], 2), 
                    axis=1
                )
                
                # Sezione giacenze
                if include_giacenze:
                    # Crea un contenitore per le giacenze
                    giacenze = {}
                    
                    # Organizza per categoria
                    categorie_giacenze = df_mese_filtrato['Categoria'].dropna().unique()
                    
                    st.subheader("Inserisci Giacenze Attuali")
                    cols = st.columns(3)
                    col_idx = 0
                    
                    for categoria in categorie_giacenze:
                        with cols[col_idx % 3]:
                            st.markdown(f"**{categoria}**")
                            prodotti_categoria = df_mese_filtrato[df_mese_filtrato['Categoria'] == categoria]
                            
                            for idx, row in prodotti_categoria.iterrows():
                                prodotto = row['Articolo']
                                if pd.notna(prodotto):
                                    # Crea un ID univoco per ogni input
                                    input_key = f"giacenza_{prodotto}_{idx}"
                                    giacenze[prodotto] = st.number_input(
                                        prodotto, 
                                        min_value=0.0, 
                                        value=0.0, 
                                        step=1.0,
                                        key=input_key
                                    )
                            
                            col_idx += 1
                    
                    # Aggiungi giacenze al dataframe
                    df_mese_filtrato['Giacenza'] = df_mese_filtrato['Articolo'].map(giacenze).fillna(0)
                    
                    # Calcola quantità da ordinare
                    df_mese_filtrato['Da Ordinare'] = df_mese_filtrato['Quantità con Buffer'] - df_mese_filtrato['Giacenza']
                    df_mese_filtrato['Da Ordinare'] = df_mese_filtrato['Da Ordinare'].apply(lambda x: max(0, x))
                    
                    # Arrotonda quantità da ordinare
                    df_mese_filtrato['Da Ordinare'] = df_mese_filtrato.apply(
                        lambda row: round(row['Da Ordinare']) 
                        if pd.notna(row.get('UDM')) and row['UDM'] in ['pz', 'kg', 'g', 'conf'] 
                        else round(row['Da Ordinare'], 2), 
                        axis=1
                    )
                    
                    # Mostra tabella con giacenze
                    st.subheader("Lista Prodotti da Ordinare")
                    
                    # Colonne da visualizzare
                    cols_display = ['Categoria', 'Articolo', 'UDM', 'Coefficiente', 'Consumo Previsto', 
                                   'Quantità con Buffer', 'Giacenza', 'Da Ordinare']
                    
                    # Aggiungi colonne di costo se disponibili
                    if 'Costo Unitario' in df_mese_filtrato.columns:
                        cols_display.extend(['Costo Unitario', 'Costo Totale Previsto'])
                    
                    # Calcola costo totale dell'ordine
                    costo_totale_ordine = 0
                    if 'Costo Unitario' in df_mese_filtrato.columns:
                        df_mese_filtrato['Costo Totale Ordine'] = df_mese_filtrato['Da Ordinare'] * df_mese_filtrato['Costo Unitario']
                        costo_totale_ordine = df_mese_filtrato['Costo Totale Ordine'].sum()
                        cols_display.append('Costo Totale Ordine')
                    
                    st.dataframe(
                        df_mese_filtrato[cols_display].style.format({
                            'Coefficiente': '{:.5f}',
                            'Consumo Previsto': '{:.2f}',
                            'Quantità con Buffer': '{:.2f}',
                            'Giacenza': '{:.2f}',
                            'Da Ordinare': '{:.2f}',
                            'Costo Unitario': '{:.2f} €',
                            'Costo Totale Previsto': '{:.2f} €',
                            'Costo Totale Ordine': '{:.2f} €'
                        }),
                        use_container_width=True,
                        height=400
                    )
                    
                    # Mostra costo totale dell'ordine
                    if costo_totale_ordine > 0:
                        st.metric("Costo Totale Ordine", f"{costo_totale_ordine:.2f} €")
                    
                    # Lista ordinata per il report
                    st.subheader("Report Ordine")
                    
                    # Filtra solo prodotti da ordinare
                    df_da_ordinare = df_mese_filtrato[df_mese_filtrato['Da Ordinare'] > 0].copy()
                    
                    if not df_da_ordinare.empty:
                        # Ordina per categoria
                        df_da_ordinare = df_da_ordinare.sort_values(['Categoria', 'Articolo'])
                        
                        # Crea report per categoria
                        categorie_ordine = df_da_ordinare['Categoria'].unique()
                        
                        report_text = f"ORDINE COLAZIONI - {datetime.now().strftime('%d/%m/%Y')}\n"
                        report_text += f"Numero colazioni: {num_colazioni} (Buffer: {buffer_percentuale}%)\n"
                        report_text += f"Distribuzione: {colazioni_giornaliere} colazioni/giorno per {giorni_necessari} giorni\n\n"
                        
                        for categoria in categorie_ordine:
                            report_text += f"--- {str(categoria).upper()} ---\n"
                            prodotti_cat = df_da_ordinare[df_da_ordinare['Categoria'] == categoria]
                            
                            for _, row in prodotti_cat.iterrows():
                                costo_info = ""
                                if 'Costo Unitario' in row and pd.notna(row['Costo Unitario']) and row['Costo Unitario'] > 0:
                                    costo_info = f" - {row['Costo Unitario']:.2f}€/unità"
                                
                                report_text += f"{row['Articolo']}: {row['Da Ordinare']} {row['UDM']}{costo_info}\n"
                            
                            report_text += "\n"
                        
                        if costo_totale_ordine > 0:
                            report_text += f"\nCosto totale stimato: {costo_totale_ordine:.2f} €\n"
                        
                        # Mostra e permetti download
                        st.text_area("Report Ordine", report_text, height=300)
                        
                        st.download_button(
                            "Scarica Report Ordine",
                            report_text,
                            f"ordine_colazioni_{datetime.now().strftime('%Y%m%d')}.txt",
                            key="download-report"
                        )
                        
                        # Download CSV dell'ordine
                        csv_ordine = df_da_ordinare.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Scarica Ordine come CSV",
                            csv_ordine,
                            f"ordine_colazioni_{datetime.now().strftime('%Y%m%d')}.csv",
                            "text/csv",
                            key='download-ordine-csv'
                        )
                else:
                    # Mostra tabella senza giacenze
                    st.subheader("Lista Prodotti")
                    
                    # Colonne da visualizzare
                    cols_display = ['Categoria', 'Articolo', 'UDM', 'Coefficiente', 'Consumo Previsto', 
                                   'Quantità con Buffer']
                    
                    # Aggiungi colonne di costo se disponibili
                    if 'Costo Unitario' in df_mese_filtrato.columns:
                        cols_display.extend(['Costo Unitario', 'Costo Totale Previsto'])
                        
                        # Calcola costo totale 
                        costo_totale = df_mese_filtrato['Costo Totale Previsto'].sum()
                        if costo_totale > 0:
                            st.metric("Costo Totale Stimato", f"{costo_totale:.2f} €")
                            
                        # Calcola costo medio per colazione
                        if num_colazioni > 0:
                            costo_medio = costo_totale / num_colazioni
                            st.metric("Costo Medio per Colazione", f"{costo_medio:.2f} €")
                    
                    st.dataframe(
                        df_mese_filtrato[cols_display].style.format({
                            'Coefficiente': '{:.5f}',
                            'Consumo Previsto': '{:.2f}',
                            'Quantità con Buffer': '{:.2f}',
                            'Costo Unitario': '{:.2f} €',
                            'Costo Totale Previsto': '{:.2f} €'
                        }),
                        use_container_width=True,
                        height=400
                    )
                    
                    # Download previsione
                    csv_previsione = df_mese_filtrato.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Scarica previsione come CSV",
                        csv_previsione,
                        f"previsione_colazioni_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        key='download-previsione'
                    )

if __name__ == "__main__":
    main()