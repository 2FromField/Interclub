import streamlit as st
import utils
import altair as alt
import sqlite3
import pandas as pd
from streamlit_extras.stylable_container import stylable_container
import numpy as np

##################################################################
#                          DONNEES                               #
##################################################################

# Import des tables
TABLE_INTERCLUB = utils.TABLE_INTERCLUB

# Types de match
S_TYPES = {"SH1", "SH2", "SH3", "SH4", "SD1", "SD2"}
D_TYPES = {"DH", "DH1", "DH2", "DD", "DD1", "DD2"}
M_TYPES = {"MX", "MX1", "MX2"}

# Icones
WIN_ICON = "🔥"
COLD_ICON = "❄️"

# Classements dans l'ordre inverse
REVERS_CLASSEMENTS = utils.CLASSEMENTS[::-1]

##################################################################
#                         FONCTIONS                              #
##################################################################


def calculating_grind(player_name: str):
    """Calcul des points remportés OU perdus dans les différents types de matchs (Simple / Double / Mixte)

    Args:
        player_name (str): Nom complet du joueur ("NOM Prénom").

    Returns:
        (gs, us, gd, ud, gm, um): (pts gagnés, perdus, ... en simple[0,1]/double[2,3]/mixte[4,5])
    """
    gs, us = 0, 0
    gd, ud = 0, 0
    gm, um = 0, 0
    for i in range(len(df)):
        if "/" in df["player"][i]:
            p1 = df["player"][i].split("/")[0]
            p2 = df["player"][i].split("/")[1]
            pts = (
                df["aob_grind"][i].split("/")[0]
                if player_name == p1
                else df["aob_grind"][i].split("/")[1]
            )
            #
            if df["type_match"][i] in ["DH", "DH1", "DH2", "DD1", "DD2"]:
                if str(pts)[:1] == "-":
                    ud += int(str(pts[1:]))
                else:
                    gd += int(pts)
            else:
                if str(pts)[:1] == "-":
                    um += int(str(pts)[1:])
                else:
                    gm += int(pts)
        else:
            pts = df["aob_grind"][i]
            if str(pts)[:1] == "-":
                us += int(str(pts)[1:])
            else:
                gs += int(pts)
    #
    return (
        gs,
        us,
        gd,
        ud,
        gm,
        um,
    )


