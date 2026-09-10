import streamlit as st

# Sayfa yapılandırman (zaten varsa altına ekle)
# st.set_page_config(page_title="Avşar Krom Katalog", layout="wide")

# Apple Tasarım Prensipleri CSS Enjeksiyonu
apple_css = """
<style>
    /* Tipografi - Optik boyutlandırma ve sistem fontları */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    h1, h2, h3 {
        letter-spacing: -0.02em !important; /* Büyük metinlerde negatif tracking */
        font-weight: 600 !important;
    }

    /* Butonlar - Anında tepki (Response) ve yumuşak sınırlar */
    .stButton > button {
        border-radius: 12px !important;
        transition: transform 100ms ease-out, box-shadow 200ms ease, background-color 200ms ease !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        font-weight: 500 !important;
    }
    
    /* Butona basıldığı an (Touch-down) fiziksel küçülme hissi */
    .stButton > button:active {
        transform: scale(0.97) !important; 
        box-shadow: none !important;
    }

    /* Üst Bar - Materyal ve Derinlik (Translucency) */
    header[data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
    }

    /* Kartlar ve Konteynerler - Yumuşak köşeler ve hafif derinlik */
    div[data-testid="stVerticalBlock"] > div.element-container {
        border-radius: 16px;
    }
    
    /* Resimler - Keskin hatları yumuşatma */
    img {
        border-radius: 12px;
    }
</style>
"""

st.markdown(apple_css, unsafe_allow_html=True)
