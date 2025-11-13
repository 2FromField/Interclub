import streamlit as st
import utils
import altair as alt
import sqlite3
import pandas as pd

st.set_page_config(page_title="Statistiques", layout="wide")

st.title("Statistiques")

##################################################################
#                            LAYOUT                              #
##################################################################
c1, c2 = st.columns([2, 5], gap="small")
with c1:
    options_teams = ["-- Toutes les équipes --"] + utils.TABLE_INTERCLUB[
        "division"
    ].unique().tolist()
    filter_by_teal = st.selectbox(
        "Filtrer par équipe:",
        options_teams,
        index=0,
        key="dd_team_filter",
    )
with c2:
    if st.session_state.get("dd_team_filter") == "-- Toutes les équipes --":
        options_players = ["-- Tous les joueurs --"] + utils.TABLE_PLAYERS[
            "name"
        ].unique().tolist()
        filter_by_player = st.selectbox(
            "Filtrer par joueur:",
            options_players,
            index=0,
            key="dd_player_filter",
        )
    else:
        filtered_df = utils.TABLE_PLAYERS[
            utils.TABLE_PLAYERS["division"]
            .fillna("")
            .str.contains(str(st.session_state.get("dd_team_filter")), na=False)
        ].reset_index(drop=True)
        #
        options_players = ["-- Tous les joueurs --"] + utils.TABLE_PLAYERS[
            (
                utils.TABLE_PLAYERS["division"]
                .fillna("")
                .str.contains(str(st.session_state.get("dd_team_filter")), na=False)
            )
        ]["name"].unique().tolist()
        filter_by_player = st.selectbox(
            "Filtrer par joueur:",
            options_players,
            index=0,
            key="dd_player_filter",
        )

##################################################################
#                     GESTION FILTRES                            #
##################################################################

m_ic = utils.TABLE_MATCHS.merge(
    utils.TABLE_INTERCLUB[["id", "date", "division", "aob_team", "opponent_team"]],
    left_on="id",
    right_on="id",
    how="left",
)


# --- helpers ---
def split2(series: pd.Series):
    """Retourne (p1, p2) en découpant à '/', avec strip et '' si absent."""
    s = series.fillna("").astype(str).str.strip()
    parts = s.str.split("/", n=1, expand=True)
    p1 = parts[0].fillna("").str.strip()
    p2 = (
        (parts[1].fillna("").str.strip())
        if parts.shape[1] > 1
        else pd.Series([""] * len(s), index=s.index)
    )
    return p1, p2


def split2_col(df: pd.DataFrame, col: str):
    """Applique split2 sur df[col] si la colonne existe, sinon sur une série vide."""
    base = df[col] if col in df.columns else pd.Series([""] * len(df), index=df.index)
    return split2(base)


def join_if_two(p1: pd.Series, p2: pd.Series, sep=" / "):
    """'A' + ' / B' seulement si p2 non vide."""
    p1 = p1.fillna("").astype(str)
    p2 = p2.fillna("").astype(str)
    return p1.where(p2.eq(""), p1 + sep + p2)


# 2) Découper les champs potentiellement composés
m_ic["aob_p1_id"], m_ic["aob_p2_id"] = split2_col(m_ic, "aob_player_id")
m_ic["aob_rank_p1"], m_ic["aob_rank_p2"] = split2_col(m_ic, "aob_rank")
m_ic["aob_pts_p1"], m_ic["aob_pts_p2"] = split2_col(m_ic, "aob_pts")

# (optionnel) caster les points en numériques
for col in ["aob_pts_p1", "aob_pts_p2"]:
    m_ic[col] = pd.to_numeric(m_ic[col], errors="coerce")

# 3) Résoudre noms via mapping id → name
players = utils.TABLE_PLAYERS.copy()
players["id_norm"] = players["id_player"].astype(str).str.strip()
id_to_name = players.set_index("id_norm")["name"].to_dict()

m_ic["aob_p1_name"] = (
    m_ic["aob_p1_id"].astype(str).str.strip().map(id_to_name).fillna("")
)
m_ic["aob_p2_name"] = (
    m_ic["aob_p2_id"].astype(str).str.strip().map(id_to_name).fillna("")
)

# 4) Colonnes combinées (si 2 joueurs)
m_ic["player"] = join_if_two(m_ic["aob_p1_name"], m_ic["aob_p2_name"])
m_ic["rank"] = join_if_two(m_ic["aob_rank_p1"], m_ic["aob_rank_p2"])

