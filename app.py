import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Tőzsde Platform", page_icon="📈", layout="wide")

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Gyakorlat01",        
        database="TozsdeAdatok" 
    )
    cursor = connection.cursor()
except mysql.connector.Error as err:
    st.error(f"Adatbázis hiba: {err}")
    st.stop()

st.sidebar.title("Navigáció")
menupont = st.sidebar.radio("Ugrás ide:", ["Főoldal", "Kimutatások (Nyilvános)", "Személyes Adatok (Védett)"])

# Főoldal
if menupont == "Főoldal":
    st.title("Tőzsde és Osztalék Napló 📈")
    st.write("Üdvözöllek a valós idejű tőzsdei szimulációs platformodon!")
    st.warning("⚠️ FIGYELMEZTETÉS: Ez egy teszt alkalmazás! Kérjük, hogy biztonsági okokból NE adjon meg sehol valós adatokat!")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Felhasználó regisztráció")
        with st.form("felhasznalo_form", clear_on_submit=True):
            nev = st.text_input("Név (pl. Teszt Elek):")
            email = st.text_input("E-mail cím:")
            eletkor = st.number_input("Életkor:", min_value=18, max_value=99, value=25)
            bankszamla = st.text_input("Fiktív bankszámlaszám (Pontosan 5 számjegy):", max_chars=5)
            
            submit_user = st.form_submit_button("Profil mentése")
            
            if submit_user:
                if not nev or not email or not bankszamla:
                    st.error("Minden mező kötelező!")
                elif not bankszamla.isdigit() or len(bankszamla) != 5:
                    st.error("A bankszámlaszámnak pontosan 5 jegyű számnak kell lennie!")
                else:
                    try:
                        # Javítva
                        query = "INSERT INTO Felhasznalok (nev, email, eletkor, bankszamlaszam, regisztracio_datuma) VALUES (%s, %s, %s, %s, %s);"
                        cursor.execute(query, (nev, email, eletkor, bankszamla, datetime.now().date()))
                        connection.commit()
                        st.success(f"🎉 '{nev}' regisztrálva!")
                    except mysql.connector.Error as err:
                        st.error(f"Hiba: {err}")

    with col2:
        st.subheader("🛒 Részvény vásárlás (VÉTEL)")
        
        cursor.execute("SELECT user_id, nev FROM Felhasznalok;")
        felhasznalok = cursor.fetchall()
        user_opciok = {f[1]: f[0] for f in felhasznalok}
        
        cursor.execute("SELECT ticker, cegnev, aktualis_ar, penznem FROM Reszvenyek;")
        reszvenyek_adatok = cursor.fetchall()
        reszveny_opciok = [f"{r[0]} - {r[1]} ({r[2]} {r[3]})" for r in reszvenyek_adatok]
        reszveny_arak = {r[0]: r[2] for r in reszvenyek_adatok}

        if user_opciok and reszveny_opciok:
            with st.form("vetel_form", clear_on_submit=True):
                valasztott_user_nev = st.selectbox("Ki vásárol?", list(user_opciok.keys()))
                valasztott_reszveny_str = st.selectbox("Melyik részvényt?", reszveny_opciok)
                mennyiseg = st.number_input("Darabszám:", min_value=1, max_value=1000, value=1)
                
                submit_trade = st.form_submit_button("Tranzakció indítása")
                
                if submit_trade:
                    selected_ticker = valasztott_reszveny_str.split(" - ")[0]
                    u_id = user_opciok[valasztott_user_nev]
                    v_ar = reszveny_arak[selected_ticker]
                    
                    try:
                        query = "INSERT INTO Tranzakciok (user_id, ticker, muvelet_tipus, mennyiseg, veteli_ar, tranzakcio_ideje) VALUES (%s, %s, 'VÉTEL', %s, %s, %s);"
                        cursor.execute(query, (u_id, selected_ticker, mennyiseg, v_ar, datetime.now()))
                        connection.commit()
                        st.success(f"✅ Sikeresen megvásárolva {mennyiseg} db {selected_ticker}!")
                    except mysql.connector.Error as err:
                        st.error(f"Hiba: {err}")
        else:
            st.info("Kérjük regisztráljon legalább egy felhasználót a vásárláshoz!")

