import firebase_admin
import streamlit as st
import hashlib
from firebase_admin import credentials, firestore, initialize_app
import json

firebase_config_str = st.secrets["firebase"]["my_settings"]

# Convert the string to a dictionary
firebase_config_dict = dict(firebase_config_str)

# Use the dictionary to initialize Firebase credentials
cred = credentials.Certificate(firebase_config_dict)

# Initialize the Firebase app
try:
    # Initialize the app with a service account, granting admin privileges
    if not firebase_admin._apps:
        cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
except Exception as err:
    # Swallow the error (log it or handle it)
    print(f"Error during Firebase initialization: {err}")
db = firestore.client()
# Password Hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Password Verification
def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# Register Function
def register():
    with st.form(key="register"):
        st.subheader('Register')
        username = st.text_input('Username')
        email = st.text_input('Email')
        name = st.text_input('Full Name')
        age = st.number_input('Age', min_value=5, max_value=100)
        gender = st.selectbox('Gender', ['Male', 'Female', 'Other'])
        job = st.text_input('Occupation')
        address = st.text_input('Address')
        password = st.text_input('Password', type='password')
        confirm_password = st.text_input('Confirm Password', type='password')

        if st.form_submit_button('Register'):
            user_doc = db.collection('users').document(username).get()
            if user_doc.to_dict():
                st.error('Username is not available!')
            elif password != confirm_password:
                st.error('Passwords do not match!')
            else:
                hashed_password = hash_password(password)
                user_data = {
                    "email": email,
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "job": job,
                    "address": address,
                    "password": hashed_password,
                    "created_at": firestore.SERVER_TIMESTAMP
                }
                # Save to Firestore
                db.collection('users').document(username).set(user_data)
                st.session_state.username = username
                st.session_state.logged_in = True
                st.session_state.user_info = user_data
                st.success("Registration successful!")
                st.rerun()

# Login Function
def login():
    with st.form(key="login"):
        st.subheader('Login')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')

        if st.form_submit_button('Login'):
            user_doc = db.collection('users').document(username).get()
            if not user_doc.to_dict():
                st.error('Username is incorrect!')
            else:
                user_data = user_doc.to_dict()
                if verify_password(user_data['password'], password):
                    st.session_state.username = username
                    st.session_state.logged_in = True
                    st.session_state.user_info = user_data
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error('Incorrect password!')

# Guest Login
def guest_login():
    if st.button('Guest Login'):
        st.session_state.logged_in = True
        st.session_state.username = 'Guest'
        st.session_state.user_info = {"username": "Guest", "info": "Guest user"}
        st.success("Guest login successful!")
        st.rerun()

# Main App
if __name__ == '__main__':
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.expander('GRAVITY FALL', expanded=True):
            login_tab, create_tab = st.tabs(["Login", "Create account"])
            with create_tab:
                register()
            with login_tab:
                login()
            guest_login()
    else:
        st.write(f"Welcome, {st.session_state.username}!")
