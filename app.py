import streamlit as st
import sqlite3
import os
import urllib.parse
import pandas as pd

# 1. SAYFA YAPILANDIRMASI (KESİNLİKLE EN ÜSTTE OLMALI)
st.set_page_config(page_title="Avşar Krom Katalog", layout="wide", page_icon="⚙️")

# 2. APPLE TASARIM PRENSİPLERİ CSS ENJEKSİYONU
apple_css = """
<style>
    /* Tipografi - Optik boyutlandırma ve sistem fontları */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    h1, h2, h3 {
        letter-spacing: -0.02em !important;
        font-weight: 600 !important;
    }

    /* Butonlar - Anında tepki, yumuşak sınırlar ve metalik görünüm */
    .stButton > button {
        border-radius: 12px !important;
        transition: transform 100ms ease-out, box-shadow 200ms ease, background-color 200ms ease !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        font-weight: 500 !important;
        background-color: #F5F5F7 !important; 
        color: #1D1D1F !important;
    }
    
    /* Butona basıldığı an (Touch-down) fiziksel küçülme */
    .stButton > button:active {
        transform: scale(0.97) !important; 
        box-shadow: none !important;
        background-color: #E8E8ED !important;
    }
    
    /* Vurgulu Butonlar (Sepete Ekle, WhatsApp) */
    .stButton > button[kind="primary"] {
        background-color: #0071E3 !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:active {
        background-color: #005BB5 !important;
    }

    /* Üst Bar - Materyal ve Derinlik (Translucency) */
    header[data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
    }

    /* Resimler - Keskin hatları yumuşatma */
    img {
        border-radius: 12px;
    }
</style>
"""
st.markdown(apple_css, unsafe_allow_html=True)

# 3. VERİTABANI VE KLASÖR KURULUMU
DB_YOLU = 'avsarkrom.db'
GORSEL_KLASOR = 'gorseller'

if not os.path.exists(GORSEL_KLASOR):
    os.makedirs(GORSEL_KLASOR)

