import streamlit as st

def show_sidebar():
    st.sidebar.image("data/images/logo.png", use_column_width=True)
    st.sidebar.markdown('### 🏕️ Welcome to the Gravity Falls Adventure!')

    st.sidebar.markdown('Instructions:')
    st.sidebar.markdown('1. 🏞️ **Log in to your account.**')
    st.sidebar.markdown('2. 💬 **Use the chat feature - "Talk to Dipper and Mabel" to share your thoughts and challenges.**')
    st.sidebar.markdown('3. 🗺️ **When you have enough information or finish the conversation, Dipper and Mabel will provide advice on building good habits.**')
    st.sidebar.markdown('4. 📈 **Your progress will be saved. You can use the user feature - "Track Your Journey" to see detailed statistics on your habits and improvements.**')
