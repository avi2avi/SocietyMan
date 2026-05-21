# SocietyMan x Society360 Integration Implementation Guide

**Date:** May 19, 2026  
**Phase:** Phase 1 - Core Enhancements  
**Status:** ✅ Implementation Complete

---

## 📦 What Was Added

### New Database Models
1. **VisitorApproval** - Pre-registration and approval workflow for visitors
2. **MaintenanceCategory** - Categorize maintenance requests
3. **MaintenanceWorkLog** - Track work progress on tickets
4. **MaintenanceRating** - Resident feedback on maintenance work
5. **AnnouncementEnhanced** - Enhanced announcements with types and scheduling
6. **ForumPostEnhanced** - Forum with tags and moderation
7. **BillCycle** - Monthly billing cycle management
8. **Receipt** - Digital receipts for payments
9. **Amenity** - Community amenities/facilities
10. **AmenityBooking** - Booking system for amenities

### New API Routes

#### 🔧 Maintenance Enhanced (`/api/maintenance`)
```
POST   /maintenance/categories              # Create maintenance category
GET    /maintenance/categories              # List all categories
POST   /maintenance/{id}/work-logs          # Add work log entry
GET    /maintenance/{id}/work-logs          # Get work logs
POST   /maintenance/{id}/rate               # Rate completed work
GET    /maintenance/{id}/rating             # Get rating/feedback
GET    /maintenance/analytics/summary       # Get analytics dashboard
```

#### 📢 Communications Enhanced (`/api/communications`)
```
POST   /communications/announcements         # Create announcement
GET    /communications/announcements         # List announcements
PATCH  /communications/announcements/{id}/publish  # Publish
GET    /communications/announcements/{id}   # Get & track views
POST   /communications/forum                # Create forum post
GET    /communications/forum                # List forum posts
GET    /communications/forum/{id}           # Get forum post
PATCH  /communications/forum/{id}/moderate  # Moderate post
```

#### 👥 Visitors Enhanced (`/api/visitors/enhanced`)
```
POST   /visitors/enhanced/pre-register      # Pre-register visitor
GET    /visitors/enhanced/pending-approvals # List pending approvals
PATCH  /visitors/enhanced/approvals/{id}    # Approve/reject visitor
GET    /visitors/enhanced/history           # Get visitor history
GET    /visitors/enhanced/analytics         # Get analytics
GET    /visitors/enhanced/passes/{id}       # Get QR pass
```

#### 🏛️ Amenities (`/api/amenities`)
```
POST   /amenities                           # Create amenity
GET    /amenities                           # List amenities
GET    /amenities/{id}                      # Get amenity details
POST   /amenities/{id}/bookings             # Book amenity
GET    /amenities/{id}/bookings             # List bookings
GET    /amenities/{id}/availability         # Check availability
PATCH  /amenities/{id}/bookings/{bid}/confirm  # Confirm booking
DELETE /amenities/{id}/bookings/{bid}       # Cancel booking
GET    /amenities/{id}/usage-stats          # Get usage statistics
```

---

## 🗄️ Database Migration Steps

### Step 1: Create Migration File
```bash
cd app/api
# Alembic will be used to handle database migrations
```

### Step 2: Run Migrations
```bash
# Using SQLAlchemy with the existing setup
python scripts/migrate_db.py
```

### Step 3: Verify Tables Created
All these new tables will be auto-created when the app starts (SQLAlchemy creates tables defined in Base.metadata):
- `visitor_approvals`
- `maintenance_categories`
- `maintenance_work_logs`
- `maintenance_ratings`
- `announcements_enhanced`
- `forum_posts_enhanced`
- `bill_cycles`
- `receipts`
- `amenities`
- `amenity_bookings`

---

## 🚀 How to Use the New Features

### 1. Visitor Pre-Approval System

**For Residents:**
```bash
# Pre-register a visitor
POST /api/visitors/enhanced/pre-register
{
  "visitor_log_id": 1,
  "vehicle_number": "MH02AB1234",
  "vehicle_type": "car",
  "parking_slot": "A-101"
}

# Check pending approvals
GET /api/visitors/enhanced/pending-approvals

# Get QR pass for approved visitor
GET /api/visitors/enhanced/passes/{approval_id}
```

