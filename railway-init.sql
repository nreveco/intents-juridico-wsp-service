-- ══════════════════════════════════════════════════════════════
-- WhatsApp AI Automation - Railway Database Schema
-- ══════════════════════════════════════════════════════════════
-- Based on SQLAlchemy models from app/db/models.py
-- PostgreSQL 16+
-- ══════════════════════════════════════════════════════════════

-- Drop existing tables (in correct order to respect FK constraints)
DROP TABLE IF EXISTS quote_items CASCADE;
DROP TABLE IF EXISTS quotes CASCADE;
DROP TABLE IF EXISTS leads CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS case_inquiries CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS fee_structures CASCADE;
DROP TABLE IF EXISTS legal_services CASCADE;
DROP TABLE IF EXISTS legal_categories CASCADE;
DROP TABLE IF EXISTS business_settings CASCADE;
DROP TABLE IF EXISTS businesses CASCADE;

-- Drop enum types if they exist
DROP TYPE IF EXISTS businesstype CASCADE;
DROP TYPE IF EXISTS conversationstatus CASCADE;
DROP TYPE IF EXISTS bookingstatus CASCADE;
DROP TYPE IF EXISTS quotestatus CASCADE;
DROP TYPE IF EXISTS legalarea CASCADE;
DROP TYPE IF EXISTS caseurgency CASCADE;
DROP TYPE IF EXISTS caseinquirystatus CASCADE;

-- ══════════════════════════════════════════════════════════════
-- ENUM TYPES
-- ══════════════════════════════════════════════════════════════

CREATE TYPE businesstype AS ENUM (
    'restaurant',
    'cafe',
    'shop',
    'workshop',
    'clinic',
    'construction',
    'liquor_store',
    'law_firm',
    'other'
);

CREATE TYPE conversationstatus AS ENUM (
    'active',
    'human_handoff',
    'closed'
);

CREATE TYPE bookingstatus AS ENUM (
    'pending',
    'confirmed',
    'cancelled'
);

CREATE TYPE quotestatus AS ENUM (
    'draft',
    'sent',
    'accepted',
    'rejected'
);

CREATE TYPE legalarea AS ENUM (
    'penal',
    'familia',
    'civil'
);

CREATE TYPE caseurgency AS ENUM (
    'low',
    'medium',
    'high'
);

CREATE TYPE caseinquirystatus AS ENUM (
    'pending',
    'in_review',
    'accepted',
    'rejected',
    'closed'
);

-- ══════════════════════════════════════════════════════════════
-- CORE TABLES
-- ══════════════════════════════════════════════════════════════

-- Business (multi-tenant core)
CREATE TABLE businesses (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    phone_number_id VARCHAR(50) UNIQUE NOT NULL,
    whatsapp_token VARCHAR(500) NOT NULL,
    business_type businesstype DEFAULT 'other',
    welcome_message TEXT,
    human_support_phone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Business Settings
CREATE TABLE business_settings (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) UNIQUE NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    address VARCHAR(500),
    city VARCHAR(100),
    maps_url VARCHAR(500),
    hours JSONB DEFAULT '{}'::jsonb,
    currency VARCHAR(10) DEFAULT 'CLP',
    currency_symbol VARCHAR(5) DEFAULT '$'
);

-- ══════════════════════════════════════════════════════════════
-- LEGAL CATALOG
-- ══════════════════════════════════════════════════════════════

