from supabase import create_client, Client
import streamlit as st

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

import json

# Funzione per convertire i messaggi in formato JSON
def convert_messages_to_json(messages):
    return json.dumps(messages)

# Funzione per convertire i messaggi da JSON a lista di messaggi
def convert_json_to_messages(json_data):
    if isinstance(json_data, list):
        return json_data
    elif isinstance(json_data, str):
        return json.loads(json_data)
    else:
        return []

# Inserimento dei messaggi nel database
def insert_chat(client: Client, id_chat, autore):
    return client.table("CHAT").insert(
        [{"id_chat": id_chat, "autore": autore}]
    ).execute()

# Recupero dei messaggi dal database
def get_chat(client: Client, autore, id_chat):
    result = client.table("CHAT").select("*").eq("autore", autore).eq("id_chat", id_chat).execute()
    print(result)
    if len(result.data) > 0:
        chat_data = result.data[0]
        chat_messages_json = chat_data["conversazione"]
        messages = convert_json_to_messages(chat_messages_json)
        return messages
    return []

def update_chat(client: Client, id_chat, conversazione):
    return client.table("CHAT").update(
        {"conversazione": conversazione}
    ).eq("id_chat", id_chat).execute()

def delete_chat(client: Client, id_chat):
    return client.table("CHAT").delete().eq("id_chat", id_chat).execute()

def get_all_chat(client: Client, autore):
    return client.table("CHAT").select("*").eq("autore", autore).execute()


