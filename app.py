import streamlit as st
import sqlite3
import os
import urllib.parse

# Sayfa ayarları - Daha ferah görünüm için genişlik ayarları
st.set_page_config(page_title="Avşar Krom Sistemi", layout="centered", initial_sidebar_state="collapsed")

# --- VERİTABANI BAĞLANTISI ---
def urun_getir(kod):
    conn = sqlite3.connect('avsarkrom.db')
    c = conn.cursor()
    c.execute("SELECT * FROM urunler WHERE urun_kodu=?", (kod,))
    veri = c.fetchone()
    conn.close()
    return veri

# --- URL KONTROLLERİ ---
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
        st.toast(f"✅ {adi} sepetinize eklendi!", icon="🛒") # Yukarıda şık bir bildirim çıkar

    def sepeti_temizle():
        st.session_state.sepet = []

    if urun_kodu:
        urun = urun_getir(urun_kodu)
        
        if urun:
            # Üst Başlık Kısmı - Ortalanmış ve şık
            st.markdown(f"<h1 style='text-align: center;'>{urun[1]}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: gray; font-size: 18px;'>Stok Kodu: {urun[0]}</p>", unsafe_allow_html=True)
            
            # Stok durumu yakalama
            try:
                stok_adedi = int(urun[7]) if urun[7] is not None else 0
            except IndexError:
                stok_adedi = 0
                
            stok_durum_metni = "Stoktan Teslim" if stok_adedi > 0 else "Yeni İmalat"
            
            st.write("") # Boşluk
            
            # Sütunları bölme - Fotoğraf kısmı biraz daha geniş (1.3) ve aralarında geniş boşluk (gap="large") var
            col1, col2 = st.columns([1.3, 1], gap="large")
            
            with col1:
                # Görsel Kutusu
                with st.container(border=True):
                    if os.path.exists(urun[5]):
                        st.image(urun[5], use_container_width=True)
                    else:
                        st.info("Bu ürün için görsel yüklenmemiş.")
                
                if stok_adedi > 0:
                    st.success("📦 **Stok Durumu:** Hazır (Hemen Teslim)")
                else:
                    st.warning("⚙️ **Stok Durumu:** Sipariş Üzerine Üretilir")
                    
            with col2:
                # Teknik Detaylar Kutusu
                with st.container(border=True):
                    st.markdown("#### Teknik Özellikler")
                    st.markdown(f"**📏 Ölçüler:** {urun[2]}")
                    st.markdown(f"**🧱 Malzeme:** {urun[3]}")
                    st.markdown(f"**📋 Detaylar:** {urun[6]}")
                
                # Fiyat ve Sepet Kutusu
                with st.container(border=True):
                    st.metric(label="Güncel Fiyat", value=f"{urun[4]:,.2f} ₺")
                    st.caption("*(Fiyatlara %20 KDV dahil değildir)*")
                    
                    st.write("")
                    # type="primary" butonu daha belirgin yapar
                    if st.button("🛒 Teklif Sepetime Ekle", use_container_width=True, type="primary"):
                        sepete_ekle(urun[0], urun[1], urun[4], stok_durum_metni)
                        
            st.write("")
            st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'><i>Bu ürün Avşar Krom tesislerinde yüksek kalite standartlarında üretilmiştir.</i></p>", unsafe_allow_html=True)
            
        else:
            st.error("Ürün bulunamadı veya sistemden kaldırılmış.")
    else:
        st.title("Avşar Krom - Sistem Girişi")
        st.write("Lütfen ürün detaylarını görmek için bir ürün karekodu okutun.")

    # --- DİNAMİK TEKLİF SEPETİ VE WHATSAPP GÖNDERİMİ ---
    if len(st.session_state.sepet) > 0:
        st.write("")
        st.write("")
        
        # Sepeti şık bir kutu içine alıyoruz
        with st.container(border=True):
            st.header("🛒 Teklif Sepetiniz")
            st.write("Seçtiğiniz ürünler aşağıda listelenmiştir.")
            st.divider()
            
            ara_toplam = 0
            mesaj_metni = "Merhaba Avşar Krom, aşağıdaki ürünler için sipariş/teklif detaylarını görüşmek istiyorum:\n\n"
            
            for i, item in enumerate(st.session_state.sepet):
                st.markdown(f"**{i+1}. {item['kodu']}** - {item['adi']} ({item['durum']})")
                st.markdown(f"<div style='text-align: right;'><b>{item['fiyat']:,.2f} ₺</b></div>", unsafe_allow_html=True)
                st.write("")
                ara_toplam += item['fiyat']
                mesaj_metni += f"- {item['kodu']} {item['adi']} ({item['durum']})\n"
                
            kdv = ara_toplam * 0.20
            genel_toplam = ara_toplam + kdv
            
            mesaj_metni += f"\nAra Toplam: {ara_toplam:,.2f} TL"
            mesaj_metni += f"\nKDV (%20): {kdv:,.2f} TL"
            mesaj_metni += f"\nGenel Toplam: {genel_toplam:,.2f} TL"
            
            st.divider()
            
            col_toplam1, col_toplam2 = st.columns(2)
            with col_toplam1:
                st.write(f"Ara Toplam:")
                st.write(f"KDV (%20):")
                st.subheader(f"Genel Toplam:")
            with col_toplam2:
                st.markdown(f"<div style='text-align: right;'>{ara_toplam:,.2f} ₺</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>{kdv:,.2f} ₺</div>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align: right;'>{genel_toplam:,.2f} ₺</h3>", unsafe_allow_html=True)
            
            telefon = "905323333806"
            url_mesaj = urllib.parse.quote(mesaj_metni)
            whatsapp_url = f"https://wa.me/{telefon}?text={url_mesaj}"
            
            st.write("")
            st.markdown(f'''
                <a href="{whatsapp_url}" target="_blank" style="display: block; width: 100%; padding: 15px; background-color: #25D366; color: white; text-align: center; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 8px; margin-bottom: 10px;">
                    📲 WhatsApp'tan Teklif İste
                </a>
            ''', unsafe_allow_html=True)
            
            if st.button("🗑️ Sepeti Temizle", use_container_width=True):
                sepeti_temizle()
                st.rerun()
