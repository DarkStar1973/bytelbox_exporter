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
python -m bbox_exporter --password VOTRE_MOT_DE_PASSE

# Avec options
python -m bbox_exporter \
  --password VOTRE_MOT_DE_PASSE \
  --port 9100 \
  --bbox-url https://mabbox.bytel.fr \
  --log-level INFO
```

## Options disponibles

- `--bbox-url` : URL de base de la Bbox (défaut: https://mabbox.bytel.fr)
- `--password` : Mot de passe pour l'API Bbox (requis)
- `--port` : Port d'écoute pour l'exporter (défaut: 9100)
- `--verify-ssl` : Vérifier les certificats SSL
- `--log-level` : Niveau de logging (DEBUG, INFO, WARNING, ERROR)

## Configuration Prometheus

Ajoutez à votre `prometheus.yml` :

```yaml
scrape_configs:
  - job_name: 'bbox'
    static_configs:
      - targets: ['localhost:9100']
```

## Métriques exportées

### Métriques LAN globales
- `bbox_lan_rx_bytes_total` : Octets reçus
- `bbox_lan_rx_packets_total` : Paquets reçus
- `bbox_lan_rx_errors_total` : Erreurs en réception
- `bbox_lan_rx_discards_total` : Paquets rejetés en réception
- `bbox_lan_tx_bytes_total` : Octets transmis
- `bbox_lan_tx_packets_total` : Paquets transmis
- `bbox_lan_tx_errors_total` : Erreurs en transmission
- `bbox_lan_tx_discards_total` : Paquets rejetés en transmission

### Métriques par port
- `bbox_port_rx_bandwidth_kbps{port="N"}` : Bande passante RX (kbps)
- `bbox_port_tx_bandwidth_kbps{port="N"}` : Bande passante TX (kbps)
- `bbox_port_rx_bytes_total{port="N"}` : Octets reçus
- `bbox_port_tx_bytes_total{port="N"}` : Octets transmis
- `bbox_port_rx_packets_total{port="N"}` : Paquets reçus
- `bbox_port_tx_packets_total{port="N"}` : Paquets transmis

## Structure du projet

```
bbox_exporter/
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

1. Créez `bbox_exporter/collectors/wan.py`
2. Implémentez la classe `WanCollector` avec une méthode `collect()`
3. Enregistrez le collecteur dans `main.py`

## Licence

MIT
