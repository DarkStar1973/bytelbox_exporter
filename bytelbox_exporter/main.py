import logging
import argparse
from prometheus_client import start_http_server, REGISTRY

from .auth import BboxAuth
from .collectors import LanCollector, WanCollector, HostsCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description='Bbox Prometheus Exporter - Exporte les métriques du routeur Bbox'
    )
    parser.add_argument(
        '--bytelbox-url',
        default='https://mabbox.bytel.fr',
        help='URL de base de la Bbox (défaut: https://mabbox.bytel.fr)'
    )
    parser.add_argument(
        '--password',
        required=True,
        help='Mot de passe pour l\'API Bbox'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9100,
        help='Port d\'écoute pour l\'exporter (défaut: 9100)'
    )
    parser.add_argument(
        '--verify-ssl',
        action='store_true',
        help='Vérifier les certificats SSL'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Niveau de logging (défaut: INFO)'
    )
    
    return parser.parse_args()


def main():
    """Point d'entrée principal de l'exporter"""
    args = parse_args()
    
    # Configuration du logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Initialisation de l'authentification
    auth = BboxAuth(args.bytelbox_url, args.password, args.verify_ssl)
    
    # Authentification initiale
    logger.info("Tentative d'authentification sur la Bbox...")
    if not auth.authenticate():
        logger.error("Échec de l'authentification initiale. Vérifiez votre mot de passe.")
        return 1
    
    # Enregistrement des collecteurs
    logger.info("Enregistrement des collecteurs de métriques...")
    lan_collector = LanCollector(auth)
    REGISTRY.register(lan_collector)

    wan_collector = WanCollector(auth)
    REGISTRY.register(wan_collector)

    hosts_collector = HostsCollector(auth)
    REGISTRY.register(hosts_collector)
    
    # Démarrage du serveur HTTP
    start_http_server(args.port)
    logger.info(f"Exporter démarré sur le port {args.port}")
    logger.info(f"Métriques disponibles sur http://localhost:{args.port}/metrics")
    
    # Boucle infinie
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Arrêt de l'exporter")
        return 0


if __name__ == '__main__':
    exit(main())
