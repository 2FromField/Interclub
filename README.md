# Interclub AOB — App Streamlit (Google Sheets + Streamlit Community Cloud)

---

![Streamlit](https://img.shields.io/badge/Kubernetes-3069DE?style=for-the-badge&logo=kubernetes&logoColor=white)
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Google Sheet](https://img.shields.io/badge/Google%20Sheets-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)

---

Une application Streamlit pour :

- Enregistrer les rencontres d’interclubs (formulaires dynamiques par catégorie),
- Historiser les matchs (simples/doubles/mixte),
- Visualiser l’évolution des classements/points et quelques KPI,
- Le tout branché sur Google Sheets (lecture/écriture),
- Déployé sur Streamlit Community Cloud (\*.streamlit.app).

# ✨ Fonctionnalités

- Saisie guidée des feuilles de matchs
- Formulaires par catégorie (H2, V3, D5, …) avec dépendances (joueurs filtrés par division).
- Saisie simple/double/mixte, sets, points, rangs, “grind/ungrind”.
- Bouton Enregistrer avec modal de confirmation.
- Historique & Filtres
- Filtres par équipe, joueur, résultat (victoire/nulle/défaite).
- Affichage des feuilles avec détails “on demand”.
- Statistiques & DataViz
- Courbes Altair (évolution des points et/ou classement).
- KPIs (victoires, points cumulés, ratios S/D/M…).
- Stockage & Persistance
- Données dans Google Sheets : tables TABLE_INTERCLUB, TABLE_MATCHS, TABLE_PLAYERS.
- Accès via gspread + OAuth service account.
- Déploiement GitHub → Streamlit Community Cloud.
- Secrets sécurisés (credentials GCP + SHEET_ID) via Secrets Manager Streamlit.

# 📦 Aperçu technique

- Frontend : Streamlit
- Données : Google Sheets (via gspread, google-auth)
- Viz : Altair
- Pandas pour la logique data (split double “A/B”, mapping rangs, KPIs)
- Gestion d’état : st.session_state (confirmations, filtres, formulaires)
- Cache : @st.cache_data pour les lectures stables

# 🗂️ Arborescence (exemple)

```
📁 env-uv/
├── 📁 .streamlit
│   ├── 🔒 secrets.toml
├── 📁 .venv
├── 📁 app
│   ├── 📁 assets
│   │   └── 📁 img
│   │       ├── 🖼️ AOB_LOGO.jpg
│   │       ├── ...
│   ├── 📁 pages
│   │   ├── 🐍 0_Accueil.py
│   │   ├── 🐍 1_Historique.py
│   │   ├── 🐍 2_Statistiques.py
│   │   └── 🐍 3_Record.py
│   ├── 🐍 app.py
│   ├── 🐍 auth.py
│   └── 🐍 utils.py
├── ⚙️ .gitignore
├── 📝 README.md
├── 🐍 main.py
├── ⚙️ pyproject.toml
└── 📄 uv.lock
```

Astuce : si vous utilisez uv localement, conservez aussi requirements.txt pour Streamlit Cloud.

# ✅ Prérequis

- Un compte Google et un Google Sheet (formaté avec vos onglets de données).
- Un projet Google Cloud avec un Service Account et une clé JSON.
- Un repo GitHub public/privé contenant cette app.

# 🔐 Google Cloud & Google Sheets (accès service account)

1. Créer un Service Account (GCP → IAM & Admin → Service Accounts) et générer une clé JSON.
2. Dans Google Sheets, partager le document à l’e-mail du service account (le compte doit avoir au moins Éditeur sur le fichier).
3. Notez l’ID du Sheet, l’URL ressemble à `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit#gid=0` et <SHEET_ID> est la valeur à copier.
4. Onglets requis dans votre fichier (exemples) :

- TABLE_PLAYERS : id_player, name, division, ...
- TABLE_MATCHS : id, type_match, aob_player_id, opponent_player, aob_rank, opponent_rank, aob_pts, opponent_pts, set1, set2, set3, aob_grind opponent_grind, win
- TABLE_INTERCLUB : id, date, journey, division, aob_team, opponent_team, aob_score, opponent_score

# 🔑 Secrets (local & cloud)

En local, créez `.streamlit/secrets.toml` pour y stocker vos données sensibles (comme ci-joint):

```
SHEET_ID = "<votre_sheet_id>"
[record_lock]
pin = "your-pin"
[admin]
password = "admin-password"
[gcp]
type = "service_account"
project_id = "<...>"
private_key_id = "<...>"
private_key = """-----BEGIN PRIVATE KEY-----
...votre clé...
-----END PRIVATE KEY-----"""
client_email = "<service-account>@<project>.iam.gserviceaccount.com"
client_id = "<...>"
token_uri = "https://oauth2.googleapis.com/token"
Attention aux retours à la ligne dans private_key. Gardez bien les délimiteurs BEGIN/END.
Sur Streamlit Community Cloud
Dans Manage App → Settings → Secrets, collez le même contenu (YAML/TOML-like).
Ajoutez SHEET_ID et le bloc [gcp].
```

‡

# 🧰 Installation & Lancement (local)

1. Cloner: `git clone https://github.com/2FromField/$REPO.git && cd env-uv`

2. Python 3.10+ recommandé: `python -m venv .venv && source .venv/bin/activate # Windows: .venv\Scripts\activate`

3. Dépendances: `pip install -r requirements.txt`

4. Secrets: créez .streamlit/secrets.toml comme ci-dessus

5. Lancer: `uv run streamlit run app/app.py`

# ☁️ Déploiement — Streamlit Community Cloud

1. Poussez le code sur GitHub (branche main de préférence).
2. Allez sur streamlit.io → Community Cloud → Deploy an app.
3. Pointez vers votre repo/branche, et chemin du script (ex: app/app.py).
4. Dans Secrets, collez le contenu de votre secrets.toml.
5. Vérifiez que le `requirements.txt` contient au minimum :

- streamlit
- pandas
- gspread
- google-auth
- altair
  Ainsi qu'un `runtime.txt` avec python-3.10.

6. Déployez. L’URL aura la forme https://<app-name>-<user>.streamlit.app.

# 🧩 Points clés d’implémentation

1. Google Sheets

- Connexion via gspread + google.oauth2.service_account.Credentials.
- Utilitaires append_row_sheet() / write_sheet() pour écrire proprement (aligner l’ordre des colonnes).

2. Formulaires

- st.form + st.form_submit_button.
- Modal de confirmation (st.modal / st.dialog) avant la vraie écriture (utilise st.session_state).

3. Clés uniques Streamlit

- Donnez des key uniques à chaque widget : f"{match}\_aob_name", etc., pour éviter StreamlitDuplicateElementKey.

4. Filtres dépendants

- Quand categorie change, on peut pop des valeurs dépendantes dans st.session_state pour forcer le refresh des selectbox.

5. Altair

- Y numérique (points) + mark_rule pour afficher des seuils horizontaux + annotations.
- Si multi-couches avec légendes différentes : .resolve_scale(color="independent").

# 🧪 Données

_TABLE_PLAYERS_
| Colonne | Description | Type |
| ----------- | ------------------------------------------------------------ | ------ |
| `id_player` | Identifiant unique du joueur | string |
| `name` | Nom complet du joueur | string |
| `division` | Division du joueur (ex. `D3` ou `V3/D3` pour multi-division) | string |
| `…` | Autres champs éventuels (club, sexe, licence, etc.) | — |

_TABLE_MATCHS_
| Colonne | Description | Type |
| ----------------- | ------------------------------------------------------------------------------------- | ------------------------------ |
| `id` | Identifiant unique de la ligne de match | integer |
| `type_match` | Type de match : `SH1`, `SH2`, `SD1`, `SD2`, `DH`, `DH1`, `DH2`, `DD`, `MX1`, `MX2`, … | string (enum) |
| `aob_player_id` | ID(s) joueur(s) AOB : `42` (simple) ou `42/10` (double/mixte) | string |
| `opponent_player` | Nom(s) joueur(s) adverse(s) : `NOM` ou `NOM1/NOM2` | string |
| `aob_rank` | Rang(s) AOB : `D9` (simple) ou `D9 / D8` (double/mixte) | string |
| `opponent_rank` | Rang(s) adverses : même format que `aob_rank` | string |
| `aob_pts` | Point(s) AOB : `1108` (simple) ou `1083 / 1057` (double/mixte) | string (nombre ou « n1 / n2 ») |
| `opponent_pts` | Point(s) adverses : même format que `aob_pts` | string (nombre ou « n1 / n2 ») |
| `set1` | Score set 1 au format `AOB/ADV` (ex. `21-18/19-21`) | string |
| `set2` | Score set 2 au format `AOB/ADV` | string |
| `set3` | Score set 3 au format `AOB/ADV` (vide si 2 sets) | string |
| `aob_grind` | Gain/perte points AOB : `14/14` ou `-11/-11` (double), `20` ou `-8` (simple) | string |
| `opponent_grind` | Gain/perte points adverses : même format que `aob_grind` | string |
| `win` | Vainqueur : `aob` ou `opponent` (calculé par le helper `winner(...)`) | string (enum) |

_TABLE_INTERCLUB_
| Colonne | Description | Type |
| ---------------- | ------------------------------------------ | ---------- |
| `id` | Identifiant unique de la rencontre | integer |
| `date` | Date de la rencontre (format `YYYY-MM-DD`) | date (ISO) |
| `journey` | Journée, ex. `J3` | string |
| `division` | Division (ex. `H2`, `V3`, `D5`, …) | string |
| `aob_team` | Nom de l’équipe AOB (ex. `AOB35-1`) | string |
| `opponent_team` | Nom de l’équipe adverse | string |
| `aob_score` | Score total AOB sur la rencontre | integer |
| `opponent_score` | Score total adverse sur la rencontre | integer |

# 🚀 Roadmap (idées)

- Authentification simple (mot de passe partage d’équipe).
- Export PDF/CSV des feuilles de match.
- D'avantages de statistiques d'équipes / individuelles
- Connexion directe aux résultats officiels et ouvertures à tous clubs
- Tests unitaires sur les helpers (split, winner, merges).

# 🤝 Contribuer

Fork, branche (feat/...), PR bienvenue.

# 📄 Licence

MIT — faites-en bon usage et partagez vos améliorations 🙌
