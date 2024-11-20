import os
import json
from datetime import datetime
import streamlit as st
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from firebase_admin import credentials, firestore
import firebase_admin
from llama_index.core.tools import FunctionTool
from src.global_settings import INDEX_STORAGE, SCORES_FILE
from src.prompts import CUSTOM_AGENT_SYSTEM_TEMPLATE
from llama_index.core.storage.chat_store import SimpleChatStore  # Import SimpleChatStore and ChatMessage
from llama_index.core.types import ChatMessage

db = firestore.client()

user_avatar = "data/images/mabel.png"
professor_avatar = "data/images/dipper.png"
FIREBASE_DB_PATH = 'chat_store'

import tempfile

def load_chat_store(username):
    
    # Fetch the conversation data from Firebase
    ref = db.collection(FIREBASE_DB_PATH).document(username)
    chat_data = ref.get().to_dict()
    print(chat_data)
    if chat_data is None:
        chat_data = {}
    if "store" in chat_data:
            chat_store = SimpleChatStore()
            for username, messages in chat_data['store'].items():
                for message in messages:
                    # Create a ChatMessage instance
                    chat_message = ChatMessage(
                        role=message['role'],
                        content=message['content']
                    )
                    # Add the message to the chat store
                    chat_store.add_message(key=username, message=chat_message)
    else:
        chat_store = SimpleChatStore()
            
    

    return chat_store

def save_chat_store(chat_store, username):
    # Reference to the Firestore document based on the username
    ref = db.collection(FIREBASE_DB_PATH).document(username)
    
    # Check if the document exists
    if not ref.get().exists:
        ref = db.collection(FIREBASE_DB_PATH).add(username)
        # Initialize with default values for a new user
        ref.set({
            "store": {username: []},
            "last_updated": datetime.now().isoformat()
        })
    
    # Extract messages for the given user
    messages = chat_store.messages.get(username, [])
    
    # Prepare data to save
    chat_data = {
        "store": {
            username: [msg.__dict__ for msg in messages]
        },
        "last_updated": datetime.now().isoformat()
    }
    
    # Save or update the document in Firestore
    ref.set(chat_data)

def display_messages(chat_store, container, key):
    with container:
        for message in chat_store.get_messages(key=key):
            if message.role == "user":
                with st.chat_message(message.role, avatar=user_avatar):
                    st.markdown(message.content)
            elif message.role == "assistant" and message.content != None:
                with st.chat_message(message.role, avatar=professor_avatar):
                    st.markdown(message.content)


def initialize_chatbot(chat_store, container, username, user_info):
    memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000, 
        chat_store=chat_store, 
        chat_store_key=username
    )  
    storage_context = StorageContext.from_defaults(
        persist_dir=INDEX_STORAGE
    )
    index = load_index_from_storage(
        storage_context, index_id="vector"
    )
    habit_engine = index.as_query_engine(
        similarity_top_k=3,
    )
    habit_tool = QueryEngineTool(
        query_engine=habit_engine, 
        metadata=ToolMetadata(
            name="habit",
            description=(
                f"Provide function to  "
                f"people need to change habit"
            ),
        )
    )   

    agent = OpenAIAgent.from_tools(
        tools=[habit_tool], 
        memory=memory,
        system_prompt=CUSTOM_AGENT_SYSTEM_TEMPLATE.format(user_info=user_info)
    )
    display_messages(chat_store, container, key=username)
    return agent

def chat_interface(agent, chat_store, container):  
    username = st.session_state['username']
    if not db.collection(FIREBASE_DB_PATH).document(username).get().exists:
        with container:
            with st.chat_message(name="assistant", avatar=professor_avatar):
                st.markdown("Hello, we are Dipper and Mabel, we here to help you.")
    prompt = st.chat_input("Ask me a question...")
    if prompt:
        with container:
            with st.chat_message(name="user", avatar=user_avatar):
                st.markdown(prompt)
            response = str(agent.chat(prompt))
            with st.chat_message(name="assistant", avatar=professor_avatar):
                st.markdown(response)
                
        conversation_data = {
                "store": {
                    username: [
                        {
                            "role": "user",
                            "content": prompt,
                            "additional_kwargs": {}
                        },
                        {
                            "role": "assistant",
                            "content": response,
                            "additional_kwargs": {}
                        }
                    ]
                },
                "last_updated": datetime.now().isoformat()
            }
        # Check if the document exists
    if not ref.get().exists:
        ref = db.collection(FIREBASE_DB_PATH).document(username)
        # Initialize with default values for a new user
        ref.set({
            "store": {username: []},
            "last_updated": datetime.now().isoformat()
        })
    
        ref = db.collection(FIREBASE_DB_PATH).document(username)
        ref.update({
            "store." + username: firestore.ArrayUnion(conversation_data["store"][username]),
            "last_updated": conversation_data["last_updated"]
        })
                