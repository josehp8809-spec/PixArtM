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
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            # Migraciones Multi-tenant: Agregar tenant_id con valor por defecto 1 a todas las tablas principales
            tables_to_migrate = ["users", "lines", "contacts", "messages", "orders", "products", "quick_replies", "conversation_status", "user_lines"]
            for table in tables_to_migrate:
                cur.execute(
                    f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS tenant_id INTEGER REFERENCES tenants(id) DEFAULT 1"
                )
                # Llenar registros anteriores huérfanos con el tenant 1
                cur.execute(f"UPDATE {table} SET tenant_id = 1 WHERE tenant_id IS NULL")
            
            # Cambiar clave primaria de contacts a compuesta (wa_id, tenant_id)
            try:
                # Verificar si ya es compuesta buscando en las restricciones
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

            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"[DB] Error inicializando tablas: {e}")
            return False

    # ── Messages ──────────────────────────────────────────────────────

    def save_message(self, wa_id, msg_type, body, agent_username=None, line_id=None, tenant_id=1):
         if not self._check_available():
             return False
         try:
             conn = self.get_connection()
             cur = conn.cursor()
             cur.execute(
                 "INSERT INTO messages (wa_id, type, body, agent_username, line_id, tenant_id) VALUES (%s, %s, %s, %s, %s, %s)",
                 (wa_id, msg_type, body, agent_username, line_id, tenant_id),
             )
             if msg_type in ("OUTBOUND_INIT", "OUTBOUND_REPLY"):
                 cur.execute(
                     "INSERT INTO quota_logs (type, agent_username, tenant_id) VALUES (%s, %s, %s)",
                     (msg_type, agent_username, tenant_id),
                 )
             conn.commit()
             cur.close()
             conn.close()
             return True
         except Exception as e:
             print(f"[DB] Error guardando mensaje: {e}")
             return False

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
             conn = self.get_connection()
             cur = conn.cursor()
             cur.execute(
                 """
                 SELECT type, body, created_at, agent_username, line_id
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

    ROLE_LIMITS = {"admin": 2, "coordinator": 3, "agent": 10}

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

    def get_all_users(self, tenant_id):
        """Obtiene todos los usuarios de un tenant específico."""
        if not self._check_available():
            return []
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, username, full_name, role, is_active, created_at FROM users WHERE tenant_id = %s ORDER BY role, username",
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

    def create_line(self, name, phone_number_id, access_token, welcome_message, welcome_active, color, tenant_id):
        if not self._check_available(): return False, "DB no disponible"
        if self.count_lines(tenant_id) >= self.MAX_LINES: return False, f"Límite de {self.MAX_LINES} líneas alcanzado"
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "INSERT INTO lines (name, phone_number_id, access_token, welcome_message, welcome_active, color, tenant_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (name, phone_number_id, access_token, welcome_message, welcome_active, color, tenant_id)
            )
            conn.commit(); cur.close(); conn.close(); return True, ""
        except Exception as e: return False, str(e)

    def get_all_lines(self, tenant_id):
        if not self._check_available(): return []
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT id, name, phone_number_id, access_token, welcome_message, welcome_active, color, is_active FROM lines WHERE tenant_id = %s ORDER BY id", (tenant_id,))
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        except Exception: return []

    def get_line_by_id(self, line_id, tenant_id):
        if not self._check_available(): return None
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT id, name, phone_number_id, access_token, welcome_message, welcome_active, color, is_active, tenant_id FROM lines WHERE id = %s AND tenant_id = %s", (line_id, tenant_id))
            row = cur.fetchone(); cur.close(); conn.close()
            if not row: return None
            keys = ["id","name","phone_number_id","access_token","welcome_message","welcome_active","color","is_active","tenant_id"]
            return dict(zip(keys, row))
        except Exception: return None

    def get_line_by_phone_id(self, phone_number_id):
        """Obtiene la línea por su id de teléfono (usado por webhook Meta, por lo que incluye el tenant_id)."""
        if not self._check_available(): return None
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute("SELECT id, name, phone_number_id, access_token, welcome_message, welcome_active, color, is_active, tenant_id FROM lines WHERE phone_number_id = %s AND is_active = TRUE", (phone_number_id,))
            row = cur.fetchone(); cur.close(); conn.close()
            if not row: return None
            keys = ["id","name","phone_number_id","access_token","welcome_message","welcome_active","color","is_active","tenant_id"]
            return dict(zip(keys, row))
        except Exception: return None

    def update_line(self, line_id, name, phone_number_id, access_token, welcome_message, welcome_active, color, tenant_id):
        if not self._check_available(): return False
        try:
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                "UPDATE lines SET name=%s, phone_number_id=%s, access_token=%s, welcome_message=%s, welcome_active=%s, color=%s WHERE id=%s AND tenant_id=%s",
                (name, phone_number_id, access_token, welcome_message, welcome_active, color, line_id, tenant_id)
            )
            conn.commit(); cur.close(); conn.close(); return True
        except Exception: return False

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
                            COALESCE(cs.unread,0) AS unread
                     FROM messages m
                     LEFT JOIN conversation_status cs
                           ON cs.wa_id = m.wa_id AND cs.line_id IS NOT DISTINCT FROM m.line_id
                     WHERE m.tenant_id = %s
                     GROUP BY m.wa_id, m.line_id, cs.status, cs.unread
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
                            COALESCE(cs.unread,0) AS unread
                     FROM messages m
                     LEFT JOIN conversation_status cs
                           ON cs.wa_id = m.wa_id AND cs.line_id IS NOT DISTINCT FROM m.line_id
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
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO conversation_status (wa_id, line_id, status, unread)
                VALUES (%s, %s, 'pending', 1)
                ON CONFLICT (wa_id, COALESCE(line_id, 0))
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
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO conversation_status (wa_id, line_id, unread)
                VALUES (%s, %s, 0)
                ON CONFLICT (wa_id, COALESCE(line_id, 0))
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
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO conversation_status (wa_id, line_id, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (wa_id, COALESCE(line_id, 0))
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
            conn = self.get_connection(); cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO conversation_status (wa_id, line_id, assigned_to, tenant_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (wa_id, COALESCE(line_id, 0))
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
            if status:
                conditions.append("status = %s")
                params.append(status)
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

db = Database()
