# SocietyMan - Quick Start Guide for New Features

## Getting Started

### First Time Setup

1. **Ensure Backend is Running**
   ```bash
   docker compose up postgres redis -d
   uvicorn app.main:app --reload
   ```

2. **Start Frontend**
   ```bash
   cd web-dashboard
   npm install
   npm run dev
   ```

3. **Access Application**
   - Admin: http://localhost:5173/admin
   - Regular: http://localhost:5173

---

## Feature Quick Access

### 👥 Member Management
**Path:** Society Admin → Members Management

**Common Tasks:**
| Task | Steps |
|------|-------|
| View all members | Members Management → View All Members |
| Add one member | Members Management → Add New Member → Fill form → Submit |
| Add 50+ members | Members Management → Bulk Import → Upload CSV |
| Approve member | Members Management → Member Approvals → Click Approve |
| Find a member | View All Members → Use search/filter |
| Edit member access | Click member row → Edit permissions |

**CSV Format for Bulk Import:**
```csv
full_name,email,phone,password,role
John Doe,john@example.com,9876543210,password123,resident
Jane Smith,jane@example.com,9876543211,password123,resident
```

**Expected Time:**
- Single member: 2 minutes
- Bulk import (100 members): 5 minutes

---

### 🅿️ Parking Management
**Path:** Society Admin → Parking Management

**Common Tasks:**
| Task | Steps |
|------|-------|
| View vehicles | Parking → Vehicles |
| View slots | Parking → Parking Slots |
| Generate report | Parking → Parking Reports |

**Features Available:**
- View total registered vehicles
- Monitor gate passes
- Track parking assignments
- Generate usage reports

**Expected Time:**
- View status: 1 minute
- Generate report: 2 minutes

---

### 💰 Billing Management
**Path:** Society Admin → Billing Management

**Common Tasks:**
| Task | Steps |
|------|-------|
| View all bills | Bills → Click "View All Bills" |
| Create new bill | Create Bill → Fill form → Submit |
| Check collections | View Bills → See dashboard summary |
| Generate report | Billing Reports → Select month |
| Send reminders | (Ready for WhatsApp integration) |

**Bill Creation Form:**
- Billing Month: Select from calendar
- Amount: Enter maintenance amount
- Description: Add bill details
- Auto-assigns to all members

**Expected Time:**
- View bills: 1 minute
- Create bill: 5 minutes
- Generate report: 2 minutes

---

### 🤝 Vendor Management
**Path:** Society Admin → Vendor Management

**Common Tasks:**
| Task | Steps |
|------|-------|
| View vendors | All Vendors → See directory |
| Add vendor | Add Vendor → Fill form → Submit |
| Track performance | Vendor Performance → View ratings |
| Track payments | Vendor Payments → View history |

**Vendor Registration:**
- Vendor Name: Business name
- Email: Contact email
- Phone: Contact number
- Category: Service type (Maintenance, Repair, Cleaning, etc.)
- Address: Business address

**Expected Time:**
- Add vendor: 3 minutes
- View performance: 2 minutes

---

### 📊 Reports & Analytics
**Path:** Society Admin → Reports

**Available Reports:**

**Billing Reports:**
- Monthly Billing Report - All bills for a month
- Outstanding Dues Report - Members not paid
- Collection Report - Payment tracking
- Vendor Payables Report - What you owe vendors

**Member Reports:**
- Member Directory - All members list
- New Members Report - Recently added
- Member Status Report - Active/Inactive
- Family Details Report - Resident info

**Operations Reports:**
- Staff Attendance - Daily attendance tracking
- Visitor Log - Guest entries
- Complaint Resolution - Ticket status
- Amenity Usage - Facility bookings

**Download Options:**
- CSV format - Spreadsheet compatible
- PDF format - Print friendly
- Excel format - Excel compatible

**Expected Time:**
- Generate report: 1 minute
- Download: 30 seconds

---

## Dashboard Overview

**Location:** Overview → Quick Links

Quick metrics shown:
- 👥 **Members** - Total registered + new
- 💵 **Billing** - Pending dues amount
- 🤝 **Vendors** - Total vendors
- 🚗 **Parking** - Vehicles registered

---

## Operations Health

**Location:** Operations Health tab

Real-time metrics:
- Total Assets
- AMC due renewals
- Inventory items
- Staff status
- Vehicle count
- Gate passes issued
- Amenity bookings
- Compliance status

---

## Common Workflows

### Workflow 1: New Resident Onboarding
```
1. Add member (Members → Add New Member)
2. Assign parking (Parking → Add Slot)
3. Create bill (Billing → Create Bill)
4. Send welcome notice (Communications → Ready)
Expected: 10 minutes
```

### Workflow 2: Vendor Management
```
1. Add vendor (Vendors → Add Vendor)
2. Assign work (Via tickets - future)
3. Track performance (Vendors → Performance)
4. Process payment (Vendors → Payments)
Expected: 15 minutes per vendor
```

### Workflow 3: Monthly Billing
```
1. Create bill (Billing → Create Bill → Select month)
2. Review pending (Billing → Bills List)
3. Generate report (Reports → Billing Reports)
4. Send reminder (Via WhatsApp - future)
5. Track collection (Billing → Track Payments)
Expected: 30 minutes for 100 residents
```

### Workflow 4: Bulk Member Import
```
1. Prepare CSV file with member data
2. Go to Members → Bulk Import
3. Upload CSV file
4. System imports all members
5. Approve members in approvals section
6. Send welcome emails
Expected: 5-10 minutes for 100 members
```

---

## Tips & Tricks

### 💡 Pro Tips

