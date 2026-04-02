# 🌐 Network Monitor & Alert System

Système de surveillance réseau en temps réel développé en Python et Bash.

## 📋 Description
Ce projet surveille un réseau local (LAN) en :
- Découvrant les hôtes actifs (ARP + ICMP)
- Scannant les ports TCP ouverts
- Surveillant la bande passante
- Générant des alertes en temps réel

## 🛠️ Technologies
- Python 3.13
- scapy, psutil, requests, rich
- SQLite3
- Bash/Shell

## 🚀 Installation
```bash
git clone https://github.com/nizarelyahyaoui/network-monitor.git
cd network-monitor
python3 -m venv .venv
source .venv/bin/activate
pip install scapy psutil requests pyyaml rich
```

## ▶️ Utilisation
```bash
python3 main.py --subnet 192.168.1.0/24 --interval 30
```

## 📊 Résultats
- Ports détectés sur 192.168.1.1 : 23 (Telnet), 80 (HTTP), 443 (HTTPS)
- Alertes sauvegardées en SQLite et JSONL
- CPU : ~3%, RAM : ~37%

## 👨‍💻 Auteur
Nizar — Projet Réseaux et Systèmes
