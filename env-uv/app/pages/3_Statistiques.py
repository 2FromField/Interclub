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
    # Dates
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # --- match_type à partir de type_match: SH/SD -> S, DH/DD -> D, MX -> M ---
    # si ta colonne s'appelle déjà "match_type", commente ces 2 lignes
    df["match_type"] = df["type_match"].astype(str).str[0].str.upper()
    df["match_type_label"] = (
        df["match_type"]
        .map({"S": "Simple", "D": "Double", "M": "Mixte"})
        .fillna("Autre")
    )

    # --- Split simple/double en lignes unitaires ---
    def split2(s: pd.Series):
        s = s.fillna("").astype(str)
        parts = s.str.split("/", n=1)
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
                    "match_type": df["match_type"],
                    "match_type_label": df["match_type_label"],
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
                    "match_type": df["match_type"],
                    "match_type_label": df["match_type_label"],
                }
            ),
        ],
        ignore_index=True,
    )

    # nettoyer
    unit_rows = unit_rows[unit_rows["player"].str.len() > 0].copy()
    unit_rows["rank"] = unit_rows["rank"].str.strip()
    unit_rows["pts"] = pd.to_numeric(
        unit_rows["pts"].str.replace(",", "."), errors="coerce"
    )

    # Axe Y catégoriel (N1 en haut)
    unit_rows["rank"] = pd.Categorical(
        unit_rows["rank"], categories=utils.CLASSEMENTS, ordered=True
    )

    # --- Sélection joueur ---
    who = st.session_state.get("dd_player_filter")
    if who and who != "-- Tous les joueurs --":
        df_player = unit_rows[unit_rows["player"] == who].sort_values("date")

        if df_player.empty:
            st.warning(f"Aucune donnée pour {who}.")
        else:
            # ton line chart existant (df_player + rank catégoriel)
            base = (
                alt.Chart(df_player)
                .mark_line(point=True, interpolate="step-after")
                .encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y(
                        "pts:Q",
                        scale=alt.Scale(domain=[300, 2000]),
                        title="Points de classement",
                    ),
                    tooltip=["date:T", "rank:N", "pts:Q"],
                )
                .properties(height=320)
            )

            # --- LIGNE + ANNOTATION ---
            # 2) Seuils multiples (valeur Y + label + couleur)
            thresholds = [
                {"y": 400, "label": "P12/NC", "color": "#b2af0061"},
                {"y": 600, "label": "P11", "color": "#b2af0061"},
                {"y": 800, "label": "P10", "color": "#b2af0061"},
                {"y": 1000, "label": "D9", "color": "#cb87006f"},
                {"y": 1200, "label": "D8", "color": "#cb87006f"},
                {"y": 1400, "label": "D7", "color": "#cb87006f"},
                {"y": 1600, "label": "R6", "color": "#cb000062"},
                {"y": 1800, "label": "R5", "color": "#cb000062"},
                {"y": 2000, "label": "R4", "color": "#cb000062"},
            ]
            lines_df = pd.DataFrame(thresholds)

            # Assure que l’échelle Y inclut tous les seuils
            y_min = min(df_player["pts"].min(), lines_df["y"].min())
            y_max = max(df_player["pts"].max(), lines_df["y"].max())
            base = base.encode(
                y=alt.Y(
                    "pts:Q",
                    title="Points de classement",
                    scale=alt.Scale(domain=[y_min, y_max]),
                )
            )

            # 3) Règles horizontales (une par ligne du DF)
            rules = (
                alt.Chart(lines_df)
                .mark_rule(strokeDash=[4, 4], strokeWidth=2)
                .encode(
                    y="y:Q",
                    color=alt.Color(
                        "label:N",
                        scale=alt.Scale(range=lines_df["color"].tolist()),
                        legend=None,
                    ),
                )
            )

            # 4) Labels à droite (x = date max)
            x_max = df_player["date"].max()
            labels = (
                alt.Chart(lines_df.assign(x=x_max))
                .mark_text(align="left", dx=6, dy=-6, fontWeight="bold")
                .encode(
                    x="x:T",
                    y="y:Q",
                    text="label:N",
                    color=alt.Color(
                        "label:N",
                        scale=alt.Scale(range=lines_df["color"].tolist()),
                        legend=None,
                    ),
                )
            )

            chart = (base + rules + labels).resolve_scale(x="shared", y="shared")
            st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Sélectionnez un joueur pour afficher le graphique.")
