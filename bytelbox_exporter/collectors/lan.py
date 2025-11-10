import logging
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily

logger = logging.getLogger(__name__)


class LanCollector:
    """Collecteur de métriques LAN de la Bbox"""
    
    def __init__(self, auth):
        """
        Initialise le collecteur LAN
        
        Args:
            auth: Instance de BboxAuth pour les requêtes authentifiées
        """
        self.auth = auth
    
    def collect(self):
        """
        Collecte les métriques LAN pour Prometheus
        
        Yields:
            MetricFamily: Métriques au format Prometheus
        """
        # Collecte des statistiques LAN
        yield from self._collect_lan_stats()
        
        # Collecte des informations IP LAN
        yield from self._collect_lan_ip()
    
    def _collect_lan_stats(self):
        """Collecte les statistiques LAN /lan/stats"""
        response = self.auth.get('/api/v1/lan/stats')
        if not response:
            logger.error("Impossible de récupérer les statistiques LAN")
            return
        
        try:
            data = response.json()
            lan_stats = data[0]['lan']['stats']
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Erreur lors du parsing des données LAN stats: {e}")
            return
        
        # === Métriques globales LAN RX ===
        rx_bytes = GaugeMetricFamily(
            'bytelbox__lan_rx_bytes_total',
            'Nombre total d\'octets reçus sur le LAN',
            labels=[]
        )
        rx_bytes.add_metric([], float(lan_stats['rx']['bytes']))
        yield rx_bytes
        
        rx_packets = GaugeMetricFamily(
            'bytelbox__lan_rx_packets_total',
            'Nombre total de paquets reçus sur le LAN',
            labels=[]
        )
        rx_packets.add_metric([], float(lan_stats['rx']['packets']))
        yield rx_packets
        
        rx_errors = GaugeMetricFamily(
            'bytelbox__lan_rx_errors_total',
            'Nombre total d\'erreurs en réception sur le LAN',
            labels=[]
        )
        rx_errors.add_metric([], float(lan_stats['rx']['packetserrors']))
        yield rx_errors
        
        rx_discards = GaugeMetricFamily(
            'bytelbox__lan_rx_discards_total',
            'Nombre total de paquets rejetés en réception sur le LAN',
            labels=[]
        )
        rx_discards.add_metric([], float(lan_stats['rx']['packetsdiscards']))
        yield rx_discards
        
        # === Métriques globales LAN TX ===
        tx_bytes = GaugeMetricFamily(
            'bytelbox__lan_tx_bytes_total',
            'Nombre total d\'octets transmis sur le LAN',
            labels=[]
        )
        tx_bytes.add_metric([], float(lan_stats['tx']['bytes']))
        yield tx_bytes
        
        tx_packets = GaugeMetricFamily(
            'bytelbox__lan_tx_packets_total',
            'Nombre total de paquets transmis sur le LAN',
            labels=[]
        )
        tx_packets.add_metric([], float(lan_stats['tx']['packets']))
        yield tx_packets
        
        tx_errors = GaugeMetricFamily(
            'bytelbox__lan_tx_errors_total',
            'Nombre total d\'erreurs en transmission sur le LAN',
            labels=[]
        )
        tx_errors.add_metric([], float(lan_stats['tx']['packetserrors']))
        yield tx_errors
        
        tx_discards = GaugeMetricFamily(
            'bytelbox__lan_tx_discards_total',
            'Nombre total de paquets rejetés en transmission sur le LAN',
            labels=[]
        )
        tx_discards.add_metric([], float(lan_stats['tx']['packetsdiscards']))
        yield tx_discards
        
        # === Métriques par port ===
        port_rx_bandwidth = GaugeMetricFamily(
            'bytelbox__port_rx_bandwidth_kbps',
            'Bande passante en réception par port (kbps)',
            labels=['port']
        )
        port_tx_bandwidth = GaugeMetricFamily(
            'bytelbox__port_tx_bandwidth_kbps',
            'Bande passante en transmission par port (kbps)',
            labels=['port']
        )
        port_rx_bytes = GaugeMetricFamily(
            'bytelbox__port_rx_bytes_total',
            'Nombre total d\'octets reçus par port',
            labels=['port']
        )
        port_tx_bytes = GaugeMetricFamily(
            'bytelbox__port_tx_bytes_total',
            'Nombre total d\'octets transmis par port',
            labels=['port']
        )
        port_rx_packets = GaugeMetricFamily(
            'bytelbox__port_rx_packets_total',
            'Nombre total de paquets reçus par port',
            labels=['port']
        )
        port_tx_packets = GaugeMetricFamily(
            'bytelbox__port_tx_packets_total',
            'Nombre total de paquets transmis par port',
            labels=['port']
        )
        
        for port in lan_stats['port']:
            port_id = str(port['index'])
            
            port_rx_bandwidth.add_metric([port_id], float(port['rx']['bandwidth']))
            port_tx_bandwidth.add_metric([port_id], float(port['tx']['bandwidth']))
            port_rx_bytes.add_metric([port_id], float(port['rx']['bytes']))
            port_tx_bytes.add_metric([port_id], float(port['tx']['bytes']))
            port_rx_packets.add_metric([port_id], float(port['rx']['packets']))
            port_tx_packets.add_metric([port_id], float(port['tx']['packets']))
        
        yield port_rx_bandwidth
        yield port_tx_bandwidth
        yield port_rx_bytes
        yield port_tx_bytes
        yield port_rx_packets
        yield port_tx_packets
    
    def _collect_lan_ip(self):
        """Collecte les informations IP LAN /lan/ip"""
        response = self.auth.get('/api/v1/lan/ip')
        if not response:
            logger.error("Impossible de récupérer les informations IP LAN")
            return
        
        try:
            data = response.json()
            lan_data = data[0]['lan']
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Erreur lors du parsing des données LAN IP: {e}")
            return
        
        # Informations IP LAN
        lan_ip_info = InfoMetricFamily(
            'bytelbox__lan_ip',
            'Informations sur la configuration IP LAN'
        )
        lan_ip_info.add_metric(
            [],
            {
                'state': lan_data['ip']['state'],
                'ipaddress': lan_data['ip']['ipaddress'],
                'netmask': lan_data['ip']['netmask'],
                'mac': lan_data['ip']['mac'],
                'hostname': lan_data['ip']['hostname'],
                'domain': lan_data['ip']['domain']
            }
        )
        yield lan_ip_info
        
        # MTU LAN
        lan_mtu = GaugeMetricFamily(
            'bytelbox__lan_mtu',
            'MTU de l\'interface LAN',
            labels=[]
        )
        lan_mtu.add_metric([], float(lan_data['ip']['mtu']))
        yield lan_mtu
        
        # État IPv6 LAN
        lan_ipv6_enabled = GaugeMetricFamily(
            'bytelbox__lan_ipv6_enabled',
            'IPv6 activé sur le LAN (1=activé, 0=désactivé)',
            labels=[]
        )
        lan_ipv6_enabled.add_metric([], float(lan_data['ip']['ip6enable']))
        yield lan_ipv6_enabled
        
        # Nombre d'adresses IPv6 LAN
        lan_ipv6_count = GaugeMetricFamily(
            'bytelbox__lan_ipv6_addresses_count',
            'Nombre d\'adresses IPv6 sur le LAN',
            labels=[]
        )
        lan_ipv6_count.add_metric([], float(len(lan_data['ip'].get('ip6address', []))))
        yield lan_ipv6_count
        
        # État des ports du switch
        switch_port_state = GaugeMetricFamily(
            'bytelbox__switch_port_state',
            'État du port du switch (1=Up, 0=Down)',
            labels=['port', 'link_mode']
        )
        switch_port_blocked = GaugeMetricFamily(
            'bytelbox__switch_port_blocked',
            'Port du switch bloqué (1=bloqué, 0=non bloqué)',
            labels=['port']
        )
        switch_port_flickering = GaugeMetricFamily(
            'bytelbox__switch_port_flickering',
            'Port du switch en flickering (1=flickering, 0=stable)',
            labels=['port']
        )
        
        for port in lan_data['switch']['ports']:
            port_id = str(port['id'])
            link_mode = port['link_mode']
            state_value = 1.0 if port['state'] == 'Up' else 0.0
            
            switch_port_state.add_metric([port_id, link_mode], state_value)
            switch_port_blocked.add_metric([port_id], float(port['blocked']))
            switch_port_flickering.add_metric([port_id], float(port['flickering']))
        
        yield switch_port_state
        yield switch_port_blocked
        yield switch_port_flickering