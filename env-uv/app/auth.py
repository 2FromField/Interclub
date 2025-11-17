import streamlit as st


def check_pin(page_key: str, secret_path: str = "record_lock.pin"):
    flag_key = f"{page_key}_pin_ok"
    pin_key = f"{page_key}_pin_input"
    error_key = f"{page_key}_pin_error"

    # ✅ Déjà validé : on ne dessine plus l'UI du PIN
    if st.session_state.get(flag_key, False):
        return True

    # --- CSS ---
    st.markdown(
        """
        <style>
        .stButton>button {
            padding: 30px;
            font-size: 2rem;
        }
        .pin-dots-wrapper {
            display: flex;
            justify-content: center;
        }
        .pin-dots {
            font-size: 2.2rem;
            letter-spacing: 0.6rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # récupérer le PIN dans st.secrets
    real_pin = st.secrets
    for part in secret_path.split("."):
        real_pin = real_pin[part]
    real_pin = str(real_pin)
    pin_len = len(real_pin)

    # init state
    if pin_key not in st.session_state:
        st.session_state[pin_key] = ""
    if error_key not in st.session_state:
        st.session_state[error_key] = ""

    st.title("🔐 Déverrouiller l'accès")

    # --- handlers ---
    def handle_digit(d):
        cur = st.session_state[pin_key]
        if len(cur) < pin_len:
            cur += d
            st.session_state[pin_key] = cur

        # check PIN quand on a atteint la longueur
        if len(st.session_state[pin_key]) == pin_len:
            if st.session_state[pin_key] == real_pin:
                st.session_state[flag_key] = True
                st.session_state[error_key] = ""
                st.session_state[pin_key] = ""
                st.rerun()  # fait disparaître l’UI PIN
            else:
                st.session_state[error_key] = "Code incorrect"
                st.session_state[pin_key] = ""

    def handle_clear():
        st.session_state[pin_key] = ""
        st.session_state[error_key] = ""

    def handle_delete():
        cur = st.session_state[pin_key]
        st.session_state[pin_key] = cur[:-1]

    # --- 1) D'abord, les boutons (pour mettre à jour le state) ---
    buttons = ["1", "0", "C", "⌫"]

    for label in buttons:
        if label in ("0", "1"):
            if st.button(
                label, key=f"{page_key}_btn_{label}", use_container_width=True
            ):
                handle_digit(label)
        elif label == "C":
            if st.button("C", key=f"{page_key}_btn_clear", use_container_width=True):
                handle_clear()
        elif label == "⌫":
            if st.button("⌫", key=f"{page_key}_btn_del", use_container_width=True):
                handle_delete()

    # --- 2) Ensuite, on affiche les points en fonction du state mis à jour ---
    current_pin = st.session_state[pin_key]
    dots = "".join("●" if i < len(current_pin) else "○" for i in range(pin_len))
    st.markdown(
        f'<div class="pin-dots-wrapper"><span class="pin-dots">{dots}</span></div>',
        unsafe_allow_html=True,
    )

    # message d'erreur éventuel
    if st.session_state.get(error_key):
        st.error(st.session_state[error_key])

    return False


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
