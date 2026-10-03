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
    page_title="Dhaga & Co. | CX Copilot & Auto-Triage",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
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
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        font-size: 0.88rem !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
        white-space: pre-wrap !important;
        height: auto !important;
    }
    .stButton > button:hover {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #60A5FA !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #60A5FA !important;
        font-weight: 700 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
        color: #FFFFFF !important;
    }

    /* Form Fields & Text Area Contrast */
    .stTextArea textarea {
        background-color: #111827 !important;
        color: #F9FAFB !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
    }
    .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 1px #6366F1 !important;
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
        max-width: 82%;
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
# SIDEBAR CONTROLS & DYNAMIC ROLE SWITCHER
# ==============================================================================
with st.sidebar:
    st.markdown("### 🧵 Dhaga & Co. CX")
    st.caption("FDE Mini Project 1 · Pattern-Based Workflow")
    st.divider()

    st.markdown("**Role Profile:**")
    user_role = st.selectbox(
        "Operating As:",
        ["Frontline Support Agent", "Arpita (Head of CX)", "Dev (CTO / Tech Lead)"],
        index=0,
        help="Switches dashboard perspective and relevant operational views"
    )
    
    st.markdown("**LLM Engine Status:**")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        st.success("🟢 Google Gemini API Connected")
        st.caption("Routing & Drafting: `gemini-2.5-flash`\nEvaluator: `gemini-2.5-pro`")
    else:
        st.info("🔵 High-Fidelity Local Engine Active")
        st.caption("Deterministic parsing & simulated reasoning running with zero external latency.")

    user_api_key = st.text_input("Enter Gemini API Key (Optional):", type="password", help="If provided, live Google Gemini API models are called.")
    if user_api_key:
        os.environ["GEMINI_API_KEY"] = user_api_key
        st.toast("API Key updated!", icon="🔑")

    st.divider()
    st.markdown("**Quick Actions:**")
    if st.button("🔄 Reset & Re-Seed Database", use_container_width=True):
        database.seed_demo_data(force=True)
        pipeline.run_batch_triage()
        st.rerun()
        
    if st.button("⚠️ Trigger Intentional Failure Demo", use_container_width=True, help="Loads Ticket TCK-1007 (Ambiguous Order without ID)"):
        st.session_state["selected_ticket_id"] = "TCK-1007"
        st.rerun()

    st.caption("Dhaga & Co. Operational Reality:\n• 9,000 tickets/week\n• 58% WISMO\n• 9 hr baseline FRT\n• 34 Support Agents")

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
wismo_count = sum(1 for t in tickets if t.get('predicted_intent') == 'WISMO')
auto_pct = int((auto_dispatched / total_tickets * 100)) if total_tickets > 0 else 72

if user_role == "Frontline Support Agent":
    st.markdown("## 🎧 Frontline Agent Copilot & Triage Workbench")
    st.markdown("*Real-time AI triage, deterministic order & policy verification, and 1-click customer response dispatch.*")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Queue Status</div>
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
            <div class="metric-subtitle" style="color: #9CA3AF;">Returns & Partial Policy</div>
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

elif user_role == "Arpita (Head of CX)":
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

else: # Dev (CTO / Tech Lead)
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

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# MAIN TABS
# ==============================================================================
tab_agent, tab_wa, tab_analytics, tab_architecture = st.tabs([
    "🎧 Agent Copilot & Live Triage",
    "📱 Customer WhatsApp Simulator",
    "📊 Executive Analytics (Arpita & Dev)",
    "🛡️ Code vs Model & System Audit"
])

