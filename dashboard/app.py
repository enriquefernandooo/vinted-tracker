import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.price_analysis import analyse_preise

st.set_page_config(page_title="Vinted Tracker", page_icon="👕", layout="centered")

st.title("👕 Vinted Tracker")
st.caption("Preisanalyse & Inventory für Vinted Reselling")

st.header("Preisfinder")

col1, col2 = st.columns(2)

with col1:
    suchbegriff = st.text_input("Artikel", placeholder="z.B. Nike Air Force 42")

with col2:
    einkaufspreis = st.number_input("Einkaufspreis (€)", min_value=0.0, step=0.5)

if st.button("Analyse starten"):
    if not suchbegriff:
        st.warning("Bitte einen Suchbegriff eingeben.")
    elif einkaufspreis <= 0:
        st.warning("Bitte einen Einkaufspreis eingeben.")
    else:
        with st.spinner("Vinted wird durchsucht..."):
            ergebnis = analyse_preise(suchbegriff, einkaufspreis)
        
        if ergebnis:
            st.success("Analyse abgeschlossen!")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Empfohlener VK", f"{ergebnis['empfehlung']}€")
            col2.metric("Marge", f"{ergebnis['marge_euro']}€")
            col3.metric("Marge %", f"{ergebnis['marge_prozent']}%")
            
            with st.expander("Details anzeigen"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Median Preis", f"{ergebnis['median']}€")
                    st.metric("Durchschnitt", f"{ergebnis['durchschnitt']}€")
                with col2:
                    st.metric("Günstigstes", f"{ergebnis['minimum']}€")
                    st.metric("Teuerstes", f"{ergebnis['maximum']}€")
                
                st.caption(f"Basierend auf {ergebnis['anzahl_artikel']} Artikeln auf Vinted")
        else:
            st.error("Keine Ergebnisse gefunden. Anderen Suchbegriff versuchen.")