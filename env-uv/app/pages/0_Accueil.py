import streamlit as st
import base64
from pathlib import Path
import utils
from auth import check_pin

# 🔒 protéger cette page avec le PIN
if not check_pin(page_key="record", secret_path="record_lock.pin"):
    st.stop()

##################################################################
#                          DONNEES                               #
##################################################################
TABLE_INTERCLUB = utils.read_sheet("TABLE_INTERCLUB")

##################################################################
#                         FONCTIONS                              #
##################################################################


# Upload d'image en local
def img_to_html(
    rel_path_from_app_dir: str,
    alt="image",
    style="max-width:100%; height:auto; text-align: center",
):
    """Convertir une image au format .png/.jpg en une balise HTML

    Args:
        rel_path_from_app_dir (str): Chemin relatif au fichier image.
        alt (str, optional): Type de fichie, ("image" par défaut).
        style (str, optional): Style CSS additionnel (par défaut: "max-width:100%; height:auto; text-align: center").
    """
    # __file__ = app/pages/0_Accueil.py  → parents[1] = app/
    app_dir = Path(__file__).resolve().parents[1]
    path = (app_dir / rel_path_from_app_dir).resolve()  # ex: "assets/img/AOB_LOGO.jpg"
    data = path.read_bytes()  # lève clairement si absent
    ext = path.suffix.lstrip(".").lower()
    b64 = base64.b64encode(data).decode()
    return f'<img src="data:image/{ext};base64,{b64}" alt="{alt}" style="{style}">'


# Définir V/D/E
def match_output(division: str):
    """Calcul des résultats d'interclub (victoire (V) / Egalité (E) / Défaite (D)) et du nombre de points remporté en conséquence.

    Args:
        division (str): Division de l'équipe (PR / D3 / D2 / D5 / V3 / H2)

    Returns:
        (v,e,d,pts) : (Nombre de victoires, égalités, défaites, somme des points remportés)
    """
    df = TABLE_INTERCLUB[(TABLE_INTERCLUB["division"] == division)].reset_index(
        drop=True
    )
    v = (df["aob_score"] > df["opponent_score"]).sum()
    d = (df["aob_score"] < df["opponent_score"]).sum()
    e = (df["aob_score"] == df["opponent_score"]).sum()

    # Calcul du nombre de points
    pts = v * 3 + e * 2 + d * 1
    return v, e, d, pts


##################################################################
#                           LAYOUT                               #
##################################################################

st.set_page_config(page_title="Accueil", layout="wide")

# -- Image du club de badminton d'Orgères (35230)
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


# -- Images des équipes dans les différentes divisions de la saison 2025/26
def show_teams(path):
    html = f"""
        <div style="display:flex; justify-content:center; padding:8px; border-radius:12px; margin-bottom:30px">
        {img_to_html(path, alt="Logo", style="width:280px; border-radius:12px;")}
        </div>
        """
    return html


c1, c2, c3 = st.columns(3, gap="small")
with c1:
    st.markdown(show_teams("assets/img/PR.jpg"), unsafe_allow_html=True)
    st.markdown(show_teams("assets/img/D5.jpg"), unsafe_allow_html=True)
with c2:
    st.markdown(show_teams("assets/img/D2.jpg"), unsafe_allow_html=True)
    st.markdown(show_teams("assets/img/H2.jpg"), unsafe_allow_html=True)
with c3:
    st.markdown(show_teams("assets/img/D3.jpg"), unsafe_allow_html=True)
    st.markdown(show_teams("assets/img/V3.jpg"), unsafe_allow_html=True)
