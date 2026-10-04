import streamlit as st
import os

st.set_page_config(
    page_title="Dhaga & Co. CX Copilot | Executive Presentation Slides",
    page_icon="📽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to hide Streamlit UI chromes for an authentic presentation feeling
st.markdown("""
<style>
    /* Hide Streamlit header, footer, and minimize margins */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    #MainMenu {
        display: none !important;
    }
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
        height: 100vh !important;
        min-height: 920px !important;
    }
</style>
""", unsafe_allow_html=True)

# Load the dedicated standalone PowerPoint HTML slide deck
html_path = os.path.join(os.path.dirname(__file__), "..", "presentation", "index.html")

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        presentation_html = f.read()
    
    top_c1, top_c2 = st.columns([3, 7])
    with top_c1:
        st.page_link("app.py", label="← Return to Workbench & Live App", icon="🎧")
    with top_c2:
        st.caption("Press F5 or '▶ Start Slide Show' for fullscreen PowerPoint experience")
        
    st.components.v1.html(presentation_html, height=920, scrolling=False)
else:
    st.error("Presentation file not found at presentation/index.html")

