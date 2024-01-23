import streamlit as st
from dbmemory import insert_chat, get_chat, update_chat, delete_chat, get_all_chat, get_all_ai, download_vector_store
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import time
import random

def get_ai_names_and_paths(ai_data):
    ai_names = ["Nessuna IA specifica"]
    ai_paths = ["Nessuna IA specifica"]
    for ai in ai_data:
        ai_names.append(ai["nomeAI"])
        ai_paths.append(ai["path"])
    return ai_names, ai_paths

def select_ai(ai_names, ai_paths):
    ai_select = st.sidebar.selectbox("Seleziona una IA:", ai_names, index=0 if "ai_select" not in st.session_state else ai_names.index(st.session_state.ai_name))
    if ai_select != "Nessuna IA specifica":
        st.session_state.ai_name = ai_select
        st.session_state.ai_path = ai_paths[ai_names.index(ai_select)]
    else:
        st.session_state.ai_name = "Nessuna IA specifica"
        st.session_state.ai_path = "Nessuna IA specifica"

def load_ai_if_not_present():
    if st.session_state.ai_name not in st.session_state.qa:
        with st.spinner("Caricamento IA..."):
            qa = download_vector_store(st.session_state.supabase, st.session_state.ai_path, st.session_state.ai_name)
            st.session_state.qa[st.session_state.ai_name] = qa

def chat():
    with st.sidebar:
        st.header("ℹ️ Cronologia Chat")
        st.write("")
        st.write("")

        if 'llm' not in st.session_state:
            st.session_state.llm = ChatOpenAI( temperature=0, max_tokens=600, streaming=True, openai_api_key=st.session_state.OPENAI_API_KEY , model_name="gpt-4")

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

        ai_all = get_all_ai(st.session_state.supabase, st.session_state.nome_utente)
        ai_names, ai_paths = get_ai_names_and_paths(ai_all.data)
        select_ai(ai_names, ai_paths)
        if st.session_state.ai_name != "Nessuna IA specifica":
            st.session_state.qa = st.session_state.get('qa', {})
            load_ai_if_not_present()

                


        if prompt := st.chat_input("Ciao, come posso aiutarti?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                if st.session_state.ai_name != "Nessuna IA specifica":
                    with st.spinner("Caricamento risposta..."):
                        result = st.session_state.qa[st.session_state.ai_name]({"query": prompt})
                        full_response += result["result"]
                        if result["source_documents"] is not None:
                            full_response += "\n---\n"
                            for document in result["source_documents"]:
                                full_response += "\n\n" + str(document)
                else:
                    for response in st.session_state.llm.stream(prompt):
                        full_response += str(response.content)
                        message_placeholder.markdown(full_response + "▌")

                #se full response contine ---
                if full_response.find("---") != -1:
                    full_response = full_response.split("---")   
                    source_documents = full_response[1]
                    full_response = full_response[0]
                    message_placeholder.markdown(full_response)
                    with st.expander("Mostra documenti relativi alla domanda : " + prompt[0:7] + "..."):
                        st.write(source_documents)
                else:
                    message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            update_chat(st.session_state.supabase, st.session_state.chat_id, st.session_state.messages)

