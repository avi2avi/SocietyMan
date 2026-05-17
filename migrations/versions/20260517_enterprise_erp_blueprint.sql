-- Enterprise ERP additive migration blueprint for PostgreSQL/SQLite demo mode.
-- The current SQLAlchemy app also creates these tables through metadata for local demos.
CREATE TABLE IF NOT EXISTS tenants (
  id INTEGER PRIMARY KEY,
  uuid VARCHAR(36) NOT NULL UNIQUE,
  name VARCHAR(160) NOT NULL,
  slug VARCHAR(120) NOT NULL UNIQUE,
  region VARCHAR(20) DEFAULT 'IN',
  plan VARCHAR(40) DEFAULT 'starter',
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME,
  updated_at DATETIME,
  deleted_at DATETIME
);
CREATE INDEX IF NOT EXISTS ix_tenants_slug ON tenants(slug);
CREATE TABLE IF NOT EXISTS erp_records (
  id INTEGER PRIMARY KEY,
  uuid VARCHAR(36) NOT NULL UNIQUE,
  tenant_key VARCHAR(120) NOT NULL,
  module_key VARCHAR(80) NOT NULL,
  record_type VARCHAR(80) NOT NULL,
  title VARCHAR(200) NOT NULL,
  status VARCHAR(60) DEFAULT 'draft',
  payload_json TEXT DEFAULT '{}',
  owner_user_id INTEGER,
  created_at DATETIME,
  updated_at DATETIME,
  deleted_at DATETIME
);
CREATE INDEX IF NOT EXISTS ix_erp_records_tenant_module_status ON erp_records(tenant_key, module_key, status, deleted_at);