# pts en texte lisible ("12 / 8"), sans 'None'
p1_txt = m_ic["aob_pts_p1"].astype("Int64").astype(str).replace("<NA>", "", regex=False)
p2_txt = m_ic["aob_pts_p2"].astype("Int64").astype(str).replace("<NA>", "", regex=False)
m_ic["pts"] = join_if_two(p1_txt, p2_txt)

# 5) Sélection finale
result = m_ic[
    ["type_match", "date", "division", "aob_team", "player", "rank", "pts"]
].reset_index(drop=True)

# Filtre d'équipe
df = result.copy()

team_sel = st.session_state.get("dd_team_filter")
player_sel = st.session_state.get("dd_player_filter")

# 1) Filtre équipe (si sélectionnée)
if team_sel and team_sel != "-- Toutes les équipes --":
    df = df[df["division"] == team_sel].reset_index(drop=True)

# 2) Filtre joueur (match par token, insensible à la casse)
if player_sel and player_sel != "-- Tous les joueurs --":
    target = player_sel.strip().casefold()
    # explode pour un match vectorisé sur chaque token séparé par '/'
    tokens = (
        df["player"]
        .fillna("")
        .str.split("/")  # -> liste de noms
        .explode()  # une ligne par nom
        .str.strip()
        .str.casefold()  # normalisation
    )
    mask = tokens.eq(target).groupby(level=0).any()  # any par ligne d'origine
    df = df[mask].reset_index(drop=True)

# Dataframe filtrés (df) à partir des dropdowns
st.dataframe(df, use_container_width=True)


##################################################################
#                       STATS JOUEUR                             #
##################################################################

# # -- Graphique
# Si df est vide ou si la colonne 'player' n'existe pas, on sort proprement
if df.empty or "player" not in df.columns:
    st.info("Aucune donnée à tracer.")
else:
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")

    # --- Déplier les lignes simple/double en lignes unitaires ---
    def split2(s: pd.Series):
        """Retourne (p1, p2) en découpant sur '/', robuste si série vide."""
        s = s.fillna("").astype(str)
        parts = s.str.split("/", n=1)  # -> Series de listes/None
        p1 = parts.str[0].fillna("").str.strip()
        p2 = parts.str[1].fillna("").str.strip()
        return p1, p2

    p1, p2 = split2(df["player"])
    r1, r2 = split2(df["rank"])
    pt1, pt2 = split2(df["pts"])

    unit_rows = pd.concat(
        [
            pd.DataFrame(
                {
                    "date": df["date"],
                    "division": df["division"],
                    "aob_team": df["aob_team"],
                    "player": p1,
                    "rank": r1,
                    "pts": pt1,
                }
            ),
            pd.DataFrame(
                {
                    "date": df["date"],
                    "division": df["division"],
                    "aob_team": df["aob_team"],
                    "player": p2,
                    "rank": r2,
                    "pts": pt2,
                }
            ),
        ],
        ignore_index=True,
    )

    # garder seulement les lignes avec un player non vide
    unit_rows = unit_rows[unit_rows["player"].str.len() > 0].copy()

    # normaliser rank/pts
    unit_rows["rank"] = unit_rows["rank"].str.strip()
    unit_rows["pts"] = pd.to_numeric(
        unit_rows["pts"].str.replace(",", "."), errors="coerce"
    )

    # ordre de l'axe Y (catégoriel)
    unit_rows["rank"] = pd.Categorical(
        unit_rows["rank"], categories=utils.CLASSEMENTS, ordered=True
    )

    # --- Sélection du joueur puis tracé ---
    who = st.session_state.get("dd_player_filter")

    if who != "-- Tous les joueurs --":
        df_player = unit_rows[unit_rows["player"] == who].sort_values("date")
        #
        if df_player.empty:
            st.warning(f"Aucune donnée pour {who}.")
        else:
            chart = (
                alt.Chart(df_player)
                .mark_line(point=True, interpolate="step-after")
                .encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y("rank:O", sort=utils.CLASSEMENTS, title="Classement"),
                    tooltip=[
                        alt.Tooltip("date:T"),
                        alt.Tooltip("rank:N"),
                        alt.Tooltip("pts:Q", title="Points"),
                    ],
                )
                .properties(height=320, title=f"Évolution du classement — {who}")
            )
            st.altair_chart(chart, use_container_width=True)
