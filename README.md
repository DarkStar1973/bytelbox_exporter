# Bbox Prometheus Exporter

Exporter Prometheus pour routeur Bbox (Bouygues Telecom).

## Installation

```bash
# Installation des dépendances
pip install -r requirements.txt

# Ou installation du package
pip install -e .
```

## Utilisation

```bash
# Lancement basique
python -m bytelbox_exporter --password VOTRE_MOT_DE_PASSE

# Avec options
python -m bytelbox_exporter \
  --password VOTRE_MOT_DE_PASSE \
  --port 9100 \
  --bytelbox-url https://mabbox.bytel.fr \
  --log-level INFO
```

## Options disponibles

- `--bytelbox-url` : URL de base de la Bbox (défaut: https://mabbox.bytel.fr)
- `--password` : Mot de passe pour l'API Bbox (requis)
- `--port` : Port d'écoute pour l'exporter (défaut: 9100)
- `--verify-ssl` : Vérifier les certificats SSL
- `--log-level` : Niveau de logging (DEBUG, INFO, WARNING, ERROR)

## Configuration Prometheus

Ajoutez à votre `prometheus.yml` :

```yaml
scrape_configs:
  - job_name: 'bytelbox'
    static_configs:
      - targets: ['localhost:9100']
```

## Métriques exportées

### Métriques LAN globales
- `bytelbox_lan_rx_bytes_total` : Octets reçus
- `bytelbox_lan_rx_packets_total` : Paquets reçus
- `bytelbox_lan_rx_errors_total` : Erreurs en réception
- `bytelbox_lan_rx_discards_total` : Paquets rejetés en réception
- `bytelbox_lan_tx_bytes_total` : Octets transmis
- `bytelbox_lan_tx_packets_total` : Paquets transmis
- `bytelbox_lan_tx_errors_total` : Erreurs en transmission
- `bytelbox_lan_tx_discards_total` : Paquets rejetés en transmission

### Métriques par port
- `bytelbox_port_rx_bandwidth_kbps{port="N"}` : Bande passante RX (kbps)
- `bytelbox_port_tx_bandwidth_kbps{port="N"}` : Bande passante TX (kbps)
- `bytelbox_port_rx_bytes_total{port="N"}` : Octets reçus
- `bytelbox_port_tx_bytes_total{port="N"}` : Octets transmis
- `bytelbox_port_rx_packets_total{port="N"}` : Paquets reçus
- `bytelbox_port_tx_packets_total{port="N"}` : Paquets transmis

## Structure du projet

```
bytelbox_exporter/
├── __init__.py
├── __main__.py
├── main.py              # Point d'entrée et CLI
├── auth.py              # Gestion de l'authentification
└── collectors/
    ├── __init__.py
    └── lan.py           # Collecteur LAN
```

## Ajouter un nouveau collecteur

Pour ajouter un endpoint (exemple `/wan/stats`) :

1. Créez `bytelbox_exporter/collectors/wan.py`
2. Implémentez la classe `WanCollector` avec une méthode `collect()`
3. Enregistrez le collecteur dans `main.py`

## Licence

MIT
