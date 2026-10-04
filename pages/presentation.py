import streamlit as st
import os

st.set_page_config(
    page_title="Dhaga & Co. | Executive Pitch Deck",
    page_icon="📽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load the dedicated standalone HTML slide deck
html_path = os.path.join(os.path.dirname(__file__), "..", "presentation", "index.html")

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        presentation_html = f.read()
    
    # Render with full-screen container styling
    st.components.v1.html(presentation_html, height=920, scrolling=False)
else:
    st.error("Presentation file not found at presentation/index.html")
