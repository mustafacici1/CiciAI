import streamlit as st
import json
import google.generativeai as genai
import urllib.parse

# --- 1. SAYFA AYARLARI ---
st.set_page_config(
    page_title="Cici AI",
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
    
    /* Animasyonlu arka plan */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Genel arka plan - Animasyonlu gradient */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e293b, #312e81, #1e3a8a, #0f172a);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        position: relative;
        overflow: hidden;
    }
    
    /* Parlayan noktalar arka plan efekti */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(6, 182, 212, 0.1) 0%, transparent 50%);
        pointer-events: none;
        animation: pulse 8s ease-in-out infinite;
    }
    
    /* Başlık stili - Animasyonlu */
    h1 {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
        animation: gradientShift 3s ease infinite, float 3s ease-in-out infinite;
        letter-spacing: 2px;
        text-shadow: 0 0 30px rgba(99, 102, 241, 0.5);
    }
    
    /* Ana açıklama metni - Animasyonlu */
    .main-description {
        text-align: center;
        color: #cbd5e1;
        font-size: 1.1rem;
        line-height: 1.8;
        margin: 1.5rem auto;
        max-width: 650px;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
        animation: slideIn 0.8s ease-out;
        transition: all 0.3s ease;
    }
    
    .main-description:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.3);
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    /* Chat mesaj kutuları - Gelişmiş animasyonlar */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        animation: slideIn 0.5s ease-out;
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        transform: translateX(5px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.3);
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
    
    /* Sidebar - Gelişmiş arka plan */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.3);
        backdrop-filter: blur(10px);
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
    
    /* Link buton - Gelişmiş animasyon */
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.8rem !important;
        font-weight: 600 !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
        position: relative;
        overflow: hidden;
    }
    
    .stButton button::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton button:hover::before {
        left: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.6) !important;
    }
    
    .stButton button:active {
        transform: translateY(-1px) scale(1.02) !important;
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
    
    /* Sidebar profil kartı - Gelişmiş */
    .profile-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15));
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(99, 102, 241, 0.4);
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .profile-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.3);
    }
    
    /* Görüntü container - Animasyonlu */
    .image-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .image-container img {
        animation: float 4s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.5));
        transition: all 0.3s ease;
    }
    
    .image-container img:hover {
        transform: scale(1.1) rotate(5deg);
        filter: drop-shadow(0 0 30px rgba(139, 92, 246, 0.8));
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
    
    st.markdown('<p class="caption">© 2025 Cici AI<br>Yapay Zeka Destekli Asistan ✨</p>', unsafe_allow_html=True)

# --- 5. ANA EKRAN ---
st.title("🤖 Cici AI")

st.markdown("""
<div class="main-description">
    ✨ <strong>Merhaba! Ben Cici AI</strong> ✨<br>
    Mustafa'nın dijital versiyonuyum. 🚀<br><br>
    CV'si, Tunus ve T7DGaming stajları veya geliştirdiği projeler hakkında<br>
    bana dilediğini sorabilirsin!
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
