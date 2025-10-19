import os
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.title("HealthBuddy - Asisten Kesehatanmu")

def get_api_key_input():
    """Minta pengguna untuk memasukkan Google API Key jika belum ada di .env."""
    if "GOOGLE_API_KEY" not in os.environ:
        if "GOOGLE_API_KEY" not in st.session_state:
            st.session_state["GOOGLE_API_KEY"] = ""
        
        if st.session_state["GOOGLE_API_KEY"]:
            return st.write("Masukkan Google API Key")
        
        col1, col2 = st.columns((80, 20))
        with col1:
            api_key = st.text_input("Google API Key", label_visibility="collapsed", type="password")
        with col2:
            is_submit_pressed = st.button("Submit")
        
        if is_submit_pressed:
            st.session_state["GOOGLE_API_KEY"] = api_key
            os.environ["GOOGLE_API_KEY"] = st.session_state["GOOGLE_API_KEY"]
        
        if not st.session_state["GOOGLE_API_KEY"]:
            st.stop()
        st.rerun()

def load_llm():
    """Inisialisasi model AI dari Google Generative AI."""
    if "llm" not in st.session_state:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Kamu adalah HealthBuddy, asisten kesehatan yang ramah dan informatif. Berikan saran kesehatan umum, tips nutrisi, dan gaya hidup sehat dengan bahasa yang santai namun jelas. Selalu ingatkan pengguna bahwa saranmu bukan pengganti konsultasi dokter. Jawab dalam bahasa Indonesia."),
            ("placeholder", "{chat_history}"),
            ("human", "{input}")
        ])
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        chain = prompt | llm | StrOutputParser()
        st.session_state["llm"] = chain
    return st.session_state["llm"]

def get_chat_history():
    """Dapatkan riwayat percakapan."""
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    return st.session_state["chat_history"]

def clear_chat_history():
    """Hapus riwayat percakapan."""
    if st.button("Hapus Riwayat"):
        st.session_state["chat_history"] = []
        st.rerun()

def display_chat_message(message):
    """Tampilkan pesan di kolom chat."""
    role = "User" if isinstance(message, HumanMessage) else "HealthBuddy"
    with st.chat_message(role):
        st.markdown(message.content)

def display_chat_history(chat_history):
    """Tampilkan seluruh riwayat percakapan."""
    for chat in chat_history:
        display_chat_message(chat)

def user_query_to_llm(llm, chat_history):
    """Proses input pengguna dan dapatkan respon dari LLM."""
    prompt = st.chat_input("Tanya tentang kesehatan, nutrisi, atau gaya hidup!")
    if not prompt:
        return
    
    chat_history.append(HumanMessage(content=prompt))
    display_chat_message(chat_history[-1])
    
    response = llm.invoke({
        "chat_history": chat_history,
        "input": prompt
    })
    
    chat_history.append(AIMessage(content=response))
    display_chat_message(chat_history[-1])

def main():
    """Fungsi utama aplikasi."""
    get_api_key_input()
    llm = load_llm()
    chat_history = get_chat_history()
    clear_chat_history()
    display_chat_history(chat_history)
    user_query_to_llm(llm, chat_history)

if __name__ == "__main__":
    main()