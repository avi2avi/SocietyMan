#!/usr/bin/env python
"""Direct DB seeder for SocietyMan - inserts societies, members, visitors, bills, and other feature data."""
import sys
sys.path.insert(0, '.')
from datetime import datetime, timedelta
from random import choice, randint

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.core.enums import Role, VisitorType, PaymentMethod, PaymentProvider
from app.models.entities import (
    Society,
    User,
    Unit,
    ResidentProfile,
    VisitorLog,
    Invoice,
    Payment,
    Tenant,
    Vendor,
    VendorInvoice,
    Asset,
    InventoryItem,
    StaffMember,
    StaffAttendance,
    Ticket,
    Notice,
    Document,
    WhatsAppMessageLog,
    PurchaseRequest,
    GatePass,
    Vehicle,
    ComplianceEvent,
    AIAutomationJob,
    WorkflowDefinition,
    ERPRecord,
    Notification,
)


def create_demo_data():
    societies_data = [
        ("Green Valley Apartments", "Bandra", "Maharashtra", "400050", "admin@greenvalle.com"),
        ("Skyline Towers", "Gurgaon", "Haryana", "122001", "admin@skyline.com"),
        ("Westend Park", "Bangalore", "Karnataka", "560001", "admin@westend.com"),
        ("Riverside Heights", "Delhi", "Delhi", "110001", "admin@riverside.com"),
        ("Pearl Residency", "Chennai", "Tamil Nadu", "600001", "admin@pearl.com"),
    ]

    first_names = ["Rajesh", "Priya", "Arun", "Sneha", "Vikram", "Anjali", "Rahul", "Neha", "Karan", "Pooja", "Deepak", "Zara"]
    last_names = ["Sharma", "Patel", "Verma", "Singh", "Reddy", "Kumar", "Nair", "Iyer", "Gupta", "Desai"]

    with SessionLocal() as db:
        created = {"societies": 0, "members": 0, "visitor_logs": 0, "invoices": 0, "payments": 0}

        for s_idx, (name, city, state, pincode, admin_email) in enumerate(societies_data):
            society = db.query(Society).filter(Society.name == name).first()
            if not society:
                society = Society(
                    name=name,
                    address=f"{100 + s_idx} Demo Street",
                    city=city,
                    state=state,
                    pincode=pincode,
                    admin_contact_name=f"{name} Admin",
                    admin_contact_email=admin_email,
                    admin_contact_phone="9999990000",
                    is_approved=True,
                    approved_at=datetime.utcnow(),
                )
                db.add(society)
                db.flush()
                created["societies"] += 1

            # Create units
            units = []
            buildings = ["Tower A", "Tower B"]
            for building in buildings:
                for unit_num in range(1, 6):
                    unit_number = f"{unit_num}01"
                    unit = Unit(building=building, unit_number=unit_number, unit_type="residential", parking_car_slots=1, parking_bike_slots=1)
                    db.add(unit)
                    db.flush()
                    units.append(unit)

            # Create residents
            for i in range(12):
                fname = first_names[i % len(first_names)]
                lname = last_names[i % len(last_names)]
                email = f"{fname.lower()}.{lname.lower()}{s_idx}@{name.lower().replace(' ', '')}.com"
                phone = f"9{900000000 + s_idx*100 + i}"
                if db.query(User).filter(User.email == email).first():
                    continue
                user = User(full_name=f"{fname} {lname}", email=email, phone=phone, password_hash=hash_password("resident123"), role=Role.RESIDENT, society_id=society.id, is_active=True)
                db.add(user)
                db.flush()
                created["members"] += 1

                rp = ResidentProfile(user_id=user.id, unit_id=units[i % len(units)].id, occupancy_type="owner", move_in_date=datetime.utcnow() - timedelta(days=365))
                db.add(rp)

                # Visitor logs (2 per resident)
                for v in range(2):
                    entry_date = datetime.utcnow() - timedelta(days=randint(10, 350))
                    visitor = VisitorLog(resident_user_id=user.id, visitor_name=choice(["Friend", "Delivery", "Family", "Service Provider"]), visitor_phone=f"98{7000000 + randint(0,9999999):07d}", visitor_type=choice([VisitorType.GUEST, VisitorType.DELIVERY]), purpose="visit", entry_at=entry_date, exit_at=entry_date + timedelta(hours=2))
                    db.add(visitor)
                    created["visitor_logs"] += 1

                # Invoices for last 12 months
                for m in range(12):
                    invoice_date = datetime.utcnow() - timedelta(days=30*(11-m))
                    billing_month = invoice_date.strftime("%Y-%m")
                    maintenance_charge = 3500
                    parking_charge = 500
                    special_levy = 1000 if m % 3 == 0 else 0
                    adjustments = -500 if m % 4 == 0 else 0
                    total_amount = maintenance_charge + parking_charge + special_levy + adjustments
                    invoice = Invoice(unit_id=units[i % len(units)].id, billing_month=billing_month, maintenance_charge=maintenance_charge, parking_charge=parking_charge, special_levy=special_levy, adjustments=adjustments, total_amount=total_amount, status=("paid" if m > 3 else ("pending" if m < 2 else "unpaid")))
                    db.add(invoice)
                    db.flush()
                    created["invoices"] += 1

                    # Payments for some invoices
                    if m > 3 and (m % 3 != 0):
                        payment = Payment(invoice_id=invoice.id, amount=total_amount, method=choice([PaymentMethod.UPI, PaymentMethod.NET_BANKING]), provider=PaymentProvider.RAZORPAY, provider_order_id=f"order_{invoice.id}_{m}", provider_payment_id=f"pay_{invoice.id}_{m}", reference_id=f"ref_{invoice.id}_{m}", paid_at=invoice_date + timedelta(days=5))
                        db.add(payment)
                        created["payments"] += 1

            # Create some vendors and vendor invoices
            for vendor_idx in range(3):
                vname = f"Vendor {s_idx}-{vendor_idx}"
                vendor = db.query(Vendor).filter(Vendor.name == vname).first()
                if not vendor:
                    vendor = Vendor(name=vname, category=choice(["Electrical", "Plumbing", "Security"]), contact_name="Vendor Contact", contact_phone=f"98{6000000 + vendor_idx}")
                    db.add(vendor)
                    db.flush()
                vinv = VendorInvoice(vendor_id=vendor.id, amount=randint(1000,10000), invoice_month=datetime.utcnow().strftime("%Y-%m"), status=choice(["pending","paid"]), description="Monthly vendor bill")
                db.add(vinv)

            # Assets & inventory
            asset = Asset(society_id=society.id, name="Generator", category="Electrical", location="Basement", purchase_value=50000, installed_at=datetime.utcnow() - timedelta(days=400), warranty_expires_at=datetime.utcnow() + timedelta(days=200), amc_expires_at=datetime.utcnow() + timedelta(days=365))
            db.add(asset)
            item = InventoryItem(society_id=society.id, name="Security Register", sku=f"SEC-{s_idx}", category="stationery", quantity=5, min_quantity=10, unit_cost=50)
            db.add(item)

            # Staff & attendance
            staff = StaffMember(society_id=society.id, full_name="Gate Guard", phone=f"98{5000000 + s_idx}", role="guard", department="security", shift_name="morning", is_active=True)
            db.add(staff)
            db.flush()
            attendance = StaffAttendance(staff_member_id=staff.id, society_id=society.id, check_in_at=datetime.utcnow() - timedelta(days=1), check_out_at=datetime.utcnow())
            db.add(attendance)

            # Tickets, notices, documents
            ticket = Ticket(resident_user_id=1 if db.query(User).first() else None, title="Leaky Tap", description="Kitchen tap leaking", status="open")
            db.add(ticket)
            notice = Notice(title="Annual AGM", body="AGM scheduled next month", created_by_user_id=1 if db.query(User).first() else None)
            db.add(notice)
            doc = Document(name="Bylaws", category="policy", file_url="/docs/bylaws.pdf", uploaded_by_user_id=1 if db.query(User).first() else None)
            db.add(doc)

            # WhatsApp message logs
            wa = WhatsAppMessageLog(user_id=1 if db.query(User).first() else None, provider="meta", message_body="Test message", status="queued")
            db.add(wa)

            # Purchase requests and gate passes
            pr = PurchaseRequest(society_id=society.id, requested_by_user_id=1 if db.query(User).first() else None, title="Buy bulbs", amount=2000, status="pending")
            db.add(pr)
            gp = GatePass(society_id=society.id, issued_to_name="Contractor", issued_to_phone="9876543210", pass_type="material", purpose="Delivery", status="issued", valid_from=datetime.utcnow(), valid_until=datetime.utcnow() + timedelta(days=1))
            db.add(gp)

            # Vehicles
            vehicle = Vehicle(society_id=society.id, registration_number=f"MH{9000 + s_idx}{randint(100,999)}", vehicle_type="car", owner_user_id=None)
            db.add(vehicle)

            # Compliance events
            ce = ComplianceEvent(society_id=society.id, event_type="safety", title="Fire Drill", description="Annual fire drill", status="open", due_at=datetime.utcnow() + timedelta(days=30))
            db.add(ce)

        # Platform-level AI automations and workflows
        if not db.query(AIAutomationJob).filter(AIAutomationJob.key == "dues-reminder").first():
            db.add(AIAutomationJob(key="dues-reminder", name="Dues Reminder", description="Reminds residents of overdue invoices", confidence_score=0.9, status="ready", scheduled_for=datetime.utcnow()))
        if not db.query(WorkflowDefinition).filter(WorkflowDefinition.key == "invoice-follow-up").first():
            db.add(WorkflowDefinition(key="invoice-follow-up", name="Invoice Follow Up", trigger="invoice.overdue", definition="Send reminder", tenant_key="platform"))

        # ERP records and notifications
        erp = ERPRecord(tenant_key="platform", module_key="maintenance-billing-accounting", record_type="report", title="Seeder run report", payload_json='{"note":"seeded demo"}', owner_user_id=None)
        db.add(erp)
        notif = Notification(user_id=1 if db.query(User).first() else None, tenant_key="platform", title="Data seeded", body="Comprehensive demo data inserted", channel="in-app")
        db.add(notif)

        # Tenant
        if not db.query(Tenant).filter(Tenant.slug == "societyman-demo").first():
            tenant = Tenant(name="SocietyMan Demo", slug="societyman-demo", region="IN", plan="society-pro")
            db.add(tenant)

        db.commit()

        print("Seeding summary:")
        for k, v in created.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    create_demo_data()
    print("Done.")