**For Admin/Society Admin:**
```bash
# List all pending approvals
GET /api/visitors/enhanced/pending-approvals

# Approve visitor
PATCH /api/visitors/enhanced/approvals/{id}
{
  "approval_status": "approved",
  "parking_slot": "A-101"
}

# Reject with reason
PATCH /api/visitors/enhanced/approvals/{id}
{
  "approval_status": "rejected",
  "rejection_reason": "Insufficient information"
}
```

### 2. Enhanced Maintenance Management

**Create Category:**
```bash
POST /api/maintenance/categories
{
  "name": "Plumbing",
  "description": "Water supply and drainage issues",
  "icon": "🚰",
  "color": "#3b82f6",
  "sort_order": 1
}
```

**Add Work Log:**
```bash
POST /api/maintenance/{ticket_id}/work-logs
{
  "staff_user_id": 5,
  "description": "Fixed water leakage in bathroom",
  "hours_spent": 2.5
}
```

**Rate Maintenance:**
```bash
POST /api/maintenance/{ticket_id}/rate
{
  "rating": 4.5,
  "feedback": "Work was completed on time, but could be cleaner"
}
```

### 3. Announcements with Types

```bash
# Create Notice-type announcement
POST /api/communications/announcements
{
  "title": "Water Supply Maintenance",
  "content": "Water will be cut from 10 AM - 2 PM tomorrow",
  "announcement_type": "notice",
  "priority": "high"
}

# Create scheduled Event
POST /api/communications/announcements
{
  "title": "Annual Festival",
  "content": "Community festival on Dec 25th",
  "announcement_type": "event",
  "scheduled_for": "2026-12-25T18:00:00",
  "expires_at": "2026-12-26T00:00:00"
}

# List by type
GET /api/communications/announcements?announcement_type=event
```

### 4. Forum with Tags

```bash
# Create tagged forum post
POST /api/communications/forum
{
  "title": "Parking issues in Block A",
  "content": "Need to discuss better parking management",
  "category": "general",
  "tags": "parking,block-a,issues"
}

# Search by tag
GET /api/communications/forum?tag=parking

# Moderate post
PATCH /api/communications/forum/{post_id}/moderate?moderate=true
```

### 5. Amenities Booking

```bash
# List amenities
GET /api/amenities

# Check availability
GET /api/amenities/1/availability?start_datetime=2026-05-20T10:00:00&end_datetime=2026-05-20T12:00:00

# Book amenity
POST /api/amenities/1/bookings
{
  "start_datetime": "2026-05-20T10:00:00",
  "end_datetime": "2026-05-20T12:00:00",
  "purpose": "Birthday celebration"
}

# View bookings (Admin)
GET /api/amenities/1/bookings

# Get usage stats
GET /api/amenities/1/usage-stats
```

---

## 🔐 Permission Model

### Visitor Pre-Approval
- **Residents**: Can pre-register visitors, view their approvals
- **Society Admin**: Can approve/reject, view all pending
- **Platform Admin**: Can manage everything

### Maintenance Enhancement
- **Residents**: Can create tickets, view work logs, rate completion
- **Staff**: Can add work logs, update ticket status
- **Admin**: Full access to categories and analytics

### Announcements
- **Admins**: Create, publish, schedule announcements
- **All Users**: View published announcements

### Forum
- **Residents**: Create posts, view, comment
- **Admins**: Moderate posts, delete inappropriate content

### Amenities
- **Residents**: Book amenities, check availability
- **Admins**: Create amenities, confirm bookings, view analytics

---

## 🔄 API Response Format

All enhanced endpoints follow standard REST patterns with consistent response formats:

### Success Response (200, 201)
```json
{
  "id": 1,
  "society_id": 1,
  "field": "value",
  "created_at": "2026-05-19T10:00:00",
  "updated_at": "2026-05-19T10:00:00"
}
```

### Error Response (400, 403, 404)
```json
{
  "detail": "Error message describing the issue"
}
```

### List Response
```json
[
  { "id": 1, "field": "value" },
  { "id": 2, "field": "value" }
]
```

---

## 📊 Analytics Endpoints

### Maintenance Analytics
```bash
GET /api/maintenance/analytics/summary
```

