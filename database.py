import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "dhaga_cx.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        phone_number TEXT NOT NULL UNIQUE,
        email TEXT,
        city TEXT NOT NULL,
        tier TEXT CHECK(tier IN ('Tier-1', 'Tier-2', 'Tier-3')) DEFAULT 'Tier-2',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL REFERENCES customers(customer_id),
        sku TEXT NOT NULL,
        product_name TEXT NOT NULL,
        product_category TEXT NOT NULL,
        quantity INTEGER DEFAULT 1,
        total_amount REAL NOT NULL,
        payment_mode TEXT CHECK(payment_mode IN ('COD', 'PREPAID')) NOT NULL,
        order_status TEXT NOT NULL,
        courier_partner TEXT,
        awb_number TEXT,
        order_date TIMESTAMP NOT NULL,
        dispatched_date TIMESTAMP,
        delivered_date TIMESTAMP,
        expected_delivery_date DATE NOT NULL,
        delivery_address TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS shipment_tracking_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT NOT NULL REFERENCES orders(order_id),
        awb_number TEXT NOT NULL,
        event_timestamp TIMESTAMP NOT NULL,
        hub_location TEXT NOT NULL,
        event_status TEXT NOT NULL,
        event_description TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS support_tickets (
        ticket_id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        raw_message TEXT NOT NULL,
        language_detected TEXT DEFAULT 'Hinglish',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ticket_status TEXT DEFAULT 'NEW'
    );

    CREATE TABLE IF NOT EXISTS ticket_triage_audit (
        audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT UNIQUE NOT NULL REFERENCES support_tickets(ticket_id),
        matched_order_id TEXT,
        predicted_intent TEXT,
        sentiment TEXT,
        extracted_entities TEXT,
        router_confidence REAL,
        deterministic_policy_check TEXT,
        order_lookup_success INTEGER DEFAULT 0,
        generated_draft TEXT,
        evaluator_passed INTEGER DEFAULT 0,
        evaluator_score REAL,
        evaluator_reasoning TEXT,
        dispatch_mode TEXT,
        final_response_sent TEXT,
        agent_id TEXT,
        agent_modified_draft INTEGER DEFAULT 0,
        model_router_name TEXT,
        model_evaluator_name TEXT,
        input_tokens INTEGER DEFAULT 0,
        output_tokens INTEGER DEFAULT 0,
        cost_inr REAL DEFAULT 0.0,
        execution_time_ms INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def seed_demo_data(force=False):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] > 0 and not force:
        conn.close()
        return

    cursor.executescript("DELETE FROM ticket_triage_audit; DELETE FROM support_tickets; DELETE FROM shipment_tracking_events; DELETE FROM orders; DELETE FROM customers;")

    now = datetime.now()
    two_days_ago = (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    four_days_ago = (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")
    five_days_ago = (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    eight_days_ago = (now - timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S")
    sixteen_days_ago = (now - timedelta(days=16)).strftime("%Y-%m-%d %H:%M:%S")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    in_three_days = (now + timedelta(days=3)).strftime("%Y-%m-%d")

    customers_data = [
        ("CUST-101", "Pooja Sharma", "+919876543210", "pooja.sharma@gmail.com", "Patna", "Tier-2"),
        ("CUST-102", "Ankit Verma", "+919876543211", "ankit.v@yahoo.com", "Bhopal", "Tier-2"),
        ("CUST-103", "Rituja Patil", "+919876543212", "rituja.p@outlook.com", "Nagpur", "Tier-2"),
        ("CUST-104", "Megha Mukherjee", "+919876543213", "megha.m@gmail.com", "Ranchi", "Tier-3"),
        ("CUST-105", "Sunil Joshi", "+919876543214", "sjoshi99@gmail.com", "Indore", "Tier-2"),
        ("CUST-106", "Kavita Yadav", "+919876543215", "kavita.yadav@gmail.com", "Jaipur", "Tier-2"),
        ("CUST-107", "Simran Kaur", "+919876500007", "simran.k@gmail.com", "Ludhiana", "Tier-2"), # Ambiguous user
        ("CUST-108", "Neha Reddy", "+919876543217", "neha.reddy@gmail.com", "Warangal", "Tier-3"),
        ("CUST-109", "Vikram Rathore", "+919876543218", "vrathore@gmail.com", "Jodhpur", "Tier-2"),
        ("CUST-110", "Sneha Roy", "+919876543219", "sneha.roy@gmail.com", "Guwahati", "Tier-3"),
    ]
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", customers_data)

    orders_data = [
        # 1. Active WISMO - In Transit
        ("DH-10492", "CUST-101", "W-KURTI-042", "Cotton Flared Anarkali Kurti (Rust)", "Womenswear", 1, 849.0, "COD", "IN_TRANSIT", "Delhivery", "DEL-889102", four_days_ago, two_days_ago, None, tomorrow, "Flat 302, Kankarbagh, Patna, Bihar - 800020"),
        # 2. Delayed WISMO - Weather hold
        ("DH-10495", "CUST-102", "M-SHIRT-110", "Casual Cotton Mandarin Shirt (Olive)", "Mens", 1, 799.0, "PREPAID", "PROCESSING", "Shiprocket", "SR-771928", five_days_ago, None, None, in_three_days, "H.No 12, Arera Colony, Bhopal, MP - 462016"),
        # 3. Delivered 2 days ago - Fit return eligible
        ("DH-10501", "CUST-103", "W-KURTI-088", "Straight Rayon Printed Kurti (Indigo Blue)", "Womenswear", 1, 699.0, "COD", "DELIVERED", "Ekart", "EK-554109", five_days_ago, four_days_ago, two_days_ago, two_days_ago, "Plot 45, Dharampeth, Nagpur, Maharashtra - 440010"),
        # 4. Delivered 3 days ago - Defect return eligible
        ("DH-10508", "CUST-104", "K-FROCK-019", "Floral Festive Girls Frock (Yellow)", "Kidswear", 1, 549.0, "COD", "DELIVERED", "Delhivery", "DEL-991044", eight_days_ago, five_days_ago, two_days_ago, two_days_ago, "Bariatu Road, Ranchi, Jharkhand - 834009"),
        # 5. Reverse Pickup Delayed
        ("DH-10480", "CUST-105", "W-PALAZZO-012", "Solid Wide-leg Rayon Palazzo (Black)", "Womenswear", 1, 499.0, "PREPAID", "RETURN_REQUESTED", "Ekart", "EK-998124", sixteen_days_ago, eight_days_ago, five_days_ago, five_days_ago, "Vijay Nagar, Indore, MP - 452010"),
        # 6. Hostile COD Delivery Failure
        ("DH-10515", "CUST-106", "W-DUPATTA-03", "Chanderi Silk Golden Zari Dupatta", "Womenswear", 2, 899.0, "COD", "RTO", "Delhivery", "DEL-123984", four_days_ago, two_days_ago, None, tomorrow, "C-Scheme, Jaipur, Rajasthan - 302001"),
        # 7 & 8: Ambiguous Orders for Simran Kaur (+919876500007)
        ("DH-10520", "CUST-107", "W-KURTI-101", "A-Line Embroidered Kurti (Maroon)", "Womenswear", 1, 999.0, "COD", "SHIPPED", "Delhivery", "DEL-665511", two_days_ago, now.strftime("%Y-%m-%d %H:%M:%S"), None, in_three_days, "Model Town, Ludhiana, Punjab - 141002"),
        ("DH-10521", "CUST-107", "K-SET-004", "Boys Ethnic Kurta Pyjama Set", "Kidswear", 1, 849.0, "COD", "PROCESSING", "Ekart", "EK-112233", now.strftime("%Y-%m-%d %H:%M:%S"), None, None, in_three_days, "Model Town, Ludhiana, Punjab - 141002"),
        # 9. Return Expired (>7 days - Strict Out-of-Policy)
        ("DH-10470", "CUST-108", "W-SUIT-099", "3-Piece Cotton Kurta Pant Set", "Womenswear", 1, 1399.0, "PREPAID", "DELIVERED", "Shiprocket", "SR-443322", sixteen_days_ago, sixteen_days_ago, sixteen_days_ago, sixteen_days_ago, "Subedari, Warangal, Telangana - 506001"),
        # 10. False delivery / Guard check
        ("DH-10525", "CUST-110", "W-KURTI-050", "Tiered Maxi Kurti (Sage Green)", "Womenswear", 1, 749.0, "COD", "DELIVERED", "Delhivery", "DEL-778899", five_days_ago, two_days_ago, now.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%Y-%m-%d"), "Zoo Road, Guwahati, Assam - 781024"),
        # 11. Partial Policy Exception (Delivered 9 days ago with minor stitching issue)
        ("DH-10475", "CUST-109", "M-KURTA-021", "Handloom Cotton Festive Kurta (Beige)", "Mens", 1, 999.0, "COD", "DELIVERED", "Ekart", "EK-882211", sixteen_days_ago, (now - timedelta(days=11)).strftime("%Y-%m-%d %H:%M:%S"), (now - timedelta(days=9)).strftime("%Y-%m-%d %H:%M:%S"), (now - timedelta(days=9)).strftime("%Y-%m-%d"), "Jodhpur, Rajasthan - 342001"),
    ]
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", orders_data)

    tracking_data = [
        # DH-10492 events
        ("DH-10492", "DEL-889102", four_days_ago, "Bhiwandi Fulfilment Centre", "MANIFESTED", "Order packed and Manifest raised"),
        ("DH-10492", "DEL-889102", two_days_ago, "Bhiwandi Hub", "IN_TRANSIT", "Bagged and in transit to Patna Hub"),
        ("DH-10492", "DEL-889102", now.strftime("%Y-%m-%d %H:%M:%S"), "Patna Hub", "ARRIVED", "Reached Patna Distribution Hub. Ready for final mile dispatch tomorrow morning."),
        # DH-10495 events
        ("DH-10495", "SR-771928", five_days_ago, "Gurugram Fulfilment Centre", "DELAYED", "Stock allocation under quality check; dispatch rescheduled"),
        # DH-10515 events
        ("DH-10515", "DEL-123984", four_days_ago, "Jaipur Hub", "DISPATCHED", "Out for delivery"),
        ("DH-10515", "DEL-123984", two_days_ago, "Jaipur Hub", "FAILED_ATTEMPT", "Delivery attempted; customer refused payment / unreachable. Flagged RTO."),
        # DH-10525 events
        ("DH-10525", "DEL-778899", now.strftime("%Y-%m-%d %H:%M:%S"), "Guwahati Hub", "DELIVERED", "Delivered to security/neighbor as per OTP verification."),
    ]
    cursor.executemany("INSERT INTO shipment_tracking_events (order_id, awb_number, event_timestamp, hub_location, event_status, event_description) VALUES (?, ?, ?, ?, ?, ?)", tracking_data)

    tickets_data = [
        ("TCK-1001", "WhatsApp", "+919876543210", "Bhai mera order #DH-10492 kab tak aayega? 4 din ho gaye abhi tak mila nahi.", "Hinglish", four_days_ago, "NEW"),
        ("TCK-1002", "Freshdesk", "+919876543211", "Order #DH-10495 abhi tak dispatch nahi hua! Mera event hai Tuesday ko, cancel kar do agar kal tak dispatch nahi hua toh.", "Hinglish", two_days_ago, "NEW"),
        ("TCK-1003", "WhatsApp", "+919876543212", "Kurti ka size bohot tight hai, mujhe XL exchange karna hai please. Order #DH-10501. Kaise return process karu?", "Hinglish", two_days_ago, "NEW"),
        ("TCK-1004", "Freshdesk", "+919876543213", "Mera dress ka color bilkul alag aaya hai picture se aur stitching bhi kharab hai. Mujhe refund chahiye order #DH-10508 ka.", "Hinglish", two_days_ago, "NEW"),
        ("TCK-1005", "Freshdesk", "+919876543214", "Return request dali thi order #DH-10480 par 10 din ho gaye koi pickup karne nahi aaya! Mera paisa kab aayega?", "Hinglish", two_days_ago, "NEW"),
        ("TCK-1006", "WhatsApp", "+919876543215", "Bakwaas service! Delivery boy ne bina ghar aaye update kar diya customer not available. COD order tha #DH-10515, main consumer forum me complain karunga!", "Hinglish", now.strftime("%Y-%m-%d %H:%M:%S"), "NEW"),
        ("TCK-1007", "WhatsApp", "+919876500007", "Mera parcel nahi aaya abhi tak refund do turant!", "Hinglish", now.strftime("%Y-%m-%d %H:%M:%S"), "NEW"), # Intentional failure
        ("TCK-1008", "Freshdesk", "+919876543217", "Maine 2 week pehle kurti li thi #DH-10470, ab return karni hai pasand nahi aayi.", "Hinglish", now.strftime("%Y-%m-%d %H:%M:%S"), "NEW"), # Expired return
        ("TCK-1009", "WhatsApp", "+919876543218", "Bhaiya COD me delivery charges extra lagte hai kya? Aur Tuesday collection kab drop hoga?", "Hinglish", now.strftime("%Y-%m-%d %H:%M:%S"), "NEW"),
        ("TCK-1010", "Freshdesk", "+919876543219", "App me status delivered dikha raha hai par security guard ya mujhe kisi ko nahi mila! Order #DH-10525 check karo please.", "Hinglish", now.strftime("%Y-%m-%d %H:%M:%S"), "NEW"),
        ("TCK-1011", "WhatsApp", "+919876543218", "Bhaiya kurta #DH-10475 9 din pehle deliver hua tha, par stitching loose nikal gayi hai. Can I exchange it?", "Hinglish", now.strftime("%Y-%m-%d %H:%M:%S"), "NEW"),
    ]
    cursor.executemany("INSERT INTO support_tickets VALUES (?, ?, ?, ?, ?, ?, ?)", tickets_data)

    conn.commit()
    conn.close()

def lookup_order_details(order_id_or_phone: str) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]], bool, List[str]]:
    """
    Deterministic code lookup against SQLite/Postgres.
    Returns: (order_dict, tracking_events_list, is_ambiguous, list_of_ambiguous_ids)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cleaned = order_id_or_phone.strip()
    
    # 1. Search by exact Order ID
    cursor.execute("SELECT o.*, c.full_name, c.phone_number, c.city, c.tier FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE UPPER(o.order_id) = ?", (cleaned.upper(),))
    row = cursor.fetchone()
    if row:
        order_dict = dict(row)
        cursor.execute("SELECT * FROM shipment_tracking_events WHERE order_id = ? ORDER BY event_timestamp DESC", (order_dict['order_id'],))
        events = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return order_dict, events, False, []

    # 2. Search by Phone Number
    cursor.execute("""
        SELECT o.order_id, o.product_name, o.order_status, o.order_date
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE c.phone_number = ? OR c.phone_number LIKE ?
        ORDER BY o.order_date DESC
    """, (cleaned, f"%{cleaned[-10:]}%"))
    matches = cursor.fetchall()

    if len(matches) > 1:
        # Ambiguous! Multiple active orders found for this customer phone
        ambiguous_ids = [f"{m['order_id']} ({m['product_name']} - {m['order_status']})" for m in matches]
        conn.close()
        return None, [], True, ambiguous_ids

    if len(matches) == 1:
        single_order_id = matches[0]['order_id']
        cursor.execute("SELECT o.*, c.full_name, c.phone_number, c.city, c.tier FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_id = ?", (single_order_id,))
        order_dict = dict(cursor.fetchone())
        cursor.execute("SELECT * FROM shipment_tracking_events WHERE order_id = ? ORDER BY event_timestamp DESC", (order_dict['order_id'],))
        events = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return order_dict, events, False, []

    conn.close()
    return None, [], False, []

def check_return_eligibility(order_dict: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Pure Python deterministic check for 7-day return policy.
    Never relies on model arithmetic.
    """
    if order_dict.get('order_status') != 'DELIVERED':
        return False, f"Order status is '{order_dict.get('order_status')}', not DELIVERED. Returns can only be initiated on delivered orders."
    
    delivered_str = order_dict.get('delivered_date')
    if not delivered_str:
        return False, "Delivery date record missing in order database."
    
    try:
        delivered_date = datetime.strptime(delivered_str[:10], "%Y-%m-%d")
        days_since = (datetime.now() - delivered_date).days
        if days_since <= 7:
            return True, f"Eligible for return (Delivered {days_since} days ago; within 7-day window)."
        else:
            return False, f"Return window expired ({days_since} days since delivery. Dhaga policy is strictly 7 days)."
    except Exception as e:
        return False, f"Date calculation error: {str(e)}"

def save_audit_record(audit_data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO ticket_triage_audit (
            ticket_id, matched_order_id, predicted_intent, sentiment,
            extracted_entities, router_confidence, deterministic_policy_check,
            order_lookup_success, generated_draft, evaluator_passed,
            evaluator_score, evaluator_reasoning, dispatch_mode,
            final_response_sent, agent_id, agent_modified_draft,
            model_router_name, model_evaluator_name, input_tokens,
            output_tokens, cost_inr, execution_time_ms
        ) VALUES (
            :ticket_id, :matched_order_id, :predicted_intent, :sentiment,
            :extracted_entities, :router_confidence, :deterministic_policy_check,
            :order_lookup_success, :generated_draft, :evaluator_passed,
            :evaluator_score, :evaluator_reasoning, :dispatch_mode,
            :final_response_sent, :agent_id, :agent_modified_draft,
            :model_router_name, :model_evaluator_name, :input_tokens,
            :output_tokens, :cost_inr, :execution_time_ms
        )
    """, audit_data)
    
    # Also update support_tickets status
    new_status = 'AUTO_RESOLVED' if audit_data.get('dispatch_mode') == 'AUTO_DISPATCH' else 'PENDING_AGENT_REVIEW'
    if audit_data.get('predicted_intent') == 'ESCALATION_HOSTILE':
        new_status = 'ESCALATED'
        
    cursor.execute("UPDATE support_tickets SET ticket_status = ? WHERE ticket_id = ?", (new_status, audit_data['ticket_id']))
    conn.commit()
    conn.close()

def update_agent_review(ticket_id: str, approved_response: str, agent_id: str = "Agent_34", was_modified: bool = False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ticket_triage_audit 
        SET final_response_sent = ?, agent_id = ?, agent_modified_draft = ?, dispatch_mode = 'AGENT_DISPATCH'
        WHERE ticket_id = ?
    """, (approved_response, agent_id, 1 if was_modified else 0, ticket_id))
    cursor.execute("UPDATE support_tickets SET ticket_status = 'AGENT_RESOLVED' WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()

def escalate_ticket(ticket_id: str, reason: str = "Escalated by Agent to Senior Lead"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ticket_triage_audit 
        SET dispatch_mode = 'SUPERVISOR_ESCALATE', evaluator_reasoning = ?
        WHERE ticket_id = ?
    """, (reason, ticket_id))
    cursor.execute("UPDATE support_tickets SET ticket_status = 'ESCALATED' WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()

def get_all_tickets_view():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            t.ticket_id, t.source, t.customer_phone, t.raw_message, t.created_at, t.ticket_status,
            a.matched_order_id, a.predicted_intent, a.sentiment, a.extracted_entities, a.router_confidence,
            a.deterministic_policy_check, a.order_lookup_success, a.generated_draft, a.evaluator_passed,
            a.evaluator_score, a.evaluator_reasoning, a.dispatch_mode, a.final_response_sent,
            a.agent_id, a.agent_modified_draft, a.model_router_name, a.model_evaluator_name,
            a.input_tokens, a.output_tokens, a.cost_inr, a.execution_time_ms,
            o.product_name, o.product_category, o.total_amount, o.payment_mode, o.order_status,
            o.expected_delivery_date, o.courier_partner, o.awb_number, o.delivered_date, o.order_date,
            c.full_name, c.city, c.tier
        FROM support_tickets t
        LEFT JOIN ticket_triage_audit a ON t.ticket_id = a.ticket_id
        LEFT JOIN orders o ON a.matched_order_id = o.order_id
        LEFT JOIN customers c ON (o.customer_id = c.customer_id OR t.customer_phone = c.phone_number)
        ORDER BY t.ticket_id ASC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
