#  Felhőalapú Tőzsde és Osztalék Platform

Ez egy teljes körű (End-to-End) webalkalmazás, amely egy leegyszerüsített tranzakciók szimulációját és árfolyamadatok vizualizációját látja el felhőalapú környezetben.

Éles Elérés
* **Weboldal:** [Kattints ide a megnyitáshoz](https://tozsde-platform-lmbnzav7xkrorqsurf7pzs.streamlit.app/)

#Alkalmazott Technológiák
* **Frontend / Dashboard:** Python & Streamlit Cloud
* **Adatbázis-kezelés:** MySQL (Relációs adatbázis-modell)
* **Felhőalapú Infrastruktúra:** Railway Cloud (MySQL bázis)
* **Adatfeldolgozás & Grafikonok:** Pandas, Plotly Express
* **Verziókezelés:** Git & GitHub

## 📋Főbb Funkciók
* **Felhasználói regisztráció:** Új ügyfelek rögzítése validált adatokkal közvetlenül a felhős MySQL-be.
* **Tranzakció-kezelés (VÉTEL):** Dinamikus részvényvásárlás a bázisban tárolt aktuális árak alapján.
* **Interaktív kimutatások:** Portfólió-eloszlás (Pie chart) és történeti árfolyamváltozások (Line chart) vizualizációja.
* **Adminisztrátori felület:** Jelszóval védett felület a regisztrált ügyfelek privát adatainak megtekintéséhez.

## 🔒 Adatbiztonság
Az alkalmazás hozzáférési adatai (Credentials) nem szerepelnek a forráskódban; a biztonságos adatbázis-kommunikáció a Streamlit felhő környezeti változóin keresztül (**Secrets Management**) valósul meg.
