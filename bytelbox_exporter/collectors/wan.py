import logging
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily

logger = logging.getLogger(__name__)


class WanCollector:
    """Collecteur de métriques WAN de la Bbox"""
    
    def __init__(self, auth):
        """
        Initialise le collecteur WAN
        
        Args:
            auth: Instance de BboxAuth pour les requêtes authentifiées
        """
        self.auth = auth
    
    def collect(self):
        """
        Collecte les métriques WAN pour Prometheus
        
        Yields:
            MetricFamily: Métriques au format Prometheus
        """
        # Collecte des informations IP WAN
        yield from self._collect_wan_ip()
        
        # Collecte des statistiques WAN
        yield from self._collect_wan_ip_stats()
        
        # Collecte des statistiques FTTH
        yield from self._collect_wan_ftth_stats()
        
        # Collecte des diagnostics WAN
        yield from self._collect_wan_diags()
    
    def _collect_wan_ip(self):
        """Collecte les informations IP WAN /wan/ip"""
        response = self.auth.get('/api/v1/wan/ip')
        if not response:
            logger.error("Impossible de récupérer les informations IP WAN")
            return
        
        try:
            data = response.json()
            wan_data = data[0]['wan']
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Erreur lors du parsing des données WAN IP: {e}")
            return
        
        # État de l'internet WAN
        wan_internet_state = GaugeMetricFamily(
            'bytelbox__wan_internet_state',
            'État de la connexion internet WAN',
            labels=[]
        )
        wan_internet_state.add_metric([], float(wan_data['internet']['state']))
        yield wan_internet_state
        
        # État de l'interface WAN
        wan_interface_state = GaugeMetricFamily(
            'bytelbox__wan_interface_state',
            'État de l\'interface WAN',
            labels=['id']
        )
        wan_interface_state.add_metric(
            [str(wan_data['interface']['id'])],
            float(wan_data['interface']['state'])
        )
        yield wan_interface_state
        
        # Interface par défaut
        wan_interface_default = GaugeMetricFamily(
            'bytelbox__wan_interface_default',
            'Interface WAN par défaut (1=oui, 0=non)',
            labels=['id']
        )
        wan_interface_default.add_metric(
            [str(wan_data['interface']['id'])],
            float(wan_data['interface']['default'])
        )
        yield wan_interface_default
        
        # Informations IP WAN
        wan_ip_info = InfoMetricFamily(
            'bytelbox__wan_ip',
            'Informations sur la configuration IP WAN'
        )
        wan_ip_info.add_metric(
            [],
            {
                'address': wan_data['ip']['address'],
                'gateway': wan_data['ip']['gateway'],
                'subnet': wan_data['ip']['subnet'],
                'mac': wan_data['ip']['mac'],
                'state': wan_data['ip']['state'],
                'ip6state': wan_data['ip']['ip6state'],
                'link_type': wan_data['link']['type'],
                'link_state': wan_data['link']['state']
            }
        )
        yield wan_ip_info
        
        # MTU WAN
        wan_mtu = GaugeMetricFamily(
            'bytelbox__wan_mtu',
            'MTU de l\'interface WAN',
            labels=[]
        )
        wan_mtu.add_metric([], float(wan_data['ip']['mtu']))
        yield wan_mtu
        
        # CGNAT activé
        wan_cgnat = GaugeMetricFamily(
            'bytelbox__wan_cgnat_enabled',
            'CGNAT activé sur le WAN (1=activé, 0=désactivé)',
            labels=[]
        )
        wan_cgnat.add_metric([], float(wan_data['ip']['cgnatenable']))
        yield wan_cgnat
        
        # MAP-T activé
        wan_mapt = GaugeMetricFamily(
            'bytelbox__wan_mapt_enabled',
            'MAP-T activé sur le WAN (1=activé, 0=désactivé)',
            labels=[]
        )
        wan_mapt.add_metric([], float(wan_data['ip']['maptenable']))
        yield wan_mapt
        
        # Nombre d'adresses IPv6 WAN
        wan_ipv6_count = GaugeMetricFamily(
            'bytelbox__wan_ipv6_addresses_count',
            'Nombre d\'adresses IPv6 sur le WAN',
            labels=[]
        )
        wan_ipv6_count.add_metric([], float(len(wan_data['ip'].get('ip6address', []))))
        yield wan_ipv6_count
    
    def _collect_wan_ip_stats(self):
        """Collecte les statistiques IP WAN /wan/ip/stats"""
        response = self.auth.get('/api/v1/wan/ip/stats')
        if not response:
            logger.error("Impossible de récupérer les statistiques IP WAN")
            return
        
        try:
            data = response.json()
            wan_stats = data[0]['wan']['ip']['stats']
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Erreur lors du parsing des données WAN IP stats: {e}")
            return
        
        # Statistiques RX WAN
        wan_rx_bytes = GaugeMetricFamily(
            'bytelbox__wan_rx_bytes_total',
            'Nombre total d\'octets reçus sur le WAN',
            labels=[]
        )
        wan_rx_bytes.add_metric([], float(wan_stats['rx']['bytes']))
        yield wan_rx_bytes
        
        wan_rx_packets = GaugeMetricFamily(
            'bytelbox__wan_rx_packets_total',
            'Nombre total de paquets reçus sur le WAN',
            labels=[]
        )
        wan_rx_packets.add_metric([], float(wan_stats['rx']['packets']))
        yield wan_rx_packets
        
        wan_rx_errors = GaugeMetricFamily(
            'bytelbox__wan_rx_errors_total',
            'Nombre total d\'erreurs en réception sur le WAN',
            labels=[]
        )
        wan_rx_errors.add_metric([], float(wan_stats['rx']['packetserrors']))
        yield wan_rx_errors
        
        wan_rx_discards = GaugeMetricFamily(
            'bytelbox__wan_rx_discards_total',
            'Nombre total de paquets rejetés en réception sur le WAN',
            labels=[]
        )
        wan_rx_discards.add_metric([], float(wan_stats['rx']['packetsdiscards']))
        yield wan_rx_discards
        
        wan_rx_bandwidth = GaugeMetricFamily(
            'bytelbox__wan_rx_bandwidth_kbps',
            'Bande passante en réception sur le WAN (kbps)',
            labels=[]
        )
        wan_rx_bandwidth.add_metric([], float(wan_stats['rx']['bandwidth']))
        yield wan_rx_bandwidth
        
        wan_rx_occupation = GaugeMetricFamily(
            'bytelbox__wan_rx_occupation_percent',
            'Occupation de la bande passante en réception (%)',
            labels=[]
        )
        wan_rx_occupation.add_metric([], float(wan_stats['rx']['occupation']))
        yield wan_rx_occupation
        
        wan_rx_max_bandwidth = GaugeMetricFamily(
            'bytelbox__wan_rx_max_bandwidth_kbps',
            'Bande passante maximale en réception (kbps)',
            labels=[]
        )
        wan_rx_max_bandwidth.add_metric([], float(wan_stats['rx']['maxBandwidth']))
        yield wan_rx_max_bandwidth
        
        wan_rx_contractual_bandwidth = GaugeMetricFamily(
            'bytelbox__wan_rx_contractual_bandwidth_kbps',
            'Bande passante contractuelle en réception (kbps)',
            labels=[]
        )
        wan_rx_contractual_bandwidth.add_metric([], float(wan_stats['rx']['contractualBandwidth']))
        yield wan_rx_contractual_bandwidth
        
        # Statistiques TX WAN
        wan_tx_bytes = GaugeMetricFamily(
            'bytelbox__wan_tx_bytes_total',
            'Nombre total d\'octets transmis sur le WAN',
            labels=[]
        )
        wan_tx_bytes.add_metric([], float(wan_stats['tx']['bytes']))
        yield wan_tx_bytes
        
        wan_tx_packets = GaugeMetricFamily(
            'bytelbox__wan_tx_packets_total',
            'Nombre total de paquets transmis sur le WAN',
            labels=[]
        )
        wan_tx_packets.add_metric([], float(wan_stats['tx']['packets']))
        yield wan_tx_packets
        
        wan_tx_errors = GaugeMetricFamily(
            'bytelbox__wan_tx_errors_total',
            'Nombre total d\'erreurs en transmission sur le WAN',
            labels=[]
        )
        wan_tx_errors.add_metric([], float(wan_stats['tx']['packetserrors']))
        yield wan_tx_errors
        
        wan_tx_discards = GaugeMetricFamily(
            'bytelbox__wan_tx_discards_total',
            'Nombre total de paquets rejetés en transmission sur le WAN',
            labels=[]
        )
        wan_tx_discards.add_metric([], float(wan_stats['tx']['packetsdiscards']))
        yield wan_tx_discards
        
        wan_tx_bandwidth = GaugeMetricFamily(
            'bytelbox__wan_tx_bandwidth_kbps',
            'Bande passante en transmission sur le WAN (kbps)',
            labels=[]
        )
        wan_tx_bandwidth.add_metric([], float(wan_stats['tx']['bandwidth']))
        yield wan_tx_bandwidth
        
        wan_tx_occupation = GaugeMetricFamily(
            'bytelbox__wan_tx_occupation_percent',
            'Occupation de la bande passante en transmission (%)',
            labels=[]
        )
        wan_tx_occupation.add_metric([], float(wan_stats['tx']['occupation']))
        yield wan_tx_occupation
        
        wan_tx_max_bandwidth = GaugeMetricFamily(
            'bytelbox__wan_tx_max_bandwidth_kbps',
            'Bande passante maximale en transmission (kbps)',
            labels=[]
        )
        wan_tx_max_bandwidth.add_metric([], float(wan_stats['tx']['maxBandwidth']))
        yield wan_tx_max_bandwidth
        
        wan_tx_contractual_bandwidth = GaugeMetricFamily(
            'bytelbox__wan_tx_contractual_bandwidth_kbps',
            'Bande passante contractuelle en transmission (kbps)',
            labels=[]
        )
        wan_tx_contractual_bandwidth.add_metric([], float(wan_stats['tx']['contractualBandwidth']))
        yield wan_tx_contractual_bandwidth
    
    def _collect_wan_ftth_stats(self):
        """Collecte les statistiques FTTH /wan/ftth/stats"""
        response = self.auth.get('/api/v1/wan/ftth/stats')
        if not response:
            logger.error("Impossible de récupérer les statistiques FTTH")
            return
        
        try:
            data = response.json()
            ftth_data = data[0]['wan']['ftth']
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Erreur lors du parsing des données FTTH: {e}")
            return
        
        # Informations FTTH
        ftth_info = InfoMetricFamily(
            'bytelbox__wan_ftth',
            'Informations sur la connexion FTTH'
        )
        ftth_info.add_metric(
            [],
            {
                'mode': ftth_data['mode'],
                'state': ftth_data['state']
            }
        )
        yield ftth_info
        
        # État FTTH
        ftth_state = GaugeMetricFamily(
            'bytelbox__wan_ftth_state',
            'État de la connexion FTTH (1=Up, 0=Down)',
            labels=['mode']
        )
        ftth_state.add_metric(
            [ftth_data['mode']],
            1.0 if ftth_data['state'] == 'Up' else 0.0
        )
        yield ftth_state
    
    def _collect_wan_diags(self):
        """Collecte les diagnostics WAN /wan/diags"""
        response = self.auth.get('/api/v1/wan/diags')
        if not response:
            logger.error("Impossible de récupérer les diagnostics WAN")
            return
        
        try:
            data = response.json()
            diags = data[0]['diags']
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Erreur lors du parsing des données de diagnostics WAN: {e}")
            return
        
        # Diagnostics DNS
        for i, dns_diag in enumerate(diags.get('dns', [])):
            protocol = dns_diag.get('protocol', 'unknown')
            status = dns_diag.get('status', 'unknown')
            
            # Métriques DNS min/max/average
            if dns_diag.get('tries', 0) > 0:
                dns_min = GaugeMetricFamily(
                    'bytelbox__wan_dns_min_ms',
                    'Temps de réponse DNS minimum (ms)',
                    labels=['index', 'protocol', 'status']
                )
                dns_min.add_metric([str(i), protocol, status], float(dns_diag['min']))
                yield dns_min
                
                dns_max = GaugeMetricFamily(
                    'bytelbox__wan_dns_max_ms',
                    'Temps de réponse DNS maximum (ms)',
                    labels=['index', 'protocol', 'status']
                )
                dns_max.add_metric([str(i), protocol, status], float(dns_diag['max']))
                yield dns_max
                
                dns_avg = GaugeMetricFamily(
                    'bytelbox__wan_dns_average_ms',
                    'Temps de réponse DNS moyen (ms)',
                    labels=['index', 'protocol', 'status']
                )
                dns_avg.add_metric([str(i), protocol, status], float(dns_diag['average']))
                yield dns_avg
            
            # Statistiques de succès/erreurs DNS
            dns_success = GaugeMetricFamily(
                'bytelbox__wan_dns_success_total',
                'Nombre de requêtes DNS réussies',
                labels=['index', 'protocol', 'status']
            )
            dns_success.add_metric([str(i), protocol, status], float(dns_diag.get('success', 0)))
            yield dns_success
            
            dns_error = GaugeMetricFamily(
                'bytelbox__wan_dns_error_total',
                'Nombre de requêtes DNS en erreur',
                labels=['index', 'protocol', 'status']
            )
            dns_error.add_metric([str(i), protocol, status], float(dns_diag.get('error', 0)))
            yield dns_error
            
            dns_tries = GaugeMetricFamily(
                'bytelbox__wan_dns_tries_total',
                'Nombre total de tentatives DNS',
                labels=['index', 'protocol', 'status']
            )
            dns_tries.add_metric([str(i), protocol, status], float(dns_diag.get('tries', 0)))
            yield dns_tries
        
        # Diagnostics PING
        for i, ping_diag in enumerate(diags.get('ping', [])):
            protocol = ping_diag.get('protocol', 'unknown')
            status = ping_diag.get('status', 'unknown')
            
            # Métriques PING min/max/average
            if ping_diag.get('tries', 0) > 0:
                ping_min = GaugeMetricFamily(
                    'bytelbox__wan_ping_min_us',
                    'Temps de réponse PING minimum (µs)',
                    labels=['index', 'protocol', 'status']
                )
                ping_min.add_metric([str(i), protocol, status], float(ping_diag['min']))
                yield ping_min
                
                ping_max = GaugeMetricFamily(
                    'bytelbox__wan_ping_max_us',
                    'Temps de réponse PING maximum (µs)',
                    labels=['index', 'protocol', 'status']
                )
                ping_max.add_metric([str(i), protocol, status], float(ping_diag['max']))
                yield ping_max
                
                ping_avg = GaugeMetricFamily(
                    'bytelbox__wan_ping_average_us',
                    'Temps de réponse PING moyen (µs)',
                    labels=['index', 'protocol', 'status']
                )
                ping_avg.add_metric([str(i), protocol, status], float(ping_diag['average']))
                yield ping_avg
            
            # Statistiques de succès/erreurs PING
            ping_success = GaugeMetricFamily(
                'bytelbox__wan_ping_success_total',
                'Nombre de ping réussis',
                labels=['index', 'protocol', 'status']
            )
            ping_success.add_metric([str(i), protocol, status], float(ping_diag.get('success', 0)))
            yield ping_success
            
            ping_error = GaugeMetricFamily(
                'bytelbox__wan_ping_error_total',
                'Nombre de ping en erreur',
                labels=['index', 'protocol', 'status']
            )
            ping_error.add_metric([str(i), protocol, status], float(ping_diag.get('error', 0)))
            yield ping_error
            
            ping_tries = GaugeMetricFamily(
                'bytelbox__wan_ping_tries_total',
                'Nombre total de tentatives ping',
                labels=['index', 'protocol', 'status']
            )
            ping_tries.add_metric([str(i), protocol, status], float(ping_diag.get('tries', 0)))
            yield ping_tries
        
        # Diagnostics HTTP
        for i, http_diag in enumerate(diags.get('http', [])):
            protocol = http_diag.get('protocol', 'unknown')
            status = http_diag.get('status', 'unknown')
            
            # Métriques HTTP min/max/average
            if http_diag.get('tries', 0) > 0:
                http_min = GaugeMetricFamily(
                    'bytelbox__wan_http_min_us',
                    'Temps de réponse HTTP minimum (µs)',
                    labels=['index', 'protocol', 'status']
                )
                http_min.add_metric([str(i), protocol, status], float(http_diag['min']))
                yield http_min
                
                http_max = GaugeMetricFamily(
                    'bytelbox__wan_http_max_us',
                    'Temps de réponse HTTP maximum (µs)',
                    labels=['index', 'protocol', 'status']
                )
                http_max.add_metric([str(i), protocol, status], float(http_diag['max']))
                yield http_max
                
                http_avg = GaugeMetricFamily(
                    'bytelbox__wan_http_average_us',
                    'Temps de réponse HTTP moyen (µs)',
                    labels=['index', 'protocol', 'status']
                )
                http_avg.add_metric([str(i), protocol, status], float(http_diag['average']))
                yield http_avg
            
            # Statistiques de succès/erreurs HTTP
            http_success = GaugeMetricFamily(
                'bytelbox__wan_http_success_total',
                'Nombre de requêtes HTTP réussies',
                labels=['index', 'protocol', 'status']
            )
            http_success.add_metric([str(i), protocol, status], float(http_diag.get('success', 0)))
            yield http_success
            
            http_error = GaugeMetricFamily(
                'bytelbox__wan_http_error_total',
                'Nombre de requêtes HTTP en erreur',
                labels=['index', 'protocol', 'status']
            )
            http_error.add_metric([str(i), protocol, status], float(http_diag.get('error', 0)))
            yield http_error
            
            http_tries = GaugeMetricFamily(
                'bytelbox__wan_http_tries_total',
                'Nombre total de tentatives HTTP',
                labels=['index', 'protocol', 'status']
            )
            http_tries.add_metric([str(i), protocol, status], float(http_diag.get('tries', 0)))
            yield http_tries