def kpi_card(title: str, value: str | float, sub=None):
    """Carte des KPIs

    Args:
        title (str): Nom de la carte.
        value (int|float): Valeur affichée.
        sub (html): divisions html supplémentaires (ex: <div class="div-exemple">text</div>).
    """
    sub_html = f"<div class='kpi-sub'>{sub}</div>" if sub else ""
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-title">{title}</div>
          <div class="kpi-value">{value}</div>
          {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_rate(wins: int, total: int, pct=True, ndigits=1):
    """Calcul du pourcentage de victoire par match

    Args:
        wins (int): Nombre de victoires.
        total (int): Nombre de matchs total.
        pct (bool, optional): Résultat en pourcentage (True par défaut).
        ndigits (int, optional): Nombre de décimale en sortie (1 par défaut).
    """
    if total == 0:
        return "—" if pct else "0/0"  # à toi de choisir l’affichage
    if pct:
        return f"{round(100 * wins / total, ndigits)}%"
    else:
        return f"{wins}/{total}"


def group_rate(df: pd.DataFrame, types: dict):
    """Calcul du pourcentage de victoire par type de match (simple/double/mixte)

    Args:
        df (pd.DataFrame): Jeu de données.
        types (dict): Liste des matchs possibles par type de match (ex: simple pour ["SD1","SH2",etc])
    """
    sub = df[df["type_match"].isin(types)]
    total = len(sub)
    wins = (sub["win"].str.lower() == "aob").sum()
    return safe_rate(wins, total, pct=True, ndigits=0)  # % sans décimal


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


def best_ranks_lists(df: pd.DataFrame, player_name: str):
    """Récupération des meilleurs rangs atteints dans les 3 catégories de match par un joueur.

    Args:
        df (pd.DataFrame): Jeu de données.
        player_name (str): Nom du joueur ("NOM Prénom").
    """
    # Copie du jeu de données
    s = df.copy()

    # Filtrage selon le type de match
    s["type_match"] = s["type_match"].astype(str).str.upper()
    s["match_type"] = (
        s["type_match"].str[0].map({"S": "Simple", "D": "Double", "M": "Mixte"})
    )

    def split2(col: pd.Series):
        col = col.fillna("").astype(str)
        parts = col.str.split("/", n=1, expand=True)

        c1 = parts[0].str.strip()
        # get la deuxième colonne si elle existe, sinon valeurs NaN -> remplacées par ""
        c2 = (
            parts[1].fillna("").str.strip()
            if parts.shape[1] > 1
            else pd.Series("", index=col.index)
        )

        return c1, c2

    # Variables
    p1, p2 = split2(s["player"])
    r1, r2 = split2(s["rank"])

    player = pd.Series("", index=s.index)
    rank = pd.Series("", index=s.index)

    mask1 = p1.eq(player_name)
    player[mask1] = p1[mask1]
    rank[mask1] = r1[mask1]

    mask2 = p2.eq(player_name)
    player[mask2] = p2[mask2]
    rank[mask2] = r2[mask2]

    unit = pd.DataFrame(
        {
            "player": player,
            "rank": rank,
            "match_type": s["match_type"],
        }
    )

    unit = unit[
        (unit["player"] == player_name) & (unit["rank"].isin(REVERS_CLASSEMENTS))
    ].copy()

    unit["rank"] = unit["rank"].astype(
        pd.CategoricalDtype(REVERS_CLASSEMENTS, ordered=True)
    )

    best = unit.groupby(["player", "match_type"], as_index=False)["rank"].max()

    list_simple = best.loc[best["match_type"] == "Simple", "rank"].astype(str).tolist()
    list_double = best.loc[best["match_type"] == "Double", "rank"].astype(str).tolist()
    list_mixte = best.loc[best["match_type"] == "Mixte", "rank"].astype(str).tolist()

    # Si la liste est vide -> "..."
    best_simple = list_simple[0] if len(list_simple) > 0 else "..."
    best_double = list_double[0] if len(list_double) > 0 else "..."
    best_mixte = list_mixte[0] if len(list_mixte) > 0 else "..."

    return best_simple, best_double, best_mixte


def current_streak(results: list):
    """Déterminer le type de streak (LOOSE/WIN)"""
    if not results:  # si la liste est vide
        return None, 0

    last = results[-1]  # résultat du dernier match
    streak = 0

    for r in reversed(results):
        if r == last:
            streak += 1
        else:
            break

    if last == "W":
        return "win", streak
    else:
        return "loss", streak


##################################################################
#                           LAYOUT                               #
##################################################################
st.set_page_config(page_title="Statistiques", layout="wide")


##################################################################
#                             CSS                                #
##################################################################
st.markdown(
    """
<style>
.kpi-card{
  background:#f1f3f5;           /* gris clair */
  border:1px solid #e5e7eb;
  border-radius:14px;
  padding:18px 14px;
  text-align:center;
  min-height:110px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  margin-bottom: 30px;
}
.kpi-title{
  font-size:.85rem;
  letter-spacing:.02em;
  text-transform:uppercase;
  color:#374151;                 /* gris foncé */
  margin:0 0 6px 0;
  opacity:.85;
}
.kpi-value{
  font-size:2rem;                /* valeur bien visible */
  font-weight:800;
  margin:0;
  color:#111827;
}
.kpi-sub{
  font-size:.9rem;
  color:#6b7280;
  margin-top:4px;
}
</style>
""",
    unsafe_allow_html=True,
)

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

# -- Jointures entre les tables
# 1) Entre la table 'INTERCLUB' et 'MATCH'
m_ic = utils.TABLE_MATCHS.merge(
    TABLE_INTERCLUB[["id", "date", "division", "aob_team", "opponent_team"]],
    left_on="id",
    right_on="id",
    how="left",
)

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

# 5) Sélection finale - Dataframe utilisable
result = m_ic[
    [
        "id",
        "type_match",
        "date",
        "division",
        "aob_team",
        "opponent_team",
        "player",
        "opponent_rank",
        "rank",
        "pts",
        "win",
        "aob_grind",
        "opponent_grind",
    ]
].reset_index(drop=True)

# Copie du dataframe
df = result.copy()

# -- Variables issues des dropdowns en entête
team_sel = st.session_state.get("dd_team_filter")
player_sel = st.session_state.get("dd_player_filter")

# -- Filtre équipe (si sélectionnée uniquement)
if (
    team_sel
    and team_sel != "-- Toutes les équipes --"
    and player_sel == "-- Tous les joueurs --"
):
    df = df[df["division"] == team_sel].reset_index(drop=True)

    c1, c2, c3, c4, c5 = st.columns(5, gap="small")
    with c1:
        kpi_card("Rencontres jouées", f'{df["id"].nunique()}', "saison 2025/26")
    with c2:
        # Définir V/D/E
        def match_output(team):
            df = TABLE_INTERCLUB[(TABLE_INTERCLUB["division"] == team)].reset_index(
                drop=True
            )
            v = (df["aob_score"] > df["opponent_score"]).sum()
            d = (df["aob_score"] < df["opponent_score"]).sum()
            e = (df["aob_score"] == df["opponent_score"]).sum()

            # Calcul du nombre de points
            pts = v * 3 + e * 2 + d * 1
            return v, e, d, pts

        kpi_card(
            "Résultats",
            f"{str(match_output(team_sel)[0])} / {str(match_output(team_sel)[1])} / {str(match_output(team_sel)[2])}",
            "Victoire(s) / Egalité(s) / Défaite(s)",
        )
    with c3:
        kpi_card(
            "Matchs joués",
            f'{len(df[(df["type_match"].isin(["SH1","SH2","SH3","SH4","SD1","SD2"]))])} / {len(df[(df["type_match"].isin(["DH","DH1","DH2","DD", "DD1"]))])} / {len(df[(df["type_match"].isin(["MX","MX1","MX2"]))])}',
            "Simple / Double / Mixte",
        )
    with c4:
        s_rate = group_rate(df, S_TYPES)
        d_rate = group_rate(df, D_TYPES)
        m_rate = group_rate(df, M_TYPES)

        kpi_card(
            "Victoires",
            f'{len(df[(df["type_match"].isin(["SH1","SH2","SH3","SH4","SD1","SD2"])) & (df["win"] == "aob")])} / {len(df[(df["type_match"].isin(["DH","DH1","DH2","DD", "DD1", "DD2"])) & (df["win"] == "aob")])} / {len(df[(df["type_match"].isin(["MX","MX1","MX2"])) & (df["win"] == "aob")])}',
            f"{s_rate} / {d_rate} / {m_rate}",
        )
    with c5:
        interclub_team_sel = TABLE_INTERCLUB[
            (TABLE_INTERCLUB["division"] == team_sel)
        ].reset_index(drop=True)

        # Nouvelle colonnes éphémère donnant l'issue du match
        interclub_team_sel["result"] = np.where(
            interclub_team_sel["aob_score"] >= interclub_team_sel["opponent_score"],
            "W",
            np.where(
                interclub_team_sel["aob_score"] < interclub_team_sel["opponent_score"],
                "L",
                "D",
            ),  # "D" pour nul
        )

        matchs_list = interclub_team_sel[
            "result"
        ].tolist()  # Convertion de la colonne en liste

        kpi_text, kpi_icon = (
            ("Win Streak", WIN_ICON)
            if current_streak(matchs_list)[0] == "win"
            else ("Lose Streak", COLD_ICON)
        )

        #
        kpi_card("Série", f"{current_streak(matchs_list)[1]} {kpi_icon}", kpi_text)

# -- Filtre joueur (match par token, insensible à la casse)
elif player_sel and player_sel != "-- Tous les joueurs --":
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

    #
    df_kpi = df.copy()

    # -- Segmentation en colonnes des cartes KPIs
    c1, c2, c3, c4, c5 = st.columns(5, gap="small")
    with c1:
        kpi_card("Rencontres jouées", f'{df_kpi["id"].nunique()}', "saison 2025/26")
    with c2:
        kpi_card(
            "Matchs joués",
            f'{len(df_kpi[(df_kpi["type_match"].isin(["SH1","SH2","SH3","SH4","SD1","SD2"]))])} / {len(df_kpi[(df_kpi["type_match"].isin(["DH","DH1","DH2","DD"]))])} / {len(df_kpi[(df_kpi["type_match"].isin(["MX","MX1","MX2"]))])}',
            "Simple / Double / Mixte",
        )
    with c3:
        s_rate = group_rate(df_kpi, S_TYPES)
        d_rate = group_rate(df_kpi, D_TYPES)
        m_rate = group_rate(df_kpi, M_TYPES)

        kpi_card(
            "Victoires",
            f'{len(df_kpi[(df_kpi["type_match"].isin(["SH1","SH2","SH3","SH4","SD1","SD2"])) & (df_kpi["win"] == "aob")])} / {len(df_kpi[(df_kpi["type_match"].isin(["DH","DH1","DH2","DD", "DD1", "DD2"])) & (df_kpi["win"] == "aob")])} / {len(df_kpi[(df_kpi["type_match"].isin(["MX","MX1","MX2"])) & (df_kpi["win"] == "aob")])}',
            f"{s_rate} / {d_rate} / {m_rate}",
        )
    with c4:
        gs, us, gd, ud, gm, um = calculating_grind(player_sel)
        kpi_card(
            "Points remportés",
            f"{gs-us} / {gd-ud} / {gm-um}",
            "Simple / Double / Mixte",
        )
    with c5:
        player_best_rank = best_ranks_lists(df_kpi, player_sel)
        kpi_card(
            "Meilleurs rangs",
            f"{player_best_rank[0]} / {player_best_rank[1]} / {player_best_rank[2]}",
            "Simple / Double / Mixte",
        )

else:
    # -- Filtre équipe (si sélectionnée uniquement)
    players = df["player"].str.split("/")
    player_rank = df["rank"].str.split("/")
    points = df["aob_grind"].astype(str).str.split("/")
    categorie = df["type_match"].str.replace(r"\d+", "", regex=True)
    date = df["date"]

    # Explode en gardant l’alignement grâce à l’index
    df_long = pd.DataFrame(
        {
            "player": players.explode().str.strip(),
            "player_rank": player_rank.explode().str.strip(),
            "points": points.explode().str.strip().astype(int),
            "categorie": categorie,
            "date": date,
        }
    )

    #
    s1, s2, s3, s4, s5 = st.columns(5, gap="small")
    with s1:
        # Caluler la somme de points remportés en totalité
        df_points_tot_par_joueur = (
            df_long.groupby("player", as_index=False)["points"]
            .sum()
            .sort_values("points", ascending=False)
        ).reset_index(drop=True)

        # Caluler la somme de points remportés par type de match
        df_points_par_joueur = (
            df_long.groupby(["player", "categorie"], as_index=False)["points"]
            .sum()
            .sort_values("points", ascending=False)
        )

        # Dataframe du joueur ayant remporté le plus de points (avec chaque type de match)
        pts_eater = df_points_par_joueur[
            (
                df_points_par_joueur["player"]
                == df_points_tot_par_joueur.loc[0, "player"]
            )
        ].reset_index(drop=True)

        # Simple
        mask_s = pts_eater["categorie"].str.contains("S", na=False)
        pts_s = pts_eater.loc[mask_s, "points"].iloc[0] if mask_s.any() else 0
        if pts_s == 0:
            pts_s = 0
        elif "-" in str(pts_s):
            pts_s = f"{pts_s}"
        else:
            pts_s = f"+{pts_s}"
        # Double
        mask_d = pts_eater["categorie"].str.contains("D", na=False)
        pts_d = pts_eater.loc[mask_d, "points"].iloc[0] if mask_d.any() else 0
        if pts_d == 0:
            pts_d = 0
        elif "-" in str(pts_d):
            pts_d = f"{pts_d}"
        else:
            pts_d = f"+{pts_d}"
        # Mixte
        mask_m = pts_eater["categorie"].str.contains("MX", na=False)
        pts_m = pts_eater.loc[mask_m, "points"].iloc[0] if mask_m.any() else 0
        if pts_m == 0:
            pts_m = 0
        elif "-" in str(pts_m):
            pts_m = f"{pts_m}"
        else:
            pts_m = f"+{pts_m}"

        #
        kpi_card("Point Eater", pts_eater["player"][0], f"{pts_s} / {pts_d} / {pts_m}")
    with s2:
        # Compter les victoires dans l'ordre chronologique
        df_long = df_long.sort_values(["player", "date"])

        # Créer une colonne "is_win" sommant les victoires
        df_long["is_win"] = df_long["points"] > 0

        # Calculer le win streak pour chaque match
        def compute_streak(s):
            # s est une Series de booléens (is_win) pour UN joueur
            groups = (~s).cumsum()  # chaque défaite crée un nouveau groupe
            streak = s.groupby(groups).cumsum()
            return streak

        df_long["win_streak"] = df_long.groupby("player")["is_win"].transform(
            compute_streak
        )

        # Win Streak max par joueur
        df_win_streak = (
            df_long.groupby("player", as_index=False)["win_streak"]
            .max()
            .rename(columns={"win_streak": "best_win_streak"})
            .sort_values("best_win_streak", ascending=False)
        ).reset_index(drop=True)

        #
        kpi_card(
            "Win Streaker",
            df_win_streak["player"][0],
            f"🔥{df_win_streak['best_win_streak'][0]}",
        )
    with s3:
        # Nombre de match total joués par joueur
        df_match_count = (
            df_long.groupby("player", as_index=False)
            .size()  # nombre de lignes = nombre de matchs joués
            .rename(columns={"size": "nb_matchs"})
            .sort_values("nb_matchs", ascending=False)
        ).reset_index(drop=True)
        #
        kpi_card(
            "Match Marathoner",
            df_match_count["player"][0],
            df_match_count["nb_matchs"][0],
        )
    with s4:
        # Garder les matchs remportés
        df_wins = df_long[df_long["points"] > 0].copy()

        # Trouver la ligne avec le nombre de points maximal
        if df_wins.empty:
            # personne n'a de match gagné
            best_row = None
        else:
            best_row = df_wins[
                df_wins["points"] == df_wins["points"].max()
            ].reset_index(drop=True)

        kpi_card("Clutch Performer", best_row["player"][0], f"+{best_row['points'][0]}")
    with s5:
        # Winrate global par joueur
        df_winrate_par_joueur = (
            df_long.assign(is_win=df_long["points"] > 0)  # True si victoire
            .groupby("player", as_index=False)
            .agg(
                nb_matchs=("is_win", "size"),
                nb_wins=("is_win", "sum"),
                winrate=(
                    "is_win",
                    "mean",
                ),  # moyenne de True/False = ratio de victoires
            )
        )

        # passer le winrate en pourcentage
        df_winrate_par_joueur["winrate"] = (
            df_winrate_par_joueur["winrate"] * 100
        ).round(1)

        # optionnel : trier par winrate puis nb_matchs
        df_winrate_par_joueur = df_winrate_par_joueur.sort_values(
            ["winrate", "nb_matchs"], ascending=[False, False]
        ).reset_index(drop=True)

        # Winrate par type de match
        df_winrate_par_joueur_cat = (
            df_long.assign(is_win=df_long["points"] > 0)
            .groupby(["player", "categorie"], as_index=False)
            .agg(
                nb_matchs=("is_win", "size"),
                nb_wins=("is_win", "sum"),
                winrate=("is_win", "mean"),
            )
        )

        df_winrate_par_joueur_cat["winrate"] = (
            df_winrate_par_joueur_cat["winrate"] * 100
        ).round(1)

        df_winrate_par_joueur_cat = df_winrate_par_joueur_cat.sort_values(
            ["player", "categorie"], ascending=[False, False]
        ).reset_index(drop=True)

        df_winrate_master = df_winrate_par_joueur_cat[
            (df_winrate_par_joueur_cat["player"] == df_winrate_par_joueur["player"][0])
        ].reset_index(drop=True)

        # Simple
        mask_s_cat = df_winrate_master["categorie"].str.contains("S", na=False)
        pts_s_cat = (
            df_winrate_master.loc[mask_s_cat, "winrate"].iloc[0]
            if mask_s_cat.any()
            else 0
        )
        nb_s_cat = (
            df_winrate_master.loc[mask_s_cat, "nb_matchs"].iloc[0]
            if mask_s_cat.any()
            else 0
        )
        # Double
        mask_d_cat = df_winrate_master["categorie"].str.contains("D", na=False)
        pts_d_cat = (
            df_winrate_master.loc[mask_d_cat, "winrate"].iloc[0]
            if mask_d_cat.any()
            else 0
        )
        nb_d_cat = (
            df_winrate_master.loc[mask_d_cat, "nb_matchs"].iloc[0]
            if mask_d_cat.any()
            else 0
        )
        # Mixte
        mask_m_cat = df_winrate_master["categorie"].str.contains("MX", na=False)
        pts_m_cat = (
            df_winrate_master.loc[mask_m_cat, "winrate"].iloc[0]
            if mask_m_cat.any()
            else 0
        )
        nb_m_cat = (
            df_winrate_master.loc[mask_m_cat, "nb_matchs"].iloc[0]
            if mask_m_cat.any()
            else 0
        )

        #
        kpi_card(
            "Winrate Master",
            df_winrate_master["player"][0],
            f"{pts_s_cat}%({nb_s_cat}) / {pts_d_cat}%({nb_d_cat}) / {pts_m_cat}%({nb_m_cat})",
        )
    # Si aucun élément n'est renseigné dans les dropdowns
    st.info("Sélectionnez un joueur/équipe pour afficher ses statistiques d'interclub")


##################################################################
#                         GRAPHIQUE                              #
##################################################################

# Si df est vide ou si la colonne 'player' n'existe pas, on sort proprement
if df.empty or "player" not in df.columns:
    st.info("Aucune donnée à tracer.")
else:
    # Dates
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")

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
        st.title("EVOLUTION")

        df_player = unit_rows[unit_rows["player"] == who].sort_values("date")

        if df_player.empty:
            st.warning(f"Aucune donnée pour {who}.")
        else:
            # Couleur des catégories de match
            domain_base = ["Simple", "Double", "Mixte"]  # adapte à tes valeurs
            range_base = ["#2563eb", "#10b981", "#f59e0b"]  # ta palette
            # Linechart existant (df_player + rank catégoriel)
            base = (
                alt.Chart(df_player)
                .mark_line(point=True, interpolate="step-after")
                .encode(
                    x=alt.X("date:T", title=None),
                    y=alt.Y(
                        "pts:Q",
                        scale=alt.Scale(domain=[300, 2000]),
                        title="Points de classement",
                    ),
                    color=alt.Color(
                        "match_type_label:N",
                        scale=alt.Scale(domain=domain_base, range=range_base),
                        title=None,
                        legend=alt.Legend(
                            orient="bottom",  # position de la légende
                            direction="horizontal",  # optionnel : horizontale
                        ),
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
            pts_min = df_player["pts"].min()
            pts_max = df_player["pts"].max()
            margin = 100  # marge autour des points

            if pd.notna(pts_min) and pd.notna(pts_max):
                y_min = max(0, pts_min - margin)
                y_max = pts_max + margin

                # 2) Filtrer les seuils visibles dans cette fenêtre
                lines_df_zoom = lines_df[
                    (lines_df["y"] >= y_min) & (lines_df["y"] <= y_max)
                ].copy()

                # 3) Appliquer l’échelle Y au line chart
                base = base.encode(
                    y=alt.Y(
                        "pts:Q",
                        title="Points de classement",
                        scale=alt.Scale(domain=[y_min, y_max]),
                    )
                )

                # 4) Si au moins un seuil est dans la fenêtre, on trace rules + labels avec lines_df_zoom
                if not lines_df_zoom.empty:
                    rules = (
                        alt.Chart(lines_df_zoom)
                        .mark_rule(strokeDash=[4, 4], strokeWidth=2)
                        .encode(
                            y="y:Q",
                            color=alt.Color(
                                "label:N",
                                scale=alt.Scale(range=lines_df_zoom["color"].tolist()),
                                legend=None,
                            ),
                        )
                    )

                    x_max = df_player["date"].max()
                    labels = (
                        alt.Chart(lines_df_zoom.assign(x=x_max))
                        .mark_text(align="left", dx=6, dy=-6, fontWeight="bold")
                        .encode(
                            x="x:T",
                            y="y:Q",
                            text="label:N",
                            color=alt.Color(
                                "label:N",
                                scale=alt.Scale(range=lines_df_zoom["color"].tolist()),
                                legend=None,
                            ),
                        )
                    )

                    chart = (base + rules + labels).resolve_scale(
                        color="independent", x="shared", y="shared"
                    )
                else:
                    # aucun seuil dans la fenêtre → juste la courbe
                    chart = base

                st.altair_chart(chart, use_container_width=True)


##################################################################
#                    OVERVIEW INDIVIDUEL                         #
##################################################################
def box_html_indiv(color: str, text: str) -> str:
    return f"""
    <div style="
        width: 30px;
        height: 30px;
        background-color: {color};
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 12px;
        font-weight: bold;
        flex: 0 0 auto;
    ">
        {text}
    </div>
    """


# helpers pour la couleur
def match_box_indiv(df: pd.DataFrame, type_match: str, line: int) -> str:
    value = df[type_match].iloc[line]

    # Choix de la couleur
    if "-" in str(value):
        color = "red"
        text = str(value)
    elif pd.isna(value):
        color = "grey"
        text = "..."
    else:
        color = "green"
        text = f"+{value}"

    return box_html_indiv(color, text)


if player_sel and player_sel != "-- Tous les joueurs --":
    st.title("ACTIVITES")

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

    #
    df_kpi = df.copy()

    # Rencontres jouées par le joueur sélectionné
    journeys = list(df_kpi.id.unique())

    # Dataframe des activités
    df_activity = pd.DataFrame(
        [], columns=["date", "opponent", "simple", "double", "mixte"]
    )

    for d in journeys:
        df_filtered = df_kpi[df_kpi["id"] == d].reset_index(drop=True)
        df_filtered["date"] = df_filtered["date"].dt.strftime("%d-%m-%Y")

        if df_filtered.empty:
            continue  # au cas où aucune ligne pour cette date

        row_idx = len(df_activity)  # index du nouveau dataframe

        df_activity.loc[row_idx, "date"] = df_filtered.loc[0, "date"]
        df_activity.loc[row_idx, "opponent"] = df_filtered.loc[0, "opponent_team"]

        for i in range(len(df_filtered)):
            if df_filtered.loc[i, "match_type_label"] == "Simple":
                df_activity.loc[row_idx, "simple"] = df_filtered.loc[i, "aob_grind"]
            if df_filtered.loc[i, "match_type_label"] == "Double":
                df_activity.loc[row_idx, "double"] = (
                    df_filtered.loc[i, "aob_grind"].split("/")[0]
                    if df_filtered.loc[i, "player"].split("/")[0] == player_sel
                    else df_filtered.loc[i, "aob_grind"].split("/")[1]
                )
            if df_filtered.loc[i, "match_type_label"] == "Mixte":
                df_activity.loc[row_idx, "mixte"] = (
                    df_filtered.loc[i, "aob_grind"].split("/")[0]
                    if df_filtered.loc[i, "player"].split("/")[0] == player_sel
                    else df_filtered.loc[i, "aob_grind"].split("/")[1]
                )

    # Entete des catégories
    row_title = f"""
        <div style='
            display: flex;
            flex-wrap: nowrap;
            align-items: center;
            gap: 6px;
            overflow-x: auto;
            padding: 4px 0;
        '>
            <div style='
                flex: 0 0 100px;          /* largeur fixe de la "colonne" date+équipe */
                max-width: 180px;
                white-space: nowrap;      /* tout sur une ligne */
                overflow: hidden;         /* si trop long, on coupe */
                text-overflow: ellipsis;  /* ... à la fin */
                color: white;
                font-weight: bold;
            '>
            </div>
            <div style='
                    flex: 0 0 100px;          /* largeur fixe de la "colonne" date+équipe */
                    max-width: 180px;
                    white-space: nowrap;      /* tout sur une ligne */
                    overflow: hidden;         /* si trop long, on coupe */
                    text-overflow: ellipsis;  /* ... à la fin */
                    color: white;
                    font-weight: bold;
                '>
            </div>
            {box_html_indiv("transparent", "S")}
            {box_html_indiv("transparent", "D")}
            {box_html_indiv("transparent", "M")}
        """
    st.markdown(row_title, unsafe_allow_html=True)

    # Points remportés ou non à chaque rencontre
    for k in range(len(df_activity) - 1, -1, -1):
        row_html = f"""
            <div style='
                display: flex;
                flex-wrap: nowrap;
                align-items: center;
                gap: 6px;
                overflow-x: auto;
                padding: 4px 0;
            '>
                <div style='
                    flex: 0 0 100px;          /* largeur fixe de la "colonne" date+équipe */
                    max-width: 180px;
                    white-space: nowrap;      /* tout sur une ligne */
                    overflow: hidden;         /* si trop long, on coupe */
                    text-overflow: ellipsis;  /* ... à la fin */
                    color: white;
                    font-weight: bold;
                '>
                    {df_activity.date[k]}
                </div>
                <div style='
                    flex: 0 0 100px;          /* largeur fixe de la "colonne" date+équipe */
                    max-width: 180px;
                    white-space: nowrap;      /* tout sur une ligne */
                    overflow: hidden;         /* si trop long, on coupe */
                    text-overflow: ellipsis;  /* ... à la fin */
                    color: white;
                    font-weight: bold;
                '>
                    {df_activity.opponent[k]}
                </div>
                {match_box_indiv(df_activity, 'simple', k)}
                {match_box_indiv(df_activity, 'double', k)}
                {match_box_indiv(df_activity, 'mixte', k)}
            """

        st.markdown(row_html, unsafe_allow_html=True)


##################################################################
#                      OVERVIEW D'EQUIPE                         #
##################################################################
def box_html(color: str, text: str) -> str:
    return f"""
    <div style="
        width: 30px;
        height: 30px;
        background-color: {color};
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 12px;
        font-weight: bold;
        flex: 0 0 auto;
    ">
        {text}
    </div>
    """


# helpers pour la couleur
def match_box(df: pd.DataFrame, type_match: str, label: str) -> str:
    win = df.loc[df.type_match == type_match, "win"].iloc[0]
    color = "green" if win == "aob" else "red"
    return box_html(color, label)


def matrix_color(df: pd.DataFrame, division: str):
    # Formatage de la date
    df["date"] = df["date"].dt.strftime("%d-%m-%Y")
    #
    if division in ["PR", "D3", "D2"]:
        row_html = f"""
            <div style='
                display: flex;
                flex-wrap: nowrap;
                align-items: center;
                gap: 6px;
                overflow-x: auto;
                padding: 4px 0;
            '>
                <div style='
                    flex: 0 0 70px;          /* largeur fixe de la "colonne" date+équipe */
                    max-width: 180px;
                    white-space: nowrap;      /* tout sur une ligne */
                    overflow: hidden;         /* si trop long, on coupe */
                    text-overflow: ellipsis;  /* ... à la fin */
                    color: white;
                    font-weight: bold;
                '>
                    {df.opponent_team.iloc[0]}
                </div>

                {match_box(df, 'SH1', 'SH1')}
                {match_box(df, 'SH2', 'SH2')}
                {match_box(df, 'SD1', 'SD1')}
                {match_box(df, 'SD2', 'SD2')}
                {match_box(df, 'DH',  'DH')}
                {match_box(df, 'DD',  'DD')}
                {match_box(df, 'MX1', 'MX1')}
                {match_box(df, 'MX2', 'MX2')}
            """

        st.markdown(row_html, unsafe_allow_html=True)
    #
    if division == "D5":
        row_html = f"""
            <div style='
                display: flex;
                flex-wrap: nowrap;
                align-items: center;
                gap: 6px;
                overflow-x: auto;
                padding: 4px 0;
            '>
                <div style='
                    flex: 0 0 70px;          /* largeur fixe de la "colonne" date+équipe */
                    max-width: 180px;
                    white-space: nowrap;      /* tout sur une ligne */
                    overflow: hidden;         /* si trop long, on coupe */
                    text-overflow: ellipsis;  /* ... à la fin */
                    color: white;
                    font-weight: bold;
                '>
                    {df.opponent_team.iloc[0]}
                </div>

                {match_box(df, 'SH1', 'SH1')}
                {match_box(df, 'SH2', 'SH2')}
                {match_box(df, 'SD1', 'SD1')}
                {match_box(df, 'DH',  'DH')}
                {match_box(df, 'DD',  'DD')}
                {match_box(df, 'MX1', 'MX1')}
                {match_box(df, 'MX2', 'MX2')}
            """

        st.markdown(row_html, unsafe_allow_html=True)
    #
    if division == "H2":
        row_html = f"""
            <div style='
                display: flex;
                flex-wrap: nowrap;
                align-items: center;
                gap: 6px;
                overflow-x: auto;
                padding: 4px 0;
            '>
                <div style='
                    flex: 0 0 70px;          /* largeur fixe de la "colonne" date+équipe */
                    max-width: 180px;
                    white-space: nowrap;      /* tout sur une ligne */
                    overflow: hidden;         /* si trop long, on coupe */
                    text-overflow: ellipsis;  /* ... à la fin */
                    color: white;
                    font-weight: bold;
                '>
                    {df.opponent_team.iloc[0]}
                </div>

                {match_box(df, 'SH1', 'SH1')}
                {match_box(df, 'SH2', 'SH2')}
                {match_box(df, 'SH3', 'SH3')}
                {match_box(df, 'SH4', 'SH4')}
                {match_box(df, 'DH1',  'DH1')}
                {match_box(df, 'DH2',  'DH2')}
            """

        st.markdown(row_html, unsafe_allow_html=True)
    #
    if division == "V3":
        row_html = f"""
            <div style='
                display: flex;
                flex-wrap: nowrap;
                align-items: center;
                gap: 6px;
                overflow-x: auto;
                padding: 4px 0;
            '>
                <div style='
                    flex: 0 0 70px;          /* largeur fixe de la "colonne" date+équipe */
                    max-width: 180px;
                    white-space: nowrap;      /* tout sur une ligne */
                    overflow: hidden;         /* si trop long, on coupe */
                    text-overflow: ellipsis;  /* ... à la fin */
                    color: white;
                    font-weight: bold;
                '>
                    {df.opponent_team.iloc[0]}
                </div>

                {match_box(df, 'SH1', 'SH1')}
                {match_box(df, 'SH2', 'SH2')}
                {match_box(df, 'DH',  'DH')}
                {match_box(df, 'DD',  'DD')}
                {match_box(df, 'MX1',  'MX1')}
                {match_box(df, 'MX2',  'MX2')}
            """

        st.markdown(row_html, unsafe_allow_html=True)


# -- Filtre équipe (si sélectionnée uniquement)
if (
    team_sel
    and team_sel != "-- Toutes les équipes --"
    and player_sel == "-- Tous les joueurs --"
):
    df = df[df["division"] == team_sel].reset_index(drop=True)

    journey_ids = list(df.id.unique())[
        ::-1
    ]  # De la date la + récente à la plus ancienne

    for d in journey_ids:
        id_df = df[(df.id == d)].reset_index(drop=True)
        matrix_color(df=id_df, division=team_sel)
