import streamlit as st
import base64
from pathlib import Path
from streamlit_extras.stylable_container import stylable_container
import utils

# -- Import des données
TABLE_INTERCLUB = utils.read_sheet("TABLE_INTERCLUB")

# -- Fonction de la page "Accueil"


# Upload d'image en local
def img_to_html(
    rel_path_from_app_dir: str, alt="image", style="max-width:100%; height:auto;"
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
def match_output_mixte(team):
    df = TABLE_INTERCLUB[(TABLE_INTERCLUB["division"] == team)].reset_index(drop=True)
    v = (df["aob_score"] > 4).sum()
    d = (df["aob_score"] < 4).sum()
    e = (df["aob_score"] == 4).sum()
    return v, d, e


def match_output_men(team):
    df = TABLE_INTERCLUB[(TABLE_INTERCLUB["division"] == team)].reset_index(drop=True)
    v = (df["aob_score"] > 3).sum()
    d = (df["aob_score"] < 3).sum()
    e = (df["aob_score"] == 3).sum()
    return v, d, e


# -- LAYOUT

st.set_page_config(page_title="Accueil", layout="wide")

t1, t2 = st.columns([1, 5])
with t1:
    html = f"""
    <div style="display:flex; justify-content:center; padding:8px; border-radius:12px">
    {img_to_html("assets/img/AOB_LOGO.jpg", alt="Logo", style="width:220px; border-radius:12px;")}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
with t2:
    st.markdown(
        f"<div style='font-size:10rem; text-align:center'>SAISON 2025/26</div>",
        unsafe_allow_html=True,
    )


with stylable_container(key="box-vert-PR", css_styles=utils.draw_box):
    c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 1, 1, 1, 1, 1, 1], gap="small")
    with c1:
        table_item("Equipes")
        table_item("PR")
        table_item("D2")
        table_item("D3")
        table_item("D5")
        table_item("H2")
        table_item("V3")
    with c2:
        table_item("J")
        table_item(len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "PR"]))
        table_item(len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "D2"]))
        table_item(len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "D3"]))
        table_item(len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "D5"]))
        table_item(len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "H2"]))
        table_item(len(TABLE_INTERCLUB[TABLE_INTERCLUB["division"] == "V3"]))
    with c3:
        table_item("V")
        table_item(str(match_output_mixte("PR")[0]))
        table_item(str(match_output_mixte("D2")[0]))
        table_item(str(match_output_mixte("D3")[0]))
        table_item(str(match_output_mixte("D5")[0]))
        table_item(str(match_output_mixte("H2")[0]))
        table_item(str(match_output_mixte("V3")[0]))
    with c4:
        table_item("D")
        table_item(str(match_output_mixte("PR")[1]))
        table_item(str(match_output_mixte("D2")[1]))
        table_item(str(match_output_mixte("D3")[1]))
        table_item(str(match_output_mixte("D5")[1]))
        table_item(str(match_output_mixte("H2")[1]))
        table_item(str(match_output_mixte("V3")[1]))
    with c5:
        table_item("E")
        table_item(str(match_output_mixte("PR")[2]))
        table_item(str(match_output_mixte("D2")[2]))
        table_item(str(match_output_mixte("D3")[2]))
        table_item(str(match_output_mixte("D5")[2]))
        table_item(str(match_output_mixte("H2")[2]))
        table_item(str(match_output_mixte("V3")[2]))
    with c6:
        table_item("B")
        table_item("")
        table_item("")
        table_item("")
        table_item("")
        table_item("")
        table_item("")
    with c7:
        table_item("Pts")
        table_item("")
        table_item("")
        table_item("")
        table_item("")
        table_item("")
        table_item("")
