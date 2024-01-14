from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from os import path
import os
import random
import shutil
import time
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader
from dbmemory import upload_vector_store, add_ai
import streamlit as st



def load_docs(directory):
  loader = DirectoryLoader(directory)
  documents = loader.load()
  return documents

def split_docs(documents,chunk_size=300,chunk_overlap=20):
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
  docs = text_splitter.split_documents(documents)
  return docs

def buildAI(nome_utente):
    #create temporary folder
    if not path.exists('temp'):
        os.mkdir('temp')
    directory = 'temp'

    st.subheader('🤖💬 Crea un IA allenata sui tuoi PDF\n\n')
    file = st.file_uploader("STEP 1: Carica i tuoi PDF", type=["pdf"])

    if file is not None:
        # add file to temporary folder
        with open(os.path.join(directory,file.name),"wb") as f:
            f.write(file.getbuffer())
        st.success("File caricato con successo!")
        time.sleep(1)

        st.write('STEP 2: Dai un nome adeguato alla tua IA')
        nome = st.text_input('Inserisci il nome della tua IA : ')
        if st.button("Crea IA"):
            with st.status("Caricamento documenti...") as status:
                documents = load_docs(directory)
                time.sleep(1)
                status.update(label="Documenti caricati con successo!")
                time.sleep(1)
                status.update(label="Divido i documenti...")
                docs = split_docs(documents)
                time.sleep(1)
                status.update(label="Documenti divisi con successo!")
                time.sleep(1)
                status.update(label="Creo un Vector Store...")
                nome_db = str(random.randint(0,100000)) + "db"
                embeddings = OpenAIEmbeddings(openai_api_key=st.session_state.OPENAI_API_KEY)
                db = Chroma.from_documents(docs, embeddings, persist_directory=f"./chroma_db_{nome_db}")
                db.persist()
                st.write(db.get().keys())
                st.write(len(db.get()["ids"]))
                time.sleep(1)
                status.update(label="Vector Store creato con successo!")
                time.sleep(1)
                status.update(label="Allenamento in corso...")
                #zippo la cartella con il db
                shutil.make_archive(f'chroma_db_{nome_db}', 'zip', f'chroma_db_{nome_db}')
                time.sleep(3)
                status.update(label="Allenamento completato!")
                time.sleep(1)
                #salvo l'IA su supabase
                status.update(label="Salvataggio IA su Supabase...")
                time.sleep(1)
                with open(f'chroma_db_{nome_db}.zip', 'rb') as f:
                    blob = f.read()
                    upload_vector_store(st.session_state.supabase, blob, nome)
                    add_ai(st.session_state.supabase, nome_utente, nome)
                    time.sleep(1)
                status.update(label="IA salvata con successo!")

               
                #delete temporary folder
                shutil.rmtree(directory)
                #remove chroma_db/ folder and zip file
                shutil.rmtree(f'chroma_db_{nome_db}')
                os.remove(f'chroma_db_{nome_db}.zip')
                time.sleep(1)
                status.update(label="Pulizia cartella temporanea...")
                    
            st.success("IA creata con successo!")
            st.info("Ora puoi utilizzare la tua IA nella sezione CHAT")
