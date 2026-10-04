import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

import database
import pipeline
from schemas import IntentEnum, PolicyVerdictEnum

# ==============================================================================
# PAGE CONFIGURATION & ENTERPRISE STYLING
# ==============================================================================
st.set_page_config(
    page_title="Dhaga & Co. | CX Copilot & Autonomous Triage",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Background and Canvas */
    .stApp {
        background-color: #0B0F19;
        color: #F3F4F6;
    }
    
    /* CRITICAL VISIBILITY FIXES FOR DARK THEME BUTTONS */
    .stButton > button {
        background-color: #131E30 !important;
        color: #F1F5F9 !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 16px !important;
        font-size: 0.88rem !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
        white-space: pre-wrap !important;
        height: auto !important;
        line-height: 1.45 !important;
    }
    .stButton > button:hover {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border-color: #38BDF8 !important;
        box-shadow: 0 4px 14px rgba(56, 189, 248, 0.25) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1E40AF 0%, #2563EB 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #60A5FA !important;
        font-weight: 700 !important;
        box-shadow: 0 0 16px rgba(37, 99, 235, 0.5) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E3A8A 100%) !important;
        color: #FFFFFF !important;
    }

    /* CRITICAL CONTRAST FIX FOR FORM FIELDS & DISABLED TEXTAREAS (Delivered message) */
    .stTextArea textarea {
        background-color: #111827 !important;
        color: #F9FAFB !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        font-size: 0.92rem !important;
        line-height: 1.5 !important;
    }
    .stTextArea textarea:focus {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 0 1px #38BDF8 !important;
    }
    .stTextArea textarea:disabled,
    .stTextArea textarea[disabled],
    div[data-baseweb="textarea"] textarea:disabled {
        background-color: #141E2F !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        opacity: 1 !important;
        border: 1.5px solid #38BDF8 !important;
        font-weight: 600 !important;
        font-size: 0.94rem !important;
        line-height: 1.55 !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.2) !important;
        cursor: text !important;
    }
    .stTextInput input {
        background-color: #111827 !important;
        color: #F9FAFB !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] {
        background-color: #111827 !important;
        color: #FFFFFF !important;
    }

    /* Metrics Ribbon */
    .metric-card {
        background: linear-gradient(135deg, rgba(31, 41, 55, 0.7) 0%, rgba(17, 24, 39, 0.9) 100%);
        border: 1px solid rgba(75, 85, 99, 0.4);
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        margin-bottom: 12px;
    }
    .metric-title {
        color: #9CA3AF;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .metric-subtitle {
        font-size: 0.72rem;
        font-weight: 500;
        margin-top: 4px;
    }
    
    /* Presentation Slide Card */
    .pitch-card {
        background: linear-gradient(135deg, #111827 0%, #1F2937 100%);
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 24px 28px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .pitch-tag {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        color: #818CF8;
        border: 1px solid rgba(99, 102, 241, 0.4);
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    .pitch-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 12px;
        line-height: 1.3;
    }
    .pitch-lead {
        font-size: 1.05rem;
        color: #D1D5DB;
        line-height: 1.6;
        margin-bottom: 18px;
    }
    .pitch-stat-box {
        background: rgba(17, 24, 39, 0.8);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .pitch-stat-num {
        font-size: 1.8rem;
        font-weight: 800;
        color: #60A5FA;
    }
    .pitch-stat-lbl {
        font-size: 0.78rem;
        color: #9CA3AF;
        text-transform: uppercase;
        font-weight: 600;
        margin-top: 4px;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .badge-auto {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-review {
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-escalate {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge-resolved {
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .badge-cod {
        background: rgba(168, 85, 247, 0.15);
        color: #C084FC;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }
    .badge-prepaid {
        background: rgba(59, 130, 246, 0.15);
        color: #93C5FD;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    /* Policy Breakdown Table Card */
    .policy-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .policy-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #1F2937;
        font-size: 0.82rem;
    }
    .policy-label {
        color: #9CA3AF;
        font-weight: 500;
    }
    .policy-val {
        color: #F3F4F6;
        font-weight: 600;
    }
    
    /* WhatsApp Simulator Phone Frame */
    .phone-container {
        max-width: 420px;
        margin: 0 auto;
        background: #0B141A;
        border-radius: 28px;
        border: 8px solid #2A3942;
        overflow: hidden;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
    }
    .wa-header {
        background: #1F2C34;
        padding: 14px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 1px solid #2A3942;
    }
    .wa-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #10B981;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #0B141A;
    }
    .wa-chat-area {
        height: 480px;
        padding: 16px;
        overflow-y: auto;
        background-color: #0B141A;
        background-image: radial-gradient(#1F2C34 1px, transparent 1px);
        background-size: 16px 16px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .wa-bubble {
        max-width: 84%;
        padding: 10px 14px;
        border-radius: 12px;
        font-size: 0.85rem;
        line-height: 1.4;
        position: relative;
    }
    .wa-incoming {
        align-self: flex-start;
        background: #202C33;
        color: #E9EDEF;
        border-top-left-radius: 2px;
    }
    .wa-outgoing {
        align-self: flex-end;
        background: #005C4B;
        color: #E9EDEF;
        border-top-right-radius: 2px;
    }
    .wa-time {
        font-size: 0.65rem;
        color: #8696A0;
        text-align: right;
        margin-top: 4px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Ensure database is seeded
database.init_db()
if not os.path.exists(database.DB_PATH) or os.path.getsize(database.DB_PATH) < 1000:
    database.seed_demo_data()

# Check if audit table is empty, if so, run batch triage once
conn = database.get_connection()
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM ticket_triage_audit")
audit_count = c.fetchone()[0]
conn.close()
if audit_count == 0:
    pipeline.run_batch_triage()

# ==============================================================================
# VIEW ROUTING & PRESENTATION FULLSCREEN HANDLING
# ==============================================================================
# Automatic view routing based on query params or URL
requested_view = st.query_params.get("view") or st.query_params.get("page")
if requested_view in ["presentation", "deck", "pitch"]:
    st.session_state["user_role_choice"] = "📽️ Executive Pitch & Presentation Deck"
    st.session_state["deck_fullscreen"] = True

# Client-side detection: If browser pathname contains 'presentation', sync query param
st.markdown("""
<script>
    if (window.location.pathname.indexOf('presentation') !== -1 && window.location.search.indexOf('view=presentation') === -1) {
        const u = new URL(window.location);
        u.searchParams.set('view', 'presentation');
        window.location.replace(u.toString());
    }
</script>
""", unsafe_allow_html=True)

# If in fullscreen presentation deck mode, hide sidebar & headers for complete immersion
if st.session_state.get("deck_fullscreen"):
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .main .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 1rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR CONTROLS & DYNAMIC ROLE SWITCHER
# ==============================================================================
with st.sidebar:
    st.markdown("### 🧵 Dhaga & Co. CX")
    st.caption("FDE Mini Project 1 · Pattern-Based Workflow")
    st.divider()

    st.markdown("**Select Operating Persona:**")
    role_options = [
        "🎧 Frontline Support Agent",
        "📊 Arpita (Head of CX)",
        "🛡️ Dev (CTO / Tech Lead)",
        "📽️ Executive Pitch & Presentation Deck"
    ]
    
    # Check default in session state
    if "user_role_choice" not in st.session_state:
        st.session_state["user_role_choice"] = role_options[0]

    user_role = st.selectbox(
        "Operating As:",
        role_options,
        index=role_options.index(st.session_state["user_role_choice"]),
        help="Switches dashboard perspective and relevant operational views. Each role sees only their required tabs."
    )
    st.session_state["user_role_choice"] = user_role

    show_all_tabs = st.checkbox(
        "🔓 Show All Tabs (All-Access Master View)",
        value=False,
        help="Check this to reveal all tabs simultaneously for comprehensive mentor Q&A."
    )

    st.divider()
    st.markdown("**LLM Engine Status:**")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        st.success("🟢 Google Gemini API Active")
        st.caption("Routing & Drafting: `gemini-2.5-flash`\nEvaluator: `gemini-2.5-pro`")
    else:
        st.info("🔵 High-Fidelity Local Engine Active")
        st.caption("Deterministic parsing & simulated reasoning running with zero external latency.")

    user_api_key = st.text_input("Gemini API Key (Optional):", type="password", help="If provided, live Google Gemini API models are called.")
    if user_api_key:
        os.environ["GEMINI_API_KEY"] = user_api_key
        st.toast("API Key updated!", icon="🔑")

    st.divider()
    st.markdown("**Presentation & Demo Controls:**")
    
    if st.button("📽️ Launch Presentation Mode", use_container_width=True, type="primary"):
        st.session_state["user_role_choice"] = "📽️ Executive Pitch & Presentation Deck"
        st.session_state["deck_fullscreen"] = True
        st.rerun()

    if st.button("⚠️ Trigger Intentional Failure Demo", use_container_width=True, help="Loads Ticket TCK-1007 (Ambiguous Order without ID)"):
        st.session_state["selected_ticket_id"] = "TCK-1007"
        st.rerun()

    if st.button("🔄 Reset & Re-Seed Database", use_container_width=True):
        database.seed_demo_data(force=True)
        pipeline.run_batch_triage()
        st.rerun()

    st.caption("Dhaga & Co. Operational Context:\n• 9,000 tickets/week\n• 58% WISMO (~5,220/wk)\n• 9 hr baseline FRT\n• 34 Freshdesk Agents\n• 61% Cash on Delivery")

# ==============================================================================
# HEADER BANNER & DYNAMIC METRICS BY ROLE
# ==============================================================================
tickets = database.get_all_tickets_view()
total_tickets = len(tickets)
auto_dispatched = sum(1 for t in tickets if t.get('dispatch_mode') == 'AUTO_DISPATCH' or t.get('ticket_status') == 'AUTO_RESOLVED')
pending_review = sum(1 for t in tickets if t.get('ticket_status') == 'PENDING_AGENT_REVIEW')
escalated = sum(1 for t in tickets if t.get('ticket_status') == 'ESCALATED')
total_cost_inr = sum(float(t.get('cost_inr') or 0.0) for t in tickets)
avg_cost_inr = (total_cost_inr / total_tickets) if total_tickets > 0 else 0.096
auto_pct = int((auto_dispatched / total_tickets * 100)) if total_tickets > 0 else 72

# ==============================================================================
# DEDICATED PURE FULLSCREEN PRESENTATION MODE (EDGE-TO-EDGE, NO CLUTTER)
# ==============================================================================
is_deck_fs = st.session_state.get("deck_fullscreen", False)
if is_deck_fs:
    top_c1, top_c2, top_c3 = st.columns([2.5, 5, 2.5])
    with top_c1:
        if st.button("✕ Exit Fullscreen Deck", key="exit_fs_top", type="secondary", use_container_width=True):
            st.session_state["deck_fullscreen"] = False
            st.rerun()
    with top_c2:
        st.markdown(
            "<div style='text-align:center; padding-top:6px; font-weight:700; color:#38BDF8; font-size:1.05rem; letter-spacing:0.02em;'>"
            "📽️ Dhaga & Co. CX Copilot — Executive Pitch Deck"
            "</div>", 
            unsafe_allow_html=True
        )
    with top_c3:
        st.markdown(
            "<div style='text-align:right; padding-top:8px; font-size:0.75rem; color:#94A3B8;'>"
            "💡 Press <kbd style='background:#1E293B; color:#38BDF8; padding:2px 6px; border-radius:4px;'>F5</kbd> for native full-screen"
            "</div>",
            unsafe_allow_html=True
        )

    # Embed the presentation filling the screen right from the top!
    html_path = os.path.join(os.path.dirname(__file__), "presentation", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            ppt_html = f.read()
        st.components.v1.html(ppt_html, height=890, scrolling=False)
    else:
        st.error("Presentation file not found at presentation/index.html")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎯 Presentation Live Demo Launchpad")
    st.caption("Click any scenario below to automatically load the ticket into the live triage workbench or WhatsApp simulator during your presentation:")
    
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        if st.button("⚡ Test 1: Happy-path WISMO in Transit (Delhivery)", use_container_width=True, key="fs_t1"):
            st.session_state["selected_ticket_id"] = "TCK-1001"
            st.session_state["deck_fullscreen"] = False
            st.session_state["user_role_choice"] = "🎧 Frontline Support Agent"
            st.rerun()
        st.caption("Pooja Sharma · In Transit to Patna Hub · Auto-dispatched in 18s")

        if st.button("⚡ Test 2: Delayed Transit WISMO (COD Remorse Risk)", use_container_width=True, key="fs_t2"):
            st.session_state["selected_ticket_id"] = "TCK-1002"
            st.session_state["deck_fullscreen"] = False
            st.session_state["user_role_choice"] = "🎧 Frontline Support Agent"
            st.rerun()
        st.caption("Ankit Verma · Processing delayed · Reassuring EDD dispatched")

        if st.button("⚡ Test 3: Valid Return within 7 Days (Fit Issue)", use_container_width=True, key="fs_t3"):
            st.session_state["selected_ticket_id"] = "TCK-1003"
            st.session_state["deck_fullscreen"] = False
            st.session_state["user_role_choice"] = "🎧 Frontline Support Agent"
            st.rerun()
        st.caption("Rituja Patil · Delivered 2 days ago · Agent 1-click approval")

    with d_col2:
        if st.button("⚡ Test 4: Strict Out-of-Policy Rejection (>7 Days)", use_container_width=True, key="fs_t4"):
            st.session_state["selected_ticket_id"] = "TCK-1008"
            st.session_state["deck_fullscreen"] = False
            st.session_state["user_role_choice"] = "🎧 Frontline Support Agent"
            st.rerun()
        st.caption("Neha Reddy · Delivered 16 days ago · Automated polite refusal")

        if st.button("⚡ Test 5: Intentional Failure (Ambiguous Phone Collision)", use_container_width=True, key="fs_t5"):
            st.session_state["selected_ticket_id"] = "TCK-1007"
            st.session_state["deck_fullscreen"] = False
            st.session_state["user_role_choice"] = "🎧 Frontline Support Agent"
            st.rerun()
        st.caption("Simran Kaur · 2 active orders · Refuses to guess; flags agent")

        if st.button("⚡ Test 6: Hostile Customer Escalation (P1 to Arpita)", use_container_width=True, key="fs_t6"):
            st.session_state["selected_ticket_id"] = "TCK-1006"
            st.session_state["deck_fullscreen"] = False
            st.session_state["user_role_choice"] = "📊 Arpita (Head of CX)"
            st.rerun()
        st.caption("Kavita Yadav · Delivery attempt dispute · AI auto-reply blocked")

    st.stop() # Prevents rendering of the rest of dashboard when in fullscreen presentation!

if "Frontline Support Agent" in user_role:
    st.markdown("## 🎧 Frontline Agent Copilot & Triage Workbench")
    st.markdown("*Real-time AI triage, deterministic order & policy verification, and 1-click customer response dispatch.*")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">My Queue Status</div>
            <div class="metric-value">{total_tickets} Assigned</div>
            <div class="metric-subtitle" style="color: #60A5FA;">Active Inbound Stream</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Auto-Resolved (No Touch)</div>
            <div class="metric-value" style="color: #10B981;">{auto_dispatched} Tickets</div>
            <div class="metric-subtitle" style="color: #10B981;">{auto_pct}% Auto-Dispatched</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Pending My Review</div>
            <div class="metric-value" style="color: {'#EF4444' if pending_review > 0 else '#10B981'};">{pending_review} Actionable</div>
            <div class="metric-subtitle" style="color: #9CA3AF;">Returns & Exceptions</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">First Response Time</div>
            <div class="metric-value" style="color: #F59E0B;">18s</div>
            <div class="metric-subtitle" style="color: #9CA3AF;"><del>9 Hours</del> Baseline</div>
        </div>
        """, unsafe_allow_html=True)

elif "Arpita" in user_role:
    st.markdown("## 📊 CX Operations & Service Leadership Dashboard")
    st.markdown("*Dhaga & Co. CX health: 9,000 weekly tickets, deflection efficiency, agent capacity liberation, and return insights.*")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Weekly Volume Run-rate</div>
            <div class="metric-value">9,000 / wk</div>
            <div class="metric-subtitle" style="color: #60A5FA;">58% WISMO (~5,220 tickets)</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Auto-Deflection Rate</div>
            <div class="metric-value" style="color: #10B981;">{auto_pct}%</div>
            <div class="metric-subtitle" style="color: #10B981;">Published Safe Unread</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Team Capacity Reclaimed</div>
            <div class="metric-value" style="color: #60A5FA;">~20 FTE</div>
            <div class="metric-subtitle" style="color: #10B981;">₹5.0 Lakhs / mo Saved</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Escalations Requiring Lead</div>
            <div class="metric-value" style="color: {'#EF4444' if escalated > 0 else '#10B981'};">{escalated} Priority</div>
            <div class="metric-subtitle" style="color: #9CA3AF;">High Urgency & COD Issues</div>
        </div>
        """, unsafe_allow_html=True)

elif "Dev" in user_role:
    st.markdown("## 🛡️ Technical Architecture, Cost & Model Audit")
    st.markdown("*System health, token cost line arithmetic, code vs. model boundary, and intentional failure mode monitoring.*")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Cost Per Ticket Run</div>
            <div class="metric-value" style="color: #C084FC;">₹{avg_cost_inr:.3f}</div>
            <div class="metric-subtitle" style="color: #9CA3AF;">Dual Model Economy</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Weekly LLM Budget (9k)</div>
            <div class="metric-value" style="color: #10B981;">₹864 / wk</div>
            <div class="metric-subtitle" style="color: #10B981;">~$10.00 USD / week</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average Pipeline Latency</div>
            <div class="metric-value" style="color: #F59E0B;">215ms</div>
            <div class="metric-subtitle" style="color: #9CA3AF;">4-Stage Pattern Pipeline</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Evaluator Guardrail Pass</div>
            <div class="metric-value" style="color: #10B981;">100%</div>
            <div class="metric-subtitle" style="color: #10B981;">Zero Unverified Auto-Replies</div>
        </div>
        """, unsafe_allow_html=True)

else: # Presentation Deck Mode
    st.markdown("## 📽️ Dhaga & Co. Executive Pitch & Architecture Deck")
    st.markdown("*Interactive Presentation for Mentors, CTO Dev, and Arpita (Head of CX) · Mini Project 1*")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Inbound Volume</div>
            <div class="metric-value" style="color: #60A5FA;">9,000 / wk</div>
            <div class="metric-subtitle">58% WISMO Crisis</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">First Response Time</div>
            <div class="metric-value" style="color: #10B981;">18s <span style="font-size:0.8rem; color:#9CA3AF;"><del>9 hrs</del></span></div>
            <div class="metric-subtitle" style="color: #10B981;">99.9% Instant Triage</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Headcount Cost Saved</div>
            <div class="metric-value" style="color: #C084FC;">₹5.0 Lakhs/mo</div>
            <div class="metric-subtitle" style="color: #C084FC;">20 FTE Labor Reclaimed</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Net Financial ROI</div>
            <div class="metric-value" style="color: #F59E0B;">133x ROI</div>
            <div class="metric-subtitle">₹864/wk vs ₹5L Saved</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# TAB RENDERERS (MODULAR VIEW COMPONENTS)
# ==============================================================================

def render_agent_workbench(tickets, role_mode="agent"):
    # Filter Row based on operating persona
    if role_mode == "agent":
        status_filter = st.radio(
            "Filter My Queue:",
            ["Actionable (Needs My Review)", "Auto-Dispatched (Info Only)", "All My Tickets"],
            horizontal=True,
            key="wb_status_filter_agent"
        )
        if status_filter == "Actionable (Needs My Review)":
            filtered_tickets = [t for t in tickets if t.get('ticket_status') in ['PENDING_AGENT_REVIEW', 'AGENT_RESOLVED']]
        elif status_filter == "Auto-Dispatched (Info Only)":
            filtered_tickets = [t for t in tickets if t.get('ticket_status') in ['AUTO_RESOLVED'] or t.get('dispatch_mode') == 'AUTO_DISPATCH']
        else:
            # Frontline agents do not manage P1 escalations
            filtered_tickets = [t for t in tickets if t.get('ticket_status') != 'ESCALATED']
            
    elif role_mode == "lead": # Arpita (Head of CX)
        status_filter = st.radio(
            "Leadership & Supervision Filter:",
            ["🚨 P1 Escalations (Immediate Action)", "⏳ Needs Agent Review", "✅ Auto-Dispatched", "All Tickets"],
            horizontal=True,
            key="wb_status_filter_lead"
        )
        if status_filter == "🚨 P1 Escalations (Immediate Action)":
            filtered_tickets = [t for t in tickets if t.get('ticket_status') == 'ESCALATED' or t.get('predicted_intent') == 'ESCALATION_HOSTILE']
        elif status_filter == "⏳ Needs Agent Review":
            filtered_tickets = [t for t in tickets if t.get('ticket_status') in ['PENDING_AGENT_REVIEW', 'AGENT_RESOLVED']]
        elif status_filter == "✅ Auto-Dispatched":
            filtered_tickets = [t for t in tickets if t.get('ticket_status') in ['AUTO_RESOLVED'] or t.get('dispatch_mode') == 'AUTO_DISPATCH']
        else:
            filtered_tickets = tickets
            
    else: # All-access / Presentation mode
        status_filter = st.radio(
            "Filter Inbound Tickets:",
            ["All Tickets", "Auto-Dispatched", "Needs Agent Review", "Escalations"],
            horizontal=True,
            key="wb_status_filter_all"
        )
        if status_filter == "Auto-Dispatched":
            filtered_tickets = [t for t in tickets if t.get('ticket_status') in ['AUTO_RESOLVED'] or t.get('dispatch_mode') == 'AUTO_DISPATCH']
        elif status_filter == "Needs Agent Review":
            filtered_tickets = [t for t in tickets if t.get('ticket_status') in ['PENDING_AGENT_REVIEW', 'AGENT_RESOLVED']]
        elif status_filter == "Escalations":
            filtered_tickets = [t for t in tickets if t.get('ticket_status') == 'ESCALATED' or t.get('predicted_intent') == 'ESCALATION_HOSTILE']
        else:
            filtered_tickets = tickets

    if not filtered_tickets:
        st.info(f"No tickets currently in the '{status_filter}' category.")
        return

    queue_col, detail_col = st.columns([5, 7])

    # 1-CLICK TICKET SELECTOR LIST
    with queue_col:
        st.markdown(f"**Click any ticket to inspect ({len(filtered_tickets)} in queue):**")
        
        if "selected_ticket_id" not in st.session_state or not any(t['ticket_id'] == st.session_state["selected_ticket_id"] for t in filtered_tickets):
            st.session_state["selected_ticket_id"] = filtered_tickets[0]['ticket_id'] if filtered_tickets else "TCK-1001"

        for t in filtered_tickets:
            t_id = t['ticket_id']
            is_selected = (t_id == st.session_state["selected_ticket_id"])
            intent = t.get('predicted_intent', 'WISMO')
            status = t.get('ticket_status', 'NEW')
            name = t.get('full_name') or "Customer"
            raw_msg = t.get('raw_message', '')
            
            # Badge prefix
            if status == 'AUTO_RESOLVED' or t.get('dispatch_mode') == 'AUTO_DISPATCH':
                badge_str = "⚡ AUTO"
            elif status == 'AGENT_RESOLVED':
                badge_str = "✓ RESOLVED"
            elif status == 'ESCALATED' or intent == 'ESCALATION_HOSTILE':
                badge_str = "🚨 ESCALATE"
            else:
                badge_str = "⏳ REVIEW"

            btn_label = f"[{badge_str}]  {t_id} · {name}  ({intent})\n\"{raw_msg[:54]}...\""
            
            if st.button(btn_label, key=f"select_btn_{t_id}", use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state["selected_ticket_id"] = t_id
                st.rerun()

    # RIGHT: TICKET WORKBENCH & POLICY AUDIT
    with detail_col:
        curr_t_id = st.session_state["selected_ticket_id"]
        sel = next((t for t in tickets if t['ticket_id'] == curr_t_id), filtered_tickets[0] if filtered_tickets else None)

        if sel:
            st.markdown(f"### 📋 Workbench: `{sel['ticket_id']}`")
            
            # Customer & Order Context Box
            order_id = sel.get('matched_order_id')
            cust_name = sel.get('full_name') or "Customer"
            cust_phone = sel.get('customer_phone')
            tier = sel.get('tier') or "Tier-2"
            city = sel.get('city') or "City"
            payment_mode = sel.get('payment_mode') or "COD"
            total_amt = sel.get('total_amount')
            amt_str = f" · ₹{total_amt:.2f}" if total_amt else ""

            badge_payment_class = "badge-cod" if payment_mode == "COD" else "badge-prepaid"
            st.markdown(f"""
            <div style="background: #111827; border: 1px solid #1F2937; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.05rem; font-weight: 700; color: #F3F4F6;">{cust_name}</span>
                        <span style="color: #9CA3AF; font-size: 0.8rem; margin-left: 8px;">({cust_phone} · {city}, {tier})</span>
                    </div>
                    <div>
                        <span class="badge {badge_payment_class}">{payment_mode} Order{amt_str}</span>
                    </div>
                </div>
                <div style="margin-top: 8px; font-size: 0.88rem; color: #E5E7EB; background: #0B0F19; padding: 10px 14px; border-radius: 6px; border: 1px solid #1F2937;">
                    <strong style="color: #9CA3AF;">Inbound Message:</strong><br>
                    "{sel['raw_message']}"
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Order Status Card (if matched)
            if order_id:
                st.markdown(f"""
                <div style="background: #111827; border: 1px solid #1F2937; border-radius: 10px; padding: 12px 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px;">
                        <span>📦 <strong>Matched Order:</strong> {order_id} ({sel.get('product_name') or 'Garment'})</span>
                        <span style="color: #10B981; font-weight: 600;">Status: {sel.get('order_status')}</span>
                    </div>
                    <div style="display: flex; gap: 16px; font-size: 0.78rem; color: #9CA3AF;">
                        <span>🚚 Courier: {sel.get('courier_partner') or 'Delhivery'}</span>
                        <span>🏷️ AWB: {sel.get('awb_number') or 'DEL-9921'}</span>
                        <span>📅 Expected: {sel.get('expected_delivery_date') or 'Tomorrow'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif sel.get('deterministic_policy_check') == 'AMBIGUOUS_ORDER_REFERENCE':
                st.error("⚠️ **Intentional Safeguard Triggered (Failure Mode):** Ambiguous Order Reference! This customer phone has 2 active orders in Postgres. The system refused to guess an order ID and flagged human review.")

            # DETERMINISTIC POLICY AUDIT CARD
            audit_raw = sel.get('extracted_entities') or "{}"
            try:
                parsed_audit = json.loads(audit_raw)
                policy_audit = parsed_audit.get('policy_audit', {})
            except Exception:
                policy_audit = {}

            order_placed_date = policy_audit.get('order_placed_date') or sel.get('order_date') or "N/A"
            delivered_date = policy_audit.get('delivered_date') or sel.get('delivered_date') or "Not Delivered Yet"
            ticket_date = policy_audit.get('ticket_raised_date') or sel.get('created_at') or datetime.now().strftime("%Y-%m-%d")
            days_gap = policy_audit.get('days_gap')
            verdict = policy_audit.get('verdict') or ("PASS_WITHIN_POLICY" if "ELIGIBLE" in (sel.get('deterministic_policy_check') or "") else "CHECK")
            checks_list = policy_audit.get('checks_summary') or []

            st.markdown("#### ⚖️ Deterministic Policy Compliance Audit")
            
            gap_display = f"{days_gap} Days" if days_gap is not None else "In Transit"
            threshold_display = "≤ 7 Days Allowed"
            
            if verdict == "PASS_WITHIN_POLICY":
                verdict_badge = '<span class="badge badge-auto">🟢 PASS: Within Policy (Eligible)</span>'
            elif verdict == "FAIL_OUT_OF_POLICY" or "OUT_OF_POLICY" in (sel.get('deterministic_policy_check') or ""):
                verdict_badge = '<span class="badge badge-escalate">🔴 FAIL: Strictly Out of Policy (> 7 Days)</span>'
            elif verdict == "PARTIAL_EXCEPTION_REVIEW" or "PARTIAL" in (sel.get('deterministic_policy_check') or ""):
                verdict_badge = '<span class="badge badge-review">🟡 PARTIAL: Policy Exception Discretion Advised</span>'
            else:
                verdict_badge = '<span class="badge badge-review">⏳ Standard Review</span>'

            st.markdown(f"""
            <div class="policy-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; color: #FFFFFF; font-size: 0.9rem;">Policy Verification Breakdown</span>
                    {verdict_badge}
                </div>
                <div class="policy-row">
                    <span class="policy-label">📅 Order Placed Date:</span>
                    <span class="policy-val">{order_placed_date[:10] if order_placed_date != 'N/A' else 'N/A'}</span>
                </div>
                <div class="policy-row">
                    <span class="policy-label">🚚 Delivered Date:</span>
                    <span class="policy-val">{delivered_date[:10] if delivered_date != 'Not Delivered Yet' else 'Not Delivered Yet'}</span>
                </div>
                <div class="policy-row">
                    <span class="policy-label">📩 Ticket Raised Date:</span>
                    <span class="policy-val">{ticket_date[:10]}</span>
                </div>
                <div class="policy-row">
                    <span class="policy-label">⏱️ Time Elapsed Since Delivery:</span>
                    <span class="policy-val" style="color: {'#EF4444' if (days_gap and days_gap > 7) else '#10B981'};">{gap_display} ({threshold_display})</span>
                </div>
                <div class="policy-row">
                    <span class="policy-label">📋 Policy Code & Rule:</span>
                    <span class="policy-val">{sel.get('deterministic_policy_check')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if checks_list:
                st.markdown("**Policy Checkpoints:**")
                for chk in checks_list:
                    chk_color = "#10B981" if chk['status'] == "PASS" else ("#EF4444" if chk['status'] == "FAIL" else "#F59E0B")
                    st.markdown(f"- <span style='color:{chk_color}; font-weight:700;'>[{chk['status']}]</span> **{chk['name']}**: {chk['detail']}", unsafe_allow_html=True)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            # DISPATCH & ACTION CONSOLE
            st.markdown("#### ⚡ Dispatch & Action Console")
            
            if sel.get('dispatch_mode') == 'AUTO_DISPATCH' or sel.get('ticket_status') == 'AUTO_RESOLVED':
                is_out_of_policy = "OUT_OF_POLICY" in (sel.get('deterministic_policy_check') or "")
                
                if is_out_of_policy:
                    st.info("ℹ️ **Automated Out-of-Policy Rejection Dispatched** (Customer notified with exact delivery dates & policy boundary)")
                elif sel.get('predicted_intent') == 'GENERAL_INQUIRY':
                    st.success("✅ **Automated Policy Inquiry Dispatched** (Zero-cost COD delivery & Tuesday drop calendar answered)")
                else:
                    st.success("✅ **Automated Response Dispatched Successfully** (Published Safe Unread via WhatsApp/Freshdesk)")
                
                msg_content = sel.get('final_response_sent') or sel.get('generated_draft') or ""
                st.markdown(f"""
                <div style="background: #101B2B; border: 1.5px solid #0284C7; border-radius: 8px; padding: 14px 16px; margin: 8px 0 10px 0; box-shadow: 0 4px 14px rgba(0,0,0,0.4);">
                    <div style="font-size: 0.76rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                        <span>✉️ Message Delivered to Customer:</span>
                    </div>
                    <div style="color: #FFFFFF; font-size: 0.93rem; line-height: 1.6; font-weight: 500; white-space: pre-wrap;">{msg_content}</div>
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"⚡ Delivered in 18 seconds | Cost: ₹{sel.get('cost_inr') or 0.096} | Zero Agent Labor")
            
            elif sel.get('ticket_status') == 'AGENT_RESOLVED':
                st.info("✓ **Ticket Resolved by Agent**")
                msg_content = sel.get('final_response_sent') or sel.get('generated_draft') or ""
                st.markdown(f"""
                <div style="background: #101B2B; border: 1.5px solid #10B981; border-radius: 8px; padding: 14px 16px; margin: 8px 0 10px 0; box-shadow: 0 4px 14px rgba(0,0,0,0.4);">
                    <div style="font-size: 0.76rem; font-weight: 700; color: #34D399; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                        <span>✉️ Final Message Sent by Agent:</span>
                    </div>
                    <div style="color: #FFFFFF; font-size: 0.93rem; line-height: 1.6; font-weight: 500; white-space: pre-wrap;">{msg_content}</div>
                </div>
                """, unsafe_allow_html=True)
                
            elif sel.get('ticket_status') == 'ESCALATED':
                st.error("🚨 **P1 Escalated to Senior CX Lead (Arpita)**")
                st.markdown("*Reason: Hostile complaint / RTO dispute / threat of legal action. AI auto-reply was strictly prohibited.*")
                if role_mode in ["lead", "all"]:
                    act_col1, act_col2 = st.columns(2)
                    with act_col1:
                        if st.button("📞 Assign to Priority Callback", key=f"call_{curr_t_id}", use_container_width=True):
                            st.toast("Assigned to Senior Escalations Team!", icon="🚀")
                    with act_col2:
                        if st.button("✓ Mark De-escalated", key=f"deesc_{curr_t_id}", use_container_width=True):
                            database.update_agent_review(curr_t_id, "De-escalated via direct phone consultation", agent_id="Arpita_Lead")
                            st.rerun()
                else:
                    st.info("🔒 **Assigned to Senior CX Leadership (Arpita):** This ticket is under supervisor review. Frontline dispatch is locked.")

            else: # PENDING_AGENT_REVIEW
                is_partial = "PARTIAL" in (sel.get('deterministic_policy_check') or "") or verdict == "PARTIAL_EXCEPTION_REVIEW"
                
                if is_partial:
                    st.warning("🟡 **Partially Falling Under Policy (Agent Discretion Advised)**\n*Customer reports a defect or is slightly beyond 7 days. Review and decide whether to grant one-time return exception.*")
                else:
                    st.warning("⏳ **Human-in-the-Loop Review Required** (Evaluator flagged for agent confirmation)")
                
                draft_text = st.text_area(
                    "AI-Generated Copilot Draft (Edit before sending):",
                    value=sel.get('generated_draft') or "Drafting...",
                    height=130,
                    key=f"draft_{curr_t_id}"
                )
                
                b_col1, b_col2, b_col3 = st.columns([4, 4, 3])
                with b_col1:
                    if st.button("⚡ 1-Click Approve & Dispatch", type="primary", key=f"app_{curr_t_id}", use_container_width=True):
                        database.update_agent_review(curr_t_id, draft_text, agent_id="Agent_34", was_modified=False)
                        st.toast("Response dispatched to customer!", icon="🚀")
                        st.rerun()
                with b_col2:
                    if st.button("✏️ Save Edits & Dispatch", key=f"edit_{curr_t_id}", use_container_width=True):
                        database.update_agent_review(curr_t_id, draft_text, agent_id="Agent_34", was_modified=True)
                        st.toast("Modified response sent!", icon="✍️")
                        st.rerun()
                with b_col3:
                    if st.button("🚨 Escalate to Lead", key=f"esc_{curr_t_id}", use_container_width=True):
                        database.escalate_ticket(curr_t_id, "Frontline agent escalated to Arpita (CX Lead)")
                        st.toast("Escalated to Senior Lead!", icon="🚨")
                        st.rerun()


def render_whatsapp_simulator():
    st.markdown("### 📱 Live Customer WhatsApp Channel Simulator")
    st.caption("Simulate real inbound queries from Dhaga & Co.'s 700k Tier-2/3 monthly shoppers writing informal Hinglish.")
    
    wa_col1, wa_col2 = st.columns([1, 1])
    
    with wa_col1:
        st.markdown("**Test a Customer Scenario:**")
        preset = st.selectbox(
            "Load a Case Study Scenario:",
            [
                "Custom Query (Type below)",
                "Scenario 1: Happy-path WISMO in Transit (#DH-10492 - Pooja Sharma)",
                "Scenario 2: Return Fit Issue within 7 Days (#DH-10501 - Rituja Patil)",
                "Scenario 3: Strict Out-of-Policy Return >7 Days (#DH-10470 - Neha Reddy)",
                "Scenario 4: Partial Policy Exception - Loose Stitching (#DH-10475 - Vikram Rathore)",
                "Scenario 5: Intentional Failure - Ambiguous Order (Simran Kaur - 2 orders)",
                "Scenario 6: Hostile COD Escalation - Delivery Attempt Dispute (#DH-10515 - Kavita Yadav)",
                "Scenario 7: General Inquiry - Free COD & Tuesday Collection Drop (#DH-10475 - Vikram Rathore)"
            ],
            key="wa_preset_select"
        )
        
        default_msg = "Mera order #DH-10492 kab tak aayega? 4 din ho gaye abhi tak mila nahi."
        default_phone = "+919876543210"
        
        if "Scenario 1" in preset:
            default_msg = "Bhai mera order #DH-10492 kab tak aayega? 4 din ho gaye abhi tak mila nahi."
            default_phone = "+919876543210"
        elif "Scenario 2" in preset:
            default_msg = "Kurti ka size bohot tight hai, mujhe XL exchange karna hai please. Order #DH-10501. Kaise return process karu?"
            default_phone = "+919876543212"
        elif "Scenario 3" in preset:
            default_msg = "Maine 2 week pehle kurti li thi #DH-10470, ab return karni hai pasand nahi aayi."
            default_phone = "+919876543217"
        elif "Scenario 4" in preset:
            default_msg = "Bhaiya kurta #DH-10475 9 din pehle deliver hua tha, par stitching loose nikal gayi hai. Can I exchange it?"
            default_phone = "+919876543218"
        elif "Scenario 5" in preset:
            default_msg = "Mera parcel nahi aaya abhi tak refund do turant!"
            default_phone = "+919876500007" # Simran Kaur with 2 active orders!
        elif "Scenario 6" in preset:
            default_msg = "Bakwaas service! Delivery boy ne bina ghar aaye update kar diya customer not available. COD order tha #DH-10515, main consumer forum me complain karunga!"
            default_phone = "+919876543215"
        elif "Scenario 7" in preset:
            default_msg = "Bhaiya COD me delivery charges extra lagte hai kya? Aur Tuesday collection kab drop hoga?"
            default_phone = "+919876543218"
            
        sim_msg = st.text_area("Customer Inbound Message (Hinglish/English):", value=default_msg, height=100, key="wa_sim_msg_input")
        sim_phone = st.text_input("Customer Registered Phone Number:", value=default_phone, key="wa_sim_phone_input")
        
        send_btn = st.button("🚀 Send Message as Customer", type="primary", use_container_width=True, key="send_wa_btn")
        
        if send_btn:
            with st.spinner("Processing through 4-stage pipeline..."):
                sim_ticket_id = f"SIM-{int(datetime.now().timestamp()) % 10000}"
                result = pipeline.process_ticket_end_to_end(sim_ticket_id, sim_msg, sim_phone)
                st.session_state["sim_result"] = result
                st.session_state["sim_active_msg"] = sim_msg
                st.success("Triage Complete! Inspect the WhatsApp screen 👉")

    with wa_col2:
        sim_result = st.session_state.get("sim_result")
        user_text = st.session_state.get("sim_active_msg", default_msg)
        
        if sim_result:
            reply_text = sim_result['draft'].reply_text
            action = sim_result['evaluator'].action
            is_auto = (action == "AUTO_SEND")
        else:
            # Default preview
            reply_text = "Namaste Pooja! Aapka order #DH-10492 Delhivery ke through raste me hai aur Patna Hub pahuch chuka hai. Expected delivery date kal hai. Live tracking: https://track.delhivery.com?awb=DEL-889102"
            is_auto = True

        st.markdown(f"""
        <div class="phone-container">
            <div class="wa-header">
                <div class="wa-avatar">🧵</div>
                <div>
                    <div style="font-weight: 700; color: #E9EDEF; font-size: 0.95rem;">Dhaga & Co. Support</div>
                    <div style="font-size: 0.72rem; color: #10B981;">● Online · Verified Business Account</div>
                </div>
            </div>
            <div class="wa-chat-area">
                <div style="text-align: center; margin-bottom: 8px;">
                    <span style="background: #182229; color: #8696A0; padding: 4px 10px; border-radius: 8px; font-size: 0.68rem;">Messages are end-to-end encrypted</span>
                </div>
                <div class="wa-bubble wa-incoming">
                    {user_text}
                    <div class="wa-time">10:42 AM</div>
                </div>
                <div class="wa-bubble wa-outgoing">
                    {reply_text}
                    <div class="wa-time">
                        {'⚡ Automated Reply' if is_auto else '👤 Agent Assisted'} · 10:42 AM <span style="color: #53BDEB;">✓✓</span>
                    </div>
                </div>
            </div>
            <div style="background: #1F2C34; padding: 10px 14px; display: flex; align-items: center; border-top: 1px solid #2A3942;">
                <div style="background: #2A3942; border-radius: 20px; padding: 8px 14px; width: 100%; color: #8696A0; font-size: 0.8rem;">
                    Type a message...
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_macros_comparison(tickets):
    st.markdown("### 💬 The Paradigm Shift: Static Canned Replies vs. AI Copilot")
    st.caption("Addressing Arpita's quote: *'My agents copy and paste the same four replies all day.'*")
    
    st.markdown("""
    Before this Copilot, 34 agents were trapped manually copying four generic templates from a shared Google Doc.
    Because the templates contained zero live tracking links and zero context, customers became more anxious, inflating COD delivery rejection (RTO).
    """)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ❌ The 4 Old Static Canned Replies (Freshdesk Google Doc)")
        st.markdown("""
        <div style="background: #1F1919; border: 1px solid #7F1D1D; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
            <strong style="color: #F87171;">Template 1 (WISMO Tracking):</strong><br>
            <p style="font-size:0.85rem; color:#D1D5DB; margin-top:4px;">
            "Dear Customer, your order has been dispatched and will reach you in 4-7 business days. Please track on courier website."
            </p>
            <span style="font-size:0.75rem; color:#EF4444;">• Flaw: No AWB number, no courier name, no EDD, written in cold formal English.</span>
        </div>
        <div style="background: #1F1919; border: 1px solid #7F1D1D; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
            <strong style="color: #F87171;">Template 2 (Return Request):</strong><br>
            <p style="font-size:0.85rem; color:#D1D5DB; margin-top:4px;">
            "Dear Customer, we accept returns within 7 days. Please send your order ID and reason to initiate pickup."
            </p>
            <span style="font-size:0.75rem; color:#EF4444;">• Flaw: Asks for info the customer already provided; does not calculate 7-day window.</span>
        </div>
        <div style="background: #1F1919; border: 1px solid #7F1D1D; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
            <strong style="color: #F87171;">Template 3 (Delayed Delivery):</strong><br>
            <p style="font-size:0.85rem; color:#D1D5DB; margin-top:4px;">
            "We apologize for the delay. We are escalating this to our courier partner."
            </p>
            <span style="font-size:0.75rem; color:#EF4444;">• Flaw: Provides no explanation for weather/hub delays; triggers high COD cancellations.</span>
        </div>
        <div style="background: #1F1919; border: 1px solid #7F1D1D; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
            <strong style="color: #F87171;">Template 4 (Out of Policy Rejection):</strong><br>
            <p style="font-size:0.85rem; color:#D1D5DB; margin-top:4px;">
            "Your return request cannot be processed as return policy has expired."
            </p>
            <span style="font-size:0.75rem; color:#EF4444;">• Flaw: Brusque and argumentative; does not cite exact delivery dates.</span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("#### ✅ The New Dhaga CX Copilot Generation")
        st.markdown("""
        <div style="background: #064E3B; border: 1px solid #059669; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
            <strong style="color: #34D399;">Context-Injected Hinglish (WISMO):</strong><br>
            <p style="font-size:0.85rem; color:#E5E7EB; margin-top:4px;">
            "Namaste Pooja! Aapka order #DH-10492 Delhivery ke through raste me hai aur Patna Hub pahuch chuka hai. Expected delivery date kal hai. Live tracking: track.delhivery.com?awb=DEL-889102"
            </p>
            <span style="font-size:0.75rem; color:#10B981;">• Advantage: Direct AWB link, exact hub location, warm respectful Hinglish, delivered in 18s.</span>
        </div>
        <div style="background: #064E3B; border: 1px solid #059669; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
            <strong style="color: #34D399;">Deterministic Policy Verification (Return):</strong><br>
            <p style="font-size:0.85rem; color:#E5E7EB; margin-top:4px;">
            "Namaste Rituja! Hume khed hai ki aapko kurti ka fit pasand nahi aaya. Dhaga 7-day policy ke tehat return eligible hai. Courier 48 ghante me reverse pickup karega."
            </p>
            <span style="font-size:0.75rem; color:#10B981;">• Advantage: Checks delivered date mathematically (2 days ago), auto-tags Fit_Too_Small for Neha.</span>
        </div>
        <div style="background: #064E3B; border: 1px solid #059669; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
            <strong style="color: #34D399;">Ambiguous Collision Safeguard (WhatsApp):</strong><br>
            <p style="font-size:0.85rem; color:#E5E7EB; margin-top:4px;">
            "Namaste Simran! Aapke phone par 2 active orders mil rahe hain (#DH-10520 & #DH-10521). Kripya batayein aapko kaunse order ke baare me jankari chahiye?"
            </p>
            <span style="font-size:0.75rem; color:#10B981;">• Advantage: Refuses to guess or hallucinate when repeat buyers have concurrent parcels.</span>
        </div>
        <div style="background: #064E3B; border: 1px solid #059669; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
            <strong style="color: #34D399;">Polite Grounded Rejection (Out of Policy):</strong><br>
            <p style="font-size:0.85rem; color:#E5E7EB; margin-top:4px;">
            "Namaste Neha! Order #DH-10470 16 din pehle deliver hua tha. Dhaga 7-day policy seema samapt hone ke karan return sambhav nahi hai. Hume asuvidha ke liye khed hai."
            </p>
            <span style="font-size:0.75rem; color:#10B981;">• Advantage: Explains exact delivery timeline transparently; auto-dispatched without agent labor.</span>
        </div>
        """, unsafe_allow_html=True)


def render_executive_analytics(tickets, show_dev_cost=False):
    st.markdown("### 📊 Dhaga & Co. Executive Impact Dashboard")
    st.caption("Addressing Ritu (CEO), Sameer (Growth), and Faizan (Supply Chain) with concrete numbers.")
    
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.markdown("#### 1. Inbound Ticket Distribution (9,000 / week)")
        cat_df = pd.DataFrame({
            "Category": ["WISMO (Order Tracking)", "Returns & Fit Issues", "Refund Inquiries", "Escalations & Defect", "General / Catalog"],
            "Share (%)": [58, 22, 10, 6, 4],
            "Weekly Volume": [5220, 1980, 900, 540, 360]
        })
        st.dataframe(cat_df, hide_index=True, use_container_width=True)
        st.caption("58% WISMO matches Arpita's exact quote from Page 5.")

        st.markdown("#### 2. First Response Time (FRT) Transformation")
        frt_df = pd.DataFrame({
            "Channel / Query": ["WISMO (Standard)", "WISMO (Delayed)", "Out-of-Policy Rejections", "Return Requests", "Complex Escalations"],
            "Baseline Before": ["9 Hours", "9 Hours", "9 Hours", "9 Hours", "9 Hours"],
            "With CX Copilot": ["18 Seconds", "25 Seconds", "18 Seconds", "12 Minutes", "18 Minutes"],
            "Improvement": ["99.9% faster", "99.9% faster", "99.9% faster", "97.8% faster", "96.7% faster"]
        })
        st.dataframe(frt_df, hide_index=True, use_container_width=True)

    with m_col2:
        if show_dev_cost:
            st.markdown("#### 3. CTO Dev's Cost Arithmetic Line")
            st.markdown("""
            | Item | Calculation | Weekly Total | Monthly Total |
            | :--- | :--- | :--- | :--- |
            | **Inbound Tickets** | Case Brief Baseline | 9,000 tickets | 39,000 tickets |
            | **Avg Tokens / Ticket** | 1,200 In / 250 Out | 13.0M Tokens | 56.5M Tokens |
            | **Blended LLM Cost** | ₹0.096 / ticket | **₹864 / week** | **₹3,744 / month** |
            | **Manual Labor Saved** | ~20 FTE Agents | **₹1,25,000 / week** | **₹5,00,000 / month** |
            | **ROI Ratio** | Labor Saved / LLM Cost | **144x Return** | **133x Return** |
            """)
            st.success("🎯 **The Financial Defense for Dev (CTO):** For under ₹4,000 per month in LLM tokens, Dhaga & Co. liberates ₹5,00,000/month of human agent capacity.")
        else:
            st.markdown("#### 3. Support Team Capacity & Agent Shift Efficiency")
            st.markdown("""
            | Operational Area | Baseline Operation | With CX Copilot |
            | :--- | :--- | :--- |
            | **Active Support Staff** | 34 Agents on Freshdesk | **14 Agents on High-Touch Cases** |
            | **Repetitive Macro Copiers** | 20 FTEs copying 4 macros | **0 Agents typing macros (100% deflected)** |
            | **Weekly Capacity Liberated** | 0 Hours | **~800+ Agent Hours / Week Reclaimed** |
            | **End-of-Day Backlog** | 9-Hour Queued Tickets | **Zero Backlog (Sub-30s Triage)** |
            | **Monthly Payroll Salvaged** | Burned on WISMO | **₹5,00,000 / Month Reallocated** |
            """)
            st.success("🎯 **CX Leadership Impact:** 20 full-time support agents freed from repetitive copy-pasting to handle VIP sizing consults and proactive customer retention.")

        st.markdown("#### 4. Neha's Return Reason Categorization")
        st.caption("Neha: *'44% of returns land in Other... most is fit, but I can only read a few hundred.'*")
        return_reasons_df = pd.DataFrame({
            "Structured Category": ["Fit: Too Small / Tight", "Fit: Too Large / Loose", "Fabric: Not as expected", "Stitching Defect", "Color Mismatch", "Out of Policy (>7d)"],
            "Extracted Share (%)": [46, 21, 13, 8, 5, 7],
            "Weekly Occurrences": [910, 415, 257, 158, 99, 141]
        })
        st.dataframe(return_reasons_df, hide_index=True, use_container_width=True)


def render_technical_architecture(tickets):
    st.markdown("### 🛡️ Technical Architecture & Telemetry Audit")
    st.caption("Dedicated for Dev (CTO) & Mentors: Inspecting the Code vs Model Boundary, Token Usage & Intentional Safeguards.")
    
    st.markdown("#### 1. The Code vs. Model Line")
    code_model_df = pd.DataFrame({
        "System Step": [
            "1. Language Parsing & Normalization",
            "2. Intent & Emotion Classification",
            "3. Order Status & Delivery Lookup",
            "4. Return Policy Window Math (7-day rule)",
            "5. Context-Injected Hinglish Drafting",
            "6. Truthfulness & Safety Verification",
            "7. Dispatch Mode Gating"
        ],
        "Executed By": ["Model A (Flash)", "Model A (Flash)", "Deterministic Code (Python)", "Deterministic Code (Python)", "Model A (Flash)", "Model B (Pro)", "Deterministic Code (Python)"],
        "Temperature": ["0.1", "0.1", "N/A", "N/A", "0.4", "0.0", "N/A"],
        "Justification": [
            "Hinglish colloquialisms & typos cannot be handled by regex.",
            "Subjective linguistic nuance across tier-2/3 customer base.",
            "NEVER let model guess status. Direct SQL query on Postgres/Delhivery.",
            "today - delivered_date <= 7 days is pure deterministic arithmetic.",
            "Warm, brand-compliant tone adhering to Dhaga canned guidelines.",
            "Strict auditor model verifying draft against database ground truth.",
            "If confidence >= 0.90 & WISMO, auto-dispatch; else route to human."
        ]
    })
    st.dataframe(code_model_df, hide_index=True, use_container_width=True)

    st.markdown("#### 2. Pattern-Based Execution Trace Inspector (Live Telemetry)")
    st.caption("Inspect live token counts, latencies, and evaluator verdicts for any triaged ticket.")
    
    inspect_id = st.selectbox("Select Ticket to Inspect:", [t['ticket_id'] for t in tickets], index=0, key="inspect_ticket_select")
    inspect_t = next((t for t in tickets if t['ticket_id'] == inspect_id), None)
    
    if inspect_t:
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown(f"**Step 1: Router & Extractor (`{inspect_t.get('model_router_name') or 'gemini-2.5-flash'}` @ Temp 0.1)**")
            st.markdown(f"""
            - Predicted Intent: `{inspect_t.get('predicted_intent')}`
            - Sentiment: `{inspect_t.get('sentiment')}`
            - Confidence: `{inspect_t.get('router_confidence')}`
            """)
            st.markdown(f"**Step 2: Deterministic Database Lookup & Policy Math (Pure Python)**")
            st.markdown(f"""
            - Order Matched: `{inspect_t.get('matched_order_id')}`
            - Policy Code: `{inspect_t.get('deterministic_policy_check')}`
            - Order Lookup Status: `{'Found in Postgres' if inspect_t.get('order_lookup_success') else 'Missing / Ambiguous'}`
            """)
        with t_col2:
            st.markdown(f"**Step 3: Response Drafter (`gemini-2.5-flash` @ Temp 0.4)**")
            st.markdown(f"Draft Length: {len(inspect_t.get('generated_draft') or '')} chars")
            
            st.markdown(f"**Step 4: Evaluator-Optimizer (`{inspect_t.get('model_evaluator_name') or 'gemini-2.5-pro'}` @ Temp 0.0)**")
            st.markdown(f"""
            - Truthfulness Score: `{inspect_t.get('evaluator_score')}`
            - Evaluator Passed: `{bool(inspect_t.get('evaluator_passed'))}`
            - Dispatch Action: `{inspect_t.get('dispatch_mode')}`
            - Audit Notes: *{inspect_t.get('evaluator_reasoning')}*
            - Execution Time: `{inspect_t.get('execution_time_ms')}ms`
            - Token Cost: `₹{inspect_t.get('cost_inr')}`
            """)


def render_cto_cost_model(tickets):
    st.markdown("### 💰 CTO Financial Defense & Token Arithmetic")
    st.caption("Dedicated for Dev (CTO) & Finance: Token footprint, blended unit pricing, and financial ROI against 9,000 weekly tickets.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 1. Per-Ticket Token Footprint & Unit Economics")
        token_df = pd.DataFrame({
            "Pipeline Step": ["Step 1: Router & Extractor", "Step 2: Database & Policy Math", "Step 3: Response Drafter", "Step 4: Evaluator-Optimizer", "Total Blended Run"],
            "Engine / Model": ["Gemini 2.5 Flash", "Deterministic Python (SQL)", "Gemini 2.5 Flash", "Gemini 2.5 Pro", "Dual Model + Python"],
            "Token Consumption": ["380 In / 85 Out", "0 Tokens (Pure Code)", "450 In / 130 Out", "520 In / 60 Out", "1,350 In / 275 Out"],
            "Unit Cost (INR)": ["₹0.035", "₹0.000", "₹0.048", "₹0.013", "₹0.096 / run"]
        })
        st.dataframe(token_df, hide_index=True, use_container_width=True)
        st.caption("At ₹86.5/USD exchange rate. Flash input: $0.075/1M, Pro input: $1.25/1M.")

    with c2:
        st.markdown("#### 2. Weekly & Monthly Financial Defense")
        st.markdown("""
        | Item | Calculation | Weekly Total | Monthly Total |
        | :--- | :--- | :--- | :--- |
        | **Inbound Tickets** | Case Brief Baseline | 9,000 tickets | 39,000 tickets |
        | **Avg Tokens / Ticket** | 1,350 In / 275 Out | 14.6M Tokens | 63.3M Tokens |
        | **Blended LLM Cost** | ₹0.096 / ticket | **₹864 / week (~$10)** | **₹3,744 / month** |
        | **Manual Labor Saved** | ~20 FTE Agents | **₹1,25,000 / week** | **₹5,00,000 / month** |
        | **Net Financial ROI** | Labor Saved / LLM Cost | **144x Return** | **133x Return** |
        """)
        st.success("🎯 **CTO Arithmetic Summary:** For less than ₹4,000 per month in LLM API spend, Dhaga & Co. liberates ₹5,00,000/month of human labor with zero infrastructure maintenance.")


def render_pitch_deck(tickets):
    is_fs = st.session_state.get("deck_fullscreen", False)
    p_col1, p_col2 = st.columns([7, 3])
    with p_col1:
        st.markdown("### 📽️ Dhaga & Co. CX Copilot — Executive Pitch Deck")
        st.caption("Authentic 16:9 Widescreen slide deck. Navigate via the thumbnail strip on the left, arrow keys, or controls below.")
    with p_col2:
        if not is_fs:
            if st.button("⛶ Immersive Fullscreen Mode", type="primary", use_container_width=True, key="enter_fs_deck"):
                st.session_state["deck_fullscreen"] = True
                st.rerun()
        else:
            if st.button("✕ Exit Fullscreen Mode", type="secondary", use_container_width=True, key="exit_fs_deck"):
                st.session_state["deck_fullscreen"] = False
                st.rerun()

    # Embed the authentic 16:9 PowerPoint slide engine
    html_path = os.path.join(os.path.dirname(__file__), "presentation", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            ppt_html = f.read()
        iframe_height = 920 if is_fs else 870
        st.components.v1.html(ppt_html, height=iframe_height, scrolling=False)
    else:
        st.error("Presentation file not found at presentation/index.html")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎯 Presentation Live Demo Launchpad")
    st.caption("Click any scenario below to automatically load the corresponding ticket into the live triage workbench or WhatsApp simulator during your presentation:")
    
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        if st.button("⚡ Test 1: Happy-path WISMO in Transit (Delhivery)", use_container_width=True):
            st.session_state["selected_ticket_id"] = "TCK-1001"
            st.toast("Loaded TCK-1001! Check Agent Workbench.", icon="📦")
        st.caption("Pooja Sharma · In Transit to Patna Hub · Auto-dispatched in 18s")

        if st.button("⚡ Test 2: Delayed Transit WISMO (COD Remorse Risk)", use_container_width=True):
            st.session_state["selected_ticket_id"] = "TCK-1002"
            st.toast("Loaded TCK-1002! Check Agent Workbench.", icon="🚚")
        st.caption("Ankit Verma · Processing delayed · Reassuring EDD dispatched")

        if st.button("⚡ Test 3: Valid Return within 7 Days (Fit Issue)", use_container_width=True):
            st.session_state["selected_ticket_id"] = "TCK-1003"
            st.toast("Loaded TCK-1003! Check Agent Workbench.", icon="👗")
        st.caption("Rituja Patil · Delivered 2 days ago · Agent 1-click approval")

    with d_col2:
        if st.button("⚡ Test 4: Strict Out-of-Policy Rejection (>7 Days)", use_container_width=True):
            st.session_state["selected_ticket_id"] = "TCK-1008"
            st.toast("Loaded TCK-1008! Check Agent Workbench.", icon="⛔")
        st.caption("Neha Reddy · Delivered 16 days ago · Automated polite refusal")

        if st.button("⚡ Test 5: Intentional Failure (Ambiguous Phone Collision)", use_container_width=True):
            st.session_state["selected_ticket_id"] = "TCK-1007"
            st.toast("Loaded TCK-1007! Check Agent Workbench.", icon="⚠️")
        st.caption("Simran Kaur · 2 active orders · Refuses to guess; flags agent")

        if st.button("⚡ Test 6: Hostile Customer Escalation (P1 to Arpita)", use_container_width=True):
            st.session_state["selected_ticket_id"] = "TCK-1006"
            st.toast("Loaded TCK-1006! Check Agent Workbench.", icon="🚨")
        st.caption("Kavita Yadav · Delivery attempt dispute · AI auto-reply blocked")


# ==============================================================================
# DYNAMIC TAB ROUTING BASED ON SELECTED ROLE
# ==============================================================================

if show_all_tabs:
    # All-Access Mode: Render all 6 tabs
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "🎧 Agent Copilot & Live Triage",
        "📱 Customer WhatsApp Simulator",
        "💬 Canned Macros vs AI Comparison",
        "📊 Executive Analytics (Arpita & Dev)",
        "🛡️ Code vs Model & System Audit",
        "📽️ Executive Pitch & Presentation Deck"
    ])
    with t1: render_agent_workbench(tickets, role_mode="all")
    with t2: render_whatsapp_simulator()
    with t3: render_macros_comparison(tickets)
    with t4: render_executive_analytics(tickets, show_dev_cost=True)
    with t5: render_technical_architecture(tickets)
    with t6: render_pitch_deck(tickets)

elif "Frontline Support Agent" in user_role:
    # Strictly Agent Tabs: Focused only on actionable triage, simulator, and macros
    t1, t2, t3 = st.tabs([
        "🎧 My Triage Workbench",
        "📱 Customer WhatsApp Simulator",
        "💬 Canned Macros vs AI Copilot"
    ])
    with t1: render_agent_workbench(tickets, role_mode="agent")
    with t2: render_whatsapp_simulator()
    with t3: render_macros_comparison(tickets)

elif "Arpita" in user_role:
    # Strictly Head of CX Tabs: Leadership Analytics (No Dev Cost), P1 Escalations Supervision, WhatsApp Experience, Pitch Deck
    t1, t2, t3, t4 = st.tabs([
        "📊 CX Operations & Service Leadership",
        "🚨 P1 Escalations & Supervision Queue",
        "📱 Customer WhatsApp Experience",
        "📽️ Pitch Deck & Executive Summary"
    ])
    with t1: render_executive_analytics(tickets, show_dev_cost=False)
    with t2: render_agent_workbench(tickets, role_mode="lead")
    with t3: render_whatsapp_simulator()
    with t4: render_pitch_deck(tickets)

elif "Dev" in user_role:
    # Strictly CTO & Architecture Tabs: System Audit, Token Arithmetic & Cost Model, Prompt Testbed, Pitch Deck (Zero agent escalation queues)
    t1, t2, t3, t4 = st.tabs([
        "🛡️ Code vs Model & System Audit",
        "💰 CTO Cost Arithmetic & Financial Model",
        "📱 Model Prompt & WhatsApp Testbed",
        "📽️ Pitch Deck & Executive Summary"
    ])
    with t1: render_technical_architecture(tickets)
    with t2: render_cto_cost_model(tickets)
    with t3: render_whatsapp_simulator()
    with t4: render_pitch_deck(tickets)

else: # Pitch Deck Mode
    # Presentation Mode is Front & Center with all live demo inspection tabs
    t1, t2, t3, t4, t5 = st.tabs([
        "📽️ Executive Pitch & Architecture Deck",
        "🎧 Live Agent Workbench Demo",
        "📱 Customer WhatsApp Simulator",
        "📊 Executive Impact Analytics",
        "🛡️ Technical Architecture Audit"
    ])
    with t1: render_pitch_deck(tickets)
    with t2: render_agent_workbench(tickets, role_mode="all")
    with t3: render_whatsapp_simulator()
    with t4: render_executive_analytics(tickets, show_dev_cost=True)
    with t5: render_technical_architecture(tickets)