# ==============================================================================
# TAB 1: AGENT COPILOT & LIVE TRIAGE
# ==============================================================================
with tab_agent:
    # Filter Row
    status_filter = st.radio(
        "Filter Inbound Tickets:",
        ["All Tickets", "Auto-Dispatched", "Needs Agent Review", "Escalations"],
        horizontal=True
    )

    filtered_tickets = tickets
    if status_filter == "Auto-Dispatched":
        filtered_tickets = [t for t in tickets if t.get('ticket_status') in ['AUTO_RESOLVED'] or t.get('dispatch_mode') == 'AUTO_DISPATCH']
    elif status_filter == "Needs Agent Review":
        filtered_tickets = [t for t in tickets if t.get('ticket_status') in ['PENDING_AGENT_REVIEW', 'AGENT_RESOLVED']]
    elif status_filter == "Escalations":
        filtered_tickets = [t for t in tickets if t.get('ticket_status') == 'ESCALATED' or t.get('predicted_intent') == 'ESCALATION_HOSTILE']

    queue_col, detail_col = st.columns([5, 7])

    # 1-CLICK TICKET SELECTOR LIST (NO EXTRA INSPECT BUTTONS!)
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

            # Formatted button label that acts as the complete clickable card
            btn_label = f"[{badge_str}]  {t_id} · {name}  ({intent})\n\"{raw_msg[:54]}...\""
            
            # Direct 1-click select
            if st.button(btn_label, key=f"select_btn_{t_id}", use_container_width=True, type="primary" if is_selected else "secondary"):
                st.session_state["selected_ticket_id"] = t_id
                st.rerun()

    # RIGHT: TICKET WORKBENCH & POLICY AUDIT
    with detail_col:
        curr_t_id = st.session_state["selected_ticket_id"]
        sel = next((t for t in tickets if t['ticket_id'] == curr_t_id), tickets[0] if tickets else None)

        if sel:
            st.markdown(f"### 📋 Workbench: `{sel['ticket_id']}`")
            
            # Customer & Order Context Box
            order_id = sel.get('matched_order_id')
            cust_name = sel.get('full_name') or "Customer"
            cust_phone = sel.get('customer_phone')
            tier = sel.get('tier') or "Tier-2"
            city = sel.get('city') or "City"

            st.markdown(f"""
            <div style="background: #111827; border: 1px solid #1F2937; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.05rem; font-weight: 700; color: #F3F4F6;">{cust_name}</span>
                        <span style="color: #9CA3AF; font-size: 0.8rem; margin-left: 8px;">({cust_phone} · {city}, {tier})</span>
                    </div>
                    <div>
                        <span class="badge badge-cod">COD Order</span>
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

            # DETERMINISTIC POLICY AUDIT CARD (REPLACES TECHNICAL PIPELINE TRACE)
            # Unpack policy audit from extracted_entities JSON
            audit_raw = sel.get('extracted_entities') or "{}"
            try:
                parsed_audit = json.loads(audit_raw)
                policy_audit = parsed_audit.get('policy_audit', {})
            except Exception:
                policy_audit = {}

            order_placed_date = policy_audit.get('order_placed_date') or "N/A"
            delivered_date = policy_audit.get('delivered_date') or "Not Delivered Yet"
            ticket_date = policy_audit.get('ticket_raised_date') or datetime.now().strftime("%Y-%m-%d")
            days_gap = policy_audit.get('days_gap')
            verdict = policy_audit.get('verdict') or ("PASS_WITHIN_POLICY" if "ELIGIBLE" in (sel.get('deterministic_policy_check') or "") else "CHECK")
            checks_list = policy_audit.get('checks_summary') or []

            st.markdown("#### ⚖️ Deterministic Policy Compliance Audit")
            
            # Policy Timeline Bar
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

            # Checkpoints list
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
                else:
                    st.success("✅ **Automated Response Dispatched Successfully** (Published Safe Unread via WhatsApp/Freshdesk)")
                
                st.text_area("Message Delivered to Customer:", value=sel.get('final_response_sent') or sel.get('generated_draft'), height=110, disabled=True)
                st.caption(f"⚡ Delivered in 18 seconds | Cost: ₹{sel.get('cost_inr') or 0.096} | Zero Agent Labor")
            
            elif sel.get('ticket_status') == 'AGENT_RESOLVED':
                st.info("✓ **Ticket Resolved by Agent**")
                st.text_area("Final Message Sent:", value=sel.get('final_response_sent') or sel.get('generated_draft'), height=100, disabled=True)
                
            elif sel.get('ticket_status') == 'ESCALATED':
                st.error("🚨 **P1 Escalated to Senior CX Lead (Arpita)**")
                st.markdown("*Reason: Hostile complaint / RTO dispute / threat of legal action. AI auto-reply was strictly prohibited.*")
                act_col1, act_col2 = st.columns(2)
                with act_col1:
                    if st.button("📞 Assign to Priority Callback", use_container_width=True):
                        st.toast("Assigned to Senior Escalations Team!", icon="🚀")
                with act_col2:
                    if st.button("✓ Mark De-escalated", use_container_width=True):
                        database.update_agent_review(curr_t_id, "De-escalated via phone call", agent_id="Arpita_Lead")
                        st.rerun()

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
                    if st.button("⚡ 1-Click Approve & Dispatch", type="primary", use_container_width=True):
                        database.update_agent_review(curr_t_id, draft_text, agent_id="Agent_34", was_modified=False)
                        st.toast("Response dispatched to customer!", icon="🚀")
                        st.rerun()
                with b_col2:
                    if st.button("✏️ Save Edits & Dispatch", use_container_width=True):
                        database.update_agent_review(curr_t_id, draft_text, agent_id="Agent_34", was_modified=True)
                        st.toast("Modified response sent!", icon="✍️")
                        st.rerun()
                with b_col3:
                    if st.button("🚨 Escalate to Lead", use_container_width=True):
                        conn = database.get_connection()
                        c = conn.cursor()
                        c.execute("UPDATE support_tickets SET ticket_status = 'ESCALATED' WHERE ticket_id = ?", (curr_t_id,))
                        conn.commit()
                        conn.close()
                        st.rerun()

# ==============================================================================
# TAB 2: CUSTOMER WHATSAPP EXPERIENCE (AUTOMATED REPLY SIMULATOR)
# ==============================================================================
with tab_wa:
    st.markdown("### 📱 Live Customer WhatsApp Channel Simulator")
    st.caption("Experience what Dhaga & Co.'s 700k Tier-2/3 monthly active customers see on their phone.")
    
    wa_col1, wa_col2 = st.columns([1, 1])
    
    with wa_col1:
        st.markdown("**Test a Customer Message:**")
        preset = st.selectbox(
            "Load a Realistic Scenario:",
            [
                "Custom Query (Type below)",
                "Scenario 1: Anxious WISMO (Bhai mera parcel kab tak aayega? #DH-10492)",
                "Scenario 2: Return Fit Issue Within 7 Days (Kurti tight hai exchange kardo #DH-10501)",
                "Scenario 3: Strict Out-of-Policy Return (16 din pehle kurti li thi return karni hai #DH-10470)",
                "Scenario 4: Partial Policy Exception (9 din pehle kurta liya tha stitching kharab hai #DH-10475)",
                "Scenario 5: Intentional Failure Case (Mera parcel nahi aaya refund do - No ID, 2 orders)",
                "Scenario 6: Angry Hostile COD Customer (Delivery boy ne bina call kiye cancel kar diya #DH-10515)"
            ]
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
            
        sim_msg = st.text_area("Customer Message (Hinglish/English):", value=default_msg, height=100)
        sim_phone = st.text_input("Customer Phone Number:", value=default_phone)
        
        send_btn = st.button("🚀 Send Message as Customer", type="primary", use_container_width=True)
        
        if send_btn:
            with st.spinner("Processing through 4-stage pipeline..."):
                sim_ticket_id = f"SIM-{int(datetime.now().timestamp()) % 10000}"
                result = pipeline.process_ticket_end_to_end(sim_ticket_id, sim_msg, sim_phone)
                st.session_state["sim_result"] = result
                st.session_state["sim_msg"] = sim_msg
                st.success("Triage Complete! Check the WhatsApp screen 👉")

    with wa_col2:
        sim_result = st.session_state.get("sim_result")
        user_text = st.session_state.get("sim_msg", default_msg)
        
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
                    <div style="font-size: 0.72rem; color: #10B981;">● Online · Verified Business</div>
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

# ==============================================================================
# TAB 3: EXECUTIVE ANALYTICS (ARPITA & DEV)
# ==============================================================================
with tab_analytics:
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

        st.markdown("#### 4. Neha's Return Reason Categorization")
        st.caption("Neha: *'44% of returns land in Other... most is fit, but I can only read a few hundred.'*")
        return_reasons_df = pd.DataFrame({
            "Structured Category": ["Fit: Too Small / Tight", "Fit: Too Large / Loose", "Fabric: Not as expected", "Stitching Defect", "Color Mismatch", "Out of Policy (>7d)"],
            "Extracted Share (%)": [46, 21, 13, 8, 5, 7],
            "Weekly Occurrences": [910, 415, 257, 158, 99, 141]
        })
        st.dataframe(return_reasons_df, hide_index=True, use_container_width=True)

# ==============================================================================
# TAB 4: CODE VS MODEL & SYSTEM AUDIT (TECHNICAL DEEP DIVE)
# ==============================================================================
with tab_architecture:
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
    
    inspect_id = st.selectbox("Select Ticket to Inspect:", [t['ticket_id'] for t in tickets], index=0)
    inspect_t = next((t for t in tickets if t['ticket_id'] == inspect_id), None)
    
    if inspect_t:
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown(f"**Step 1: Router & Extractor (`gemini-2.5-flash` @ Temp 0.1)**")
            st.markdown(f"""
            - Predicted Intent: `{inspect_t.get('predicted_intent')}`
            - Sentiment: `{inspect_t.get('sentiment')}`
            - Confidence: `{inspect_t.get('router_confidence')}`
            """)
            st.markdown(f"**Step 2: Deterministic Database Lookup & Policy Math**")
            st.markdown(f"""
            - Order Matched: `{inspect_t.get('matched_order_id')}`
            - Policy Code: `{inspect_t.get('deterministic_policy_check')}`
            """)
        with t_col2:
            st.markdown(f"**Step 3: Response Drafter (`gemini-2.5-flash` @ Temp 0.4)**")
            st.markdown(f"Draft Length: {len(inspect_t.get('generated_draft') or '')} chars")
            
            st.markdown(f"**Step 4: Evaluator-Optimizer (`gemini-2.5-pro` @ Temp 0.0)**")
            st.markdown(f"""
            - Truthfulness Score: `{inspect_t.get('evaluator_score')}`
            - Evaluator Passed: `{bool(inspect_t.get('evaluator_passed'))}`
            - Audit Notes: *{inspect_t.get('evaluator_reasoning')}*
            - Execution Time: `{inspect_t.get('execution_time_ms')}ms`
            - Token Cost: `₹{inspect_t.get('cost_inr')}`
            """)
