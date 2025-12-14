import streamlit as st
import json
import google.generativeai as genai
import urllib.parse
import time  # Geri sayım için gerekli kütüphane

# --- 1. SAYFA AYARLARI ---
st.set_page_config(
    page_title="Mustafa Cici AI",
    page_icon="🤖",
    layout="centered"
)

# --- 2. MODERN CSS TASARIMI ---
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Temel Değişkenler */
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --text-main: #f8fafc;
        --text-sub: #94a3b8;
    }
    
    /* Genel Stil */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #172554 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Başlık */
    h1 {
        background: linear-gradient(to right, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        text-align: center;
        padding-bottom: 1rem;
    }
    
    /* Sidebar Kartı */
    .profile-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    .profile-img {
        border-radius: 50%;
        border: 3px solid var(--primary);
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
        margin-bottom: 15px;
    }
    
    /* Chat Mesaj Kutuları */
    .stChatMessage {
        background-color: rgba(30, 41, 59, 0.6) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(148, 163, 184, 0.1) !important;
        padding: 15px !important;
    }
    
    /* Kullanıcı Mesajı */
    div[data-testid="user-message"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%) !important;
        border-left: 4px solid var(--primary) !important;
    }
    
    /* Asistan Mesajı */
    div[data-testid="assistant-message"] {
        background: rgba(30, 41, 59, 0.4) !important;
        border-left: 4px solid #10b981 !important;
    }

    /* Giriş Kutusu */
    .stChatInput textarea {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
    }
    
    /* Link Butonları */
    .stButton button, a[kind="primary"] {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        transition: transform 0.2s !important;
    }
    .stButton button:hover {
        transform: scale(1.02);
    }
    
    /* Sayaç Kutusu */
    .cooldown-box {
        border: 1px solid #f59e0b;
        background-color: rgba(245, 158, 11, 0.1);
        color: #fbbf24;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. VERİ YÜKLEME ---
@st.cache_data
def load_data():
    try:
        with open('verilerim.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ HATA: 'verilerim.json' dosyası bulunamadı.")
        return None

data = load_data()

# --- 4. API KONTROL ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.warning("⚠️ API Anahtarı bulunamadı! Secrets ayarlarını kontrol et.")
    st.stop()

# --- 5. YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.markdown("""
        <div class="profile-card">
            <img src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png" width="100" class="profile-img">
            <h3 style="margin:0; color:white;">Mustafa Cici</h3>
            <p style="color:#94a3b8; font-size:0.9em;">AI Digital Twin</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Hakkında")
    st.info("Bu asistan, Mustafa'nın CV'si, projeleri ve teknik yetkinlikleri hakkında soruları yanıtlamak için eğitilmiştir.")
    st.markdown("---")
    st.caption("© 2025 Mustafa Cici AI | v2.0")

# --- 6. ANA EKRAN ---
st.title("🤖 Mustafa Cici Asistanı")
st.markdown("""
    <div style="text-align: center; color: #94a3b8; margin-bottom: 30px;">
    Merhaba! Ben Mustafa'nın yapay zeka ikiziyim. <br>
    Eğitimim, stajlarım (Tunus, Dubai) veya projelerim hakkında bana istediğini sorabilirsin.
    </div>
""", unsafe_allow_html=True)

# --- 7. MESAJ GEÇMİŞİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 8. SOHBET MANTIĞI ---
if prompt := st.chat_input("💬 Bir soru sor..."):
    
    # Kullanıcı mesajını ekrana yaz
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemma-3-27b-it')

        # --- GÜÇLENDİRİLMİŞ PROMPT (TR/EN DESTEKLİ) ---
        system_prompt = f"""
        You are the AI assistant of Mustafa Cici.
        
        ### DATA SOURCE:
        The JSON below contains two keys: "tr" (Turkish) and "en" (English).
        {json.dumps(data, ensure_ascii=False)}

        ### INSTRUCTIONS:
        1. **DETECT LANGUAGE:** Identify the language of the User Question.
        2. **SELECT SOURCE:** - If English -> Use ONLY data under "en" key.
           - If Turkish -> Use ONLY data under "tr" key.
        3. **ANSWER:** Answer in the SAME language as the question.
        
        ### EXAMPLES:
        User (TR): "Mustafa nerede staj yaptı?"
        Assistant: "Mustafa, T7DGaming (Dubai) ve Tunus'ta bir oyun şirketinde staj yapmıştır."

        User (EN): "Where did Mustafa do his internship?"
        Assistant: "Mustafa interned at T7DGaming (Dubai) and a game company in Tunisia."

        ### REAL USER QUESTION:
        "{prompt}"
        
        ### YOUR ANSWER:
        """

        # CEVABI ÜRET
        with st.chat_message("assistant"):
            with st.spinner("🔍 Analiz ediliyor..."):
                response_obj = model.generate_content(system_prompt)
                full_response = response_obj.text
                
                # Bilinmeyen Bilgi Kontrolü
                if "[BILINMIYOR]" in full_response or "[UNKNOWN]" in full_response:
                    clean_response = full_response.replace("[BILINMIYOR]", "").replace("[UNKNOWN]", "")
                    st.write(clean_response)
                    
                    # Mail Gönderme Butonu
                    subject = "Botun Cevaplayamadığı Soru"
                    body = f"Soru: {prompt}"
                    mail_link = f"mailto:mustafa.cici12@hotmail.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                    
                    st.warning("⚠️ Bu detay verilerimde yok.")
                    st.markdown(f'<a href="{mail_link}" target="_blank" style="text-decoration:none;"><button style="background:linear-gradient(90deg, #4f46e5, #7c3aed); color:white; border:none; padding:8px 16px; border-radius:8px; cursor:pointer;">📧 Mustafa\'ya Mail At</button></a>', unsafe_allow_html=True)
                    
                    st.session_state.messages.append({"role": "assistant", "content": clean_response})
                else:
                    st.write(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # --- HATA YÖNETİMİ VE GERİ SAYIM (RATE LIMIT) ---
    except Exception as e:
        error_msg = str(e)
        # 429 Hatası veya Resource Exhausted kontrolü
        if "429" in error_msg or "ResourceExhausted" in error_msg:
            with st.chat_message("assistant"):
                st.error("🚦 **Hız Sınırına Takıldık (Rate Limit Reached)**")
                st.write("Çok hızlı soru sorduğun için model kısa bir mola verdi. Lütfen bekle...")
                
                # Geri Sayım Sayacı
                countdown_placeholder = st.empty()
                for i in range(90, 0, -1):
                    countdown_placeholder.markdown(f"""
                        <div class="cooldown-box">
                            ⏳ {i} saniye sonra tekrar sorabilirsin...
                        </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)
                
                countdown_placeholder.success("✅ **Sistem Hazır!** Lütfen sorunu tekrar gönder.")
        
        else:
            st.error(f"❌ Bir hata oluştu: {e}")
