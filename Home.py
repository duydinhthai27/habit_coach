import streamlit as st
from src.authenticate import login, register, guest_login
import src.sidebar as sidebar


def main():
    sidebar.show_sidebar()
    

   
    # Giao diện đăng nhập
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.expander('Gravity Fall', expanded=True):
            login_tab, create_tab, guest_tab = st.tabs(
                [
                    "Login",
                    "Sign up",
                    "Guest"
                ]
            )
            with create_tab:
                register()
            with login_tab:
                login()
            with guest_tab:
                guest_login()
    else:
        
        col1, col2 = st.columns(2)
        with col1:
            st.image("data/images/chat.jpeg")
            if st.button("Have a sip with Habit Coach"):
                st.switch_page("pages/2_💬_Chat.py")
        with col2:
            st.image("data/images/chart.jpeg")
            if st.button("Dont touch this please"):
                st.switch_page("pages/1_📈_user.py")
        st.success(f'Welcome {st.session_state.username}, build your good habits here', icon="🎉")
if __name__ == "__main__":
    main()
