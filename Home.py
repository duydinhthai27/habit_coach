import streamlit as st
from src.authenticate2 import login, register, guest_login
import src.sidebar as sidebar


def main():
    sidebar.show_sidebar()
    

   
    # Giao diện đăng nhập
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.expander('Gravity Fall', expanded=True):
            login_tab, create_tab = st.tabs(
                [
                    "Login",
                    "Sign up"
                ]
            )
            with create_tab:
                register()
            with login_tab:
                login()
    else:
        st.image("data/images/chat.jpeg")
        if st.button("Have a sip with Habit Coach"):
            st.switch_page("pages/chat.py")
        st.success(f'Welcome {st.session_state.username}, build your good habits here', icon="🎉")
if __name__ == "__main__":
    main()
