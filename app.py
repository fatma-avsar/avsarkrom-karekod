import streamlit as st
import sqlite3
import os

# Sayfa ayarları
st.set_page_config(page_title="Avşar Krom Ürün Detayı", layout="centered")

# URL'den ürün kodunu alma (Örn: ?urun=TZG-001)
query_params = st.query_params
urun_kodu = query_params.get("urun", None)

def urun_getir(kod):
    conn = sqlite3.connect('avsarkrom.db')
    c = conn.cursor()
    c.execute("SELECT * FROM urunler WHERE urun_kodu=?", (kod,))
    veri = c.fetchone()
    conn.close()
    return veri

if urun_kodu:
    # Karekoddan gelen bir ürün kodu varsa veritabanında ara
    urun = urun_getir(urun_kodu)
    
    if urun:
        st.title(f"Avşar Krom - {urun[1]}") 
        st.subheader(f"Stok Kodu: {urun[0]}")
        
        st.divider() # Araya şık bir çizgi ekler
        
        # Ekranı ikiye bölüyoruz (Telefonda alt alta görünür)
        col1, col2 = st.columns(2)
        
        with col1:
            # Görsel klasörde var mı kontrol et
            if os.path.exists(urun[5]):
                st.image(urun[5], use_container_width=True)
            else:
                st.info("Bu ürün için görsel yüklenmemiş.")
            
        with col2:
            # Yazıları büyütmek için "###" (H3 Başlık) formatını kullanıyoruz
            st.markdown(f"### **Ölçüler:** {urun[2]}")
            st.markdown(f"### **Malzeme:** {urun[3]}")
            st.markdown(f"### **Teknik Detaylar:** {urun[6]}")
            
            st.write("") # Görsel ile fiyat arasına biraz boşluk
            
            # Fiyatı büyük ve dikkat çekici göster
            st.metric(label="Güncel Fiyat", value=f"{urun[4]:,.2f} ₺")
            
            # KDV uyarısı
            st.markdown("*(Fiyatlara KDV dahil değildir)*")
            
        st.divider()
        
        st.success("Bu ürün Avşar Krom tesislerinde üretilmiştir.")
    else:
        st.error("Ürün bulunamadı veya sistemden kaldırılmış.")
else:
    # Eğer linkte ürün kodu yoksa burası açılır
    st.title("Avşar Krom - Sistem Girişi")
    st.write("Lütfen ürün detaylarını görmek için bir ürün karekodu okutun.")
