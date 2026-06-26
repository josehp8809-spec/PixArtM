-- Database Schema para Nyme (WhatsApp Business Management)

-- Extensión para IDs únicos (opcional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tabla de Contactos
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wa_id VARCHAR(20) UNIQUE NOT NULL, -- WhatsApp ID (teléfono)
    name VARCHAR(100),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Mensajes (Gestión de Estados)
CREATE TYPE message_type AS ENUM ('INBOUND', 'OUTBOUND_REPLY', 'OUTBOUND_INIT');
CREATE TYPE message_status AS ENUM ('sent', 'delivered', 'read', 'failed');

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id UUID REFERENCES contacts(id),
    wa_message_id VARCHAR(100) UNIQUE, -- ID devuelto por Meta
    type message_type NOT NULL,
    body TEXT,
    template_name VARCHAR(100), -- Solo si es OUTBOUND_INIT
    status message_status DEFAULT 'sent',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla de Auditoría de Cuotas (Máximo 15 proactivos/mes)
CREATE TABLE quota_logs (
    id SERIAL PRIMARY KEY,
    type message_type NOT NULL DEFAULT 'OUTBOUND_INIT',
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB -- Para guardar detalles del envío
);

-- Índices para optimización
CREATE INDEX idx_messages_contact ON messages(contact_id);
CREATE INDEX idx_quota_logs_date ON quota_logs(sent_at);
