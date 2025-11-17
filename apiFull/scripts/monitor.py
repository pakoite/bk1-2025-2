#!/usr/bin/env python
"""
Script simple de monitoreo para la API
"""

import requests
import time
import sys
from datetime import datetime

API_URL = "http://localhost:5000"
CHECK_INTERVAL = 60  # segundos

def check_health():
    """Verificar el health check de la API"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        data = response.json()
        
        status = data.get('status', 'unknown')
        checks = data.get('checks', {})
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Status: {status}")
        
        for check_name, check_status in checks.items():
            emoji = "✅" if check_status == "healthy" else "❌"
            print(f"  {emoji} {check_name}: {check_status}")
        
        if 'system' in data:
            system = data['system']
            print(f"  💻 CPU: {system.get('cpu_percent', 0):.1f}%")
            print(f"  🧠 RAM: {system.get('memory_percent', 0):.1f}%")
            print(f"  💾 Disk: {system.get('disk_percent', 0):.1f}%")
        
        print()
        
        return status == "healthy"
        
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error: {e}")
        print()
        return False

def main():
    """Ejecutar monitoreo continuo"""
    print("🔍 Iniciando monitoreo de la API...")
    print(f"📊 URL: {API_URL}")
    print(f"⏱️  Intervalo: {CHECK_INTERVAL} segundos")
    print()
    
    try:
        while True:
            healthy = check_health()
            
            if not healthy:
                # Aquí podrías enviar alertas (email, Slack, etc.)
                print("⚠️  ALERTA: La API no está saludable!")
                print()
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoreo detenido")
        sys.exit(0)

if __name__ == '__main__':
    main()