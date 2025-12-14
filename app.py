import streamlit as st
import json
import google.generativeai as genai
import urllib.parse

# --- 1. SAYFA AYARLARI ---
st.set_page_config(
    page_title="Mustafa Cici AI",
    page_icon="🤖",
    layout="centered"
)

# --- MODERN CSS STILI ---
st.markdown("""
<style>
    /* Ana tema renkleri */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #06b6d4;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
    }
    
    /* Genel arka plan */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Başlık stili */
    h1 {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
    }
    
    /* Ana açıklama metni */
    .main-description {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        line-height: 1.6;
        margin: 1.5rem auto;
        max-width: 600px;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Chat mesaj kutuları */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        padding: 1.2rem !important;
        margin: 0.8rem 0 !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Kullanıcı mesajları */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
    }
    
    /* Asistan mesajları */
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%) !important;
        border-color: rgba(6, 182, 212, 0.3) !important;
    }
    
    /* Input alanı */
    .stChatInputContainer {
        border-top: 1px solid rgba(99, 102, 241, 0.2) !important;
        padding-top: 1.5rem !important;
        background: linear-gradient(180deg, transparent 0%, rgba(15, 23, 42, 0.8) 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* Sidebar başlık */
    [data-testid="stSidebar"] h2 {
        color: #f1f5f9;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    /* Info kutusu */
    .stAlert {
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
    }
    
    /* Warning kutusu */
    .stWarning {
        background: rgba(251, 191, 36, 0.1) !important;
        border: 1px solid rgba(251, 191, 36, 0.3) !important;
        border-radius: 12px !important;
    }
    
    /* Link buton */
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
    }
    
    /* Caption */
    .caption {
        text-align: center;
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 1rem;
    }
    
    /* Sidebar profil kartı */
    .profile-card {
        background: rgba(99, 102, 241, 0.1);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Görüntü container */
    .image-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. VERİ YÜKLEME ---
@st.cache_data
def load_data():
    try:
        with open('verilerim.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("HATA: 'verilerim.json' dosyası bulunamadı. Lütfen GitHub'a yüklediğinden emin ol.")
        return None

data = load_data()

# --- 3. API ANAHTARI KONTROLÜ ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.warning("API Anahtarı bulunamadı! Streamlit Secrets ayarlarını kontrol et.")
    st.stop()

# --- 4. YAN MENÜ ---
with st.sidebar:
    st.markdown('<div class="profile-card">', unsafe_allow_html=True)
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=120)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.header("🎯 Hakkında")
    st.info("Bu bot, Mustafa Cici'nin staj, proje ve teknik deneyimlerini cevaplayan yapay zeka asistanıdır.")
    
    st.markdown("---")
    
    st.markdown("**💻 Geliştirici**")
    st.markdown("Mustafa Cici")
    
    st.markdown("---")
    
    st.markdown('<p class="caption">© 2025 Mustafa Cici AI<br>Yapay Zeka Destekli Asistan</p>', unsafe_allow_html=True)

# --- 5. ANA EKRAN ---
st.title("🤖 Mustafa Cici Asistanı")

st.markdown("""
<div class="main-description">
    Merhaba! Ben Mustafa'nın dijital versiyonuyum. 🚀<br>
    CV'm, Tunus ve T7DGaming stajlarım veya geliştirdiğim projeler hakkında<br>
    bana dilediğini sorabilirsin.
</div>
""", unsafe_allow_html=True)

# --- 6. GEÇMİŞİ YÜKLE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 7. KULLANICI GİRDİSİ VE CEVAP ---
if prompt := st.chat_input("💬 Mustafa hakkında ne merak ediyorsun?"):
    
    # Kullanıcı mesajını göster
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Gemini Ayarları
        genai.configure(api_key=api_key)
        
        # --- MODEL SEÇİMİ ---
        model = genai.GenerativeModel('models/gemma-3-27b-it')

        # --- SİSTEM TALİMATLARI (PROMPT) - ÖRNEKLİ (FEW-SHOT) VERSİYON ---
        system_prompt = f"""
        You are the AI assistant of Mustafa Cici. You answer questions based on the provided Data Source.

        ### DATA SOURCE (JSON - Turkish):
        {json.dumps(data, ensure_ascii=False)}

        ### INSTRUCTIONS:
        1. **LANGUAGE MATCHING (MOST IMPORTANT):** - Identify the language of the "User Question".
           - You MUST answer in the EXACT SAME language as the "User Question".
           - The Data Source is in Turkish. If the user asks in English, you must **TRANSLATE** the facts into English.

        2. **UNKNOWNS:** - If the info is not in the JSON, say "[BILINMIYOR]" followed by a polite apology in the user's language.

        ### EXAMPLES (Follow this behavior strictly):

        User Question: "Mustafa hangi okulda okuyor?"
        Assistant Answer: "Mustafa Dumlupınar Üniversitesi'nde okumaktadır."

        User Question: "Where does Mustafa study?"
        Assistant Answer: "Mustafa studies at Dumlupınar University."

        User Question: "Staj deneyimi var mı?"
        Assistant Answer: "Evet, Tunus'ta bir oyun şirketinde staj yapmıştır."

        User Question: "Does he have internship experience?"
        Assistant Answer: "Yes, he completed an internship at a game company in Tunisia."

        ### REAL USER QUESTION:
        "{prompt}"

        ### YOUR ANSWER:
        """

        # CEVABI ÜRET VE İŞLE
        with st.chat_message("assistant"):
            with st.spinner("🔍 Mustafa'nın verileri taranıyor..."):
                response_obj = model.generate_content(system_prompt)
                full_response = response_obj.text
                
                # Senaryo A: Bilinmeyen Bilgi
                if "[BILINMIYOR]" in full_response:
                    clean_response = full_response.replace("[BILINMIYOR]", "")
                    st.write(clean_response)
                    
                    # Mail Linki
                    subject = "Botun Cevaplayamadığı Soru"
                    body = f"Merhaba Mustafa,\n\nBotuna şu soruyu sordum ve cevaplayamadı:\n\n'{prompt}'\n\nBunu eklemeyi düşünebilirsin."
                    mail_link = f"mailto:mustafa.cici12@hotmail.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                    
                    # Uyarı ve Buton
                    st.warning("⚠️ Bu bilgi veri tabanımda yok. Mustafa'ya iletmek ister misin?")
                    st.link_button("📧 Soruyu Mustafa'ya Mail At", mail_link)
                    
                    st.session_state.messages.append({"role": "assistant", "content": clean_response})

                # Senaryo B: Normal Cevap
                else:
                    st.write(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        # Hata Yönetimi
        st.error(f"❌ Bir hata oluştu. Lütfen sayfayı yenileyin. Hata detayı: {e}")
