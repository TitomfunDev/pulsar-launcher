import minecraft_launcher_lib.microsoft_account as ms_auth
from minecraft_launcher_lib.exceptions import InvalidRefreshToken
import keyring
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

# All variables needed
# Microsoft / WebServer
CLIENT_ID = "1eff74ba-7d03-4976-aaeb-8866913c1776"
REDIRECT_URL = "http://localhost:9000"
PORT = 9000
intercepted_path = None
# Keyring
SERVICE_NAME = "pulsar_launcher"
ACCOUNT_KEY = "minecraft_refresh_token"


# Keyring functions
def _save_refresh_token(refresh_token: str):
    keyring.set_password(SERVICE_NAME, ACCOUNT_KEY, refresh_token)

def _get_refresh_token() -> str | None:
    return keyring.get_password(SERVICE_NAME, ACCOUNT_KEY)

def logout():
    try:
        keyring.delete_password(SERVICE_NAME, ACCOUNT_KEY)
    except Exception:
        pass

# Login functions
class OAuthRedirectHandler(BaseHTTPRequestHandler):
    """Temporary Web server listening Microsoft redirection."""
    
    def do_GET(self):
        global intercepted_path
        
        if "code=" in self.path or "error=" in self.path:
            intercepted_path = self.path
        
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        html_response = """
        <!DOCTYPE html>
        <html>
        <head><title>Connexion Réussie</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding-top: 50px; background-color: #121212; color: #ffffff;">
            <h1 style="color: #55FF55;">✅ Connexion réussie !</h1>
            <p style="font-size: 18px;">Vous pouvez maintenant fermer cette fenêtre et retourner sur le launcher si elle ne se ferme pas automatiquement.</p>
            <script>
                let timeLeft = 5;
                const timerElement = document.getElementById('timer');
                
                const countdown = setInterval(() => {
                    timeLeft--;
                    timerElement.textContent = timeLeft;
                    
                    if (timeLeft <= 0) {
                        clearInterval(countdown);
                        // Tentative de fermeture de la fenêtre/onglet
                        window.close();
                    }
                }, 1000);
            </script>
        </body>
        </html>
        """
        self.wfile.write(html_response.encode("utf-8"))

    def log_message(self, format, *args):
        return

def login():
    global intercepted_path
    intercepted_path = None

    login_url, state, code_verifier = ms_auth.get_secure_login_data(CLIENT_ID, REDIRECT_URL)

    try:
        server = HTTPServer(('localhost', PORT), OAuthRedirectHandler)
    except OSError:
        print(f"Erreur : Le port {PORT} est déjà utilisé par une autre application.")
        return None
    
    server.timeout = 120

    webbrowser.open(login_url)

    server.handle_request()
    server.server_close()

    if intercepted_path is None:
        return None

    full_redirect_url = f"{REDIRECT_URL}{intercepted_path}"

    try:
        auth_code =ms_auth.parse_auth_code_url(full_redirect_url, state)
        login_data = ms_auth.complete_login(
            CLIENT_ID, None, REDIRECT_URL, auth_code, code_verifier
        )

        _save_refresh_token(login_data["refresh_token"])

    except Exception as e:
        print(f"\n❌ Erreur lors du traitement du code : {e}")
        return None

def get_valid_session() -> dict | None:
    refresh_token = _get_refresh_token() 
    
    if not refresh_token:
        return None
        
    try:
        session_data = ms_auth.complete_refresh(CLIENT_ID, None, REDIRECT_URL, refresh_token)

        if "refresh_token" in session_data:
            _save_refresh_token(session_data["refresh_token"])
            
        return session_data
        
    except InvalidRefreshToken:
        print("La session a expiré. Une nouvelle connexion est requise.")
        logout()
        return None
    except Exception as e:
        print(f"Erreur de connexion aux serveurs Microsoft : {e}")
        return None