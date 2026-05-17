-- PostgreSQL migration blueprint for the SocietyMan operations ERP layer.
-- SQLAlchemy metadata creates these tables automatically in local/dev runs.

CREATE TABLE IF NOT EXISTS assets (
  id BIGSERIAL PRIMARY KEY,
  society_id INTEGER NOT NULL REFERENCES societies(id),
  name VARCHAR(160) NOT NULL,
  category VARCHAR(80) NOT NULL,
  location VARCHAR(160) NOT NULL,
  vendor_id INTEGER REFERENCES vendors(id),
  manufacturer VARCHAR(120),
  model_number VARCHAR(120),
  purchase_value DOUBLE PRECISION DEFAULT 0,
  installed_at TIMESTAMP,
  warranty_expires_at TIMESTAMP,
  amc_expires_at TIMESTAMP,
  maintenance_cycle_days INTEGER DEFAULT 90,
  status VARCHAR(40) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_assets_society_category_status ON assets(society_id, category, status);
CREATE INDEX IF NOT EXISTS ix_assets_amc_expires_at ON assets(amc_expires_at);

CREATE TABLE IF NOT EXISTS inventory_items (
  id BIGSERIAL PRIMARY KEY,
  society_id INTEGER NOT NULL REFERENCES societies(id),
  name VARCHAR(160) NOT NULL,
  sku VARCHAR(80) NOT NULL,
  category VARCHAR(80) NOT NULL,
  location VARCHAR(160) DEFAULT 'main store',
  quantity DOUBLE PRECISION DEFAULT 0,
  min_quantity DOUBLE PRECISION DEFAULT 0,
  unit_cost DOUBLE PRECISION DEFAULT 0,
  vendor_id INTEGER REFERENCES vendors(id),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_inventory_society_category ON inventory_items(society_id, category);
CREATE INDEX IF NOT EXISTS ix_inventory_sku ON inventory_items(sku);

CREATE TABLE IF NOT EXISTS staff_members (
  id BIGSERIAL PRIMARY KEY,
  society_id INTEGER NOT NULL REFERENCES societies(id),
  full_name VARCHAR(120) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  role VARCHAR(80) NOT NULL,
  department VARCHAR(80),
  shift_name VARCHAR(80),
  id_proof_type VARCHAR(80),
  id_proof_number VARCHAR(120),
  passcode VARCHAR(12),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_staff_members_society_role ON staff_members(society_id, role, is_active);
CREATE INDEX IF NOT EXISTS ix_staff_members_phone ON staff_members(phone);

CREATE TABLE IF NOT EXISTS staff_attendance (
  id BIGSERIAL PRIMARY KEY,
  staff_member_id INTEGER NOT NULL REFERENCES staff_members(id),
  society_id INTEGER NOT NULL REFERENCES societies(id),
  check_in_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  check_out_at TIMESTAMP,
  status VARCHAR(40) DEFAULT 'present'
);

CREATE INDEX IF NOT EXISTS ix_staff_attendance_society_checkin ON staff_attendance(society_id, check_in_at, check_out_at);

CREATE TABLE IF NOT EXISTS vehicles (
  id BIGSERIAL PRIMARY KEY,
  society_id INTEGER NOT NULL REFERENCES societies(id),
  unit_id INTEGER REFERENCES units(id),
  owner_user_id INTEGER REFERENCES users(id),
  registration_number VARCHAR(40) NOT NULL,
  vehicle_type VARCHAR(40) DEFAULT 'car',
  sticker_number VARCHAR(80),
  parking_slot VARCHAR(80),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_vehicles_society_active ON vehicles(society_id, is_active);
CREATE INDEX IF NOT EXISTS ix_vehicles_registration_number ON vehicles(registration_number);

CREATE TABLE IF NOT EXISTS gate_passes (
  id BIGSERIAL PRIMARY KEY,
  society_id INTEGER NOT NULL REFERENCES societies(id),
  issued_to_name VARCHAR(120) NOT NULL,
  issued_to_phone VARCHAR(20),
  pass_type VARCHAR(60) DEFAULT 'material',
  purpose VARCHAR(200),
  status VARCHAR(40) DEFAULT 'issued',
  valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  valid_until TIMESTAMP,
  created_by_user_id INTEGER REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_gate_passes_society_status ON gate_passes(society_id, status, valid_from);

CREATE TABLE IF NOT EXISTS purchase_requests (
  id BIGSERIAL PRIMARY KEY,
  society_id INTEGER NOT NULL REFERENCES societies(id),
  requested_by_user_id INTEGER NOT NULL REFERENCES users(id),
  vendor_id INTEGER REFERENCES vendors(id),
  title VARCHAR(180) NOT NULL,
  description TEXT,
  amount DOUBLE PRECISION DEFAULT 0,
  status VARCHAR(40) DEFAULT 'pending',
  approval_level VARCHAR(60) DEFAULT 'committee',
  approved_by_user_id INTEGER REFERENCES users(id),
  approved_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_purchase_requests_society_status ON purchase_requests(society_id, status, created_at);

CREATE TABLE IF NOT EXISTS amenity_bookings (
  id BIGSERIAL PRIMARY KEY,
  society_id INTEGER NOT NULL REFERENCES societies(id),
  amenity_name VARCHAR(120) NOT NULL,
  unit_id INTEGER REFERENCES units(id),
  resident_user_id INTEGER NOT NULL REFERENCES users(id),
  starts_at TIMESTAMP NOT NULL,
  ends_at TIMESTAMP NOT NULL,
  amount DOUBLE PRECISION DEFAULT 0,
  status VARCHAR(40) DEFAULT 'booked',
  payment_status VARCHAR(40) DEFAULT 'unpaid',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_amenity_bookings_society_start ON amenity_bookings(society_id, amenity_name, starts_at);

CREATE TABLE IF NOT EXISTS compliance_events (
  id BIGSERIAL PRIMARY KEY,
  society_id INTEGER NOT NULL REFERENCES societies(id),
  event_type VARCHAR(80) NOT NULL,
  title VARCHAR(180) NOT NULL,
  description TEXT,
  status VARCHAR(40) DEFAULT 'open',
  due_at TIMESTAMP,
  closed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_compliance_events_society_type_status ON compliance_events(society_id, event_type, status);
CREATE INDEX IF NOT EXISTS ix_compliance_events_due_at ON compliance_events(due_at);
