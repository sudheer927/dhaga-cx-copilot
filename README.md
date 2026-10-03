# 🧵 Dhaga & Co. CX Copilot & Autonomous Triage MVP
**Mini Project 1: Pattern-Based Workflow**  
**Stakeholders:** Arpita (Head of CX), Dev (CTO), Ritu (CEO)  
**Deliverable:** Working MVP with Deployed Frontend, Discovery Note & Build Note  

---

## 1. What It Does
Dhaga & Co. receives **9,000 support tickets a week** across Freshdesk and WhatsApp (via Gupshup). **58% (~5,220 tickets/week) are "Where is my order?" (WISMO)** queries. Frontline agents spend their entire day copy-pasting the same four canned replies, resulting in an **average first response time of 9 hours**.

This MVP implements a **pattern-based AI workflow**:
1. **Automates WISMO Resolution:** Reliably identifies tracking requests in unstructured Hinglish/English, programmatically retrieves ground truth from Postgres/Delhivery, validates safety, and dispatches instant automated WhatsApp replies in **under 30 seconds**.
2. **Human-in-the-Loop Copilot:** Pre-populates contextual drafts for returns, exchanges, and refund inquiries, allowing agents to 1-click approve, edit, or escalate.
3. **Structured Upstream Tagging:** Categorizes 100% of tickets with verified intents and reasons, solving Category Head Neha's blindspot where 44% of returns landed in an unread "Other" box.

---

## 2. Cold Start in Five Minutes (How to Run Locally)

### Prerequisites
* Python 3.10+ installed
* (Optional) `GEMINI_API_KEY` for live Google Gemini calls. If absent, the app operates automatically on its built-in high-fidelity deterministic engine.

### Quick Start Commands
```bash
# 1. Clone repository & navigate to directory
cd version2-mini-project

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Set API Key in environment or .env
# Windows PowerShell:
$env:GEMINI_API_KEY="your-gemini-api-key"
# Linux/macOS:
export GEMINI_API_KEY="your-gemini-api-key"

# 4. Launch the Streamlit Enterprise CX Application
streamlit run app.py
```
The application will open automatically in your browser at `http://localhost:8501`.

---

## 3. What It Expects
* **Input Data:** Inbound support tickets from Freshdesk or WhatsApp (Gupshup webhook) containing raw customer text (Hinglish, informal English, typos) and customer phone numbers.
* **Database Environment:** An SQLite/Postgres database (`dhaga_cx.db`) populated with customers, orders, tracking events, and support tickets mirroring Dhaga & Co.'s 11-million row Postgres orders table.

---

## 4. What It Does When Something Goes Wrong (Fails Visibly)
1. **Ambiguous Order / Missing Order ID (Intentional Failure Case):**
   * *Problem:* A customer texts *"Mera order nahi aaya"* from a phone number with multiple active orders in Postgres.
   * *Behavior:* The system **fails visibly**—it catches `AMBIGUOUS_ORDER_REFERENCE`, refuses to guess, and outputs: *"Found 2 active orders (Kurti #DH-10520 & Boys Set #DH-10521). Which one do you need help with?"*
2. **Order Not Found:**
   * Flags `ORDER_NOT_FOUND` in the agent queue and politely prompts the customer for their registered phone number or invoice number.
3. **Hallucination or Policy Drift:**
   * Model B (Evaluator-Optimizer) audits the draft. If a draft states an incorrect delivery date or unauthorized refund promise, the evaluator sets `evaluator_passed = False` and routes to frontline human review.
4. **Offline / Network Outage:**
   * If Gemini API fails or reaches quota limits, the pipeline seamlessly switches to the deterministic fallback engine without throwing unhandled exceptions.

---

## 5. Architectural Patterns Used
* **Pattern 1: Routing & Extraction (Model A - Flash @ temp 0.1):** Separates inbound tickets into 6 distinct intent paths and extracts entity IDs.
* **Pattern 2: Deterministic Policy Gate (Pure Python):** Database lookups, 7-day return policy date math (`today - delivered_date <= 7`).
* **Pattern 3: Response Drafting (Prompt Chaining - Model A @ temp 0.4):** Injects verified DB milestones into natural Hinglish replies adhering to Dhaga canned macros.
* **Pattern 4: Evaluator-Optimizer (Model B - Pro @ temp 0.0):** Compares generated draft against database ground truth. Only pre-verified WISMO queries are permitted for automated dispatch.

---

## 6. Cost Line (CTO Dev's Metric)
* **Weekly Volume:** 9,000 tickets
* **Token Footprint:** ~1,200 input tokens, ~250 output tokens per ticket
* **Average Run Cost:** **₹0.096 per ticket ($0.0011)**
* **Weekly LLM Cost:** **₹864 / week (~$10 / week)**
* **Monthly Labor Saved:** Reclaims **~20 FTE agent capacity (₹5,00,000 / month)** from repetitive copy-pasting.
