# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps

import time
import openai
import streamlit as st
import random
from dbmemory import init_connection, insert_chat, get_chat, update_chat, delete_chat, get_all_chat


st.title('🤖💬 OpenAI Chatbot')


if "OPENAI_API_KEY" not in st.session_state:
    start = st.container()
    with start:
        nome_utente = st.text_input('Inserisci il tuo nome utente : ')
        modello = st.selectbox('Seleziona il modello di IA', ('Google Gemini PRO', 'OpenAI GPT3.5'))
        api_key = st.text_input('Inserisci OpenAI API KEY:', type='password')
        
        if len(api_key)>3 and len(nome_utente)>3 :
            
            if st.button("login"):
                if not (api_key.startswith('sk-') and len(api_key)==51):
                    st.warning('HEY non è corretta!', icon='⚠️')
                else:
                    openai.api_key = api_key
                    st.session_state.OPENAI_API_KEY = api_key
                    st.session_state.nome_utente = nome_utente
                    st.session_state.supabase = init_connection()
                    st.success('Ok perfetto entriamo!', icon='👉')
                    time.sleep(2)
                    st.rerun()
        else:
            st.stop()
else:
    openai.api_key = st.session_state.OPENAI_API_KEY

with st.sidebar:
    st.header("ℹ️ Cronologia Chat")
    st.write("")
    st.write("")
    
    # Recuperiamo tutte le chat dell'utente attuale
    user_chats = get_all_chat(st.session_state.supabase, st.session_state.noe_utente)
    chat_list = ["Nuova Chat"] + [chat["id_chat"] for chat in user_chats["data"]]

    selected_chat = st.sidebar.selectbox("Seleziona una chat:", chat_list)

    if selected_chat == "Nuova Chat":
        # Logica per una nuova chat
        new_chat_name = st.text_input("Inserisci il nome per la nuova chat:", value=f"Chat_{random.randint(1000, 9999)}")
        if st.button("Inizia nuova chat"):
            st.session_state.chat_id = new_chat_name
            st.session_state.messages = []
            with st.spinner("Creazione nuova chat..."):
                insert_chat(st.session_state.supabase, new_chat_name, [], st.session_state.nome_utente)
            st.success("Chat creata con successo!")

    elif selected_chat in [chat ["id_chat"] for chat in user_chats["data"]]:
        if selected_chat != st.session_state.chat_id:
            with st.spinner("Caricamento chat..."):
                st.session_state.chat_id = selected_chat
                st.session_state.messages = get_chat(st.session_state.supabase, st.session_state.nome_utente, selected_chat)
            st.success("Chat caricata con successo!")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ciao, come posso aiutarti?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]}
                      for m in st.session_state.messages], stream=True):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    update_chat(st.session_state.supabase, st.session_state.chat_id, st.session_state.messages)
    
