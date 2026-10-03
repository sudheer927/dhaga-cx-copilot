# Discovery Note: Dhaga & Co. CX Automation & Triage
**Project:** Mini Project 1 – Pattern-Based Workflow  
**Client:** Dhaga & Co.  
**Target Stakeholder:** Arpita, Head of Customer Experience (CX)  
**Date:** October 3, 2026  

---

### 1. The Problem in the Client's Language
> *"Fifty-eight percent of tickets are some version of 'where is my order'. My agents copy and paste the same four replies all day. Average first response is nine hours."* — Arpita, Head of CX

---

### 2. Who Owns It Today and What They Do Instead
* **Owner:** Arpita, Head of CX.
* **Current Operational Practice:**
  * Support runs across **34 agents on Freshdesk**, plus an inbound **WhatsApp line managed via Gupshup**.
  * Roughly **9,000 support tickets arrive every week**, mostly in unstructured free text (Hinglish/English).
  * Agents manually read tickets, check courier portals or internal admin screens, and copy-paste responses from a shared Google Document containing four static canned replies.
  * Tagging is non-existent or irregular: agents only assign a category when they remember to, leaving Dhaga & Co. with zero real-time visibility into support trends or defect spikes.

---

### 3. Evidence from the Case Study
* **Ticket Volume & Concentration:** Dhaga & Co. receives ~9,000 tickets a week. 58% of these (~5,220 tickets/week) are basic "Where Is My Order?" (WISMO) queries (*Page 4 & 5*).
* **Speed to First Response:** First response time currently averages **9 hours** (*Page 5*).
* **Delivery Transit Realities:** Orders take **4 to 7 days** to deliver across Delhivery, Shiprocket, and Ekart—often longer into the North East (*Page 3*). This extended transit window generates high delivery anxiety among tier-2 and tier-3 shoppers.
* **Payment & Trust Profile:** **61% of orders are Cash on Delivery (COD)** (*Page 3*). COD customers who do not receive timely delivery updates develop buyer remorse or assume fraud, significantly compounding delivery refusal and RTO risks.
* **Linguistic Reality:** Customers write predominantly in **Hinglish** and informal phrasing (*Page 3*), making keyword-matching or basic regex auto-responders fail.
* **Underlying Data Assets:** Dhaga & Co. has **11 million rows of clean, trustworthy order history in Postgres** (*Page 4*). The tracking information exists; it is simply trapped behind manual agent lookups.

---

### 4. What It Costs Them
* **Time Metric (Tracked & Argued Today):** 
  * **9 hours average first response time** on Freshdesk.
* **Labor & Capacity Cost:**
  * 58% of 9,000 tickets = **5,220 tickets/week** (~745 tickets/day) are spent on repetitive lookups.
  * Approximately **20 out of 34 agents (FTE equivalent)** spend their entire working day copying and pasting 4 canned responses.
  * At an estimated fully loaded agent cost of ₹25,000–₹30,000/month, Dhaga & Co. spends **₹5.0 Lakhs to ₹6.0 Lakhs every month (~₹60–72 Lakhs annually)** just manually typing canned status updates.
* **Downstream Business Loss (RTO & Churn):**
  * Faizan (Head of Supply Chain) notes that Return-to-Origin (RTO) on COD is **26%**, costing **₹120 per failed shipment in wasted logistics** plus burned delivery slots. A 9-hour response blackout directly inflates RTO when anxious COD customers reject parcels at their doorstep.

---

### 5. What Success Looks Like & How to Measure It
Success is measured strictly using data Dhaga & Co. already tracks in **Freshdesk** and **Postgres**:

| Metric | Current Baseline | Target with MVP | Data Source |
| :--- | :--- | :--- | :--- |
| **First Response Time (WISMO)** | 9 hours | **< 60 seconds** (Instant automated reply) | Freshdesk Ticket Timestamps |
| **First Response Time (Assisted Tickets)** | 9 hours | **< 20 minutes** (Pre-drafted Copilot response) | Freshdesk Ticket Timestamps |
| **Autonomous Resolution Rate** | 0% | **≥ 70% of WISMO tickets (~3,600+ tickets/wk)** | Freshdesk Agent Assignment Logs |
| **Ticket Categorization Compliance** | "When agents remember" | **100% structured tagging** (Intent, Sentiment, Order ID) | Freshdesk Tagging Fields |
| **CX Agent Hours Reclaimed** | 0 hrs | **~800+ agent hours per week** redirected to complex return/fit cases | Agent Activity Logs |

---

### 6. Ranked Shortlist of Four Problems

#### **Rank 1: Arpita's CX Ticket Backlog & WISMO Repetition (SELECTED)**
* **Why it sits at #1:** Clear single owner (Arpita), enormous volume (9,000 tickets/week; 5,220 WISMO), verified metric (9-hour response time), backed by clean order data in Postgres. It requires no exotic ML training, operates safely with deterministic lookups, saves immediate headcount costs, and directly addresses the 61% COD customer base.

#### **Rank 2: Neha's Return Reason Blindspot ("Other" Box in Returns)**
* **Why it was considered:** Returns are 31% overall, and 44% land in an unanalysed "Other" free-text box. Neha can only read a few hundred by hand.
* **Why it sits below #1:** Return intelligence is an offline analytical/batch problem. Solving Arpita’s live triage queue not only stops active customer churn in real time but also captures structured return categories directly at ticket intake, solving Neha's problem upstream.

#### **Rank 3: Faizan's COD Return-to-Origin (RTO) Loss**
* **Why it was considered:** 26% RTO on COD costs ₹120 per occurrence across 48,000 weekly orders (~₹15 Lakhs/week logistics burn).
* **Why it sits below #1:** RTO prediction requires complex predictive modeling and carries severe false-positive risks (canceling genuine tier-2/3 orders). CTO Dev warned that Dhaga & Co. has *16 engineers and zero ML engineers*. An operational pattern-based triage workflow is maintainable on Monday; an untested ML fraud score is not.

#### **Rank 4: Vivek's Cataloguing & Listing Delay**
* **Why it was considered:** Sample-to-live takes 6 to 9 days, causing Tuesday drop calendar slips and losing traffic spikes.
* **Why it sits below #1:** The listing bottleneck is physical and operational (garment samples arriving from Tiruppur/Jaipur, studio photography, model shoots). AI product description generation only solves a 2-hour slice of a 9-day multi-department physical pipeline.

---

### 7. Biggest Assumption & Evidence That Would Prove It Wrong
* **The Biggest Assumption:**
  We assume that in the majority of WISMO queries, the customer's phone number (via WhatsApp/Gupshup) or message text contains a recognizable Order ID, phone number, or delivery reference that can be programmatically matched against Postgres orders with high confidence.
* **What Evidence Would Prove It Wrong:**
  If audit logs from Freshdesk reveal that over **40% of inbound tickets are sent from unlinked phone numbers** with no identifying details (e.g., merely stating *"Mera kapda kab milega"*), and users drop off when asked by an automated prompt for their registered mobile number or order ID, autonomous deflection will fall below 35%, forcing the system back into human-assisted routing.
