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
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=100)
    st.header("Hakkında")
    st.info("Bu bot, Mustafa Cici'nin staj, proje ve teknik deneyimlerini cevaplayan yapay zeka asistanıdır.")
    st.write("💻 **Geliştirici:** Mustafa Cici")
    st.caption("© 2025 Mustafa Cici AI")

# --- 5. ANA EKRAN ---
st.title("🤖 Mustafa Cici Asistanı")
st.write("Merhaba! Ben Mustafa'nın dijital versiyonuyum. CV'm, Tunus ve T7DGaming stajlarım veya geliştirdiğim projeler hakkında bana dilediğini sorabilirsin.")

# --- 6. GEÇMİŞİ YÜKLE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 7. KULLANICI GİRDİSİ VE CEVAP ---
if prompt := st.chat_input("Mustafa hakkında ne merak ediyorsun?"):
    
    # Kullanıcı mesajını göster
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Gemini Ayarları
        genai.configure(api_key=api_key)
        

        model = genai.GenerativeModel('gemini-1.5-flash')

        # SİSTEM TALİMATLARI (PROMPT)
        system_prompt = f"""
        ROLE: You are the professional, friendly, and helpful digital assistant of Mustafa Cici.
        
        DATA SOURCE (JSON):
        {json.dumps(data, ensure_ascii=False)}

        INSTRUCTIONS:
        1. **LANGUAGE DETECTION:** - If the user asks in **English**, answer in **English**.
           - If the user asks in **Turkish**, answer in **Turkish**.

        2. **PIVOT RULE (CRITICAL FOR INTERVIEWS):**
           - If the user asks about a technology/tool/language NOT in the JSON (e.g., React, AWS, Go):
           - **NEVER** say "He doesn't know" or "No information".
           - **INSTEAD:** Explicitly state that he doesn't actively use that specific tool, BUT immediately highlight his strength in a relevant field from the JSON.
           - *Example (TR):* "Mustafa React kullanmıyor ancak mobil uygulama geliştirme alanında Flutter ile ileri seviye projeler geliştiriyor."
           - *Example (EN):* "Mustafa doesn't currently use React, but he specializes in Flutter for cross-platform mobile development."

        3. **HANDLING TRULY UNKNOWN INFO:**
           - For non-technical, personal, or irrelevant questions (e.g., "Favorite food", "Politics") NOT in the JSON:
           - Start your response with exactly: "[BILINMIYOR]"
           - Then write a polite apology message.
        
        4. **TONE:** - Speak in the third person ("Mustafa did this...").
           - Be concise and professional.
           - Do NOT output JSON format.

        User Question: {prompt}
        """

        # CEVABI ÜRET VE İŞLE
        with st.chat_message("assistant"):
            with st.spinner("Mustafa'nın verileri taranıyor..."):
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
                    st.warning("Bu bilgi veri tabanımda yok. Mustafa'ya iletmek ister misin?")
                    st.link_button("📧 Soruyu Mustafa'ya Mail At", mail_link)
                    
                    st.session_state.messages.append({"role": "assistant", "content": clean_response})

                # Senaryo B: Normal Cevap
                else:
                    st.write(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        # Hata Yönetimi
        st.error(f"Bir hata oluştu. Lütfen sayfayı yenileyin. Hata detayı: {e}")

