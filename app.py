import streamlit as st
import sqlite3
import os
import urllib.parse

st.set_page_config(page_title="Avşar Krom Sistemi", layout="centered")

# --- VERİTABANI BAĞLANTISI ---
def urun_getir(kod):
    conn = sqlite3.connect('avsarkrom.db')
    c = conn.cursor()
    c.execute("SELECT * FROM urunler WHERE urun_kodu=?", (kod,))
    veri = c.fetchone()
    conn.close()
    return veri

# --- URL KONTROLLERİ (Hangi sayfadayız?) ---
query_params = st.query_params
sayfa = query_params.get("sayfa", None)
urun_kodu = query_params.get("urun", None)

# ==========================================
# 1. YÖNETİCİ PANELİ SAYFASI (GİZLİ SAYFA)
# ==========================================
if sayfa == "yonetim":
    st.title("🛠️ Avşar Krom - Yönetim Paneli")
    st.write("Bu alan sadece yetkili personel içindir.")
    
    sifre = st.text_input("Yönetici Şifresi", type="password")
    
    if sifre == "avsar2026":
        st.success("Giriş Başarılı!")
        st.subheader("Yeni Ürün Ekle veya Güncelle")
        
        with st.form("urun_formu"):
            yeni_kod = st.text_input("Stok Kodu (Örn: DVL-OT-001)")
            yeni_kategori = st.text_input("Kategori (Örn: Orta Tip Davlumbaz)")
            yeni_olculer = st.text_input("Ölçüler (Örn: 200x90x50 cm)")
            yeni_malzeme = st.text_input("Malzeme (Örn: 304 Kalite Paslanmaz Çelik)")
            yeni_fiyat = st.number_input("Fiyat (₺)", min_value=0.0, format="%.2f")
            yeni_gorsel = st.text_input("Görsel Yolu (Örn: gorseller/davlumbaz.png)")
            yeni_detay = st.text_area("Teknik Detaylar")
            
            # Stok Kontrol Alanı
            yeni_stok = st.number_input("Stok Miktarı (Adet)", min_value=0, step=1, help="0 girerseniz ürün 'Yeni İmalat' olarak görünür.")
            
            if st.form_submit_button("Ürünü Kaydet / Güncelle"):
                if yeni_kod:
                    conn = sqlite3.connect('avsarkrom.db')
                    c = conn.cursor()
                    c.execute('''
                        INSERT OR REPLACE INTO urunler 
                        (urun_kodu, kategori, olculer, malzeme, fiyat, gorsel_yolu, teknik_detay, stok_miktari) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (yeni_kod, yeni_kategori, yeni_olculer, yeni_malzeme, yeni_fiyat, yeni_gorsel, yeni_detay, yeni_stok))
                    conn.commit()
                    conn.close()
                    st.success(f"{yeni_kod} kodlu ürün veritabanına kaydedildi! (Stok: {yeni_stok})")
                else:
                    st.error("Stok Kodu boş bırakılamaz!")

# ==========================================
# 2. MÜŞTERİ / KAREKOD SAYFASI
# ==========================================
else:
    # Sepet (Hafıza) Sistemi
    if 'sepet' not in st.session_state:
        st.session_state.sepet = []

    def sepete_ekle(kodu, adi, fiyat, stok_durumu):
        st.session_state.sepet.append({'kodu': kodu, 'adi': adi, 'fiyat': fiyat, 'durum': stok_durumu})
        st.success(f"✅ {adi} teklif sepetinize eklendi!")

    def sepeti_temizle():
        st.session_state.sepet = []

    # Ürün Gösterimi
    if urun_kodu:
        urun = urun_getir(urun_kodu)
        
        if urun:
            st.title(f"Avşar Krom - {urun[1]}") 
            st.subheader(f"Stok Kodu: {urun[0]}")
            
            # Stok durumu yakalama
            try:
                stok_adedi = int(urun[7]) if urun[7] is not None else 0
            except IndexError:
                stok_adedi = 0
                
            if stok_adedi > 0:
                st.success(f"📦 **Stokta Hazır** (Hemen Teslim)")
                stok_durum_metni = "Stoktan Teslim"
            else:
                st.warning("⚙️ **Yeni İmalat** (Sipariş Üzerine Üretilir)")
                stok_durum_metni = "Yeni İmalat"
                
            st.divider() 
            
            col1, col2 = st.columns(2)
            
            with col1:
                if os.path.exists(urun[5]):
                    st.image(urun[5], use_container_width=True)
                else:
                    st.info("Bu ürün için görsel yüklenmemiş.")
                
            with col2:
                st.markdown(f"### **Ölçüler:** {urun[2]}")
                st.markdown(f"### **Malzeme:** {urun[3]}")
                st.markdown(f"### **Teknik Detaylar:** {urun[6]}")
                
                st.write("") 
                st.metric(label="Güncel Fiyat", value=f"{urun[4]:,.2f} ₺")
                st.markdown("*(Fiyatlara KDV dahil değildir)*")
                
                st.write("")
                if st.button("🛒 Bu Ürünü Teklif Sepetime Ekle", use_container_width=True):
                    sepete_ekle(urun[0], urun[1], urun[4], stok_durum_metni)
                    st.rerun()
                    
            st.divider()
            st.success("Bu ürün Avşar Krom tesislerinde üretilmiştir.")
        else:
            st.error("Ürün bulunamadı veya sistemden kaldırılmış.")
    else:
        st.title("Avşar Krom - Sistem Girişi")
        st.write("Lütfen ürün detaylarını görmek için bir ürün karekodu okutun.")

    # --- DİNAMİK TEKLİF SEPETİ VE WHATSAPP GÖNDERİMİ ---
    if len(st.session_state.sepet) > 0:
        st.markdown("---")
        st.header("🛒 Teklif Sepetiniz")
        
        ara_toplam = 0
        mesaj_metni = "Merhaba Avşar Krom, aşağıdaki ürünler için sipariş/teklif detaylarını görüşmek istiyorum:\n\n"
        
        for i, item in enumerate(st.session_state.sepet):
            st.markdown(f"**{i+1}. {item['kodu']}** - {item['adi']} | *{item['durum']}* | **{item['fiyat']:,.2f} ₺**")
            ara_toplam += item['fiyat']
            mesaj_metni += f"- {item['kodu']} {item['adi']} ({item['durum']})\n"
            
        kdv = ara_toplam * 0.20
        genel_toplam = ara_toplam + kdv
        
        mesaj_metni += f"\nAra Toplam: {ara_toplam:,.2f} TL"
        mesaj_metni += f"\nKDV (%20): {kdv:,.2f} TL"
        mesaj_metni += f"\nGenel Toplam: {genel_toplam:,.2f} TL"
        
        st.markdown("---")
        st.write(f"**Ara Toplam:** {ara_toplam:,.2f} ₺")
        st.write(f"**KDV (%20):** {kdv:,.2f} ₺")
        st.subheader(f"Genel Toplam: {genel_toplam:,.2f} ₺")
        
        telefon = "905323333806"
        url_mesaj = urllib.parse.quote(mesaj_metni)
        whatsapp_url = f"https://wa.me/{telefon}?text={url_mesaj}"
        
        st.write("")
        st.markdown(f'''
            <a href="{whatsapp_url}" target="_blank" style="display: block; width: 100%; padding: 15px; background-color: #25D366; color: white; text-align: center; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 8px;">
                📲 Sepeti WhatsApp ile Avşar Krom'a Gönder
            </a>
        ''', unsafe_allow_html=True)
        
        st.write("")
        if st.button("🗑️ Sepeti Temizle"):
            sepeti_temizle()
            st.rerun()
