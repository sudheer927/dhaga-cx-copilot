# Build Note: Dhaga & Co. CX Copilot & Autonomous Triage
**Project:** Mini Project 1 – Pattern-Based Workflow  
**Client:** Dhaga & Co.  
**Audience:** Dev (CTO) & Mentors  
**Pages:** 2 Pages Maximum  

---

## 1. The Code versus Model Table

| System Step | Handled By | Model / Logic | Stated Temp | Technical Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Language Parsing & Entity Extraction** | **Model A** | `gemini-2.5-flash` | `0.1` | Messy Hinglish, typos, and informal phrasing ("kab aayega", "size tight") cannot be handled by static regex. Low temperature ensures consistent extraction. |
| **Intent & Urgency Classification** | **Model A** | `gemini-2.5-flash` | `0.1` | Interprets emotional nuance (anxious COD customer vs hostile legal threat) into structured enum. |
| **Order Status & Courier Lookup** | **Deterministic Code** | Pure Python + SQLite | N/A | **A model earns its place on language, not lookup.** Direct SQL query against the 11M-row Postgres order table and courier AWB events. Zero hallucination risk. |
| **Return Window & Out-of-Policy Evaluation** | **Deterministic Code** | Pure Python (`datetime`) | N/A | Calculates `(ticket_date - delivered_date).days`. If `> 7 days`, triggers automated polite rejection; if defect reported or 8–10 days, flags for agent discretion. |
| **Context-Injected Response Drafting** | **Model A** | `gemini-2.5-flash` | `0.4` | Injects verified order facts and exact delivery dates into warm, empathetic Hinglish adhering to Dhaga's canned response tone. |
| **Truthfulness & Safety Gate (Evaluator)** | **Model B** | `gemini-2.5-pro` | `0.0` | Audits generated draft against database ground truth. Strictly forbids hallucinated dates or unauthorized refund promises before unread auto-dispatch. |
| **Dispatch Mode Routing** | **Deterministic Code** | Pure Python (`if/else`) | N/A | Auto-dispatches verified WISMO and strict Out-of-Policy rejections. Enforces human review on partial exceptions, defects, and escalations. |

---

## 2. Why Each Pattern Is There

### Pattern 1: Routing (Intent & Entity Extraction)
* **Why it's needed:** A monolithic single prompt cannot effectively triage 9,000 mixed tickets. Routing cleanly separates low-risk transactional queries (WISMO) from legally risky escalations (abusive language, fraud threats) and operational requests (returns, refunds).
* **What breaks without it:** Without routing, hostile disputes or complex return requests would be fed into standard auto-reply templates, causing customer outrage and severe brand damage.

### Pattern 2: Prompt Chaining (Extract $\rightarrow$ Query $\rightarrow$ Draft)
* **Why it's needed:** Prevents hallucination by decoupling information retrieval from language generation. Step 1 extracts the Order ID, Python executes the database query, and Step 3 drafts the response conditioned exclusively on retrieved facts.
* **What breaks without it:** If an LLM is asked to answer customer queries directly without chained database retrieval, it fabricates plausible-sounding delivery dates, misleading customers and worsening Dhaga's 26% Cash on Delivery RTO rate.

### Pattern 3: Evaluator-Optimizer Gate (The Customer Safety Guardrail)
* **Why it's needed:** Complies directly with the case study ground rule: *"Anything customer-facing either has to be safe to publish unread, or has to have a human review step designed on purpose."* The evaluator checks whether the draft contradicts DB ground truth.
* **What breaks without it:** A model might promise a free refund or misinterpret a delayed parcel as lost. The evaluator catches these edge cases and reroutes the ticket to frontline agents with a pre-populated draft.

---

## 3. The Cost Line (The Arithmetic for Dev, CTO)

Dhaga & Co. processes **9,000 support tickets a week** (approx. 39,000/month).

### Token Breakdown per Ticket:
* **Step 1 (Router/Extractor - Model A):** 380 input tokens, 85 output tokens
* **Step 3 (Drafter - Model A):** 450 input tokens, 130 output tokens
* **Step 4 (Evaluator - Model B):** 520 input tokens, 60 output tokens
* **Total per run:** ~1,350 input tokens, 275 output tokens

### Pricing Rates:
* **Model A (`gemini-2.5-flash`):** $0.10 / 1M input tokens, $0.40 / 1M output tokens
* **Model B (`gemini-2.5-pro`):** $1.25 / 1M input tokens, $5.00 / 1M output tokens
* **USD to INR Exchange Rate:** ₹86.5 / USD

### Volume Projections:
$$\text{Cost per Run} \approx \$0.00111 \approx \mathbf{₹0.096 \text{ per ticket}}$$
$$\text{Weekly LLM Cost (9,000 tickets)} = 9,000 \times ₹0.096 = \mathbf{₹864 \text{ / week}} \quad (\approx \$10.00 / \text{week})$$
$$\text{Monthly LLM Cost (39,000 tickets)} = 39,000 \times ₹0.096 = \mathbf{₹3,744 \text{ / month}} \quad (\approx \$43.00 / \text{month})$$

### Headcount & Operational ROI:
* 34 support agents spend 58% of their time on WISMO (~20 Full-Time Equivalent agents).
* 20 agents $\times$ ₹25,000/month = **₹5,00,000 / month** in human labor spent copy-pasting canned status messages.
* **Net Monthly Savings:** ₹5,00,000 - ₹3,744 $\approx$ **₹4,96,256 / month** (a **133x ROI**).

---

## 4. The Thing That Broke That We Did Not Expect

### The Unexpected Failure: Phone Number Collision in WhatsApp Messages
During testing with raw customer messages, we discovered that when tier-2/3 customers reach out over WhatsApp via Gupshup, **over 35% do not mention their Order ID in their opening message** (e.g., *"Mera parcel nahi aaya refund do"*).

When querying the customer's phone number against Postgres, we expected a single matching record. Instead, repeat buyers frequently had **two active concurrent orders** (e.g., a Kurti shipped yesterday and a Kidswear set processing today). 

### How It Broke:
Early versions of the prompt forced the LLM to pick the "most relevant" order. The model guessed wrong 50% of the time, providing tracking details for the wrong shipment and creating extreme customer confusion.

### How We Fixed It (Intentional Failure Mode Safeguard):
We implemented an explicit database collision check in deterministic Python (`lookup_order_details`). If a customer phone number returns $> 1$ active orders and no specific Order ID is in the text, the system:
1. Emits `AMBIGUOUS_ORDER_REFERENCE`.
2. Blocks automated dispatch.
3. Automatically formats a clarifying response in Hinglish displaying the exact candidate items: *"Found 2 active orders (Kurti #DH-10520 & Boys Set #DH-10521). Which one are you inquiring about?"*
4. Flags the ticket in the agent workbench with a visible warning pill.
