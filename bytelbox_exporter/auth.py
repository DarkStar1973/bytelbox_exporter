import logging
import requests
import urllib3

# Désactiver les avertissements SSL si nécessaire
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class BboxAuth:
    """Gestion de l'authentification avec la Bbox"""
    
    def __init__(self, bytelbox_url, password, verify_ssl=False):
        """
        Initialise la gestion d'authentification
        
        Args:
            bytelbox_url: URL de base de la Bbox
            password: Mot de passe pour l'API
            verify_ssl: Vérifier les certificats SSL
        """
        self.bytelbox_url = bytelbox_url.rstrip('/')
        self.password = password
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self._authenticated = False
        
    def authenticate(self):
        """
        Authentifie l'utilisateur et stocke le cookie de session
        
        Returns:
            bool: True si l'authentification a réussi
        """
        try:
            login_url = f"{self.bytelbox_url}/api/v1/login"
            response = self.session.post(
                login_url,
                data={"password": self.password},
                verify=self.verify_ssl,
                timeout=10
            )
            response.raise_for_status()
            
            # Vérification de la présence du cookie
            if 'Set-Cookie' in response.headers or self.session.cookies:
                logger.info("Authentification réussie sur la Bbox")
                self._authenticated = True
                return True
            else:
                logger.error("Pas de cookie reçu après authentification")
                self._authenticated = False
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur d'authentification: {e}")
            self._authenticated = False
            return False
    
    def get(self, endpoint, **kwargs):
        """
        Effectue une requête GET authentifiée
        
        Args:
            endpoint: Chemin de l'endpoint (ex: '/api/v1/lan/stats')
            **kwargs: Arguments supplémentaires pour requests.get
            
        Returns:
            requests.Response ou None en cas d'erreur
        """
        if not self._authenticated:
            if not self.authenticate():
                return None
        
        try:
            url = f"{self.bytelbox_url}{endpoint}"
            kwargs.setdefault('verify', self.verify_ssl)
            kwargs.setdefault('timeout', 10)
            
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête GET {endpoint}: {e}")
            # Tentative de réauthentification en cas d'erreur
            self._authenticated = False
            return None
    
    def is_authenticated(self):
        """Retourne l'état de l'authentification"""
        return self._authenticated

