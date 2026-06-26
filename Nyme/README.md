# Nyme — Plataforma WhatsApp Business

Plataforma de atención al cliente vía WhatsApp Business API. Multi-agente, multi-línea, con IA de Gemini integrada.

## Stack
- **Dashboard**: Streamlit (Python)
- **Webhook**: FastAPI + Uvicorn
- **Base de datos**: PostgreSQL
- **IA**: Google Gemini 1.5 Flash
- **Deploy**: Render.com

## Roles
| Rol | Acceso |
|-----|--------|
| Admin (max 2) | Todo: configuración, reportes, chat |
| Coordinador (max 3) | Reportes + chat |
| Agente (max 10) | Solo chat (sus líneas asignadas) |

## Setup local

### 1. Clonar y crear entorno
```bash
git clone <repo>
cd Nyme
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. Variables requeridas en `.env`
```
DB_HOST=localhost
DB_NAME=nyme_db
DB_USER=postgres
DB_PASS=tu_password
DB_PORT=5432

ADMIN_USER=admin
ADMIN_PASSWORD=cambia_esto_123

META_VERIFY_TOKEN=nyme_verify_2024

# Opcionales (se configuran desde el panel):
GEMINI_API_KEY=
```

### 4. Ejecutar
```bash
# Terminal 1 — Dashboard
streamlit run app.py

# Terminal 2 — Webhook (para desarrollo local)
python webhook.py
```

## Deploy en Render
Ver `render.yaml` — conecta el repo de GitHub y Render crea automáticamente:
- Servicio web para el Dashboard (Streamlit)
- Servicio web para el Webhook (FastAPI)
- Base de datos PostgreSQL

## Primer inicio
Al iniciar por primera vez sin usuarios, el sistema crea automáticamente
el usuario admin con las credenciales del `.env` (`ADMIN_USER` / `ADMIN_PASSWORD`).

## Configuración desde el panel
1. Inicia sesión como admin
2. Ve a ⚙️ Configuración → 📱 Líneas WhatsApp → agrega tu primera línea
3. Agrega tu API Key de Gemini en 🤖 Gemini AI
4. Crea usuarios en 👥 Gestión de Usuarios
5. Asigna agentes a líneas

## Seguridad
- Contraseñas hasheadas con bcrypt
- Webhook validado con firma SHA256 de Meta
- `.env` nunca debe subirse a GitHub (ver `.gitignore`)
