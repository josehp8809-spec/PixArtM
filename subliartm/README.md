# 🎨 Subli Art M - Catálogo Web & Studio Manager con IA Gemini

Sitio web oficial, catálogo interactivo y panel administrativo con **Google Gemini Flash** para el taller creativo **Subli Art M** (Sublimación, Corte Láser MDF, Vinil & Gran Formato, Diseño Gráfico y Edición de Video).

---

## 🌟 Características

1. **Sitio Web Público (`index.html`):**
   - Paleta luminosa, cálida y limpia (Alabastro `#F8FBFB` con acentos Teal/Aqua de la marca).
   - Carrusel interactivo automático para exhibir trabajos reales terminados.
   - Vitrina de productos de temporada (Día de Muertos, Navidad, San Valentín, Graduaciones).
   - Calculadora y cotizador rápido que arma el mensaje listo para WhatsApp con 1 clic.
   - Navegación móvil moderna y adaptable.

2. **Studio Manager & Asistente IA (`admin.html`):**
   - Diseñado para móvil y computadora (su esposa puede tomar una foto directo con el celular).
   - **Clasificador con Gemini Flash:**
     - Analiza la fotografía del trabajo y las notas rápidas de quien lo elaboró.
     - Asigna título comercial persuasivo.
     - Clasifica en la categoría correcta o **sugiere crear una nueva categoría automáticamente** si la técnica es diferente.
     - Redacta el texto publicitario para el cliente.
     - Sugiere rango de precios y etiquetas.
     - Detecta si corresponde a un especial de temporada.
   - Gestión visual del catálogo y categorías activas.

3. **Backend Serverless (`api/analyze.js`):**
   - Función Serverless para **Vercel** que ejecuta Gemini Flash de forma segura sin exponer la API key en el frontend.

---

## 🚀 Despliegue en Vercel (Paso a Paso)

1. En tu cuenta de **[Vercel](https://vercel.com)**:
   - Haz clic en **"Add New Project"** y selecciona tu repositorio `josehp8809-spec/PixArtM`.
   - En **Root Directory**, selecciona la carpeta `subliartm`.
   - En **Environment Variables**, agrega:
     - `GEMINI_API_KEY`: Tu clave de Google AI Studio (gratuita).
   - Haz clic en **Deploy**.

2. **Dominio en Cloudflare:**
   - En Cloudflare, ve a DNS de tu dominio comprado.
   - Agrega un registro `CNAME` apuntando a `cname.vercel-dns.com`.
   - En Vercel > Settings > Domains, agrega tu dominio.

---

## 🗄️ Base de Datos en Supabase (Opcional)

Si deseas sincronizar todo en la nube:
1. Crea un proyecto en [Supabase](https://supabase.com).
2. Ve a **SQL Editor**, pega y ejecuta el archivo [`supabase_schema.sql`](./supabase_schema.sql).
3. En `admin.html` (o Vercel), agrega las credenciales en el botón de Configuración.
