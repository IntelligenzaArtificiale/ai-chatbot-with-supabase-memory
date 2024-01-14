# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps

import time
import streamlit as st
import random
from chatUI import chat
from buildAI import buildAI
import asyncio
from dbmemory import init_connection
from streamlit_option_menu import option_menu



if "OPENAI_API_KEY" not in st.session_state:
    st.title('🤖💬 Log IN')
    start = st.container()
    with start:
        nome_utente = st.text_input('Inserisci il tuo nome utente : ')
        api_key = st.text_input('Inserisci OpenAI API KEY:', type='password')
        
            
        if st.button("login"):
            if not (api_key.startswith('sk-') and len(api_key)==51) or len(nome_utente) < 3:
                st.warning('HEY non è corretta!', icon='⚠️')
            else:
                st.session_state.OPENAI_API_KEY = api_key
                st.session_state.nome_utente = nome_utente
                st.session_state.supabase = init_connection()
                st.success('Ok perfetto entriamo!', icon='👉')
                time.sleep(2)
                st.rerun()
        else:
            st.stop()
else:

    st.title('🤖💬 AI memoria CHAT')

    def on_change(key):
        selection = st.session_state[key]
        #st.write(f"Selection changed to {selection}")

    if 'menu' not in st.session_state:
        menu = option_menu(None, ["AI CHAT", "Crea IA Specializzata"],
                            icons=['house','gear'],
                            on_change=on_change, key='menu', orientation="horizontal")
    else:
        menu = option_menu(st.session_state.menu, ["AI CHAT", "Crea IA Specializzata"],
                            icons=['house','gear'],
                            on_change=on_change, key='menu', orientation="horizontal")

    if menu == 'AI CHAT':
        chat()
    else:
        st.write(st.session_state.nome_utente)
        buildAI(st.session_state.nome_utente)

