import streamlit as st
import base64
from pathlib import Path
from streamlit_extras.stylable_container import stylable_container
import utils
import pandas as pd
from auth import check_password

# Faire le calendrier des équipes

# Vérification du password
if not check_password():
    st.stop()

# -- Import des données
TABLE_INTERCLUB = utils.read_sheet("TABLE_INTERCLUB")

# -- Fonction de la page "Accueil"


# Upload d'image en local
def img_to_html(
    rel_path_from_app_dir: str,
    alt="image",
    style="max-width:100%; height:auto; text-align: center",
):
    # __file__ = app/pages/0_Accueil.py  → parents[1] = app/
    app_dir = Path(__file__).resolve().parents[1]
    path = (app_dir / rel_path_from_app_dir).resolve()  # ex: "assets/img/AOB_LOGO.jpg"
    data = path.read_bytes()  # lève clairement si absent
    ext = path.suffix.lstrip(".").lower()
    b64 = base64.b64encode(data).decode()
    return f'<img src="data:image/{ext};base64,{b64}" alt="{alt}" style="{style}">'


# Elements de la table d'accueil
def table_item(text):
    st.markdown(
        f"<div style='text-align:center; padding-top:1px'><span style='float:left; font-size:1.3rem'>{text}</span></div>",
        unsafe_allow_html=True,
    )


# Définir V/D/E
def match_output(team):
    df = TABLE_INTERCLUB[(TABLE_INTERCLUB["division"] == team)].reset_index(drop=True)
    v = (df["aob_score"] > df["opponent_score"]).sum()
    d = (df["aob_score"] < df["opponent_score"]).sum()
    e = (df["aob_score"] == df["opponent_score"]).sum()

    # Calcul du nombre de points
    pts = v * 3 + e * 2 + d * 1
    return v, e, d, pts


# -- LAYOUT

st.set_page_config(page_title="Accueil", layout="wide")

html = f"""
<div style="display:flex; justify-content:center; padding:8px; border-radius:12px">
{img_to_html("assets/img/AOB_LOGO.jpg", alt="Logo", style="width:220px; border-radius:12px;")}
</div>
"""
st.markdown(html, unsafe_allow_html=True)
st.markdown(
    f"<div style='font-size:1rem; text-align:center; margin-bottom: 40px'>SAISON 2025/26</div>",
    unsafe_allow_html=True,
)

# Affichage des statistiques du club
df = pd.DataFrame(
    {
        "Equipes": ["PR", "D2", "D3", "D5", "H2", "V3"],
        "Match(s) joué(s)": [
            len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "PR"]),
            len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "D2"]),
            len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "D3"]),
            len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "D5"]),
            len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "H2"]),
            len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "V3"]),
        ],
        "Victoire(s)": [
            str(match_output("PR")[0]),
            str(match_output("D2")[0]),
            str(match_output("D3")[0]),
            str(match_output("D5")[0]),
            str(match_output("H2")[0]),
            str(match_output("V3")[0]),
        ],
        "Egalité(s)": [
            str(match_output("PR")[1]),
            str(match_output("D2")[1]),
            str(match_output("D3")[1]),
            str(match_output("D5")[1]),
            str(match_output("H2")[1]),
            str(match_output("V3")[1]),
        ],
        "Défaite(s)": [
            str(match_output("PR")[2]),
            str(match_output("D2")[2]),
            str(match_output("D3")[2]),
            str(match_output("D5")[2]),
            str(match_output("H2")[2]),
            str(match_output("V3")[2]),
        ],
        # "B": ["", "", "", "", "", ""],
        "Point(s) cumulé(s)": [
            str(match_output("PR")[3]),
            str(match_output("D2")[3]),
            str(match_output("D3")[3]),
            str(match_output("D5")[3]),
            str(match_output("H2")[3]),
            str(match_output("V3")[3]),
        ],
    }
)

# Trié par le nombre de points
df = df.sort_values("Point(s) cumulé(s)", ascending=False)

# Affichage sous forme de dataframe
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown(
    """
<style>
/* --- CORPS du tableau : centre de la 2e à la n-ième colonne --- */
[data-testid="stDataFrame"] div[role="rowgroup"] > div[role="row"] 
  > div[role="gridcell"]:not(:first-child) {
  display: flex;               /* important pour centrer correctement */
  align-items: center;
  justify-content: center;
}

/* --- EN-TÊTES : centre de la 2e à la n-ième colonne --- */
[data-testid="stDataFrame"] div[role="rowgroup"] > div[role="row"] 
  > div[role="columnheader"]:not(:first-child) {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* --- Taille de police dans toutes les cellules (corps + header) --- */
[data-testid="stDataFrame"] div[role="rowgroup"] [role="gridcell"] *,
[data-testid="stDataFrame"] div[role="rowgroup"] [role="columnheader"] * {
  font-size: 1.1rem !important;   /* ajuste à ton goût */
  line-height: 1.2;
}
</style>
""",
    unsafe_allow_html=True,
)
