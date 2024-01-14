from supabase import create_client, Client
import streamlit as st
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from zipfile import *
import os
import shutil

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


########### Vector Store ###########

def upload_vector_store(client: Client, file, nome):
    #supabase.storage.from_("testbucket").upload(file=f,path=path_on_supastorage, file_options={"content-type": "audio/mpeg"})
    return client.storage.from_("Vector DB").upload(file=file, file_options={"content-type": "application/zip"}, path=f"{nome}.zip")

def download_vector_store(client: Client, nome, ai_select):
    #    supabase.storage.from_("testbucket").upload(file=f,path=path_on_supastorage, file_options={"content-type": "audio/mpeg"})
    
    dowanload_db = client.storage.from_("Vector DB").download(path=f"{nome}")
    #create zip file
    with open(f'chroma_db_{ai_select}.zip', 'wb+') as f:
        f.write(dowanload_db)
    #extract zip file
    with ZipFile(f'chroma_db_{ai_select}.zip', 'r') as zipObj:
        zipObj.extractall(f'chroma_db_{ai_select}')

    #delete zip file
    os.remove(f'chroma_db_{ai_select}.zip')

    embeddings = OpenAIEmbeddings(openai_api_key=st.session_state.OPENAI_API_KEY)
    db = Chroma(persist_directory=f'./chroma_db_{ai_select}', embedding_function=embeddings)
    db.persist()
    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(st.session_state.llm, chain_type='stuff', retriever=retriever, return_source_documents=True)
    # del db
    shutil.rmtree(f'chroma_db_{ai_select}')
    st.sidebar.success("IA ' {} ' caricata con successo!".format(ai_select))
    return qa



#  autore path nomeAI
def add_ai(client: Client, autore, nomeAI):
    path = nomeAI + ".zip"
    return client.table("AI").insert(
        [{"autore": autore, "path": path, "nomeAI": nomeAI}]
    ).execute()

def get_ai(client: Client, autore, nomeAI):
    result = client.table("AI").select("*").eq("autore", autore).eq("nomeAI", nomeAI).execute()
    print(result)
    if len(result.data) > 0:
        ai_data = result.data[0]
        return ai_data
    return []

def get_all_ai(client: Client, autore):
    return client.table("AI").select("*").eq("autore", autore).execute()


