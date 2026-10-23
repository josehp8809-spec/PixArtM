-- ==============================================================
-- SUBLI ART M - ESQUEMA DE BASE DE DATOS Y STORAGE (SUPABASE)
-- Copia y pega este script en el SQL Editor de tu panel de Supabase
-- ==============================================================

-- 1. Tabla de Categorías del Taller
CREATE TABLE IF NOT EXISTS public.categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT DEFAULT 'sparkles',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Categorías iniciales por defecto
INSERT INTO public.categories (name, description, icon)
VALUES 
    ('Sublimación', 'Tazas, termos, playeras, cojines y textiles con tintas indelebles.', 'coffee'),
    ('Corte Láser MDF & Acrílico', 'Esferas, letreros calados, centros de mesa y lámparas 3D.', 'scissors'),
    ('Vinil & Gran Formato', 'Stickers troquelados, rotulación vehicular, lonas y vinil textil.', 'printer'),
    ('Edición & Diseño Gráfico', 'Invitaciones interactivas, logotipos, vectores de corte y video reels.', 'palette')
ON CONFLICT (name) DO NOTHING;

-- 2. Tabla de Trabajos / Productos Publicados
CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    price_range TEXT,
    description TEXT NOT NULL,
    tags TEXT[] DEFAULT '{}',
    is_seasonal BOOLEAN DEFAULT false,
    season_name TEXT,
    in_carousel BOOLEAN DEFAULT true,
    image_url TEXT NOT NULL,
    user_notes TEXT,
    ai_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Políticas de Seguridad RLS (Row Level Security)
ALTER TABLE public.categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;

-- Permitir lectura pública a cualquier visitante de la web
CREATE POLICY "Lectura pública de categorías" ON public.categories FOR SELECT USING (true);
CREATE POLICY "Lectura pública de productos" ON public.products FOR SELECT USING (true);

-- Permitir inserción y modificación a usuarios autenticados o con la anon key autorizada
CREATE POLICY "Gestión de categorías" ON public.categories FOR ALL USING (true);
CREATE POLICY "Gestión de productos" ON public.products FOR ALL USING (true);

-- ==============================================================
-- 3. Bucket de Storage para Fotografías en Alta Resolución
-- ==============================================================
INSERT INTO storage.buckets (id, name, public) 
VALUES ('product-images', 'product-images', true)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "Imágenes públicas de productos" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'product-images');

CREATE POLICY "Subida de imágenes de productos" 
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'product-images');
