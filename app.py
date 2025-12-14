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
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Ana tema renkleri - Daha soft ve modern */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #0ea5e9;
        --bg-primary: #0a0e1a;
        --bg-secondary: #151825;
        --bg-tertiary: #1f2333;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --border-color: rgba(99, 102, 241, 0.15);
    }
    
    /* Genel stil sıfırlama */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Genel arka plan - Daha yumuşak gradient */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, #1a1f35 100%);
        color: var(--text-primary);
    }
    
    /* Ana container padding */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
        max-width: 900px !important;
    }
    
    /* Başlık stili - Daha şık ve modern */
    h1 {
        background: linear-gradient(120deg, #a78bfa 0%, #6366f1 40%, #0ea5e9 80%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
    }
    
    /* Ana açıklama metni - Daha clean */
    .main-description {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.7;
        margin: 2rem auto 3rem;
        max-width: 650px;
        padding: 1.75rem 2rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(6, 182, 212, 0.05) 100%);
        border-radius: 20px;
        border: 1px solid var(--border-color);
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    /* Chat mesaj kutuları - Daha modern ve temiz */
    .stChatMessage {
        background: var(--bg-tertiary) !important;
        border-radius: 20px !important;
        border: 1px solid var(--border-color) !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    /* Kullanıcı mesajları - Gradient border efekti */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%) !important;
        border: 1px solid rgba(139, 92, 246, 0.25) !important;
    }
    
    /* Asistan mesajları */
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.06) 0%, rgba(99, 102, 241, 0.06) 100%) !important;
        border: 1px solid rgba(14, 165, 233, 0.2) !important;
    }
    
    /* Chat mesaj içerik */
    .stChatMessage p {
        font-size: 1rem;
        line-height: 1.7;
        color: var(--text-primary);
        margin: 0;
    }
    
    /* Input alanı - Daha temiz */
    .stChatInputContainer {
        border-top: 1px solid var(--border-color) !important;
        padding-top: 2rem !important;
        background: linear-gradient(180deg, transparent 0%, rgba(10, 14, 26, 0.9) 50%);
        backdrop-filter: blur(20px);
    }
    
    .stChatInput textarea {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px !important;
        color: var(--text-primary) !important;
        font-size: 1rem !important;
        padding: 1rem 1.25rem !important;
        transition: all 0.3s ease;
    }
    
    .stChatInput textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    
    /* Sidebar - Daha modern ve temiz */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] .block-container {
        padding-top: 2.5rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    
    /* Sidebar başlık */
    [data-testid="stSidebar"] h2 {
        color: var(--text-primary);
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 1.25rem;
        letter-spacing: -0.01em;
    }
    
    /* Info kutusu - Daha soft */
    .stAlert {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: 16px !important;
        color: var(--text-primary) !important;
        padding: 1rem 1.25rem !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    
    /* Warning kutusu */
    .stWarning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.08) 0%, rgba(245, 158, 11, 0.08) 100%) !important;
        border: 1px solid rgba(251, 191, 36, 0.3) !important;
        border-radius: 16px !important;
        padding: 1rem 1.25rem !important;
        font-size: 0.95rem !important;
    }
    
    /* Link buton - Daha modern ve smooth */
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.75rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3), 0 2px 8px rgba(139, 92, 246, 0.2) !important;
        letter-spacing: 0.01em !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4), 0 4px 12px rgba(139, 92, 246, 0.3) !important;
        background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 50%, #c4b5fd 100%) !important;
    }
    
    .stButton button:active {
        transform: translateY(-1px) scale(0.98) !important;
    }
    
    /* Spinner - Modern */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
        border-right-color: var(--secondary-color) !important;
    }
    
    /* Caption - Daha soft */
    .caption {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        line-height: 1.6;
        margin-top: 1.5rem;
        opacity: 0.8;
    }
    
    /* Sidebar profil kartı - Daha şık */
    .profile-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.08) 100%);
        padding: 2rem 1.5rem;
        border-radius: 24px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }
    
    .profile-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(99, 102, 241, 0.2);
    }
    
    /* Görüntü container - İyileştirilmiş */
    .image-container {
        display: flex;
        justify-content: center;
        margin-bottom: 0.5rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 50%;
        width: 140px;
        height: 140px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 0 0 40px rgba(99, 102, 241, 0.2);
    }
    
    .image-container img {
        border-radius: 50%;
        filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.3));
    }
    
    /* Sidebar markdown text */
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    [data-testid="stSidebar"] strong {
        color: var(--text-primary);
        font-weight: 600;
    }
    
    /* Horizontal rule - Daha subtle */
    [data-testid="stSidebar"] hr {
        border: none;
        height: 1px;
        background: var(--border-color);
        margin: 1.5rem 0;
    }
    
    /* Scrollbar - Modern */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.5);
    }
    
    /* Responsive düzenlemeler */
    @media (max-width: 768px) {
        h1 {
            font-size: 2.25rem !important;
        }
        
        .main-description {
            font-size: 0.95rem;
            padding: 1.5rem;
        }
        
        .stChatMessage {
            padding: 1.25rem !important;
        }
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
