import psycopg2
import bcrypt
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class Database:
    def __init__(self):
        self.dsn = os.getenv("DATABASE_URL")
        if not self.dsn:
            self.conn_params = {
                "host":     os.getenv("DB_HOST", "localhost"),
                "dbname":   os.getenv("DB_NAME", "nyme_db"),
                "user":     os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASS", "password"),
                "port":     os.getenv("DB_PORT", "5432"),
            }
        else:
            self.conn_params = None
        self._available = None

    def _check_available(self):
        if self._available is not None:
            return self._available
        try:
            conn = self.get_connection()
            conn.close()
            self._available = True
        except Exception as e:
            print(f"[DB] No disponible: {e}")
            self._available = False
        return self._available

    def get_connection(self):
        if self.dsn:
            return psycopg2.connect(self.dsn)
        return psycopg2.connect(**self.conn_params)

    def init_db(self):
        """Crea todas las tablas necesarias. Retorna True si tuvo éxito."""
        if not self._check_available():
            return False
        commands = [
            # 1. Tenants (Empresas)
            """
            CREATE TABLE IF NOT EXISTS tenants (
                id         SERIAL PRIMARY KEY,
                name       VARCHAR(200) UNIQUE NOT NULL,
                is_active  BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # 2. Users (Usuarios)
            """
            CREATE TABLE IF NOT EXISTS users (
                id            SERIAL PRIMARY KEY,
                username      VARCHAR(100) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name     VARCHAR(200),
                role          VARCHAR(20) DEFAULT 'agent',
                is_active     BOOLEAN DEFAULT TRUE,
                last_seen     TIMESTAMP DEFAULT NOW(),
                created_at    TIMESTAMP DEFAULT NOW()
            )
            """,
            # 3. Lines (Líneas de WhatsApp)
            """
            CREATE TABLE IF NOT EXISTS lines (
                id              SERIAL PRIMARY KEY,
                name            VARCHAR(100) NOT NULL,
                phone_number_id VARCHAR(100) UNIQUE NOT NULL,
                access_token    TEXT NOT NULL,
                welcome_message TEXT,
                welcome_active  BOOLEAN DEFAULT TRUE,
                color           VARCHAR(20) DEFAULT '#0A84FF',
                is_active       BOOLEAN DEFAULT TRUE,
                created_at      TIMESTAMP DEFAULT NOW()
            )
            """,
            # 4. Products (Catálogo de Productos)
            """
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                price NUMERIC(10, 2) NOT NULL,
                image_url TEXT,
                is_seasonal BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # 5. Orders (Pedidos)
            """
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                wa_id VARCHAR(20) NOT NULL,
                agent_username VARCHAR(100),
                items JSONB NOT NULL,
                total_amount NUMERIC(10, 2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                shipping_address TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # 6. Messages (Mensajes)
            """
            CREATE TABLE IF NOT EXISTS messages (
                id             SERIAL PRIMARY KEY,
                wa_id          VARCHAR(20) NOT NULL,
                type           VARCHAR(50) NOT NULL,
                body           TEXT,
                media_id       VARCHAR(200),
                media_url      TEXT,
                agent_username VARCHAR(100),
                line_id        INTEGER REFERENCES lines(id),
                created_at     TIMESTAMP DEFAULT NOW()
            )
            """,
            # 7. Quota Logs (Cuotas)
            """
            CREATE TABLE IF NOT EXISTS quota_logs (
                id SERIAL PRIMARY KEY,
                type VARCHAR(20) DEFAULT 'OUTBOUND_INIT',
                agent_username VARCHAR(50),
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tenant_id INTEGER REFERENCES tenants(id) DEFAULT 1
            )
            """,
            # 8. Settings (Configuración)
            """
            CREATE TABLE IF NOT EXISTS settings (
                key VARCHAR(100) PRIMARY KEY,
                value TEXT
            )
            """,
            # 9. Sentiment Analysis (Análisis de Sentimiento)
            """
            CREATE TABLE IF NOT EXISTS sentiment_analysis (
                id          SERIAL PRIMARY KEY,
                wa_id       VARCHAR(20) NOT NULL,
                period_date DATE NOT NULL,
                sentiment   VARCHAR(20),
                urgent      BOOLEAN DEFAULT FALSE,
                reason      TEXT,
                analyzed_at TIMESTAMP DEFAULT NOW(),
                UNIQUE (wa_id, period_date)
            )
            """,
            # 10. Quick Replies (Respuestas Rápidas)
            """
            CREATE TABLE IF NOT EXISTS quick_replies (
                id        SERIAL PRIMARY KEY,
                shortcut  VARCHAR(50) UNIQUE NOT NULL,
                title     VARCHAR(100),
                message   TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # 11. User Lines (Líneas asignadas a usuarios)
            """
            CREATE TABLE IF NOT EXISTS user_lines (
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                line_id INTEGER REFERENCES lines(id) ON DELETE CASCADE,
                PRIMARY KEY (user_id, line_id)
            )
            """,
            # 12. Conversation Status (Estados de Chat)
            """
            CREATE TABLE IF NOT EXISTS conversation_status (
                wa_id       VARCHAR(20) NOT NULL,
                line_id     INTEGER REFERENCES lines(id) DEFAULT 1,
                status      VARCHAR(20) DEFAULT 'pending',
                unread      INTEGER DEFAULT 0,
                assigned_to VARCHAR(100),
                updated_at  TIMESTAMP DEFAULT NOW(),
                PRIMARY KEY (wa_id, line_id)
            )
            """,
            # 13. Internal Rooms (Chat Interno)
            """
            CREATE TABLE IF NOT EXISTS internal_rooms (
                id         SERIAL PRIMARY KEY,
                name       VARCHAR(200),
                is_group   BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # 14. Internal Room Members (Miembros de Chat Interno)
            """
            CREATE TABLE IF NOT EXISTS internal_room_members (
                room_id INTEGER REFERENCES internal_rooms(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                PRIMARY KEY (room_id, user_id)
            )
            """,
            # 15. Internal Messages (Mensajes Internos)
            """
            CREATE TABLE IF NOT EXISTS internal_messages (
                id         SERIAL PRIMARY KEY,
                room_id    INTEGER REFERENCES internal_rooms(id) ON DELETE CASCADE,
                username   VARCHAR(100) NOT NULL,
                message    TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # 16. Contacts (Contactos)
            """
            CREATE TABLE IF NOT EXISTS contacts (
                wa_id      VARCHAR(20) PRIMARY KEY,
                name       VARCHAR(200),
                email      VARCHAR(200),
                notes      TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # 17. AI Agents (Agentes IA)
            """
            CREATE TABLE IF NOT EXISTS ai_agents (
                id            SERIAL PRIMARY KEY,
                name          VARCHAR(100) NOT NULL,
                system_prompt TEXT NOT NULL,
                line_id       INTEGER REFERENCES lines(id) ON DELETE SET NULL,
                is_active     BOOLEAN DEFAULT TRUE,
                tenant_id     INTEGER REFERENCES tenants(id) DEFAULT 1
            )
            """,
            # 18. Message Templates (Plantillas)
            """
            CREATE TABLE IF NOT EXISTS message_templates (
                id         SERIAL PRIMARY KEY,
                name       VARCHAR(100) NOT NULL,
                category   VARCHAR(50),
                language   VARCHAR(10) DEFAULT 'es',
                body_text  TEXT NOT NULL,
                tenant_id  INTEGER REFERENCES tenants(id) DEFAULT 1,
                UNIQUE(name, tenant_id)
            )
            """,
            # 19. Workflows (Automatizaciones)
            """
            CREATE TABLE IF NOT EXISTS workflows (
                id              SERIAL PRIMARY KEY,
                name            VARCHAR(100) NOT NULL,
                trigger_type    VARCHAR(50) NOT NULL,
                condition_field VARCHAR(50) NOT NULL,
                condition_value VARCHAR(255) NOT NULL,
                action_type     VARCHAR(50) NOT NULL,
                action_value    VARCHAR(255) NOT NULL,
                is_active       BOOLEAN DEFAULT TRUE,
                tenant_id       INTEGER REFERENCES tenants(id) DEFAULT 1
            )
            """,
            # 20. Pre-registrations (Pre-registros de SaaS)
            """
            CREATE TABLE IF NOT EXISTS pre_registrations (
                id SERIAL PRIMARY KEY,
                company_name VARCHAR(200) NOT NULL,
                contact_name VARCHAR(200) NOT NULL,
                contact_email VARCHAR(200) UNIQUE NOT NULL,
                contact_phone VARCHAR(50),
                notes TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # 21. Support Rooms (Salas de soporte técnico)
            """
            CREATE TABLE IF NOT EXISTS support_rooms (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER UNIQUE REFERENCES tenants(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # 22. Support Messages (Mensajes de soporte técnico)
            """
            CREATE TABLE IF NOT EXISTS support_messages (
                id SERIAL PRIMARY KEY,
                room_id INTEGER REFERENCES support_rooms(id) ON DELETE CASCADE,
                sender_username VARCHAR(100) NOT NULL,
                sender_tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """
        ]
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            for cmd in commands:
                cur.execute(cmd)
            
            # Asegurar que exista el tenant predeterminado ID 1
            cur.execute(
                "INSERT INTO tenants (id, name) VALUES (1, 'SaaS Global') ON CONFLICT (id) DO NOTHING"
            )
            # Reiniciar secuencia del id de tenants si es necesario
            cur.execute("SELECT setval('tenants_id_seq', COALESCE((SELECT MAX(id)+1 FROM tenants), 1), false)")

            # Migration: add line_id to messages if not exists
            cur.execute(
                "ALTER TABLE messages ADD COLUMN IF NOT EXISTS line_id INTEGER REFERENCES lines(id)"
            )
            # Migration: add email and notes to contacts if not exists
            cur.execute(
                "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS email VARCHAR(200)"
            )
            cur.execute(
                "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS notes TEXT"
            )
            cur.execute(
                "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS lifecycle_stage VARCHAR(50) DEFAULT 'New Customer'"
            )

            # Migraciones Empresas: Agregar campos adicionales a tenants
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS email VARCHAR(200)")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS phone VARCHAR(50)")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS website VARCHAR(300)")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS notes TEXT")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS contact_name_1 VARCHAR(200)")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS contact_email_1 VARCHAR(200)")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS contact_phone_1 VARCHAR(50)")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS contact_name_2 VARCHAR(200)")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS contact_email_2 VARCHAR(200)")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS contact_phone_2 VARCHAR(50)")

            # Migraciones Fase 4: Canales de Facebook e Instagram
            cur.execute("ALTER TABLE lines ADD COLUMN IF NOT EXISTS channel_type VARCHAR(20) DEFAULT 'whatsapp'")
            cur.execute("ALTER TABLE lines ADD COLUMN IF NOT EXISTS page_id VARCHAR(100)")
            cur.execute("ALTER TABLE lines ADD COLUMN IF NOT EXISTS app_id VARCHAR(100)")
            cur.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS channel_type VARCHAR(20) DEFAULT 'whatsapp'")
            cur.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS sender_name VARCHAR(200)")
            cur.execute("ALTER TABLE contacts ADD COLUMN IF NOT EXISTS channel_type VARCHAR(20) DEFAULT 'whatsapp'")
            
            # Migraciones Multi-tenant: Agregar tenant_id con valor por defecto 1 a todas las tablas principales
            tables_to_migrate = ["users", "lines", "contacts", "messages", "orders", "products", "quick_replies", "conversation_status", "user_lines", "quota_logs"]
            for table in tables_to_migrate:
                cur.execute(
                    f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS tenant_id INTEGER REFERENCES tenants(id) DEFAULT 1"
                )
                cur.execute(f"UPDATE {table} SET tenant_id = 1 WHERE tenant_id IS NULL")
            
            # Cambiar clave primaria de contacts a compuesta (wa_id, tenant_id)
            try:
                cur.execute("""
                    SELECT a.attname
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    WHERE i.indrelid = 'contacts'::regclass AND i.indisprimary
                """)
                pk_cols = [r[0] for r in cur.fetchall()]
                if len(pk_cols) == 1 and pk_cols[0] == "wa_id":
                    cur.execute("ALTER TABLE contacts DROP CONSTRAINT IF EXISTS contacts_pkey CASCADE")
                    cur.execute("ALTER TABLE contacts ADD PRIMARY KEY (wa_id, tenant_id)")
            except Exception as pk_err:
                print(f"[DB] Advertencia migrando clave primaria de contacts: {pk_err}")

            # ── Nuevas Tablas RAG de Agentes IA y Constructor de Flujos ──
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ai_agent_knowledge (
                    id          SERIAL PRIMARY KEY,
                    agent_id    INTEGER REFERENCES ai_agents(id) ON DELETE CASCADE,
                    source_type VARCHAR(20) NOT NULL,
                    name        VARCHAR(255) NOT NULL,
                    content     TEXT NOT NULL,
                    created_at  TIMESTAMP DEFAULT NOW(),
                    tenant_id   INTEGER REFERENCES tenants(id) DEFAULT 1
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS flow_builder (
                    id          SERIAL PRIMARY KEY,
                    name        VARCHAR(100) NOT NULL,
                    steps       JSONB NOT NULL,
                    is_active   BOOLEAN DEFAULT TRUE,
                    created_at  TIMESTAMP DEFAULT NOW(),
                    tenant_id   INTEGER REFERENCES tenants(id) DEFAULT 1
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversation_flow_state (
                    wa_id           VARCHAR(20) PRIMARY KEY,
                    flow_id         INTEGER REFERENCES flow_builder(id) ON DELETE CASCADE,
                    current_step    INTEGER DEFAULT 0,
                    collected_data  JSONB DEFAULT '{}'::jsonb,
                    updated_at      TIMESTAMP DEFAULT NOW()
                )
            """)

            # Agregar columnas de plan a la tabla tenants si no existen
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS gemini_api_key TEXT;")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS plan_name TEXT DEFAULT 'Starter';")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS billing_period TEXT DEFAULT 'monthly';")
            cur.execute("ALTER TABLE tenants ADD COLUMN IF NOT EXISTS ai_mode TEXT DEFAULT 'BYOK';")

            # Agregar columnas de plan a la tabla pre_registrations si no existen
            cur.execute("ALTER TABLE pre_registrations ADD COLUMN IF NOT EXISTS selected_plan TEXT DEFAULT 'Starter';")
            cur.execute("ALTER TABLE pre_registrations ADD COLUMN IF NOT EXISTS billing_frequency TEXT DEFAULT 'monthly';")
            cur.execute("ALTER TABLE pre_registrations ADD COLUMN IF NOT EXISTS ai_mode TEXT DEFAULT 'BYOK';")

            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error inicializando tablas: {e}")
            return False

    # ── Messages ──────────────────────────────────────────────────────

    def save_message(self, wa_id, msg_type, body, agent_username=None, line_id=None, tenant_id=1, channel_type='whatsapp', sender_name=None):
        if not self._check_available():
            return False
        conn = None
        # Step 1: Guardar el mensaje en la tabla messages
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO messages (wa_id, type, body, agent_username, line_id, tenant_id, channel_type, sender_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (wa_id, msg_type, body, agent_username, line_id, tenant_id, channel_type, sender_name),
            )
            conn.commit()
            cur.close()
            conn.close()
            conn = None  # Marcado como cerrado
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                    conn.close()
                except Exception:
                    pass
            print(f"[DB] Error guardando mensaje en tabla messages: {e}")
            return False

        # Step 2: Intentar registrar la cuota de forma independiente si aplica
        if msg_type in ("OUTBOUND_INIT", "OUTBOUND_REPLY"):
            quota_conn = None
            try:
                quota_conn = self.get_connection()
                quota_cur = quota_conn.cursor()
                quota_cur.execute(
                    "INSERT INTO quota_logs (type, agent_username, tenant_id) VALUES (%s, %s, %s)",
                    (msg_type, agent_username, tenant_id),
                )
                quota_conn.commit()
                quota_cur.close()
                quota_conn.close()
            except Exception as quota_err:
                print(f"[DB] Advertencia insertando log de cuota de forma independiente: {quota_err}")
                if quota_conn:
                    try:
                        quota_conn.rollback()
                        quota_conn.close()
                    except Exception:
                        pass
                # No retornamos False aquí, porque el mensaje en messages ya se commiteó con éxito en el Step 1

        return True

    def get_quota_usage(self, tenant_id):
         if not self._check_available():
             return 0
         try:
             conn = self.get_connection()
             cur = conn.cursor()
             month, year = datetime.now().month, datetime.now().year
             cur.execute(
                 """
                 SELECT COUNT(*) FROM quota_logs
                 WHERE EXTRACT(MONTH FROM sent_at) = %s
                   AND EXTRACT(YEAR  FROM sent_at) = %s
                   AND tenant_id = %s
                 """,
                 (month, year, tenant_id),
             )
             count = cur.fetchone()[0]
             cur.close()
             conn.close()
             return count
         except Exception as e:
             print(f"[DB] Error obteniendo cuota: {e}")
             return 0

    def get_contacts(self, tenant_id):
         if not self._check_available():
             return []
         try:
             conn = self.get_connection()
             cur = conn.cursor()
             cur.execute(
                 """
                 SELECT wa_id, MAX(created_at) AS last_msg
                 FROM messages
                 WHERE tenant_id = %s
                 GROUP BY wa_id
                 ORDER BY last_msg DESC
                 """,
                 (tenant_id,)
             )
             rows = cur.fetchall()
             cur.close()
             conn.close()
             return [r[0] for r in rows]
         except Exception as e:
             print(f"[DB] Error obteniendo contactos: {e}")
             return []

    def get_messages(self, wa_id, tenant_id):
         if not self._check_available():
             return []
         try:
             conn = self.get_connection(); cur = conn.cursor()
             cur.execute(
                 """
                 SELECT type, body, created_at, agent_username, line_id, media_id, media_url
                 FROM messages WHERE wa_id = %s AND tenant_id = %s ORDER BY created_at ASC
                 """,
                 (wa_id, tenant_id),
             )
             rows = cur.fetchall()
             cur.close()
             conn.close()
             return rows
         except Exception as e:
             print(f"[DB] Error obteniendo mensajes: {e}")
             return []

    # ── Users ─────────────────────────────────────────────────────────

    ROLE_LIMITS = {"admin": 3, "coordinator": 3, "agent": 10}

    def create_user(self, username, password, full_name, role, tenant_id):
        """Crea usuario con hash bcrypt vinculado a un tenant_id."""
        if not self._check_available():
            return False, "Base de datos no disponible"
        limit = self.ROLE_LIMITS.get(role, 0)
        if self.count_users_by_role(role, tenant_id) >= limit:
            return False, f"Límite de {role}s alcanzado ({limit} máximo)"
        try:
            pwd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash, full_name, role, tenant_id) VALUES (%s, %s, %s, %s, %s)",
                (username, pwd_hash, full_name, role, tenant_id),
            )
            conn.commit()
            cur.close()
            conn.close()
            return True, ""
        except psycopg2.errors.UniqueViolation:
            return False, f"El usuario '{username}' ya existe"
        except Exception as e:
            return False, str(e)

    def verify_user(self, username, password):
        """Verifica credenciales. Retorna dict con info del usuario y su tenant_id, o None."""
        if not self._check_available():
            return None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, username, password_hash, full_name, role, is_active, tenant_id FROM users WHERE username = %s",
                (username,),
            )
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return None
            uid, uname, pwd_hash, full_name, role, is_active, tenant_id = row
            if not is_active:
                return None
            if bcrypt.checkpw(password.encode(), pwd_hash.encode()):
                return {"id": uid, "username": uname, "full_name": full_name, "role": role, "tenant_id": tenant_id}
            return None
        except Exception as e:
            print(f"[DB] Error verificando usuario: {e}")
            return None

    def get_tenant_by_id(self, tenant_id):
        """Obtiene la información de un tenant por su ID."""
        if not self._check_available():
            return None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name, is_active, plan_name, billing_period, ai_mode FROM tenants WHERE id = %s", (tenant_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                return {
                    "id": row[0], "name": row[1], "is_active": row[2],
                    "plan_name": row[3] or "Starter",
                    "billing_period": row[4] or "monthly",
                    "ai_mode": row[5] or "BYOK"
                }
            return None
        except Exception as e:
            print(f"[DB] Error al obtener tenant por ID: {e}")
            return None

    def get_all_tenants(self):
        """Obtiene todas las empresas (tenants) activas como lista de tuplas."""
        if not self._check_available():
            return []
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name, is_active, email, phone, website, notes, contact_name_1, contact_email_1, contact_phone_1, contact_name_2, contact_email_2, contact_phone_2, plan_name, billing_period, ai_mode FROM tenants ORDER BY id ASC")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(f"[DB] Error al obtener todos los tenants: {e}")
            return []

    def update_tenant_plan(self, tenant_id, plan_name, billing_period, ai_mode):
        if not self._check_available():
            return False
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE tenants SET plan_name = %s, billing_period = %s, ai_mode = %s WHERE id = %s",
                (plan_name, billing_period, ai_mode, tenant_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error actualizando plan del tenant {tenant_id}: {e}")
            return False

    def create_tenant(self, name, email=None, phone=None, website=None, notes=None, contact_name_1=None, contact_email_1=None, contact_phone_1=None, contact_name_2=None, contact_email_2=None, contact_phone_2=None):
        """Crea una nueva empresa (tenant). Retorna (True, tenant_id) o (False, error_msg)."""
        if not self._check_available():
            return False, "Base de datos no disponible"
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO tenants (name, email, phone, website, notes, contact_name_1, contact_email_1, contact_phone_1, contact_name_2, contact_email_2, contact_phone_2) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (name, email or None, phone or None, website or None, notes or None, contact_name_1 or None, contact_email_1 or None, contact_phone_1 or None, contact_name_2 or None, contact_email_2 or None, contact_phone_2 or None)
            )
            tenant_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            return True, tenant_id
        except psycopg2.errors.UniqueViolation:
            return False, f"La empresa '{name}' ya está registrada"
        except Exception as e:
            print(f"[DB] Error creando tenant: {e}")
            return False, str(e)

    def update_tenant(self, tenant_id, name, email, phone, website, notes, contact_name_1=None, contact_email_1=None, contact_phone_1=None, contact_name_2=None, contact_email_2=None, contact_phone_2=None):
        """Actualiza datos de una empresa existente."""
        if not self._check_available():
            return False, "Base de datos no disponible"
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE tenants SET name=%s, email=%s, phone=%s, website=%s, notes=%s, "
                "contact_name_1=%s, contact_email_1=%s, contact_phone_1=%s, "
                "contact_name_2=%s, contact_email_2=%s, contact_phone_2=%s WHERE id=%s",
                (name, email or None, phone or None, website or None, notes or None, 
                 contact_name_1 or None, contact_email_1 or None, contact_phone_1 or None, 
                 contact_name_2 or None, contact_email_2 or None, contact_phone_2 or None, tenant_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            return True, ""
        except psycopg2.errors.UniqueViolation:
            return False, f"Ya existe una empresa con el nombre '{name}'"
        except Exception as e:
            return False, str(e)

    def delete_tenant(self, tenant_id):
        """Elimina una empresa (tenant) y todos sus usuarios asociados. No permite eliminar el tenant 1 (SaaS Global)."""
        if tenant_id == 1:
            return False, "No se puede eliminar la empresa principal (SaaS Global)."
        if not self._check_available():
            return False, "Base de datos no disponible"
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            # Desasociar usuarios del tenant antes de borrar
            cur.execute("UPDATE users SET tenant_id = 1 WHERE tenant_id = %s", (tenant_id,))
            cur.execute("DELETE FROM tenants WHERE id = %s", (tenant_id,))
            conn.commit()
            cur.close()
            conn.close()
            return True, ""
        except Exception as e:
            print(f"[DB] Error eliminando tenant: {e}")
            return False, str(e)

    def delete_user(self, user_id):
        """Elimina un usuario permanentemente."""
        if not self._check_available():
            return False, "Base de datos no disponible"
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            cur.close()
            conn.close()
            return True, ""
        except Exception as e:
            print(f"[DB] Error eliminando usuario: {e}")
            return False, str(e)

    def update_user_tenant(self, user_id, new_tenant_id):
        """Cambia la empresa a la que pertenece un usuario."""
        if not self._check_available():
            return False, "Base de datos no disponible"
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET tenant_id = %s WHERE id = %s", (new_tenant_id, user_id))
            conn.commit()
            cur.close()
            conn.close()
            return True, ""
        except Exception as e:
            return False, str(e)

    def update_user_password(self, user_id, new_password):
        """Actualiza la contraseña de un usuario usando bcrypt."""
        if not self._check_available():
            return False, "Base de datos no disponible"
        try:
            pwd_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (pwd_hash, user_id))
            conn.commit()
            cur.close()
            conn.close()
            return True, ""
        except Exception as e:
            return False, str(e)

    def get_all_users(self, tenant_id):
        """Obtiene todos los usuarios de un tenant específico."""
    def get_users_by_tenant(self, tenant_id):
        """Recupera usuarios vinculados a un tenant. Si es el tenant 1 (superadmin), retorna todos con el nombre de su empresa."""
        if not self._check_available():
            return []
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            if tenant_id == 1:
                cur.execute(
                    "SELECT u.id, u.username, u.full_name, u.role, u.is_active, u.created_at, t.name as tenant_name, u.tenant_id "
                    "FROM users u "
                    "LEFT JOIN tenants t ON u.tenant_id = t.id "
                    "ORDER BY u.tenant_id, u.role, u.username"
                )
            else:
                cur.execute(
                    "SELECT u.id, u.username, u.full_name, u.role, u.is_active, u.created_at, '' as tenant_name, u.tenant_id "
                    "FROM users u "
                    "WHERE u.tenant_id = %s ORDER BY u.role, u.username",
                    (tenant_id,)
                )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(f"[DB] Error obteniendo usuarios: {e}")
            return []

    def count_users_by_role(self, role, tenant_id):
        """Cuenta usuarios activos de un rol dentro de un tenant específico."""
        if not self._check_available():
            return 0
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM users WHERE role = %s AND tenant_id = %s AND is_active = TRUE", (role, tenant_id)
            )
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            return count
        except Exception:
            return 0

    def toggle_user_active(self, user_id, active, tenant_id):
        """Activa/desactiva un usuario garantizando que pertenece al tenant actual."""
        if not self._check_available():
            return False
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET is_active = %s WHERE id = %s AND tenant_id = %s", (active, user_id, tenant_id))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error actualizando usuario: {e}")
            return False

    def user_exists(self):
        """True si ya hay al menos un usuario en la tabla."""
        if not self._check_available():
            return False
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users")
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            return count > 0
        except Exception:
            return False

    # ── Settings ──────────────────────────────────────────────────────

    def get_setting(self, key, default=None):
        if not self._check_available():
            return default
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key = %s", (key,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            return row[0] if row else default
        except Exception:
            return default

    def set_setting(self, key, value):
        if not self._check_available():
            return False
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO settings (key, value) VALUES (%s, %s)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                """,
                (key, value),
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error guardando setting: {e}")
            return False

    def get_tenant_gemini_key(self, tenant_id):
        if not self._check_available() or not tenant_id:
            return None
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT gemini_api_key FROM tenants WHERE id = %s", (tenant_id,))
            row = cur.fetchone(); cur.close(); conn.close()
            return row[0] if row else None
        except Exception as e:
            print(f"[DB] Error al obtener la api key de gemini del tenant {tenant_id}: {e}")
            return None

    def update_tenant_gemini_key(self, tenant_id, key):
        if not self._check_available() or not tenant_id:
            return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("UPDATE tenants SET gemini_api_key = %s WHERE id = %s", (key, tenant_id))
            conn.commit(); cur.close(); conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error al actualizar la api key de gemini del tenant {tenant_id}: {e}")
            return False

    # ── Reports ───────────────────────────────────────────────────────

    def get_messages_in_period(self, start_dt, end_dt, agent=None):
        """Mensajes en un rango de fecha+hora. Filtra por agente si se especifica."""
        if not self._check_available():
            return []
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            if agent:
                cur.execute(
                    """
                    SELECT wa_id, type, body, agent_username, created_at
                    FROM messages
                    WHERE created_at BETWEEN %s AND %s AND agent_username = %s
                    ORDER BY created_at ASC
                    """,
                    (start_dt, end_dt, agent),
                )
            else:
                cur.execute(
                    """
                    SELECT wa_id, type, body, agent_username, created_at
                    FROM messages
                    WHERE created_at BETWEEN %s AND %s
                    ORDER BY created_at ASC
                    """,
                    (start_dt, end_dt),
                )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(f"[DB] Error obteniendo mensajes del período: {e}")
            return []

    def get_agent_stats(self, start_dt, end_dt, agent=None):
        """Cuenta mensajes enviados/recibidos por agente en el período."""
        if not self._check_available():
            return []
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            base = "WHERE created_at BETWEEN %s AND %s"
            params = [start_dt, end_dt]
            if agent:
                base += " AND agent_username = %s"
                params.append(agent)
            cur.execute(
                f"""
                SELECT agent_username, type, COUNT(*) as total
                FROM messages
                {base}
                GROUP BY agent_username, type
                ORDER BY agent_username
                """,
                params,
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(f"[DB] Error obteniendo stats de agentes: {e}")
            return []

    def save_sentiment(self, wa_id, period_date, sentiment, urgent, reason):
        """Guarda o actualiza el análisis de sentimiento de una conversación."""
        if not self._check_available():
            return False
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO sentiment_analysis (wa_id, period_date, sentiment, urgent, reason)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (wa_id, period_date)
                DO UPDATE SET sentiment=EXCLUDED.sentiment, urgent=EXCLUDED.urgent,
                              reason=EXCLUDED.reason, analyzed_at=NOW()
                """,
                (wa_id, period_date, sentiment, urgent, reason),
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error guardando sentimiento: {e}")
            return False

    def get_sentiments(self, start_date, end_date):
        """Recupera análisis de sentimientos guardados para un rango de fechas."""
        if not self._check_available():
            return []
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT wa_id, sentiment, urgent, reason, analyzed_at
                FROM sentiment_analysis
                WHERE period_date BETWEEN %s AND %s
                ORDER BY analyzed_at DESC
                """,
                (start_date, end_date),
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(f"[DB] Error obteniendo sentimientos: {e}")
            return []

    # ── Lines ─────────────────────────────────────────────────────────

    MAX_LINES = 5

    def count_lines(self, tenant_id):
        if not self._check_available(): return 0
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM lines WHERE is_active = TRUE AND tenant_id = %s", (tenant_id,))
            c = cur.fetchone()[0]; cur.close(); conn.close(); return c
        except Exception: return 0

    def create_line(self, name, phone_number_id, access_token, welcome_message, welcome_active, color, tenant_id, channel_type='whatsapp', page_id=None, app_id=None):
        if not self._check_available(): return False, "DB no disponible"
        if self.count_lines(tenant_id) >= self.MAX_LINES: return False, f"Límite de {self.MAX_LINES} líneas alcanzado"
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "INSERT INTO lines (name, phone_number_id, access_token, welcome_message, welcome_active, color, tenant_id, channel_type, page_id, app_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (name, phone_number_id, access_token, welcome_message, welcome_active, color, tenant_id, channel_type, page_id, app_id)
            )
            conn.commit(); cur.close(); conn.close(); return True, ""
        except Exception as e: return False, str(e)

    def update_line(self, line_id, name, phone_number_id, access_token, welcome_message, welcome_active, color, tenant_id, channel_type='whatsapp', page_id=None, app_id=None):
        if not self._check_available(): return False, "DB no disponible"
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "UPDATE lines SET name=%s, phone_number_id=%s, access_token=%s, welcome_message=%s, welcome_active=%s, color=%s, tenant_id=%s, channel_type=%s, page_id=%s, app_id=%s WHERE id=%s",
                (name, phone_number_id, access_token, welcome_message, welcome_active, color, tenant_id, channel_type, page_id, app_id, line_id)
            )
            conn.commit(); cur.close(); conn.close(); return True, ""
        except Exception as e: return False, str(e)

    def delete_line(self, line_id):
        if not self._check_available(): return False, "DB no disponible"
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM lines WHERE id = %s", (line_id,))
            conn.commit(); cur.close(); conn.close(); return True, ""
        except Exception as e: return False, str(e)

    def upsert_facebook_line(self, name, page_id, access_token, tenant_id, channel_type='messenger'):
        """Inserta o actualiza un canal de Facebook Messenger o Instagram para un tenant."""
        if not self._check_available():
            return False, "DB no disponible"
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            # Buscar si ya existe una línea con este page_id para el tenant
            cur.execute(
                "SELECT id FROM lines WHERE page_id = %s AND tenant_id = %s",
                (page_id, tenant_id)
            )
            row = cur.fetchone()
            if row:
                # Actualizar existente
                line_id = row[0]
                cur.execute(
                    "UPDATE lines SET name=%s, access_token=%s, channel_type=%s, is_active=TRUE WHERE id=%s",
                    (name, access_token, channel_type, line_id)
                )
                conn.commit()
                cur.close()
                conn.close()
                return True, "Canal actualizado con éxito"
            else:
                # Crear nuevo
                cur.close()
                conn.close()
                # Usar create_line interna
                return self.create_line(
                    name=name,
                    phone_number_id=None,
                    access_token=access_token,
                    welcome_message="¡Hola! Bienvenido a nuestro canal.",
                    welcome_active=True,
                    color="#0a3055" if channel_type == 'messenger' else "#d62976",
                    tenant_id=tenant_id,
                    channel_type=channel_type,
                    page_id=page_id,
                    app_id=None
                )
        except Exception as e:
            return False, str(e)

    def get_all_lines(self, tenant_id):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT id, name, phone_number_id, access_token, welcome_message, welcome_active, color, is_active, channel_type, page_id, app_id FROM lines WHERE tenant_id = %s ORDER BY id", (tenant_id,))
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        except Exception: return []

    def get_line_by_id(self, line_id, tenant_id):
        if not self._check_available(): return None
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT id, name, phone_number_id, access_token, welcome_message, welcome_active, color, is_active, tenant_id, channel_type, page_id, app_id FROM lines WHERE id = %s AND tenant_id = %s", (line_id, tenant_id))
            row = cur.fetchone(); cur.close(); conn.close()
            if not row: return None
            keys = ["id","name","phone_number_id","access_token","welcome_message","welcome_active","color","is_active","tenant_id","channel_type","page_id","app_id"]
            return dict(zip(keys, row))
        except Exception: return None

    def get_line_by_phone_id(self, phone_number_id):
        """Obtiene la línea por su id de teléfono (usado por webhook Meta, por lo que incluye el tenant_id)."""
        if not self._check_available(): return None
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT id, name, phone_number_id, access_token, welcome_message, welcome_active, color, is_active, tenant_id, channel_type, page_id, app_id FROM lines WHERE phone_number_id = %s AND is_active = TRUE", (phone_number_id,))
            row = cur.fetchone(); cur.close(); conn.close()
            if not row: return None
            keys = ["id","name","phone_number_id","access_token","welcome_message","welcome_active","color","is_active","tenant_id","channel_type","page_id","app_id"]
            return dict(zip(keys, row))
        except Exception: return None

    def get_channel_by_page_id(self, page_id):
        """Obtiene la línea/canal por su id de página (usado por webhook de FB/Instagram)."""
        if not self._check_available(): return None
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT id, name, phone_number_id, access_token, welcome_message, welcome_active, color, is_active, tenant_id, channel_type, page_id, app_id FROM lines WHERE page_id = %s AND is_active = TRUE", (page_id,))
            row = cur.fetchone(); cur.close(); conn.close()
            if not row: return None
            keys = ["id","name","phone_number_id","access_token","welcome_message","welcome_active","color","is_active","tenant_id","channel_type","page_id","app_id"]
            return dict(zip(keys, row))
        except Exception: return None


    def toggle_line_active(self, line_id, active, tenant_id):
         if not self._check_available(): return False
         try:
             conn = self.get_connection(); cur = conn.cursor()
             cur.execute("UPDATE lines SET is_active = %s WHERE id = %s AND tenant_id = %s", (active, line_id, tenant_id))
             conn.commit(); cur.close(); conn.close(); return True
         except Exception: return False

    def is_first_contact(self, wa_id, line_id):
        """True si este número nunca ha escrito a esta línea."""
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM messages WHERE wa_id=%s AND line_id=%s AND type='INBOUND'", (wa_id, line_id))
            c = cur.fetchone()[0]; cur.close(); conn.close(); return c == 0
        except Exception: return False

    # ── Quick Replies ─────────────────────────────────────────────────

    def create_quick_reply(self, shortcut, title, message, tenant_id):
         if not self._check_available(): return False, "DB no disponible"
         try:
             conn = self.get_connection(); cur = conn.cursor()
             cur.execute("INSERT INTO quick_replies (shortcut, title, message, tenant_id) VALUES (%s,%s,%s,%s)", (shortcut, title, message, tenant_id))
             conn.commit(); cur.close(); conn.close(); return True, ""
         except Exception as e: return False, str(e)

    def get_quick_replies(self, tenant_id):
         if not self._check_available(): return []
         try:
             conn = self.get_connection(); cur = conn.cursor()
             cur.execute("SELECT id, shortcut, title, message FROM quick_replies WHERE tenant_id = %s ORDER BY shortcut", (tenant_id,))
             rows = cur.fetchall(); cur.close(); conn.close(); return rows
         except Exception: return []

    def delete_quick_reply(self, qr_id, tenant_id):
         if not self._check_available(): return False
         try:
             conn = self.get_connection(); cur = conn.cursor()
             cur.execute("DELETE FROM quick_replies WHERE id = %s AND tenant_id = %s", (qr_id, tenant_id))
             conn.commit(); cur.close(); conn.close(); return True
         except Exception: return False

    # ── User-Line Assignment ──────────────────────────────────────────

    def assign_user_to_line(self, user_id, line_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO user_lines (user_id, line_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (user_id, line_id))
            conn.commit(); cur.close(); conn.close(); return True
        except Exception: return False

    def remove_user_from_line(self, user_id, line_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM user_lines WHERE user_id=%s AND line_id=%s", (user_id, line_id))
            conn.commit(); cur.close(); conn.close(); return True
        except Exception: return False

    def get_user_lines(self, user_id):
        """IDs de líneas asignadas a un usuario."""
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT line_id FROM user_lines WHERE user_id = %s", (user_id,))
            rows = cur.fetchall(); cur.close(); conn.close(); return [r[0] for r in rows]
        except Exception: return []

    def get_contacts_for_user(self, user_id, role, tenant_id):
         """Retorna contactos visibles para el usuario según su rol, líneas asignadas y tenant_id."""
         if not self._check_available(): return []
         try:
             conn = self.get_connection(); cur = conn.cursor()
             if role in ("admin", "coordinator"):
                 cur.execute(
                     """
                     SELECT m.wa_id, MAX(m.created_at) AS last_msg, m.line_id,
                            COALESCE(cs.status,'pending') AS status,
                            COALESCE(cs.unread,0) AS unread,
                            COALESCE(cs.assigned_to, '') AS assigned_to,
                            COALESCE(con.name, m.wa_id) AS name,
                            COALESCE(con.lifecycle_stage, 'New Customer') AS lifecycle_stage
                     FROM messages m
                     LEFT JOIN conversation_status cs
                           ON cs.wa_id = m.wa_id AND cs.line_id IS NOT DISTINCT FROM m.line_id
                     LEFT JOIN contacts con
                           ON con.wa_id = m.wa_id AND con.tenant_id = m.tenant_id
                     WHERE m.tenant_id = %s
                     GROUP BY m.wa_id, m.line_id, cs.status, cs.unread, cs.assigned_to, con.name, con.lifecycle_stage
                     ORDER BY last_msg DESC
                     """,
                     (tenant_id,)
                 )
             else:
                 line_ids = self.get_user_lines(user_id)
                 if not line_ids:
                     cur.close(); conn.close(); return []
                 placeholders = ",".join(["%s"] * len(line_ids))
                 cur.execute(
                     f"""
                     SELECT m.wa_id, MAX(m.created_at) AS last_msg, m.line_id,
                            COALESCE(cs.status,'pending') AS status,
                            COALESCE(cs.unread,0) AS unread,
                            COALESCE(cs.assigned_to, '') AS assigned_to,
                            COALESCE(con.name, m.wa_id) AS name,
                            COALESCE(con.lifecycle_stage, 'New Customer') AS lifecycle_stage
                     FROM messages m
                     LEFT JOIN conversation_status cs
                           ON cs.wa_id = m.wa_id AND cs.line_id IS NOT DISTINCT FROM m.line_id
                     LEFT JOIN contacts con
                           ON con.wa_id = m.wa_id AND con.tenant_id = m.tenant_id
                     WHERE m.tenant_id = %s AND m.line_id IN ({placeholders})
                     GROUP BY m.wa_id, m.line_id, cs.status, cs.unread
                     ORDER BY last_msg DESC
                     """,
                     [tenant_id] + list(line_ids)
                 )
             rows = cur.fetchall(); cur.close(); conn.close(); return rows
         except Exception as e:
             print(f"[DB] Error obteniendo contactos: {e}"); return []

    # ── Conversation Status ────────────────────────────────────────────

    def mark_conversation_unread(self, wa_id, line_id):
        """Incrementa el contador de no-leídos al llegar un mensaje entrante."""
        if not self._check_available(): return
        try:
            line_id = line_id or 1
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO conversation_status (wa_id, line_id, status, unread)
                VALUES (%s, %s, 'pending', 1)
                ON CONFLICT (wa_id, line_id)
                DO UPDATE SET unread = conversation_status.unread + 1,
                              status = CASE WHEN conversation_status.status = 'resolved'
                                           THEN 'pending' ELSE conversation_status.status END,
                              updated_at = NOW()
                """,
                (wa_id, line_id)
            )
            conn.commit(); cur.close(); conn.close()
        except Exception as e:
            print(f"[DB] Error marcando no-leídos: {e}")

    def mark_conversation_read(self, wa_id, line_id):
        """Resetea el contador de no-leídos al abrir el chat."""
        if not self._check_available(): return
        try:
            line_id = line_id or 1
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO conversation_status (wa_id, line_id, unread)
                VALUES (%s, %s, 0)
                ON CONFLICT (wa_id, line_id)
                DO UPDATE SET unread = 0, updated_at = NOW()
                """,
                (wa_id, line_id)
            )
            conn.commit(); cur.close(); conn.close()
        except Exception as e:
            print(f"[DB] Error marcando leídos: {e}")

    def set_conversation_status(self, wa_id, line_id, status):
        """Cambia el estado de una conversación: pending/active/resolved."""
        if not self._check_available(): return
        try:
            line_id = line_id or 1
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO conversation_status (wa_id, line_id, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (wa_id, line_id)
                DO UPDATE SET status = EXCLUDED.status, updated_at = NOW()
                """,
                (wa_id, line_id, status)
            )
            conn.commit(); cur.close(); conn.close()
        except Exception as e:
            print(f"[DB] Error actualizando estado: {e}")

    def assign_conversation(self, wa_id, line_id, agent_username, tenant_id):
        if not self._check_available(): return False
        try:
            line_id = line_id or 1
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO conversation_status (wa_id, line_id, assigned_to, tenant_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (wa_id, line_id)
                DO UPDATE SET assigned_to = EXCLUDED.assigned_to, updated_at = NOW()
                """,
                (wa_id, line_id, agent_username, tenant_id)
            )
            conn.commit(); cur.close(); conn.close(); return True
        except Exception as e:
            print(f"[DB] Error asignando conversación: {e}")
            return False

    def change_password(self, username, new_password):
        """Cambia la contraseña de un usuario."""
        if not self._check_available(): return False
        import bcrypt
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("UPDATE users SET password_hash=%s WHERE username=%s", (hashed, username))
            conn.commit(); cur.close(); conn.close(); return True
        except Exception: return False


    # ── Internal Presence & Rooms ─────────────────────────────────────

    def update_user_presence(self, user_id):
        if not self._check_available(): return
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("UPDATE users SET last_seen = NOW() WHERE id = %s", (user_id,))
            conn.commit(); cur.close(); conn.close()
        except Exception: pass

    def get_team_status(self):
        """Retorna lista de usuarios con indicador de si están online (< 2 min)."""
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                SELECT id, username, full_name, role, 
                       (last_seen > NOW() - INTERVAL '2 minutes') as is_online 
                FROM users WHERE is_active = TRUE ORDER BY full_name ASC
                """
            )
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        except Exception: return []

    def get_internal_messages(self, room_id=None, limit=100):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            if room_id:
                cur.execute("SELECT username, message, created_at FROM internal_messages WHERE room_id = %s ORDER BY created_at DESC LIMIT %s", (room_id, limit))
            else:
                cur.execute("SELECT username, message, created_at FROM internal_messages WHERE room_id IS NULL ORDER BY created_at DESC LIMIT %s", (limit,))
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        except Exception: return []

    def save_internal_message(self, username, message, room_id=None):
        if not self._check_available(): return
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO internal_messages (username, message, room_id) VALUES (%s, %s, %s)", (username, message, room_id))
            conn.commit(); cur.close(); conn.close()
        except Exception: pass

    def create_room(self, name, user_ids, is_group=True):
        """Crea una sala y agrega a los miembros."""
        if not self._check_available(): return None
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO internal_rooms (name, is_group) VALUES (%s, %s) RETURNING id", (name, is_group))
            room_id = cur.fetchone()[0]
            for uid in user_ids:
                cur.execute("INSERT INTO internal_room_members (room_id, user_id) VALUES (%s, %s)", (room_id, uid))
            conn.commit(); cur.close(); conn.close(); return room_id
        except Exception: return None

    # ── Contacts Directory ────────────────────────────────────────────
    def get_all_contacts(self, tenant_id):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT wa_id, name, email, notes FROM contacts WHERE tenant_id = %s ORDER BY name", (tenant_id,))
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        except Exception as e:
            print(f"[DB] Error obteniendo todos los contactos: {e}")
            return []

    def upsert_contact(self, wa_id, name, email, notes, tenant_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO contacts (wa_id, name, email, notes, tenant_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (wa_id, tenant_id)
                DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email, notes = EXCLUDED.notes
                """,
                (wa_id, name, email, notes, tenant_id)
            )
            conn.commit(); cur.close(); conn.close(); return True
        except Exception as e:
            print(f"[DB] Error guardando contacto: {e}")
            return False

    def save_product(self, name, description, price, image_url, is_seasonal, tenant_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "INSERT INTO products (name, description, price, image_url, is_seasonal, tenant_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, description, price, image_url, is_seasonal, tenant_id)
            )
            conn.commit(); cur.close(); conn.close(); return True
        except Exception as e:
            print(f"[DB] Error guardando producto: {e}")
            return False

    def update_product(self, product_id, name, description, price, image_url, is_seasonal, tenant_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                UPDATE products 
                SET name = %s, description = %s, price = %s, image_url = %s, is_seasonal = %s 
                WHERE id = %s AND tenant_id = %s
                """,
                (name, description, price, image_url, is_seasonal, product_id, tenant_id)
            )
            conn.commit(); cur.close(); conn.close(); return True
        except Exception as e:
            print(f"[DB] Error actualizando producto: {e}")
            return False

    def get_all_products(self, tenant_id, only_seasonal=False):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            if only_seasonal:
                cur.execute("SELECT id, name, description, price, image_url, is_seasonal FROM products WHERE is_seasonal = TRUE AND tenant_id = %s ORDER BY name", (tenant_id,))
            else:
                cur.execute("SELECT id, name, description, price, image_url, is_seasonal FROM products WHERE tenant_id = %s ORDER BY name", (tenant_id,))
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        except Exception as e:
            print(f"[DB] Error obteniendo productos: {e}")
            return []

    def delete_product(self, product_id, tenant_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM products WHERE id = %s AND tenant_id = %s", (product_id, tenant_id))
            conn.commit(); cur.close(); conn.close(); return True
        except Exception as e:
            print(f"[DB] Error eliminando producto: {e}")
            return False

    # ── Sales Orders ──────────────────────────────────────────────────

    def create_order(self, wa_id, agent_username, items, total_amount, shipping_address, tenant_id):
        if not self._check_available(): return None
        try:
            import json
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO orders (wa_id, agent_username, items, total_amount, shipping_address, tenant_id)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                """,
                (wa_id, agent_username, json.dumps(items), total_amount, shipping_address, tenant_id)
            )
            order_id = cur.fetchone()[0]
            conn.commit(); cur.close(); conn.close(); return order_id
        except Exception as e:
            print(f"[DB] Error creando pedido: {e}")
            return None

    def update_order_status(self, order_id, new_status, tenant_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "UPDATE orders SET status = %s, updated_at = NOW() WHERE id = %s AND tenant_id = %s",
                (new_status, order_id, tenant_id)
            )
            conn.commit(); cur.close(); conn.close(); return True
        except Exception as e:
            print(f"[DB] Error actualizando estado de pedido: {e}")
            return False

    def get_orders(self, status=None, wa_id=None):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            query = "SELECT id, wa_id, agent_username, items, total_amount, status, shipping_address, created_at, updated_at FROM orders"
            params = []
            conditions = []
            if status is not None:
                conditions.append("status = %s")
                params.append(str(status))
            if wa_id:
                conditions.append("wa_id = %s")
                params.append(wa_id)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY created_at DESC"
            cur.execute(query, params)
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        except Exception as e:
            print(f"[DB] Error obteniendo pedidos: {e}")
            return []

    def update_contact_lifecycle(self, wa_id, stage, tenant_id):
        """Actualiza la etapa de ciclo de vida del contacto."""
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            # Asegurar que el contacto exista antes de actualizar
            cur.execute(
                "INSERT INTO contacts (wa_id, lifecycle_stage, tenant_id) VALUES (%s, %s, %s) "
                "ON CONFLICT (wa_id, tenant_id) DO UPDATE SET lifecycle_stage = EXCLUDED.lifecycle_stage",
                (wa_id, stage, tenant_id)
            )
            conn.commit(); cur.close(); conn.close(); return True
        except Exception as e:
            print(f"[DB] Error actualizando ciclo de vida del contacto: {e}")
            return False

    def get_lifecycle_counts(self, tenant_id):
        """Retorna el conteo de contactos por etapa de ciclo de vida en el tenant."""
        if not self._check_available(): return {}
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT lifecycle_stage, COUNT(*) FROM contacts WHERE tenant_id = %s GROUP BY lifecycle_stage",
                (tenant_id,)
            )
            rows = cur.fetchall(); cur.close(); conn.close()
            
            # Inicializar con todas las etapas en 0
            stages = {"New Customer": 0, "Lead": 0, "Customer": 0, "Paid": 0}
            for row in rows:
                stage_name = row[0]
                if stage_name in stages:
                    stages[stage_name] = row[1]
            return stages
        except Exception as e:
            print(f"[DB] Error obteniendo conteos de ciclo de vida: {e}")
            return {}

    def get_last_inbound_time(self, wa_id, tenant_id):
        """Retorna la fecha y hora del último mensaje INBOUND del contacto."""
        if not self._check_available(): return None
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT created_at FROM messages WHERE wa_id = %s AND type = 'INBOUND' AND tenant_id = %s ORDER BY created_at DESC LIMIT 1",
                (wa_id, tenant_id)
            )
            row = cur.fetchone(); cur.close(); conn.close()
            return row[0] if row else None
        except Exception:
            return None

    # ── CRUD Agentes IA ────────────────────────────────────────────────
    def create_ai_agent(self, name, system_prompt, line_id, is_active, tenant_id):
        if not self._check_available(): return False, "DB no disponible"
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "INSERT INTO ai_agents (name, system_prompt, line_id, is_active, tenant_id) VALUES (%s, %s, %s, %s, %s)",
                (name, system_prompt, line_id if line_id != 0 else None, is_active, tenant_id)
            )
            conn.commit(); cur.close(); conn.close(); return True, None
        except Exception as e:
            print(f"[DB] Error creando agente IA: {e}")
            return False, str(e)

    def get_ai_agents(self, tenant_id):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT id, name, system_prompt, line_id, is_active FROM ai_agents WHERE tenant_id = %s ORDER BY id DESC",
                (tenant_id,)
            )
            rows = cur.fetchall(); cur.close(); conn.close()
            return [{"id": r[0], "name": r[1], "system_prompt": r[2], "line_id": r[3] or 0, "is_active": bool(r[4])} for r in rows]
        except Exception as e:
            print(f"[DB] Error obteniendo agentes IA: {e}")
            return []

    def get_active_agent_for_line(self, line_id, tenant_id):
        """Retorna el primer agente IA activo asignado a una línea específica."""
        if not self._check_available(): return None
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT id, name, system_prompt FROM ai_agents WHERE line_id = %s AND is_active = TRUE AND tenant_id = %s LIMIT 1",
                (line_id, tenant_id)
            )
            row = cur.fetchone(); cur.close(); conn.close()
            if row:
                return {"id": row[0], "name": row[1], "system_prompt": row[2]}
            return None
        except Exception as e:
            print(f"[DB] Error obteniendo agente IA activo para línea: {e}")
            return None

    def delete_ai_agent(self, agent_id, tenant_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM ai_agents WHERE id = %s AND tenant_id = %s", (agent_id, tenant_id))
            conn.commit(); cur.close(); conn.close(); return True
        except Exception as e:
            print(f"[DB] Error borrando agente IA: {e}")
            return False

    # ── CRUD Plantillas de Mensaje (Templates de Meta) ─────────────────
    def create_message_template(self, name, category, body_text, tenant_id):
        if not self._check_available(): return False, "DB no disponible"
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "INSERT INTO message_templates (name, category, body_text, tenant_id) VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (name, tenant_id) DO UPDATE SET category = EXCLUDED.category, body_text = EXCLUDED.body_text",
                (name, category, body_text, tenant_id)
            )
            conn.commit(); cur.close(); conn.close(); return True, None
        except Exception as e:
            print(f"[DB] Error creando plantilla de mensaje: {e}")
            return False, str(e)

    def get_message_templates(self, tenant_id):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT id, name, category, language, body_text FROM message_templates WHERE tenant_id = %s ORDER BY name ASC",
                (tenant_id,)
            )
            rows = cur.fetchall(); cur.close(); conn.close()
            return [{"id": r[0], "name": r[1], "category": r[2], "language": r[3], "body_text": r[4]} for r in rows]
        except Exception as e:
            print(f"[DB] Error obteniendo plantillas: {e}")
            return []

    def delete_message_template(self, template_id, tenant_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM message_templates WHERE id = %s AND tenant_id = %s", (template_id, tenant_id))
            conn.commit(); cur.close(); conn.close(); return True
        except Exception as e:
            print(f"[DB] Error borrando plantilla: {e}")
            return False

    # ── Métodos de Analítica Avanzada (Dashboard de Reportes) ───────────
    def get_average_response_time(self, tenant_id):
        """Retorna tiempo promedio de respuesta en minutos (según diferencia INBOUND -> primer OUTBOUND)."""
        if not self._check_available(): return 0.0
        try:
            conn = self.get_connection(); cur = conn.cursor()
            # Esta consulta calcula la diferencia promedio de tiempo en minutos
            cur.execute(
                """
                WITH inbound_msgs AS (
                    SELECT wa_id, created_at, lead(created_at) OVER (PARTITION BY wa_id ORDER BY created_at) as next_created_at,
                           type, lead(type) OVER (PARTITION BY wa_id ORDER BY created_at) as next_type
                    FROM messages
                    WHERE tenant_id = %s
                )
                SELECT AVG(EXTRACT(EPOCH FROM (next_created_at - created_at)) / 60)
                FROM inbound_msgs
                WHERE type = 'INBOUND' AND next_type LIKE 'OUTBOUND%%'
                """,
                (tenant_id,)
            )
            row = cur.fetchone(); cur.close(); conn.close()
            if not row or row[0] is None:
                return 0.0
            return round(float(row[0]), 1)
        except Exception as e:
            print(f"[DB] Error calculando tiempo promedio de respuesta: {e}")
            return 0.0

    def get_conversation_states_chart(self, tenant_id):
        """Devuelve el conteo de chats activos por estado en el tenant."""
        if not self._check_available(): return {}
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT COALESCE(status, 'pending'), COUNT(*) FROM conversation_status WHERE tenant_id = %s GROUP BY status",
                (tenant_id,)
            )
            rows = cur.fetchall(); cur.close(); conn.close()
            # Mapeo por consistencia
            states = {"pending": 0, "active": 0, "snoozed": 0, "resolved": 0}
            for r in rows:
                k = r[0]
                if k in states:
                    states[k] = r[1]
            return states
        except Exception as e:
            print(f"[DB] Error obteniendo estados de conversación: {e}")
            return {}

    def get_top_agents(self, tenant_id):
        """Lista agentes humanos e IA y su cantidad total de respuestas enviadas."""
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                SELECT agent_username, COUNT(*) 
                FROM messages 
                WHERE tenant_id = %s AND type LIKE 'OUTBOUND%%' AND agent_username IS NOT NULL AND agent_username != ''
                GROUP BY agent_username 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
                """,
                (tenant_id,)
            )
            rows = cur.fetchall(); cur.close(); conn.close()
            if not rows:
                return []
            return [{"agent": r[0], "count": r[1]} for r in rows if r and len(r) > 1]
        except Exception as e:
            print(f"[DB] Error obteniendo top agentes: {e}")
            return []

    # ── CRUD Automatizaciones (Workflows - Fase 3) ──────────────────────
    def create_workflow(self, name, trigger_type, condition_field, condition_value, action_type, action_value, tenant_id):
        if not self._check_available(): return False, "DB no disponible"
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "INSERT INTO workflows (name, trigger_type, condition_field, condition_value, action_type, action_value, tenant_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (name, trigger_type, condition_field, condition_value.strip().lower(), action_type, action_value, tenant_id)
            )
            conn.commit(); cur.close(); conn.close(); return True, None
        except Exception as e:
            print(f"[DB] Error creando flujo de trabajo: {e}")
            return False, str(e)

    def get_workflows(self, tenant_id):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT id, name, trigger_type, condition_field, condition_value, action_type, action_value, is_active "
                "FROM workflows WHERE tenant_id = %s ORDER BY id DESC",
                (tenant_id,)
            )
            rows = cur.fetchall(); cur.close(); conn.close()
            return [
                {
                    "id": r[0], "name": r[1], "trigger_type": r[2], "condition_field": r[3],
                    "condition_value": r[4], "action_type": r[5], "action_value": r[6], "is_active": bool(r[7])
                }
                for r in rows
            ]
        except Exception as e:
            print(f"[DB] Error obteniendo flujos de trabajo: {e}")
            return []

    def delete_workflow(self, workflow_id, tenant_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM workflows WHERE id = %s AND tenant_id = %s", (workflow_id, tenant_id))
            conn.commit(); cur.close(); conn.close(); return True
        except Exception as e:
            print(f"[DB] Error borrando flujo de trabajo: {e}")
            return False

    # ── CRUD RAG de Agentes IA (Fuentes de Conocimiento) ─────────────────
    def create_agent_knowledge(self, agent_id, source_type, name, content, tenant_id):
        if not self._check_available(): return False, "DB no disponible"
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "INSERT INTO ai_agent_knowledge (agent_id, source_type, name, content, tenant_id) VALUES (%s, %s, %s, %s, %s)",
                (agent_id, source_type, name, content, tenant_id)
            )
            conn.commit(); cur.close(); conn.close()
            return True, None
        except Exception as e:
            print(f"[DB] Error creando fuente de conocimiento: {e}")
            return False, str(e)

    def get_agent_knowledge(self, agent_id, tenant_id):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT id, agent_id, source_type, name, content, created_at FROM ai_agent_knowledge WHERE agent_id = %s AND tenant_id = %s ORDER BY id DESC",
                (agent_id, tenant_id)
            )
            rows = cur.fetchall(); cur.close(); conn.close()
            return [
                {
                    "id": r[0], "agent_id": r[1], "source_type": r[2], "name": r[3],
                    "content": r[4], "created_at": r[5].strftime("%Y-%m-%d %H:%M") if r[5] else ""
                }
                for r in rows
            ]
        except Exception as e:
            print(f"[DB] Error obteniendo fuentes de conocimiento: {e}")
            return []

    def delete_agent_knowledge(self, knowledge_id, tenant_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM ai_agent_knowledge WHERE id = %s AND tenant_id = %s", (knowledge_id, tenant_id))
            conn.commit(); cur.close(); conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error borrando fuente de conocimiento: {e}")
            return False

    # ── CRUD Constructor de Flujos (Flows) ──────────────────────────────
    def create_flow(self, name, steps, tenant_id):
        if not self._check_available(): return False, "DB no disponible"
        import json
        try:
            conn = self.get_connection(); cur = conn.cursor()
            steps_json = json.dumps(steps)
            cur.execute(
                "INSERT INTO flow_builder (name, steps, is_active, tenant_id) VALUES (%s, %s, TRUE, %s)",
                (name, steps_json, tenant_id)
            )
            conn.commit(); cur.close(); conn.close()
            return True, None
        except Exception as e:
            print(f"[DB] Error creando flujo: {e}")
            return False, str(e)

    def get_flows(self, tenant_id):
        if not self._check_available(): return []
        import json
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT id, name, steps, is_active, created_at FROM flow_builder WHERE tenant_id = %s ORDER BY id DESC",
                (tenant_id,)
            )
            rows = cur.fetchall(); cur.close(); conn.close()
            return [
                {
                    "id": r[0], "name": r[1],
                    "steps": json.loads(r[2]) if isinstance(r[2], str) else r[2],
                    "is_active": bool(r[3]), "created_at": r[4].strftime("%Y-%m-%d %H:%M") if r[4] else ""
                }
                for r in rows
            ]
        except Exception as e:
            print(f"[DB] Error obteniendo flujos: {e}")
            return []

    def delete_flow(self, flow_id, tenant_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM flow_builder WHERE id = %s AND tenant_id = %s", (flow_id, tenant_id))
            conn.commit(); cur.close(); conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error borrando flujo: {e}")
            return False

    # ── Estado del Flujo Conversacional ──────────────────────────────────
    def get_flow_state(self, wa_id):
        if not self._check_available(): return None
        import json
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT flow_id, current_step, collected_data FROM conversation_flow_state WHERE wa_id = %s",
                (wa_id,)
            )
            row = cur.fetchone(); cur.close(); conn.close()
            if not row:
                return None
            return {
                "flow_id": row[0],
                "current_step": row[1],
                "collected_data": json.loads(row[2]) if isinstance(row[2], str) else row[2]
            }
        except Exception as e:
            print(f"[DB] Error obteniendo estado del flujo: {e}")
            return None

    def save_flow_state(self, wa_id, flow_id, current_step, collected_data):
        if not self._check_available(): return False
        import json
        try:
            conn = self.get_connection(); cur = conn.cursor()
            collected_json = json.dumps(collected_data)
            cur.execute(
                """
                INSERT INTO conversation_flow_state (wa_id, flow_id, current_step, collected_data, updated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (wa_id)
                DO UPDATE SET flow_id = EXCLUDED.flow_id, current_step = EXCLUDED.current_step,
                              collected_data = EXCLUDED.collected_data, updated_at = NOW()
                """,
                (wa_id, flow_id, current_step, collected_json)
            )
            conn.commit(); cur.close(); conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error guardando estado del flujo: {e}")
            return False

    # ── Auto-Registro de Empresas ───────────────────────────────────────────
    def save_pre_registration(self, company_name, contact_name, contact_email, contact_phone, notes, selected_plan='Starter', billing_frequency='monthly', ai_mode='BYOK'):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO pre_registrations (company_name, contact_name, contact_email, contact_phone, notes, selected_plan, billing_frequency, ai_mode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (contact_email) DO NOTHING
                """,
                (company_name, contact_name, contact_email, contact_phone, notes, selected_plan, billing_frequency, ai_mode)
            )
            conn.commit(); cur.close(); conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error guardando pre-registro: {e}")
            return False

    def get_pre_registrations(self, status="pending"):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "SELECT id, company_name, contact_name, contact_email, contact_phone, notes, status, created_at, selected_plan, billing_frequency, ai_mode FROM pre_registrations WHERE status = %s ORDER BY created_at DESC",
                (status,)
            )
            rows = cur.fetchall()
            cur.close(); conn.close()
            return [
                {
                    "id": r[0],
                    "company_name": r[1],
                    "contact_name": r[2],
                    "contact_email": r[3],
                    "contact_phone": r[4],
                    "notes": r[5],
                    "status": r[6],
                    "created_at": r[7].strftime("%Y-%m-%d %H:%M:%S") if r[7] else "",
                    "selected_plan": r[8] or "Starter",
                    "billing_frequency": r[9] or "monthly",
                    "ai_mode": r[10] or "BYOK"
                }
                for r in rows
            ]
        except Exception as e:
            print(f"[DB] Error obteniendo pre-registros: {e}")
            return []

    def update_pre_registration_status(self, req_id, status):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "UPDATE pre_registrations SET status = %s WHERE id = %s",
                (status, req_id)
            )
            conn.commit(); cur.close(); conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error actualizando estado de pre-registro: {e}")
            return False

    # ── Chat de Soporte Técnico ─────────────────────────────────────────────
    def get_or_create_support_room(self, tenant_id):
        if not self._check_available(): return None
        try:
            conn = self.get_connection(); cur = conn.cursor()
            # Buscar si ya existe
            cur.execute("SELECT id FROM support_rooms WHERE tenant_id = %s", (tenant_id,))
            row = cur.fetchone()
            if row:
                room_id = row[0]
            else:
                # Crear nueva
                cur.execute(
                    "INSERT INTO support_rooms (tenant_id) VALUES (%s) RETURNING id",
                    (tenant_id,)
                )
                room_id = cur.fetchone()[0]
                conn.commit()
            cur.close(); conn.close()
            return room_id
        except Exception as e:
            print(f"[DB] Error en get_or_create_support_room: {e}")
            return None

    def save_support_message(self, room_id, sender_username, sender_tenant_id, message):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO support_messages (room_id, sender_username, sender_tenant_id, message)
                VALUES (%s, %s, %s, %s)
                """,
                (room_id, sender_username, sender_tenant_id, message)
            )
            conn.commit(); cur.close(); conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error guardando mensaje de soporte: {e}")
            return False

    def get_support_messages(self, room_id):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                SELECT id, room_id, sender_username, sender_tenant_id, message, created_at 
                FROM support_messages 
                WHERE room_id = %s 
                ORDER BY created_at ASC
                """,
                (room_id,)
            )
            rows = cur.fetchall()
            cur.close(); conn.close()
            return [
                {
                    "id": r[0],
                    "room_id": r[1],
                    "sender_username": r[2],
                    "sender_tenant_id": r[3],
                    "message": r[4],
                    "created_at": r[5]
                }
                for r in rows
            ]
        except Exception as e:
            print(f"[DB] Error obteniendo mensajes de soporte: {e}")
            return []

    def get_all_support_rooms(self):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            # Obtener salas de soporte junto al nombre del tenant correspondiente
            cur.execute(
                """
                SELECT r.id, r.tenant_id, t.name, 
                       (SELECT message FROM support_messages WHERE room_id = r.id ORDER BY created_at DESC LIMIT 1) as last_msg,
                       (SELECT created_at FROM support_messages WHERE room_id = r.id ORDER BY created_at DESC LIMIT 1) as last_time
                FROM support_rooms r
                JOIN tenants t ON r.tenant_id = t.id
                ORDER BY last_time DESC NULLS LAST
                """
            )
            rows = cur.fetchall()
            cur.close(); conn.close()
            return [
                {
                    "id": r[0],
                    "tenant_id": r[1],
                    "tenant_name": r[2],
                    "last_message": r[3] if r[3] else "Sin mensajes",
                    "last_time": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else ""
                }
                for r in rows
            ]
        except Exception as e:
            print(f"[DB] Error obteniendo salas de soporte: {e}")
            return []

    def delete_flow_state(self, wa_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM conversation_flow_state WHERE wa_id = %s", (wa_id,))
            conn.commit(); cur.close(); conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error borrando estado del flujo: {e}")
            return False

db = Database()