**Member Management:**
- Use CSV for more than 10 members
- Filter by role to find specific members
- Check pending approvals daily
- Set strong temporary passwords

**Billing:**
- Create bills on month start
- Send payment reminders mid-month
- Follow up on overdue bills
- Generate collection report end of month

**Vendors:**
- Rate vendors after each job
- Keep performance metrics updated
- Track all payments
- Maintain vendor contact list

**Reports:**
- Generate monthly for records
- Keep CSV copies for backup
- Share PDF with committee
- Use Excel for custom analysis

### ⚠️ Important Notes

- Always approve members before they can login
- Bills are auto-assigned to all approved members
- Vendors need to be registered before assigning work
- Keep passwords secure and change defaults
- Export reports regularly for backup

---

## Troubleshooting

### Common Issues

**Issue:** Members not appearing in list
- Solution: Ensure members are approved
- Check: Members → Pending → Approve

**Issue:** Bill not showing for member
- Solution: Ensure member is active
- Check: Members → View All → Status column

**Issue:** Bulk import not working
- Solution: Check CSV format
- Ensure: Headers are correct (full_name, email, phone, password, role)

**Issue:** Report download not working
- Solution: Try different format (CSV vs PDF)
- Check: Browser allows downloads

**Issue:** Vendor not showing
- Solution: Refresh page
- Check: Vendor was successfully added

---

## Feature Availability Matrix

| Feature | Status | Backend | Notes |
|---------|--------|---------|-------|
| Member Management | ✅ | ✅ | Fully working |
| Parking Management | ✅ | ✅ | Read-only for now |
| Billing Management | ✅ | ✅ | Ready for enhancement |
| Vendor Management | ✅ | 🔄 | UI ready, API pending |
| Reports (CSV) | ✅ | ✅ | Downloadable |
| Reports (PDF) | 🔄 | 🔄 | In development |
| Reports (Excel) | 🔄 | 🔄 | In development |
| WhatsApp Notifications | 🔄 | 🔄 | Configured, testing |
| Email Notifications | 🔄 | 🔄 | Configured, testing |
| Payment Gateway | 🔄 | 🔄 | Ready for integration |

---

## Keyboard Shortcuts (Coming Soon)

Will be available in future version:
- `Ctrl + M` - Go to Members
- `Ctrl + B` - Go to Billing
- `Ctrl + V` - Go to Vendors
- `Ctrl + R` - Generate Report
- `Ctrl + S` - Save/Submit form

---

## What to Do Next

### For Admins:
1. [ ] Add your first member
2. [ ] Set up parking slots
3. [ ] Create first bill
4. [ ] Add service vendors
5. [ ] Generate a report

### For Residents (When Approved):
1. [ ] Login to portal
2. [ ] Update profile
3. [ ] View billing information
4. [ ] Submit complaint ticket
5. [ ] View parking assignment

### For Developers:
1. [ ] Review `app/api/routes/` for available endpoints
2. [ ] Check `app/core/database.py` for schema
3. [ ] Read `docs/API.md` for full documentation
4. [ ] Set up local development environment
5. [ ] Create test data for features

---

## Support Resources

### Documentation
- 📖 `ENHANCEMENT_SUMMARY.md` - Detailed feature guide
- 📖 `IMPLEMENTATION_GUIDE.md` - Technical details
- 📖 `README.md` - Project overview
- 📖 `docs/API.md` - API endpoints

### API Endpoints
- `http://localhost:8000/docs` - Swagger UI
- `http://localhost:8000/redoc` - ReDoc

### Code Locations
- Frontend: `web-dashboard/src/App.jsx`
- Styles: `web-dashboard/src/styles.css`
- Backend: `app/api/routes/*.py`
- Database: `app/models/entities.py`

---

## Performance Tips

**For Optimal Performance:**
1. ✅ Keep browser cache enabled
2. ✅ Clear old reports regularly
3. ✅ Don't import more than 1000 members at once
4. ✅ Use filters to reduce data displayed
5. ✅ Close unused browser tabs

**Best Practices:**
1. ✅ Test with small dataset first
2. ✅ Use CSV for bulk operations
3. ✅ Keep backend running in background
4. ✅ Refresh data after major changes
5. ✅ Keep system updated

---

## Questions?

### Frequently Asked Questions

**Q: How often should I backup data?**
A: Export reports weekly and keep offsite backup.

**Q: Can I edit member details after adding?**
A: Yes, click on member row to edit.

**Q: What happens to bills if member leaves?**
A: Mark member as inactive. Bills remain in history.

**Q: How do I reset admin password?**
A: Use admin login code from `scripts/last_admin_code.txt`.

**Q: Can residents see other members' information?**
A: No, residents only see their own information.

**Q: How do I integrate payment gateway?**
A: See `docs/DEPLOYMENT.md` for payment setup.

---

## Latest Updates

**Version 2.0** (May 17, 2026):
- ✅ Member Management system
- ✅ Parking Management interface
- ✅ Billing Management dashboard
- ✅ Vendor Management system
- ✅ Reports generation
- ✅ CSV bulk import
- ✅ Enhanced UI/UX

**Coming Soon**:
- WhatsApp notifications
- PDF report generation
- Excel export
- Online payments
- Mobile app

---

## Getting Help

1. **Check Documentation** - Start with README.md
2. **Review API Docs** - http://localhost:8000/docs
3. **Check Logs** - Terminal/console for errors
4. **Search Issues** - GitHub issues (if applicable)
5. **Contact Support** - Email or support ticket

---

**Last Updated**: May 17, 2026
**Version**: 2.0 Quick Start
**Status**: Ready to Use ✅

Happy managing! 🎉
