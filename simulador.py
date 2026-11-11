import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta, timezone

# Configuración de semilla para que los datos sean reproducibles
np.random.seed(42)
random.seed(42)

# 1. DEFINIR EL PERIODO (30 días completos, hasta ayer a las 23:59 UTC)
hoy = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
fecha_inicio = hoy - timedelta(days=30)

# Listas para guardar los eventos
eventos_pixel = []
eventos_capi = []

# Simularemos 150 compras/día en promedio (4500 eventos en total)
total_eventos = 4500

print("Generando datos simulados...")

for i in range(total_eventos):
    # Generar una fecha aleatoria en los últimos 30 días
    dias_aleatorios = random.randint(0, 29)
    horas_aleatorias = random.randint(0, 23)
    
    # Desplazar el 40% de las compras nocturnas al horario diurno (ruido estadístico)
    if horas_aleatorias < 6 or horas_aleatorias > 21:
        if random.random() > 0.6:
            horas_aleatorias = random.randint(10, 20)

    fecha_evento = fecha_inicio + timedelta(days=dias_aleatorios, hours=horas_aleatorias, minutes=random.randint(0,59))
    event_time = int(fecha_evento.timestamp())
    event_id = f"ORDER_{10000 + i}"
    
    # Datos de usuario (simulamos que tenemos el email y teléfono hasheados)
    email_hashed = f"hash_email_{random.randint(1000, 2000)}"
    phone_hashed = f"hash_phone_{random.randint(1000, 2000)}"
    
    # Datos de la campaña
    campaign_type = random.choice(["Cold Traffic", "Retargeting"])
    valor_compra = round(random.uniform(20.0, 150.0), 2)
    
    # ---------------------------------------------------------
    # SIMULACIÓN DEL PIXEL (NAVEGADOR)
    # ---------------------------------------------------------
    # 15% de pérdida por AdBlockers
    pixel_recibe = random.random() > 0.15 
    
    if pixel_recibe:
        eventos_pixel.append({
            "event_id": event_id,
            "event_time": event_time,
            "event_source": "Pixel",
            "email_hashed": email_hashed,
            "phone_hashed": phone_hashed,
            "campaign_type": campaign_type,
            "value": valor_compra
        })
        
    # ---------------------------------------------------------
    # SIMULACIÓN DE LA CAPI (SERVIDOR)
    # ---------------------------------------------------------
    # El servidor siempre recibe el evento, pero simulamos faltas de parámetros
    server_email = email_hashed
    server_phone = phone_hashed
    
    if random.random() < 0.10:
        server_email = None 
    if random.random() < 0.05:
        server_phone = None 
        
    eventos_capi.append({
        "event_id": event_id,
        "event_time": event_time,
        "event_source": "CAPI",
        "email_hashed": server_email,
        "phone_hashed": server_phone,
        "campaign_type": campaign_type,
        "value": valor_compra
    })

# Convertir a DataFrames
df_pixel = pd.DataFrame(eventos_pixel)
df_capi = pd.DataFrame(eventos_capi)

# Guardar en CSV
df_pixel.to_csv("Eventos_Pixel.csv", index=False)
df_capi.to_csv("Eventos_CAPI.csv", index=False)

print(f"✅ Simulación terminada.")
print(f"Total de compras base: {total_eventos}")
print(f"Eventos recibidos por Pixel (Navegador): {len(df_pixel)}")
print(f"Eventos recibidos por CAPI (Servidor): {len(df_capi)}")