# Kimutatások
elif menupont == "Kimutatások (Nyilvános)":
    st.title("📊 Tőzsdei Kimutatások")
    st.info("Anonim piaci történeti trendek fix, statikus adatok alapján.")

    # Portfólió
    query_portfolio = """
    SELECT 
        t.ticker AS 'Részvény',
        SUM(CASE WHEN t.muvelet_tipus = 'VÉTEL' THEN t.mennyiseg ELSE -t.mennyiseg END) AS 'Meglévő db'
    FROM Tranzakciok t
    GROUP BY t.ticker;
    """
    df_port = pd.read_sql(query_portfolio, connection)
    
    if not df_port.empty:
        st.subheader("📈 Piaci alapú részvényeloszlás a platformon (Darabszám szerint)")
        fig1 = px.pie(df_port, values='Meglévő db', names='Részvény', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig1, use_container_width=True)
    
    # Árfolyamok
    st.subheader("📉 Történeti Árfolyamváltozások (2023 - 2026 Június, USD)")
    
    query_ar = "SELECT datum, ticker, zaro_ar AS 'zaro_ar_usd' FROM NapiArfolyamok ORDER BY datum;"
    df_ar = pd.read_sql(query_ar, connection)
    
    cursor.execute("SELECT ticker FROM Reszvenyek;")
    minden_letezo_ticker = [r[0] for r in cursor.fetchall()]

    if not df_ar.empty:
        lista_opciok = ["Összes részvény egyszerre"] + minden_letezo_ticker
        valasztott_ticker = st.selectbox("Válaszd ki a megjeleníteni kívánt részvényt:", lista_opciok)
        
        if valasztott_ticker == "Összes részvény egyszerre":
            df_grafikon = df_ar
        else:
            df_grafikon = df_ar[df_ar['ticker'] == valasztott_ticker]

        fig2 = px.line(
            df_grafikon, 
            x='datum', 
            y='zaro_ar_usd', 
            color='ticker', 
            markers=True, 
            labels={'zaro_ar_usd': 'Árfolyam értéke (USD)', 'datum': 'Dátum'}
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("A NapiArfolyamok tábla jelenleg üres. Kérjük futtasd le az SQL szkriptet!")

    # Táblázatok
    st.subheader("🗄️ Nyers adatok megtekintése")
    cursor.execute("SHOW TABLES;")
    biztonsagos_tablak = [t[0] for t in cursor.fetchall() if t[0].lower() != 'felhasznalok']
    valasztott_tabla = st.selectbox("Válaszd ki a táblát:", biztonsagos_tablak)
    df_raw = pd.read_sql(f"SELECT * FROM {valasztott_tabla};", connection)
    st.dataframe(df_raw, use_container_width=True)

# Adminisztráció
elif menupont == "Személyes Adatok (Védett)":
    st.title("🔒 Védett Személyes Adatok")
    jelszo_input = st.text_input("Adminisztrátori jelszó:", type="password")
    
    if jelszo_input == "adat01":
        st.success("🔓 Hozzáférés engedélyezve!")
        
        # Statisztika
        st.subheader("📊 Felhasználók összesített befektetései")
        query_user_invest = """
        SELECT 
            f.nev AS 'Befektető',
            SUM(CASE WHEN t.muvelet_tipus = 'VÉTEL' THEN t.mennyiseg * t.veteli_ar ELSE -(t.mennyiseg * t.veteli_ar) END) AS 'Befektetett összeg'
        FROM Tranzakciok t
        JOIN Felhasznalok f ON t.user_id = f.user_id
        GROUP BY f.nev;
        """
        df_ui = pd.read_sql(query_user_invest, connection)
        
        if not df_ui.empty:
            fig3 = px.bar(df_ui, x='Befektető', y='Befektetett összeg', color='Befektető', text_auto='.2s')
            st.plotly_chart(fig3, use_container_width=True)
            
        # Ügyfelek
        st.subheader("👥 Regisztrált ügyfelek privát adatai")
        df_users = pd.read_sql("SELECT * FROM Felhasznalok;", connection)
        st.dataframe(df_users, use_container_width=True)
            
    elif jelszo_input != "":
        st.error("❌ Helytelen jelszó!")

if 'connection' in locals() and connection.is_connected():
    cursor.close()
    connection.close()