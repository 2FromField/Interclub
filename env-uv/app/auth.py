import streamlit as st


def check_record_password(page_key: str, secret_path: str):
    """
    Protège une page avec un mot de passe.
    - page_key : identifiant unique de la page (ex: "admin")
    - secret_path : chemin dans st.secrets (ex: "admin.password")
    """

    flag_key = f"password_correct_{page_key}"
    pwd_key = f"password_{page_key}"

    def password_entered():
        # récupérer le mot de passe réel dans st.secrets
        real_pwd = st.secrets
        for part in secret_path.split("."):
            real_pwd = real_pwd[part]

        if st.session_state.get(pwd_key) == real_pwd:
            st.session_state[flag_key] = True
            del st.session_state[pwd_key]  # on efface le mdp tapé
        else:
            st.session_state[flag_key] = False

    # déjà validé pour cette page ?
    if st.session_state.get(flag_key, False):
        return True

    # sinon, afficher le formulaire
    st.title("🔐 Accès réservé aux administrateurs")
    st.text_input(
        "Mot de passe",
        type="password",
        key=pwd_key,
        on_change=password_entered,
    )

    if st.session_state.get(flag_key) is False:
        st.error("Mot de passe incorrect 😅")

    return False
