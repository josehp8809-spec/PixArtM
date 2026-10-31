-- ==============================================================
-- CASA AES - ESQUEMA DE BASE DE DATOS Y STORAGE (SUPABASE)
-- Copia y pega este script en el SQL Editor de tu panel de Supabase
-- ==============================================================

-- 1. Habilitar extensión UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Secuencia para Folios de Pedido y Código de Cliente
CREATE SEQUENCE IF NOT EXISTS public.order_folio_seq START 1001;
CREATE SEQUENCE IF NOT EXISTS public.customer_code_seq START 1;

-- 3. Tabla de Menú (Platillos de Fin de Semana y Comida del Día)
CREATE TABLE IF NOT EXISTS public.menu_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio NUMERIC(10,2) NOT NULL,
    tipo_menu TEXT NOT NULL CHECK (tipo_menu IN ('fin_de_semana', 'comida_del_dia')),
    categoria TEXT DEFAULT 'carnitas',
    disponible BOOLEAN DEFAULT true,
    imagen_url TEXT,
    opciones JSONB DEFAULT '[]'::jsonb, -- e.g. ["Maciza", "Surtida", "Cuerito", "Costilla", "Campechano"]
    orden INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Platillos iniciales del menú fijo de Casa Aes
INSERT INTO public.menu_items (nombre, descripcion, precio, tipo_menu, categoria, disponible, opciones, orden)
VALUES 
    ('Taco de carnitas', 'Tradicional taco con tortilla caliente, cebolla, cilantro y salsa al gusto.', 35.00, 'fin_de_semana', 'carnitas', true, '["Surtida", "Maciza", "Cuerito", "Costilla", "Buche"]'::jsonb, 1),
    ('Cemita de carnitas', 'Deliciosa cemita poblana rellena de auténticas carnitas estilo Quiroga con pápalo y chipotle.', 45.00, 'fin_de_semana', 'carnitas', true, '["Surtida", "Maciza", "Cuerito", "Costilla"]'::jsonb, 2),
    ('Kilo de carnitas', '1 Kilo de carnitas surtidas o a elección. Incluye tortillas calientes, salsas y limones.', 350.00, 'fin_de_semana', 'carnitas', true, '["Surtida", "Maciza", "Costilla y Cuerito", "A elegir"]'::jsonb, 3),
    ('1/2 de carnitas', 'Medio kilo de carnitas con complementos tradicionales para compartir.', 175.00, 'fin_de_semana', 'carnitas', true, '["Surtida", "Maciza", "Costilla y Cuerito", "A elegir"]'::jsonb, 4),
    ('Chilaquiles Aes', 'Crujientes totopos bañados en salsa especial de la casa, coronados con carnitas tiernas, crema y queso.', 75.00, 'fin_de_semana', 'especialidades', true, '["Salsa Roja", "Salsa Verde"]'::jsonb, 5),
    ('Quesacazo', 'Tortilla dorada al cazo rellena de abundante queso fundido y carne de carnitas con un toque crujiente.', 55.00, 'fin_de_semana', 'especialidades', true, '["Surtida", "Maciza"]'::jsonb, 6),
    ('Empanada (camarón y queso)', 'Empanada frita artesanal rellena de camarón guisado y queso derretido.', 35.00, 'fin_de_semana', 'entradas', true, '[]'::jsonb, 7),
    -- Menú del Día de ejemplo
    ('Guisado del Día: Pechuga a la Cordon Bleu', 'Acompañada de ensalada fresca y arroz rojo tradicional.', 85.00, 'comida_del_dia', 'comida_corrida', true, '["Arroz", "Frijoles", "Ambos"]'::jsonb, 8),
    ('Sopa del Día: Sopa Azteca Tradicional', 'Caldo de jitomate con tiras de tortilla frita, queso, aguacate y crema.', 45.00, 'comida_del_dia', 'sopas', true, '[]'::jsonb, 9),
    ('Agua Fresca del Día (1 Litro)', 'Agua artesanal de fruta fresca de temporada (Horchata o Jamaica).', 30.00, 'comida_del_dia', 'bebidas', true, '["Horchata", "Jamaica"]'::jsonb, 10)
ON CONFLICT DO NOTHING;

-- 4. Tabla de Clientes
CREATE TABLE IF NOT EXISTS public.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo_cliente TEXT UNIQUE NOT NULL,
    telefono TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    alias TEXT,
    direccion TEXT,
    referencias TEXT,
    total_pedidos INT DEFAULT 1,
    notas_internas TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Tabla de Pedidos
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    folio INT DEFAULT nextval('public.order_folio_seq') UNIQUE NOT NULL,
    cliente_id UUID REFERENCES public.customers(id) ON DELETE SET NULL,
    nombre_cliente TEXT NOT NULL,
    telefono TEXT NOT NULL,
    tipo_entrega TEXT NOT NULL CHECK (tipo_entrega IN ('domicilio', 'local', 'recoger')),
    direccion TEXT,
    referencias TEXT,
    metodo_pago TEXT NOT NULL CHECK (metodo_pago IN ('efectivo', 'transferencia')),
    pago_con NUMERIC(10,2), -- Cuánto dinero dio si es en efectivo para cambio
    total NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    estado TEXT NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'cocina', 'en_camino', 'concluido', 'cancelado')),
    notas TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Detalle de Artículos por Pedido
CREATE TABLE IF NOT EXISTS public.order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES public.orders(id) ON DELETE CASCADE NOT NULL,
    platillo_id UUID REFERENCES public.menu_items(id) ON DELETE SET NULL,
    nombre_platillo TEXT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    opciones_seleccionadas TEXT,
    notas_personalizadas TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 7. Índices para Alto Rendimiento
CREATE INDEX IF NOT EXISTS idx_orders_estado ON public.orders(estado);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON public.orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_customers_telefono ON public.customers(telefono);
CREATE INDEX IF NOT EXISTS idx_menu_items_tipo ON public.menu_items(tipo_menu, disponible);

-- 8. Row Level Security (RLS) Permisivo para Operación Ágil
ALTER TABLE public.menu_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Lectura pública de menú" ON public.menu_items FOR SELECT USING (true);
CREATE POLICY "Gestión total de menú" ON public.menu_items FOR ALL USING (true);

CREATE POLICY "Lectura y registro de clientes" ON public.customers FOR ALL USING (true);
CREATE POLICY "Gestión de pedidos" ON public.orders FOR ALL USING (true);
CREATE POLICY "Gestión de artículos de pedido" ON public.order_items FOR ALL USING (true);

-- 9. Habilitar Tiempo Real (Supabase Realtime)
DO $$
BEGIN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.orders;
    ALTER PUBLICATION supabase_realtime ADD TABLE public.menu_items;
    ALTER PUBLICATION supabase_realtime ADD TABLE public.customers;
EXCEPTION WHEN OTHERS THEN
    -- En caso de que ya estuvieran agregadas
    NULL;
END $$;
