from supabase import create_client, Client
import streamlit as st

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    url = "https://miqjhryivzvftfskwpou.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pcWpocnlpdnp2ZnRmc2t3cG91Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDQzNjQ1MzIsImV4cCI6MjAxOTk0MDUzMn0.7spXuEnUbVPTQiuojhc-3XzVt8BWAexC3ZeZSjsbyzo"
    return create_client(url, key)

import json

# Funzione per convertire i messaggi in formato JSON
def convert_messages_to_json(messages):
    return json.dumps(messages)

# Funzione per convertire i messaggi da JSON a lista di messaggi
def convert_json_to_messages(json_data):
    return json.loads(json_data)

# Inserimento dei messaggi nel database
def insert_chat(client: Client, id_chat, messages, autore):
    messages_json = convert_messages_to_json(messages)
    return client.table("Database per CHAT CLIENTI").insert(
        [{"id_chat": id_chat, "conversazione": messages_json, "autore": autore}]
    ).execute()

# Recupero dei messaggi dal database
def get_chat(client: Client, autore, id_chat):
    result = client.table("Database per CHAT CLIENTI").select("*").eq("autore", autore).eq("id_chat", id_chat).execute()
    if len(result["data"]) > 0:
        chat_data = result["data"][0]
        chat_messages_json = chat_data["conversazione"]
        messages = convert_json_to_messages(chat_messages_json)
        return messages
    return None

def update_chat(client: Client, id_chat, conversazione):
    return client.table("Database per CHAT CLIENTI").update(
        {"conversazione": conversazione}
    ).eq("id_chat", id_chat).execute()

def delete_chat(client: Client, id_chat):
    return client.table("Database per CHAT CLIENTI").delete().eq("id_chat", id_chat).execute()

def get_all_chat(client: Client, autore):
    return client.table("Database per CHAT CLIENTI").select("*").eq("autore", autore).execute()


