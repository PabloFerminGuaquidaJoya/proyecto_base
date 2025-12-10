#!/usr/bin/env python3
"""
Script para probar el endpoint POST /reportes/crear/
"""

import requests
import json
from datetime import date

# Configuración
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = f"{BASE_URL}/reportes/crear/"

# Datos de prueba
test_data = {
    "tipo_reporte": 1,  # Asumiendo que existe un tipo de reporte con ID 1
    "nombre_reporte": "Reporte de Prueba API",
    "descripcion": "Este es un reporte creado mediante el endpoint POST",
    "formato": "pdf",
    "fecha_inicio": "2024-01-01",
    "fecha_fin": "2024-12-31",
    "categoria": "1",
    "centro_formacion": "Centro Principal",
    "estado_maquina": "operativa"
}

def test_endpoint():
    """Función para probar el endpoint"""
    print("🔄 Probando endpoint POST /reportes/crear/")
    print(f"URL: {ENDPOINT}")
    print(f"Datos: {json.dumps(test_data, indent=2)}")
    print("-" * 50)

    try:
        # Test con JSON
        print("📤 Enviando request con Content-Type: application/json")
        response = requests.post(
            ENDPOINT,
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200 or response.status_code == 201:
            print("✅ SUCCESS!")
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")

            if response_data.get('success'):
                reporte_id = response_data.get('reporte_id')
                print(f"🆔 Reporte creado con ID: {reporte_id}")
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor")
        print("Asegúrate de que el servidor Django esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_form_data():
    """Función para probar el endpoint con form data"""
    print("\n" + "="*50)
    print("📤 Enviando request con Content-Type: application/x-www-form-urlencoded")

    try:
        response = requests.post(
            ENDPOINT,
            data=test_data,
            headers={
                'Accept': 'application/json'
            }
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200 or response.status_code == 201:
            print("✅ SUCCESS!")
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("🧪 TESTING REPORTES API ENDPOINT")
    print("="*50)

    # Test con JSON
    test_endpoint()

    # Test con form data
    test_form_data()

    print("\n" + "="*50)
    print("🔚 Pruebas completadas")
    print("\nPara usar el endpoint:")
    print("1. POST a /reportes/crear/")
    print("2. Content-Type: application/json o application/x-www-form-urlencoded")
    print("3. Campos requeridos: tipo_reporte, nombre_reporte")
    print("4. Respuesta: JSON con success=true y datos del reporte")