import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import utils
from auth import check_password

# Vérification du password
if not check_password():
    st.stop()

st.set_page_config(page_title="Historique", layout="wide")

# -- Données brutes
EQUIPE = ["H2", "V3", "PR", "D2", "D3", "D5"]

c1, c2, c3 = st.columns([3, 1, 1], gap="small")
with c1:
    # -- Dropdown de filtrage d'équipe
    categorie = st.multiselect("Equipe(s)", EQUIPE, key="equipe")
with c2:
    # -- Dropdown des journées
    day = st.multiselect(
        "Journée(s)",
        list(utils.read_sheet("TABLE_INTERCLUB")["journey"].unique()),
        key="day",
    )
with c3:
    # -- Dropdown des journées
    result = st.multiselect(
        "Résultat(s)",
        ["Victoire", "Défaite", "Nulle"],
        key="result",
    )


# --- Chargement des données (cache conseillé pour éviter de relire à chaque fois) ---
@st.cache_data(ttl=30)
def load_matches():
    return utils.read_sheet("TABLE_INTERCLUB")


df_all = load_matches()

# --- Application des filtres (à chaque rerun) ---
df = df_all.copy().reset_index(drop=True)

if categorie:  # si liste non vide
    df = df[df["division"].isin(categorie)].reset_index(
        drop=True
    )  # adapte la colonne si besoin

if day:
    df = df[df["journey"].isin(day)].reset_index(drop=True)


def filter_by_result(
    df: pd.DataFrame, selected: list, home_col="aob_score", away_col="opponent_score"
) -> pd.DataFrame:
    if not selected:
        return df

    # Convertit en numériques (au cas où ce sont des strings)
    s_home = pd.to_numeric(df[home_col], errors="coerce")
    s_away = pd.to_numeric(df[away_col], errors="coerce")

    mask = False
    if "Victoire" in selected:
        mask |= s_home > s_away
    if "Défaite" in selected:
        mask |= s_home < s_away
    if "Nulle" in selected:
        mask |= s_home == s_away

    return df[mask].reset_index(drop=True)


if result:
    df = filter_by_result(
        utils.read_sheet("TABLE_INTERCLUB"), result
    )  # adapte au nom réel de ta colonne

# --- Affichage ---
# st.dataframe(df, use_container_width=True)

# -- Mini KPI issus de la recherche
st.caption(f"{len(df)} matchs trouvés")

# Affichage des résultats
for i in reversed(range(len(df))):
    if df["aob_score"].loc[i] > df["opponent_score"].loc[i]:
        utils.box_color_histo(
            df["date"].loc[i],
            df["journey"].loc[i],
            df["id"].loc[i],
            f'{df["aob_team"].loc[i]} ({df["division"].loc[i]})',
            df["opponent_team"].loc[i],
            df["aob_score"].loc[i],
            df["opponent_score"].loc[i],
            box_style=utils.win_box,
        )
    elif df["aob_score"].loc[i] < df["opponent_score"].loc[i]:
        utils.box_color_histo(
            df["date"].loc[i],
            df["journey"].loc[i],
            df["id"].loc[i],
            f'{df["aob_team"].loc[i]} ({df["division"].loc[i]})',
            df["opponent_team"].loc[i],
            df["aob_score"].loc[i],
            df["opponent_score"].loc[i],
            box_style=utils.loose_box,
        )
    else:
        utils.box_color_histo(
            df["date"].loc[i],
            df["journey"].loc[i],
            df["id"].loc[i],
            f'{df["aob_team"].loc[i]} ({df["division"].loc[i]})',
            df["opponent_team"].loc[i],
            df["aob_score"].loc[i],
            df["opponent_score"].loc[i],
            box_style=utils.draw_box,
        )
