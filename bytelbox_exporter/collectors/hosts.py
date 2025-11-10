import logging
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily

logger = logging.getLogger(__name__)


class HostsCollector:
    """Collecteur de métriques Hosts de la Bbox"""
    
    def __init__(self, auth):
        """
        Initialise le collecteur Hosts
        
        Args:
            auth: Instance de BboxAuth pour les requêtes authentifiées
        """
        self.auth = auth
    
    def collect(self):
        """
        Collecte les métriques des hôtes pour Prometheus
        
        Yields:
            MetricFamily: Métriques au format Prometheus
        """
        response = self.auth.get('/api/v1/hosts')
        if not response:
            logger.error("Impossible de récupérer les informations des hôtes")
            return
        
        try:
            data = response.json()
            hosts_data = data[0]['hosts']
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Erreur lors du parsing des données hosts: {e}")
            return
        
        # Nombre total d'hôtes
        total_hosts = GaugeMetricFamily(
            'bytelbox_hosts_total',
            'Nombre total d\'hôtes connus',
            labels=[]
        )
        total_hosts.add_metric([], float(len(hosts_data.get('list', []))))
        yield total_hosts
        
        # Nombre d'hôtes actifs
        active_hosts = GaugeMetricFamily(
            'bytelbox_hosts_active',
            'Nombre d\'hôtes actifs',
            labels=[]
        )
        active_count = sum(1 for host in hosts_data.get('list', []) if host.get('active') == 1)
        active_hosts.add_metric([], float(active_count))
        yield active_hosts
        
        # Métriques par hôte
        host_active = GaugeMetricFamily(
            'bytelbox_host_active',
            'Hôte actif (1=actif, 0=inactif)',
            labels=['id', 'hostname', 'ipaddress', 'macaddress', 'link']
        )
        
        host_guest = GaugeMetricFamily(
            'bytelbox_host_guest',
            'Hôte invité (1=invité, 0=normal)',
            labels=['id', 'hostname', 'ipaddress', 'macaddress']
        )
        
        host_lease = GaugeMetricFamily(
            'bytelbox_host_lease_seconds',
            'Durée du bail DHCP en secondes',
            labels=['id', 'hostname', 'ipaddress', 'macaddress']
        )
        
        # Métriques Ethernet
        host_ethernet_speed = GaugeMetricFamily(
            'bytelbox_host_ethernet_speed_mbps',
            'Vitesse de connexion Ethernet en Mbps',
            labels=['id', 'hostname', 'ipaddress', 'macaddress', 'port', 'mode']
        )
        
        # Métriques WiFi
        host_wifi_rssi = GaugeMetricFamily(
            'bytelbox_host_wifi_rssi_dbm',
            'Puissance du signal WiFi en dBm',
            labels=['id', 'hostname', 'ipaddress', 'macaddress', 'band']
        )
        
        host_wifi_rate = GaugeMetricFamily(
            'bytelbox_host_wifi_rate_mbps',
            'Débit WiFi en Mbps',
            labels=['id', 'hostname', 'ipaddress', 'macaddress', 'band']
        )
        
        host_wifi_estimated_rate = GaugeMetricFamily(
            'bytelbox_host_wifi_estimated_rate_mbps',
            'Débit WiFi estimé en Mbps',
            labels=['id', 'hostname', 'ipaddress', 'macaddress', 'band']
        )
        
        host_wifi_mcs = GaugeMetricFamily(
            'bytelbox_host_wifi_mcs',
            'Index MCS WiFi',
            labels=['id', 'hostname', 'ipaddress', 'macaddress', 'band']
        )
        
        host_wifi_tx_usage = GaugeMetricFamily(
            'bytelbox_host_wifi_tx_usage_percent',
            'Utilisation TX WiFi en pourcentage',
            labels=['id', 'hostname', 'ipaddress', 'macaddress', 'band']
        )
        
        host_wifi_rx_usage = GaugeMetricFamily(
            'bytelbox_host_wifi_rx_usage_percent',
            'Utilisation RX WiFi en pourcentage',
            labels=['id', 'hostname', 'ipaddress', 'macaddress', 'band']
        )
        
        # Nombre d'adresses IPv6 par hôte
        host_ipv6_count = GaugeMetricFamily(
            'bytelbox_host_ipv6_addresses_count',
            'Nombre d\'adresses IPv6 de l\'hôte',
            labels=['id', 'hostname', 'ipaddress', 'macaddress']
        )
        
        for host in hosts_data.get('list', []):
            host_id = str(host.get('id', ''))
            hostname = host.get('hostname', 'unknown')
            ipaddress = host.get('ipaddress', '0.0.0.0')
            macaddress = host.get('macaddress', 'unknown')
            link = host.get('link', 'unknown')
            
            # État actif
            host_active.add_metric(
                [host_id, hostname, ipaddress, macaddress, link],
                float(host.get('active', 0))
            )
            
            # Invité
            host_guest.add_metric(
                [host_id, hostname, ipaddress, macaddress],
                float(host.get('guest', 0))
            )
            
            # Bail DHCP
            lease = host.get('lease', 0)
            if isinstance(lease, (int, str)):
                try:
                    lease_value = float(lease)
                    # Ignorer les baux négatifs ou nuls pour les IP statiques
                    if lease_value > 0:
                        host_lease.add_metric(
                            [host_id, hostname, ipaddress, macaddress],
                            lease_value
                        )
                except (ValueError, TypeError):
                    pass
            
            # Métriques Ethernet
            ethernet = host.get('ethernet', {})
            if ethernet.get('speed', 0) > 0:
                port = str(ethernet.get('physicalport', 0))
                mode = ethernet.get('mode', 'unknown')
                host_ethernet_speed.add_metric(
                    [host_id, hostname, ipaddress, macaddress, port, mode],
                    float(ethernet['speed'])
                )
            
            # Métriques WiFi
            wireless = host.get('wireless', {})
            band = wireless.get('band', '')
            
            if band:  # Si l'hôte est en WiFi
                # RSSI
                rssi_str = wireless.get('rssi0', '0')
                if rssi_str and rssi_str != 0:
                    try:
                        rssi_value = float(str(rssi_str).replace('"', ''))
                        host_wifi_rssi.add_metric(
                            [host_id, hostname, ipaddress, macaddress, str(band)],
                            rssi_value
                        )
                    except (ValueError, TypeError):
                        pass
                
                # Rate
                rate = wireless.get('rate', 0)
                if rate > 0:
                    host_wifi_rate.add_metric(
                        [host_id, hostname, ipaddress, macaddress, str(band)],
                        float(rate)
                    )
                
                # Estimated Rate
                estimated_rate = wireless.get('estimatedRate', 0)
                if estimated_rate > 0:
                    host_wifi_estimated_rate.add_metric(
                        [host_id, hostname, ipaddress, macaddress, str(band)],
                        float(estimated_rate)
                    )
                
                # MCS
                mcs = wireless.get('mcs', 0)
                if mcs > 0:
                    host_wifi_mcs.add_metric(
                        [host_id, hostname, ipaddress, macaddress, str(band)],
                        float(mcs)
                    )
                
                # TX/RX Usage
                tx_usage = wireless.get('txUsage', 0)
                rx_usage = wireless.get('rxUsage', 0)
                
                host_wifi_tx_usage.add_metric(
                    [host_id, hostname, ipaddress, macaddress, str(band)],
                    float(tx_usage)
                )
                
                host_wifi_rx_usage.add_metric(
                    [host_id, hostname, ipaddress, macaddress, str(band)],
                    float(rx_usage)
                )
            
            # Nombre d'adresses IPv6
            ipv6_addresses = host.get('ip6address', [])
            host_ipv6_count.add_metric(
                [host_id, hostname, ipaddress, macaddress],
                float(len(ipv6_addresses))
            )
        
        yield host_active
        yield host_guest
        yield host_lease
        yield host_ethernet_speed
        yield host_wifi_rssi
        yield host_wifi_rate
        yield host_wifi_estimated_rate
        yield host_wifi_mcs
        yield host_wifi_tx_usage
        yield host_wifi_rx_usage
        yield host_ipv6_count
        
        # Statistiques des stations WiFi par bande
        wireless_hosts = hosts_data.get('wirelesshosts', [])
        
        wifi_band_stations = GaugeMetricFamily(
            'bytelbox_wifi_band_stations_count',
            'Nombre de stations par bande WiFi',
            labels=['band_index', 'guest']
        )
        
        for band_index, band_data in enumerate(wireless_hosts):
            is_guest = '1' if band_data.get('guest', 0) == 1 else '0'
            stations_count = len(band_data.get('stations', []))
            
            wifi_band_stations.add_metric(
                [str(band_index), is_guest],
                float(stations_count)
            )
        
        yield wifi_band_stations
        
        # Statistiques des stations WiFi détaillées
        wifi_station_rssi = GaugeMetricFamily(
            'bytelbox_wifi_station_rssi_dbm',
            'RSSI des stations WiFi en dBm',
            labels=['band_index', 'macaddress']
        )
        
        wifi_station_rx_rate = GaugeMetricFamily(
            'bytelbox_wifi_station_rx_rate_mbps',
            'Débit RX des stations WiFi en Mbps',
            labels=['band_index', 'macaddress']
        )
        
        for band_index, band_data in enumerate(wireless_hosts):
            for station in band_data.get('stations', []):
                macaddress = station.get('macaddress', 'unknown')
                
                # RSSI
                rssi_str = station.get('rssi', '0')
                if rssi_str and rssi_str != '0':
                    try:
                        rssi_value = float(str(rssi_str).replace('"', ''))
                        wifi_station_rssi.add_metric(
                            [str(band_index), macaddress],
                            rssi_value
                        )
                    except (ValueError, TypeError):
                        pass
                
                # RX Rate
                rx_rate = station.get('rxRate', 0)
                if rx_rate > 0:
                    wifi_station_rx_rate.add_metric(
                        [str(band_index), macaddress],
                        float(rx_rate)
                    )
        
        yield wifi_station_rssi
        yield wifi_station_rx_rate