Response:
```json
{
  "total_tickets": 45,
  "open": 12,
  "in_progress": 8,
  "resolved": 25,
  "resolution_rate": 55.56,
  "average_rating": 4.2,
  "top_categories": [
    { "name": "Plumbing", "count": 15 },
    { "name": "Electrical", "count": 12 }
  ]
}
```

### Visitor Analytics
```bash
GET /api/visitors/enhanced/analytics
```

Response:
```json
{
  "total_visits": 234,
  "visits_by_type": [
    { "type": "delivery", "count": 89 },
    { "type": "guest", "count": 145 }
  ],
  "approvals": {
    "approved": 200,
    "rejected": 12,
    "pending": 22,
    "approval_rate": 94.34
  }
}
```

### Amenity Usage
```bash
GET /api/amenities/{id}/usage-stats
```

Response:
```json
{
  "amenity_id": 1,
  "amenity_name": "Community Hall",
  "total_bookings": 50,
  "completed": 42,
  "confirmed": 5,
  "cancelled": 3,
  "pending": 0,
  "utilization_rate": 84.0
}
```

---

## 🧪 Testing the Integration

### Step 1: Start Backend
```bash
cd h:/SocietyMan/SocietyMan
python -m uvicorn app.main:app --reload
```

### Step 2: Test Endpoints

#### Create Maintenance Category
```bash
curl -X POST http://localhost:8000/api/maintenance/categories \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Plumbing",
    "icon": "🚰",
    "color": "#3b82f6"
  }'
```

#### Create Announcement
```bash
curl -X POST http://localhost:8000/api/communications/announcements \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "System Maintenance",
    "content": "System will be down on Sunday",
    "announcement_type": "notice",
    "priority": "high"
  }'
```

#### Create Amenity
```bash
curl -X POST http://localhost:8000/api/amenities \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Community Hall",
    "capacity": 100,
    "booking_price": 500
  }'
```

---

## 📋 Data Requirements

### For Maintenance Categories
- `name` (required): Category name like "Plumbing", "Electrical"
- `icon` (optional): Emoji or icon identifier
- `color` (optional): Hex color code for UI

### For Announcements
- `title` (required): Brief title
- `content` (required): Full announcement text
- `announcement_type` (required): "notice", "meeting", or "event"
- `priority` (optional): "low", "medium", "high"
- `scheduled_for` (optional): For scheduling future publication

### For Amenities
- `name` (required): Amenity name
- `capacity` (required): Maximum persons/slots
- `booking_price` (optional): Price per booking
- `rules` (optional): Rules/guidelines for using amenity

---

## 🚨 Known Limitations & Notes

1. **QR Code Generation**: Pass numbers are generated but QR code image generation requires additional library (qrcode)
2. **Email Notifications**: Currently not integrated, can be added via webhooks
3. **Payment Gateway**: Receipts are created but PDF generation requires jsPDF or ReportLab
4. **Recurring Amenities**: Single-slot bookings only, recurring bookings are not yet supported

---

## 🔗 Integration with Existing Features

### Visitor System
- Extends existing `VisitorLog` model
- New `VisitorApproval` table acts as approval workflow
- Compatible with existing visitor entry/exit logging

### Maintenance (Tickets)
- Enhancements to existing `Ticket` model
- New models for categorization and feedback
- Backward compatible with existing tickets

### Announcements
- New enhanced model alongside existing `Notice` model
- Existing endpoints continue to work
- Enhanced version offers more features

---

## 🎯 Next Steps (Phase 2)

### Recommended Enhancements:
1. **PDF Receipt Generation** - Add jsPDF for generating payment receipts
2. **QR Code Generation** - Add qrcode library for visitor passes
3. **Email Notifications** - Integrate with existing notification service
4. **Mobile App Frontend** - React components for new features
5. **Analytics Dashboard** - Visualization of metrics and trends
6. **Scheduled Tasks** - Auto-publish scheduled announcements, generate bills
7. **File Uploads** - Maintenance work photo documentation
8. **Multi-language Support** - Translate announcements and forum

---

## 📞 Support

For implementation questions or issues:
1. Check this guide first
2. Review API route definitions in respective files
3. Refer to Pydantic schemas for request/response formats
4. Check database models for relationships

---

**Integration Status:** ✅ Phase 1 Complete  
**Ready for:** Frontend Development, Testing, Phase 2 Planning
