import streamlit as st
import json
import google.generativeai as genai

# SAYFA AYARLARI
st.set_page_config(page_title="Mustafa Cici AI", page_icon="🤖")

# 1. VERİYİ YÜKLE
@st.cache_data
def load_data():
    try:
        with open('verilerim.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Veri dosyası bulunamadı.")
        return None

data = load_data()

# 2. API ANAHTARINI GİZLİ KASADAN (SECRETS) AL
try:
    # Streamlit Cloud'daki gizli anahtarı çekiyoruz
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # Eğer lokalde çalışıyorsan ve secrets ayarlı değilse hata vermesin diye (opsiyonel)
    st.error("API Anahtarı bulunamadı! Streamlit Secrets ayarlarını kontrol et.")
    st.stop()

# 3. YAN MENÜ (SADECE BİLGİ)
with st.sidebar:
    st.header("Hakkında")
    st.success("Bu bot Mustafa Cici'nin kişisel API anahtarı ile çalışmaktadır. Ücretsiz kullanabilirsiniz.")
    st.write("💻 **Geliştirici:** Mustafa Cici")

# 4. ANA EKRAN
st.title("🤖 Mustafa Cici Asistanı")
st.write("Merhaba! Ben Mustafa'nın yapay zeka versiyonuyum. Bana stajlarım, projelerim veya teknik bilgilerim hakkında soru sorabilirsin.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        genai.configure(api_key=api_key)
        # Senin hesabında çalışan güçlü model
        model = genai.GenerativeModel('gemini-2.5-flash')

# YENİ ÇOK DİLLİ PROMPT (Bunu kopyala ve eskisinin yerine yapıştır)
        system_prompt = f"""
        ROLE: You are the professional and friendly digital assistant of Mustafa Cici.
        
        DATA SOURCE (JSON):
        {json.dumps(data, ensure_ascii=False)}

        INSTRUCTIONS:
        1. **LANGUAGE DETECTION:** Detect the language of the user's question. 
           - If the user asks in **English**, answer in **English**.
           - If the user asks in **Turkish**, answer in **Turkish**.
           - For other languages, answer in English.
        
        2. **BEHAVIOR:**
           - Be professional but friendly.
           - Use the provided JSON data as your only source of truth.
           - Do NOT use JSON format in your output. Speak naturally.
           - Refer to Mustafa in the third person (e.g., "Mustafa has worked at...", "He is experienced in...").
        
        3. **UNKNOWN INFO:**
           - If the answer is not in the JSON data, say: 
             (In English) "I don't have that information in my database, but I can forward your request to Mustafa."
             (In Turkish) "Veri tabanımda bu bilgi yok ama isterseniz Mustafa'ya iletebilirim."

        User Question: {prompt}
        """

        with st.chat_message("assistant"):
            with st.spinner("Yazıyor..."):
                response = model.generate_content(system_prompt)
                st.write(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:

        st.error(f"Bir hata oluştu: {e}")

