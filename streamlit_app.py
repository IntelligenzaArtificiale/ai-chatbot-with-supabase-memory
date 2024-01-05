# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps

import time
import openai
import streamlit as st
import random
from dbmemory import init_connection, insert_chat, get_chat, update_chat, delete_chat, get_all_chat
import asyncio

st.title('🤖💬 AI memoria CHAT')


if "OPENAI_API_KEY" not in st.session_state:
    start = st.container()
    with start:
        nome_utente = st.text_input('Inserisci il tuo nome utente : ')
        api_key = st.text_input('Inserisci OpenAI API KEY:', type='password')
        
            
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
    st.session_state.user_chats = get_all_chat(st.session_state.supabase, st.session_state.nome_utente)

    if len(st.session_state.user_chats.data) == 0:
        chat_list = ["Nuova Chat"]
    else:
        chat_list = ["Nuova Chat"] + [chat["id_chat"] for chat in st.session_state.user_chats.data]

    selected_chat = st.sidebar.selectbox("Seleziona una chat:", chat_list, index=0 if "chat_id" not in st.session_state else chat_list.index(st.session_state.chat_id))

    if selected_chat == "Nuova Chat":
        # Logica per una nuova chat
        new_chat_name = st.text_input("Inserisci il nome per la nuova chat:")
        if st.button("Inizia nuova chat") and len(new_chat_name) > 3:
            st.session_state.chat_id = new_chat_name
            st.session_state.messages = []
            with st.spinner("Creazione nuova chat..."):
                insert_chat(st.session_state.supabase, new_chat_name, st.session_state.nome_utente)
                st.success("Chat ' {} ' creata con successo!".format(new_chat_name))
                time.sleep(1)
            st.rerun()

    elif selected_chat in [chat ["id_chat"] for chat in st.session_state.user_chats.data]:
        if "chat_id" not in st.session_state:
            st.session_state.chat_id = ""
        if selected_chat != st.session_state.chat_id:
            with st.spinner("Caricamento chat..."):
                st.session_state.chat_id = selected_chat
                st.session_state.messages = get_chat(st.session_state.supabase, st.session_state.nome_utente, selected_chat)
                st.success("Chat ' {} ' caricata con successo!".format(selected_chat))

    if "user_chats" in st.session_state:
        if st.button("Aggiorna lista chat"):
            with st.spinner("Aggiornamento chat..."):
                st.session_state.user_chats = get_all_chat(st.session_state.supabase, st.session_state.nome_utente)
                st.success("Lista chat aggiornata con successo!")
                time.sleep(1)
            st.rerun()

        if st.button("Elimina chat"):
            with st.spinner("Eliminazione chat..."):
                delete_chat(st.session_state.supabase, st.session_state.chat_id)
                st.session_state.user_chats = get_all_chat(st.session_state.supabase, st.session_state.nome_utente)
                del st.session_state.messages
                del st.session_state.chat_id
                st.success("Chat eliminata con successo!")
                st.info("Seleziona una chat dalla lista per continuare")
                time.sleep(1)
            st.rerun()

if "messages" in st.session_state:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if "messages" in st.session_state:
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