-- Legal Categories
CREATE TABLE legal_categories (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    area legalarea NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Legal Services
CREATE TABLE legal_services (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    category_id VARCHAR(36) REFERENCES legal_categories(id) ON DELETE SET NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    base_price FLOAT,
    estimated_timeframe VARCHAR(100),
    requirements TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Fee Structures
CREATE TABLE fee_structures (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    service_type VARCHAR(200) NOT NULL,
    description TEXT,
    min_price FLOAT,
    max_price FLOAT,
    payment_options JSONB DEFAULT '[]'::jsonb,
    payment_facilities TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ══════════════════════════════════════════════════════════════
-- CONVERSATIONS & MESSAGES
-- ══════════════════════════════════════════════════════════════

-- Conversations
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    customer_phone VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200),
    status conversationstatus DEFAULT 'active',
    context JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Messages
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    direction VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    intent VARCHAR(50),
    wa_message_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ══════════════════════════════════════════════════════════════
-- CASE INQUIRIES (Legal Cases)
-- ══════════════════════════════════════════════════════════════

CREATE TABLE case_inquiries (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    customer_phone VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200),
    legal_area legalarea,
    legal_matter VARCHAR(200),
    description TEXT,
    urgency caseurgency DEFAULT 'medium',
    is_detained BOOLEAN DEFAULT FALSE,
    has_prior_record BOOLEAN,
    benefit_type VARCHAR(200),
    status caseinquirystatus DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- ══════════════════════════════════════════════════════════════
-- BOOKINGS
-- ══════════════════════════════════════════════════════════════

CREATE TABLE bookings (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    customer_phone VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200),
    datetime_requested VARCHAR(200),
    datetime_confirmed TIMESTAMP WITH TIME ZONE,
    service VARCHAR(200),
    notes TEXT,
    status bookingstatus DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ══════════════════════════════════════════════════════════════
-- LEADS
-- ══════════════════════════════════════════════════════════════

CREATE TABLE leads (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    phone VARCHAR(50) NOT NULL,
    name VARCHAR(200),
    first_intent VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ══════════════════════════════════════════════════════════════
-- QUOTES
-- ══════════════════════════════════════════════════════════════

CREATE TABLE quotes (
    id VARCHAR(36) PRIMARY KEY,
    business_id VARCHAR(36) NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    customer_phone VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200),
    description TEXT NOT NULL,
    notes TEXT,
    status quotestatus DEFAULT 'draft',
    total FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE quote_items (
    id VARCHAR(36) PRIMARY KEY,
    quote_id VARCHAR(36) NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
    description VARCHAR(300) NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit_price FLOAT NOT NULL
);

-- ══════════════════════════════════════════════════════════════
-- INDEXES FOR PERFORMANCE
-- ══════════════════════════════════════════════════════════════

CREATE INDEX idx_businesses_phone ON businesses(phone_number_id);
CREATE INDEX idx_conversations_business ON conversations(business_id);
CREATE INDEX idx_conversations_phone ON conversations(customer_phone);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(created_at);
CREATE INDEX idx_case_inquiries_business ON case_inquiries(business_id);
CREATE INDEX idx_case_inquiries_status ON case_inquiries(status);
CREATE INDEX idx_case_inquiries_phone ON case_inquiries(customer_phone);
CREATE INDEX idx_bookings_business ON bookings(business_id);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_leads_business ON leads(business_id);
CREATE INDEX idx_quotes_business ON quotes(business_id);
CREATE INDEX idx_legal_services_business ON legal_services(business_id);
CREATE INDEX idx_legal_categories_business ON legal_categories(business_id);

-- ══════════════════════════════════════════════════════════════
-- DEMO DATA (Optional - comment out for production)
-- ══════════════════════════════════════════════════════════════

-- Demo Business: Law Firm
INSERT INTO businesses (id, name, phone_number_id, whatsapp_token, business_type, welcome_message, human_support_phone, is_active)
VALUES (
    'demo-law-firm-001',
    'Estudio Jurídico Demo',
    'DEMO_PHONE_ID',
    'DEMO_TOKEN',
    'law_firm',
    '¡Hola! 👋 Bienvenido a nuestro estudio jurídico. ¿En qué podemos ayudarte hoy?',
    '+56912345678',
    TRUE
);

-- Business Settings
INSERT INTO business_settings (id, business_id, address, city, maps_url, hours, currency, currency_symbol)
VALUES (
    'demo-settings-001',
    'demo-law-firm-001',
    'Av. Libertador Bernardo O''Higgins 1234, Oficina 567',
    'Santiago',
    'https://maps.google.com/?q=Santiago+Centro',
    '{"lunes": "09:00-18:00", "martes": "09:00-18:00", "miércoles": "09:00-18:00", "jueves": "09:00-18:00", "viernes": "09:00-18:00"}'::jsonb,
    'CLP',
    '$'
);

-- Legal Categories
INSERT INTO legal_categories (id, business_id, area, name, description, is_active)
VALUES 
    ('cat-penal-001', 'demo-law-firm-001', 'penal', 'Defensa Penal', 'Defensa en causas penales y delitos', TRUE),
    ('cat-familia-001', 'demo-law-firm-001', 'familia', 'Derecho de Familia', 'Divorcios, pensiones alimenticias, tuiciones', TRUE),
    ('cat-civil-001', 'demo-law-firm-001', 'civil', 'Derecho Civil', 'Contratos, arrendamientos, indemnizaciones', TRUE);

-- Legal Services
INSERT INTO legal_services (id, business_id, category_id, name, description, base_price, estimated_timeframe, requirements, is_available)
VALUES 
    ('srv-001', 'demo-law-firm-001', 'cat-penal-001', 'Defensa Ley 20.000', 'Defensa penal en casos de tráfico de drogas', 500000, '3-6 meses', 'Documentos de identidad, antecedentes del caso', TRUE),
    ('srv-002', 'demo-law-firm-001', 'cat-penal-001', 'Defensa VIF', 'Defensa en casos de violencia intrafamiliar', 300000, '2-4 meses', 'Denuncia, certificados médicos si aplica', TRUE),
    ('srv-003', 'demo-law-firm-001', 'cat-familia-001', 'Divorcio de Común Acuerdo', 'Tramitación de divorcio consensuado', 200000, '1-2 meses', 'Certificado de matrimonio, acuerdo de voluntades', TRUE),
    ('srv-004', 'demo-law-firm-001', 'cat-familia-001', 'Pensión Alimenticia', 'Demanda o defensa en pensión alimenticia', 250000, '2-3 meses', 'Certificados de nacimiento, liquidaciones de sueldo', TRUE);

-- Fee Structures
INSERT INTO fee_structures (id, business_id, service_type, description, min_price, max_price, payment_options, payment_facilities)
VALUES 
    ('fee-001', 'demo-law-firm-001', 'Ley 20.000', 'Honorarios por defensa en casos de tráfico', 500000, 1500000, '["Transferencia", "Efectivo", "Tarjeta"]'::jsonb, 'Pago en cuotas disponible según el caso'),
    ('fee-002', 'demo-law-firm-001', 'VIF', 'Honorarios por defensa en violencia intrafamiliar', 300000, 800000, '["Transferencia", "Efectivo"]'::jsonb, 'Primera consulta gratis'),
    ('fee-003', 'demo-law-firm-001', 'Divorcio', 'Honorarios por tramitación de divorcio', 200000, 500000, '["Transferencia", "Tarjeta"]'::jsonb, 'Pago en 2 cuotas');

-- ══════════════════════════════════════════════════════════════
-- VERIFICATION QUERIES
-- ══════════════════════════════════════════════════════════════

-- Verify tables were created
SELECT 
    schemaname,
    tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- Count records
SELECT 'businesses' as table_name, COUNT(*) as records FROM businesses
UNION ALL
SELECT 'legal_categories', COUNT(*) FROM legal_categories
UNION ALL
SELECT 'legal_services', COUNT(*) FROM legal_services
UNION ALL
SELECT 'fee_structures', COUNT(*) FROM fee_structures;

-- Show business info
SELECT 
    b.name,
    b.business_type,
    b.phone_number_id,
    COUNT(DISTINCT lc.id) as categories,
    COUNT(DISTINCT ls.id) as services
FROM businesses b
LEFT JOIN legal_categories lc ON lc.business_id = b.id
LEFT JOIN legal_services ls ON ls.business_id = b.id
GROUP BY b.id, b.name, b.business_type, b.phone_number_id;
