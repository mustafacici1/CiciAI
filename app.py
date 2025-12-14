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

# YENİ PROMPT (Bunu eskisinin yerine yapıştır)
        system_prompt = f"""
        ROL: Sen Mustafa Cici'nin profesyonel ve samimi dijital asistanısın.
        
        KAYNAK BİLGİLER (JSON):
        {json.dumps(data, ensure_ascii=False)}

        KURALLAR:
        1. Cevaplarını KESİNLİKLE düz metin olarak ver. Asla JSON veya kod bloğu ({{"response": ...}}) kullanma.
        2. Sanki karşında bir arkadaşın veya İK uzmanı varmış gibi doğal konuş.
        3. Mustafa'nın verilerini kullan ama robot gibi listeleme, cümle içinde geçir.
        4. Bilmediğin bir şey sorulursa "Bu konuda veri tabanımda bilgi yok" de ve uydurma.
        5. Mustafa adına konuşma (Ben yaptım deme), "Mustafa yaptı", "Onun projesi" şeklinde konuş.
        
        Kullanıcı Sorusu: {prompt}
        """

        with st.chat_message("assistant"):
            with st.spinner("Yazıyor..."):
                response = model.generate_content(system_prompt)
                st.write(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:

        st.error(f"Bir hata oluştu: {e}")
