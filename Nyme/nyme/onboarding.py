import requests

class MetaOnboarding:
    def __init__(self):
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def exchange_code_for_long_lived_token(self, client_id: str, client_secret: str, redirect_uri: str, code: str) -> str:
        """
        Intercambia el código de autorización temporal de Facebook por un token de acceso
        de usuario de larga duración (que dura unos 60 días).
        """
        # Paso 1: Intercambiar el código por un token de corta duración
        token_url = f"{self.base_url}/oauth/access_token"
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "client_secret": client_secret,
            "code": code
        }
        
        try:
            print("[Onboarding] Intercambiando código por token de corta duración...")
            res = requests.get(token_url, params=params, timeout=10)
            res_data = res.json()
            if res.status_code != 200 or "access_token" not in res_data:
                print(f"[Onboarding] Error al intercambiar código: {res_data}")
                return None
            
            short_lived_token = res_data["access_token"]
            
            # Paso 2: Intercambiar el token de corta duración por uno de larga duración
            print("[Onboarding] Solicitando token de larga duración de usuario...")
            exchange_params = {
                "grant_type": "fb_exchange_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "fb_exchange_token": short_lived_token
            }
            res_exch = requests.get(token_url, params=exchange_params, timeout=10)
            res_exch_data = res_exch.json()
            if res_exch.status_code == 200 and "access_token" in res_exch_data:
                print("[Onboarding] ✅ Token de larga duración obtenido con éxito.")
                return res_exch_data["access_token"]
            
            # En caso de que falle el intercambio de larga duración, retornamos el de corta duración
            return short_lived_token
        except Exception as e:
            print(f"[Onboarding] Excepción en exchange_code_for_long_lived_token: {e}")
            return None

    def get_pages_and_instagrams(self, user_access_token: str) -> list:
        """
        Obtiene la lista de páginas de Facebook y cuentas de Instagram vinculadas de un usuario.
        Retorna una lista de diccionarios con la información de cada página e Instagram.
        """
        url = f"{self.base_url}/me/accounts"
        params = {
            "access_token": user_access_token,
            "limit": 100
        }
        
        try:
            print("[Onboarding] Solicitando páginas de Facebook...")
            response = requests.get(url, params=params, timeout=10)
            res_data = response.json()
            
            if response.status_code != 200:
                print(f"[Onboarding] Error al obtener páginas de Facebook: {res_data}")
                return []
                
            pages = res_data.get("data", [])
            results = []
            
            for page in pages:
                page_id = page.get("id")
                page_name = page.get("name")
                page_access_token = page.get("access_token") # Este token de página es permanente si el de usuario era de larga duración
                
                if not page_id or not page_access_token:
                    continue
                    
                page_info = {
                    "page_id": page_id,
                    "name": page_name,
                    "access_token": page_access_token,
                    "has_instagram": False,
                    "instagram_id": None,
                    "instagram_username": None
                }
                
                # Intentar obtener la cuenta de Instagram Business asociada a esta página
                ig_info = self.get_instagram_account_for_page(page_id, page_access_token)
                if ig_info:
                    page_info["has_instagram"] = True
                    page_info["instagram_id"] = ig_info.get("id")
                    page_info["instagram_username"] = ig_info.get("username")
                    
                results.append(page_info)
                
            return results
        except Exception as e:
            print(f"[Onboarding] Excepción en get_pages_and_instagrams: {e}")
            return []

    def get_instagram_account_for_page(self, page_id: str, page_access_token: str) -> dict:
        """
        Consulta la cuenta de Instagram Business vinculada a una página de Facebook.
        """
        url = f"{self.base_url}/{page_id}"
        params = {
            "fields": "instagram_business_account{id,username}",
            "access_token": page_access_token
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            res_data = response.json()
            
            if response.status_code == 200 and "instagram_business_account" in res_data:
                return res_data["instagram_business_account"]
        except Exception as e:
            print(f"[Onboarding] Excepción obteniendo Instagram para página {page_id}: {e}")
            
        return None

    def subscribe_app_to_page(self, page_id: str, page_access_token: str) -> bool:
        """
        Suscribe la aplicación de Meta a la página para que Meta empiece a enviar webhooks
        de mensajería de Messenger (y opcionalmente Instagram) a nuestro servidor.
        """
        url = f"{self.base_url}/{page_id}/subscribed_apps"
        params = {
            "subscribed_fields": "messages,messaging_postbacks,message_deliveries,message_reads,message_echoes",
            "access_token": page_access_token
        }
        
        try:
            print(f"[Onboarding] Suscribiendo app a la página {page_id}...")
            response = requests.post(url, params=params, timeout=10)
            res_data = response.json()
            
            if response.status_code == 200 and res_data.get("success") is True:
                print(f"[Onboarding] ✅ Suscripción exitosa para la página {page_id}")
                return True
            else:
                print(f"[Onboarding] ❌ Falló la suscripción para la página {page_id}: {res_data}")
                return False
        except Exception as e:
            print(f"[Onboarding] Excepción al suscribir app a la página {page_id}: {e}")
            return False

meta_onboarding = MetaOnboarding()