def db_baglan():
    conn = sqlite3.connect(DB_YOLU)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urunler (
            stok_kodu TEXT PRIMARY KEY,
            urun_adi TEXT,
            olculer TEXT,
            kalite TEXT,
            fiyat REAL
        )
    ''')
    conn.commit()
    return conn

# 4. SEPET SİSTEMİ
if 'sepet' not in st.session_state:
    st.session_state.sepet = []

def sepete_ekle(urun_adi, fiyat):
    st.session_state.sepet.append({'urun': urun_adi, 'fiyat': fiyat})
    st.toast(f"✅ {urun_adi} sepete eklendi!")

# 5. SAYFA YÖNLENDİRMELERİ (URL Parametreleri ile)
query_params = st.query_params

if "sayfa" in query_params and query_params["sayfa"] == "yonetim":
    # --- YÖNETİM PANELİ ---
    st.title("⚙️ Avşar Krom - Yönetim Paneli")
    sifre = st.text_input("Şifre Girin", type="password")
    
    if sifre == "avsarkrom2026": # Burayı kendi şifrenle değiştirebilirsin
        st.success("Giriş Başarılı!")
        st.subheader("Yeni Ürün Ekle")
        
        with st.form("urun_ekle_form"):
            stok_kodu = st.text_input("Stok Kodu (Örn: TZG-001)")
            urun_adi = st.text_input("Ürün Adı (Örn: Paslanmaz Çalışma Tezgahı)")
            olculer = st.text_input("Ölçüler (Örn: 190x60x85 cm)")
            kalite = st.selectbox("Malzeme Kalitesi", ["304 Kalite Paslanmaz", "430 Kalite Paslanmaz", "Galvaniz"])
            fiyat = st.number_input("Fiyat (₺)", min_value=0.0, step=100.0)
            gorsel = st.file_uploader("Ürün Görseli (Blender Render)", type=["jpg", "png", "jpeg"])
            
            ekle_btn = st.form_submit_button("Ürünü Kaydet", type="primary")
            
            if ekle_btn and stok_kodu:
                if gorsel:
                    gorsel_yolu = os.path.join(GORSEL_KLASOR, f"{stok_kodu}.png")
                    with open(gorsel_yolu, "wb") as f:
                        f.write(gorsel.getbuffer())
                
                conn = db_baglan()
                c = conn.cursor()
                c.execute("REPLACE INTO urunler (stok_kodu, urun_adi, olculer, kalite, fiyat) VALUES (?, ?, ?, ?, ?)",
                          (stok_kodu, urun_adi, olculer, kalite, fiyat))
                conn.commit()
                st.success(f"{urun_adi} başarıyla eklendi!")
    elif sifre:
        st.error("Hatalı Şifre!")

elif "urun" in query_params:
    # --- TEKİL ÜRÜN İNCELEME SAYFASI (QR Kod ile gelinen sayfa) ---
    stok_kodu = query_params["urun"]
    conn = db_baglan()
    urun = pd.read_sql_query(f"SELECT * FROM urunler WHERE stok_kodu='{stok_kodu}'", conn)
    
    if not urun.empty:
        u = urun.iloc[0]
        st.title(u['urun_adi'])
        
        col1, col2 = st.columns([1, 1])
        with col1:
            gorsel_yolu = os.path.join(GORSEL_KLASOR, f"{u['stok_kodu']}.png")
            if os.path.exists(gorsel_yolu):
                st.image(gorsel_yolu, use_container_width=True)
            else:
                st.info("Bu ürün için henüz görsel yüklenmedi.")
                
        with col2:
            st.markdown(f"**Stok Kodu:** {u['stok_kodu']}")
            st.markdown(f"**Ölçüler:** {u['olculer']}")
            st.markdown(f"**Malzeme:** {u['kalite']}")
            st.header(f"₺{u['fiyat']:,.2f}")
            
            st.button("Sepete Ekle", type="primary", on_click=sepete_ekle, args=(u['urun_adi'], u['fiyat']))
    else:
        st.warning("Ürün bulunamadı.")
        
else:
    # --- ANA KATALOG VE SEPET SAYFASI ---
    st.title("Avşar Krom - Endüstriyel Mutfak Ekipmanları")
    
    conn = db_baglan()
    urunler = pd.read_sql_query("SELECT * FROM urunler", conn)
    
    col_katalog, col_sepet = st.columns([2, 1])
    
    with col_katalog:
        if urunler.empty:
            st.info("Katalogda henüz ürün bulunmuyor. Yönetim panelinden ürün ekleyin.")
        else:
            for index, u in urunler.iterrows():
                with st.container():
                    c1, c2 = st.columns([1, 2])
                    gorsel_yolu = os.path.join(GORSEL_KLASOR, f"{u['stok_kodu']}.png")
                    with c1:
                        if os.path.exists(gorsel_yolu):
                            st.image(gorsel_yolu)
                    with c2:
                        st.subheader(u['urun_adi'])
                        st.write(f"Kalite: {u['kalite']} | Ölçü: {u['olculer']}")
                        st.write(f"**₺{u['fiyat']:,.2f}**")
                        st.button("Sepete Ekle", key=f"btn_{u['stok_kodu']}", on_click=sepete_ekle, args=(u['urun_adi'], u['fiyat']))
                    st.divider()

    with col_sepet:
        st.header("Sepetiniz")
        if not st.session_state.sepet:
            st.write("Sepetiniz şu an boş.")
        else:
            toplam = 0
            mesaj_icerigi = "Merhaba Avşar Krom, şu ürünler için sipariş vermek istiyorum:\n\n"
            for item in st.session_state.sepet:
                st.write(f"- {item['urun']} (₺{item['fiyat']})")
                toplam += item['fiyat']
                mesaj_icerigi += f"- {item['urun']}\n"
            
            st.write("---")
            st.subheader(f"Toplam: ₺{toplam:,.2f}")
            
            mesaj_icerigi += f"\nToplam Tutar: {toplam} TL"
            whatsapp_url = f"https://wa.me/905550000000?text={urllib.parse.quote(mesaj_icerigi)}" # Numaranı buraya gir
            
            st.link_button("📱 Siparişi WhatsApp'tan Gönder", whatsapp_url, type="primary")
            
            if st.button("Sepeti Temizle"):
                st.session_state.sepet = []
                st.rerun()
