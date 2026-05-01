import streamlit as st
import pandas as pd
import utils
from datetime import date


##################################################################
#                          DONNEES                               #
##################################################################
TABLE_INTERCLUB = utils.TABLE_INTERCLUB.copy()
TABLE_PLAYERS = utils.TABLE_PLAYERS.copy()
TABLE_MATCHS = utils.TABLE_MATCHS.copy()

rank_order = {
    "NC": 0,
    "P12": 1,
    "P11": 2,
    "P10": 3,
    "D9": 4,
    "D8": 5,
    "D7": 6,
    "R6": 7,
    "R5": 8,
    "R4": 9,
    "N3": 10,
    "N2": 11,
    "N1": 12,
}

# st.markdown(
#     """
# <div style="font-size: 28px;">
#     <span style="color: green;">⬆</span>
#     <span style="color: red;">⬇</span>
#     <span style="color: dodgerblue; font-size:1.6em">⬌</span>
# </div>
# """,
#     unsafe_allow_html=True,
# )


##################################################################
#                         FONCTIONS                              #
##################################################################
def rank_stylizing(rank: str):
    """Customisation de l'affichage du classement du joueur

    Args:
        rank (str): Classement officiel du joueur.
    """
    if rank == "NC":
        color = "grey"
    elif rank in ["P12", "P11", "P10"]:
        color = "orange"
    elif rank in ["D9", "D8", "D7"]:
        color = "green"
    elif rank in ["R6", "R5", "R4"]:
        color = "blue"
    elif rank in ["N3", "N2", "N1"]:
        color = "red"
    else:
        return

    st.markdown(
        f"""
        <div style="font-size: 20px;">
            <span style="
                background-color: {color};
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-weight: bold;
            ">
                {rank}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def rank_evolution(first_rank: str, last_rank: str):
    """Gestion de l'indicateur d'évolution du classement du joueur

    Args:
        first_rank (str): Classement officiel du joueur selon la date d'entrée du filtre.
        last_rank (str): Classement officiel du joueur selon la date de sortie du filtre.
    """
    if pd.isna(first_rank) or first_rank == "" or first_rank is None:
        return

    if pd.isna(last_rank) or last_rank == "" or last_rank is None:
        return

    best_rank_value = rank_order.get(first_rank)
    last_rank_value = rank_order.get(last_rank)

    if best_rank_value > last_rank_value:
        html = st.markdown(
            """
        <div style="font-size: 20px;">
            <span style="color: green; display:inline-block; margin-top:-4px;">⬆</span>
        </div>
        """,
            unsafe_allow_html=True,
        )
    elif best_rank_value == last_rank_value:
        html = st.markdown(
            """
        <div style="font-size: 20px;">
            <span style="color: dodgerblue; font-size:1.6em; display:inline-block; margin-top:-18px;">⬌</span>
        </div>
        """,
            unsafe_allow_html=True,
        )
    elif best_rank_value < last_rank_value:
        html = st.markdown(
            """
            <div style="font-size: 20px;">
                <span style="color: red; display:inline-block; transform: translateY(-2px);">⬇</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        return

    return html


def each_lines(
    name: str,
    rank_s: str,
    rank_d: str,
    rank_m: str,
    first_rank_s: str,
    first_rank_d: str,
    first_rank_m: str,
):
    """Affichage de tous les joueurs et des différents classement et évolutions.

    Args:
        name (str): NOM Prénom du joueur.
        rank_s (str): Classement officiel en simple du joueur à date d'entrée du filtre.
        rank_d (str): Classement officiel en double du joueur à date d'entrée du filtre.
        rank_m (str): Classement officiel en mixte du joueur à date d'entrée du filtre.
        first_rank_s (str): Classement officiel en simple du joueur à date de sortie du filtre.
        first_rank_d (str): Classement officiel en double du joueur à date de sortie du filtre.
        first_rank_m (str): Classement officiel en mixte du joueur à date de sortie du filtre.
        first_rank (str): Classement officiel du joueur selon la date d'entrée du dropdown.
        last_rank (str): Classement officiel du joueur selon la date de sortie du dropdown.
    """
    # Ligne de séparation
    st.markdown(
        """
        <hr style="margin: 6px 0;">
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4, c5, c6, c7 = st.columns([5, 1, 2, 1, 2, 1, 2], gap="small")
    with c1:  # Nom du joueur
        st.text(name)
    with c2:  # Classement en simple
        rank_stylizing(rank_s)
    with c3:  # UP / DOWN / EVEN
        rank_evolution(rank_s, first_rank_s)
    with c4:
        rank_stylizing(rank_d)  # Classement en double
    with c5:  # UP / DOWN / EVEN
        rank_evolution(rank_d, first_rank_d)
    with c6:  # Classement en mixte
        rank_stylizing(rank_m)
    with c7:  # UP / DOWN / EVEN
        rank_evolution(rank_m, first_rank_m)


def rank_simple(df: pd.DataFrame) -> tuple[str, str]:
    """Récupère le classement à date d'entrée du filtre et à date de sortie en simple.

    Args:
        df (pd.DataFrame): Jeu de données filtrées en fonction du joueur (via son ID)
    """
    df_simple = (
        df[df["type_match"].str.contains("SD|SH", na=False)]
        .copy()
        .reset_index(drop=True)
    )

    if df_simple.empty:
        return "", ""

    # Classement initial de la saison
    first_rank = df_simple.sort_values(by="id", ascending=True).iloc[0]["aob_rank"]

    # Dernier classement connu selon l'id le plus récent
    df_simple = df_simple.dropna(subset=["aob_rank"])
    if df_simple.empty:
        last_rank = ""
    else:
        last_rank = df_simple.sort_values(by="id", ascending=False).iloc[0]["aob_rank"]

    return first_rank, last_rank


def rank_double(
    df: pd.DataFrame,
    player_id: int,
    match_type: list[str],
) -> tuple[str, str]:
    """Récupère le classement à date d'entrée du filtre et à date de sortie en double/mixte.

    Args:
        df (pd.DataFrame): Jeu de données filtrées en fonction du joueur (via son ID).
        player_id (int): Identifiant unique du joueur.
        match_type (list[str]): Type de match joués (['MX1','MX2'] ou ['DH','DD'])
    """

    df_filtered = df[
        (df["type_match"].isin(match_type))
        & (
            df["aob_player_id"]
            .astype(str)
            .str.split("/")
            .apply(lambda ids: str(player_id) in ids)
        )
    ].copy()

    if df_filtered.empty:
        return None, None

    def extract_player_rank(row):
        ids = [i.strip() for i in str(row["aob_player_id"]).split("/")]
        ranks = [r.strip() for r in str(row["aob_rank"]).split("/")]

        if str(player_id) in ids:
            idx = ids.index(str(player_id))
            if idx < len(ranks):
                return ranks[idx]

        return None

    df_filtered["player_rank"] = df_filtered.apply(extract_player_rank, axis=1)
    df_filtered = df_filtered.dropna(subset=["player_rank"])

    if df_filtered.empty:
        return "", ""

    # Classement intial de la saison
    first_rank = df_filtered.sort_values(by="id", ascending=True).iloc[0]["player_rank"]

    # Dernier classement connu selon l'id le plus récent
    last_rank = df_filtered.sort_values(by="id", ascending=False).iloc[0]["player_rank"]

    return first_rank, last_rank


def player_has_division(division_value: str, selected_team: str):
    """Détermine l'appartenance ou non d'un joueur à une équipe enregistrée.

    Args:
        division_value (str): Liste des équipe auquel le joueur appartient.
        selected_team (_type_): Equipe recherchée depuis le filtre.
    """
    if pd.isna(division_value):
        return False

    divisions = [d.strip() for d in str(division_value).split("/")]
    return selected_team in divisions


##################################################################
#                           LAYOUT                               #
##################################################################
st.set_page_config(page_title="Historique", layout="wide")

c1, c2, c3 = st.columns([2, 5, 2], gap="small")

# -------------------------
# Dropdown équipe
# -------------------------
with c1:
    options_teams = ["-- Toutes les équipes --"] + sorted(
        utils.TABLE_INTERCLUB["division"].dropna().unique().tolist()
    )

    st.selectbox(
        "Filtrer par équipe:",
        options_teams,
        index=0,
        key="dd_team_filter_rank",
    )


# -------------------------
# Dropdown joueur
# -------------------------
with c2:
    options_players = ["-- Tous les joueurs --"] + sorted(
        TABLE_PLAYERS["name"].dropna().unique().tolist()
    )

    st.selectbox(
        "Filtrer par joueur:",
        options_players,
        index=0,
        key="dd_player_filter_rank",
    )

# -------------------------
# Dropdown saison
# -------------------------
with c3:
    options_date = st.date_input(
        "Sélectionner une période",
        value=(date(2025, 8, 1), date.today()),
        format="DD/MM/YYYY",
    )

# -------------------------
# Filtre via dropdowns
# -------------------------
display_df = utils.TABLE_PLAYERS.copy().sort_values(by="name").reset_index(drop=True)

selected_team = st.session_state.get("dd_team_filter_rank")
selected_player = st.session_state.get("dd_player_filter_rank")

if selected_team != "-- Toutes les équipes --":
    display_df = display_df[
        display_df["division"].apply(lambda x: player_has_division(x, selected_team))
    ]
    display_df = display_df.sort_values(by="name").reset_index(drop=True)

if selected_player != "-- Tous les joueurs --":
    display_df = display_df[display_df["name"] == selected_player]
    display_df = display_df.sort_values(by="name").reset_index(drop=True)


# -------------------------
# Affichage de tous les joueurs
# -------------------------
for i in range(len(display_df)):
    # Ajouter la colonne 'date' au dataframe utilisé
    df = TABLE_MATCHS.merge(TABLE_INTERCLUB[["id", "date"]], on="id", how="left")

    # S'assurer que la colonne date est bien au format date
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Filtrer seulement si deux dates sont sélectionnées
    if isinstance(options_date, tuple) and len(options_date) == 2:
        date_debut, date_fin = options_date
        df = df[(df["date"] >= date_debut) & (df["date"] <= date_fin)]

    # Générer les lignes sur la page de 'Ranking' de l'application
    each_lines(
        display_df.name[i],
        rank_simple(df=df[df.aob_player_id == display_df["id_player"][i]])[1],
        rank_double(
            df=df,
            player_id=display_df["id_player"][i],
            match_type=["DH", "DD"],
        )[1],
        rank_double(
            df=df,
            player_id=display_df["id_player"][i],
            match_type=["MX1", "MX2"],
        )[1],
        rank_simple(df=df[df.aob_player_id == display_df["id_player"][i]])[0],
        rank_double(
            df=df,
            player_id=display_df["id_player"][i],
            match_type=["DH", "DD"],
        )[0],
        rank_double(
            df=df,
            player_id=display_df["id_player"][i],
            match_type=["MX1", "MX2"],
        )[0],
    )
