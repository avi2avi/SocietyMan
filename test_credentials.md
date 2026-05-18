# Test Credentials for Society Management App

## Developer Admin Account
- Email: admin@gmail.com
- Password: Admin@123
- Role: Admin
- Access: Full platform administration, society approval, user management, and demo seeding

## Society Admin Account
- Email: admin@society.com
- Password: admin123
- Role: Society Admin
- Access: Society operations, member management, billing, gatekeeper, reports

## Gatekeeper Account
- Email: gatekeeper@society.com
- Password: gate123
- Role: Gatekeeper
- Access: Log visitors, view visitor history

## Resident Accounts

### Resident 1
- Email: resident1@society.com
- Password: resident123
- Name: Priya Sharma
- Unit: A-1

### Resident 2
- Email: resident2@society.com
- Password: resident123
- Name: Rahul Verma
- Unit: A-2

### Resident 3
- Email: resident3@society.com
- Password: resident123
- Name: Anjali Patel
- Unit: A-3

### Resident 4
- Email: resident4@society.com
- Password: resident123
- Name: Vikram Singh
- Unit: A-4

### Resident 5
- Email: resident5@society.com
- Password: resident123
- Name: Sneha Reddy
- Unit: A-5

## Society Information
- Name: Green Valley Apartments
- Address: 123 Main Street, Mumbai, Maharashtra 400001
- Total Units: 20 (10 in Building A, 10 in Building B)

## Sample Data Included
- 3 Visitor records (1 inside, 2 exited)
- 10 Bills (5 paid, 5 unpaid)
- 3 Notices (1 urgent, 2 normal)
- 3 Complaints (1 open, 1 in progress, 1 resolved)
- 3 Vendors (Security, Plumbing, Housekeeping)
- 2 Expense records

## Notes
- Start the backend and log in with `admin@gmail.com / Admin@123`.
- Use the developer panel to seed demo data via `POST /api/v1/erp/demo/seed`.
- Once seeded, open `Members Management` to see the sample residents.
