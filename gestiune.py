import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Sistem Gestiune Cereri ANAF", layout="wide")

DB_FILE = "cereri_db.csv"


def incarca_date():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=["ID", "Contribuabil", "Departament", "Status", "Data", "Detalii"])
    return pd.read_csv(DB_FILE)


def salveaza_date(df):
    df.to_csv(DB_FILE, index=False)


# Interfata
st.title("Portal Digital")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Depunere Cerere", "Verifica Status", "Panou Funcționar"])

#1: Depunere
with tab1:
    st.header("Depune o cerere noua")
    with st.form("form_depunere", clear_on_submit=False):
        nume = st.text_input("Nume Complet / Denumire Firma")
        dep = st.selectbox("Catre Departamentul", ["Asistenta Contribuabili", "Declaratii Fiscale", "Executare Silita"])
        detalii = st.text_area("Descrierea solicitarii (Ex: Solicit eliberarea certificatului de atestare...)")
        fisier = st.file_uploader("Incarca documentul suport (PDF)", type="pdf")

        submit = st.form_submit_button("Trimite Solicitarea")

        if submit:
            if nume and detalii:
                # Generare ID unic
                nou_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                data_azi = datetime.now().strftime("%Y-%m-%d %H:%M")

                noua_cerere = pd.DataFrame([[nou_id, nume, dep, "In asteptare", data_azi, detalii]],
                                           columns=["ID", "Contribuabil", "Departament", "Status", "Data", "Detalii"])

                df_actual = incarca_date()
                df_nou = pd.concat([df_actual, noua_cerere], ignore_index=True)
                salveaza_date(df_nou)

                st.success(f" Cererea a fost înregistrată! Numar de inregistrare: **{nou_id}**")
                st.warning(" Va rugam sa notati acest numar pentru a verifica statusul ulterior.")
            else:
                st.error("Te rugam sa completezi campurile obligatorii (Nume si Descriere).")

# 2: Verificare Status
with tab2:
    st.header("Verifica stadiul cererii tale")
    id_cautat = st.text_input("Introdu Numarul de Iregistrare (ex: REG-2026...)")

    if id_cautat:
        df = incarca_date()
        rezultat = df[df['ID'] == id_cautat]

        if not rezultat.empty:
            st.info(f"Status actual pentru {id_cautat}: **{rezultat['Status'].values[0]}**")
            st.write(f"Data depunerii: {rezultat['Data'].values[0]}")
        else:
            st.error("Nu a fost găsită nicio cerere cu acest numar.")

#3: FUNCȚIONAR
with tab3:
    st.header("Gestionare Cereri (Acces Funcționar)")

    parola = st.text_input("Introdu codul de acces funcționar", type="password")

    if parola == "user":
        date_cereri = incarca_date()

        if not date_cereri.empty:
            st.subheader("Lista Cereri Primite")
            st.dataframe(date_cereri, use_container_width=True)

            st.markdown("---")
            st.subheader("Actualizare Rapida")

            col1, col2 = st.columns(2)
            with col1:
                id_selectat = st.selectbox("Selecteaza ID-ul pentru modificare", date_cereri["ID"])
            with col2:
                nou_status = st.selectbox("Nou Status", ["In așteptare", "In lucru", "Finalizat", "Respins"])

            if st.button("Actualizează Status"):
                date_cereri.loc[date_cereri['ID'] == id_selectat, 'Status'] = nou_status
                salveaza_date(date_cereri)
                st.success(f"Statusul pentru {id_selectat} a fost schimbat in: {nou_status}")
                st.rerun()
        else:
            st.info("Nu exista cereri de procesat.")
    elif parola:
        st.error("Acces refuzat. Parola incorectă.")