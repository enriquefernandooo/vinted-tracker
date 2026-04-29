import streamlit as st
import sys
import os
from dotenv import load_dotenv
from supabase import create_client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.price_analysis import analyse_preise

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

st.set_page_config(page_title="Vinted Tracker", page_icon="👕", layout="centered")
st.title("👕 Vinted Tracker")
st.caption("Preisanalyse & Inventory für Vinted Reselling")

tab1, tab2 = st.tabs(["Preisfinder", "Inventory"])

with tab1:
    st.header("Preisfinder")
    col1, col2 = st.columns(2)
    with col1:
        suchbegriff = st.text_input("Artikel", placeholder="z.B. Ralph Lauren Rugby XXL")
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
            st.session_state["ergebnis"] = ergebnis
            st.session_state["suchbegriff"] = suchbegriff
            st.session_state["einkaufspreis"] = einkaufspreis

    if "ergebnis" in st.session_state:
        ergebnis = st.session_state["ergebnis"]

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

        st.divider()
        st.subheader("Artikel ins Inventory speichern")
        col1, col2 = st.columns(2)
        with col1:
            marke   = st.text_input("Marke", placeholder="z.B. Ralph Lauren")
            groesse = st.text_input("Größe", placeholder="z.B. XXL")
        with col2:
            zustand = st.selectbox("Zustand", ["Neu", "Sehr gut", "Gut", "Akzeptabel"])
            ziel_vk = st.number_input("Ziel VK (€)", value=ergebnis['empfehlung'], step=0.5)

        if st.button("Ins Inventory speichern"):
            supabase.table("inventory").insert({
                "artikel":            st.session_state["suchbegriff"],
                "marke":              marke,
                "groesse":            groesse,
                "zustand":            zustand,
                "einkaufspreis":      st.session_state["einkaufspreis"],
                "ziel_verkaufspreis": ziel_vk,
            }).execute()
            st.success("Artikel gespeichert!")
            st.session_state.pop("ergebnis")
            st.rerun()

with tab2:
    st.header("Inventory")

    if st.button("Aktualisieren"):
        st.rerun()

    daten = supabase.table("inventory").select("*").order("erstellt_am", desc=True).execute()
    artikel_liste = daten.data

    if not artikel_liste:
        st.info("Noch keine Artikel im Inventory.")
    else:
        for artikel in artikel_liste:
            with st.expander(f"{artikel['artikel']} – {artikel['status']}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Einkaufspreis", f"{artikel['einkaufspreis']}€")
                col2.metric("Ziel VK", f"{artikel['ziel_verkaufspreis']}€" if artikel['ziel_verkaufspreis'] else "–")
                col3.metric("Verkaufspreis", f"{artikel['verkaufspreis']}€" if artikel['verkaufspreis'] else "Noch aktiv")

                col1, col2, col3 = st.columns(3)

                with col1:
                    if artikel['status'] == 'aktiv':
                        if st.button("Als verkauft markieren", key=artikel['id']):
                            vk_preis = st.number_input("Verkaufspreis (€)", key=f"vk_{artikel['id']}", min_value=0.0, step=0.5)
                            supabase.table("inventory").update({
                                "status":        "verkauft",
                                "verkaufspreis": vk_preis,
                            }).eq("id", artikel['id']).execute()
                            st.success("Gespeichert!")
                            st.rerun()

                with col2:
                    if st.button("Preisverlauf", key=f"hist_{artikel['id']}"):
                        if st.session_state.get(f"show_hist_{artikel['id']}"):
                            st.session_state[f"show_hist_{artikel['id']}"] = False
                        else:
                            st.session_state[f"show_hist_{artikel['id']}"] = True

                with col3:
                    if st.button("Löschen", key=f"del_{artikel['id']}"):
                        supabase.table("inventory").delete().eq("id", artikel['id']).execute()
                        st.rerun()

                if st.session_state.get(f"show_hist_{artikel['id']}"):
                    historie = supabase.table("preis_historie").select("*").eq("artikel_id", artikel['id']).order("datum").execute()
                    historie_data = historie.data

                    if not historie_data:
                        st.info("Noch keine Preishistorie – kommt ab morgen 9 Uhr.")
                    else:
                        import pandas as pd
                        df = pd.DataFrame(historie_data)
                        df['datum'] = (pd.to_datetime(df['datum']) + pd.Timedelta(hours=2)).dt.strftime('%d.%m %H:%M')
                        st.line_chart(df.set_index('datum')['empfohlener_vk'])
                        st.caption(f"Basierend auf täglich aktualisierten Vinted-Listings")