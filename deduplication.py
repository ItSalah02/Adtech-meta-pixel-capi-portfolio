import pandas as pd
import sqlite3
import numpy as np

np.random.seed(42)  # gasto reproducible entre ejecuciones

print("Iniciando proceso de Deduplicación y SQL...")

# 1. Conectar a la base de datos en memoria
conn = sqlite3.connect(':memory:')

# 2. Cargar los CSV en DataFrames
df_pixel = pd.read_csv('Eventos_Pixel.csv')
df_capi = pd.read_csv('Eventos_CAPI.csv')

# 3. Importar los DataFrames a tablas SQL
df_pixel.to_sql('Eventos_Pixel', conn, index=False, if_exists='replace')
df_capi.to_sql('Eventos_CAPI', conn, index=False, if_exists='replace')

# 4. CONSULTA SQL MAESTRA (Usando LEFT JOIN y convirtiendo el timestamp a fecha)
query_deduplicacion = """
    SELECT 
        c.event_id,
        c.campaign_type,
        c.value,
        strftime('%Y%m%d', c.event_time, 'unixepoch') AS fecha, 
        c.email_hashed AS capi_email,
        c.phone_hashed AS capi_phone,
        p.email_hashed AS pixel_email,
        p.phone_hashed AS pixel_phone
    FROM Eventos_CAPI c
    LEFT JOIN Eventos_Pixel p ON c.event_id = p.event_id
"""

df_deduplicado = pd.read_sql_query(query_deduplicacion, conn)

# 5. CALCULAR EL MATCH SCORE (0 a 1)
def calcular_match_score(row):
    if pd.notna(row['capi_email']) and row['capi_email'] == row['pixel_email']:
        return 1.0
    elif pd.notna(row['capi_phone']) and row['capi_phone'] == row['pixel_phone']:
        return 0.5
    else:
        return 0.0

df_deduplicado['match_score'] = df_deduplicado.apply(calcular_match_score, axis=1)

# 6. GENERAR COLUMNA DE GASTO (SPEND)
# Como la columna no existía en SQL, la creamos aquí en Python
def generar_spend(row):
    if row['campaign_type'] == 'Cold Traffic':
        return round(row['value'] * np.random.uniform(0.20, 0.40), 2)
    else:
        return round(row['value'] * np.random.uniform(0.05, 0.15), 2)

df_deduplicado['spend'] = df_deduplicado.apply(generar_spend, axis=1)

# 6.5. RENOMBRAR COLUMNAS PARA EL DASHBOARD
# Cambiamos los nombres de las columnas al inglés
df_deduplicado = df_deduplicado.rename(columns={
    'campaign_type': 'Campaign Type',
    'spend': 'Spend (€)',
    'value': 'Revenue (€)',
    'match_score': 'Data Match Quality',
    'fecha': 'Date'
})

# Aseguramos que la fecha tenga un formato que Data Studio ame (AAAA-MM-DD)
# Como en el SQL ya usamos strftime('%Y%m%d'), lo convertimos aquí a YYYY-MM-DD
df_deduplicado['Date'] = pd.to_datetime(df_deduplicado['Date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

# 7. GUARDAR EL RESULTADO FINAL
df_deduplicado.to_csv('Eventos_Deduplicados.csv', index=False)

# 8. MOSTRAR RESULTADOS
print(f"\n✅ Proceso terminado.")
print(f"Total de eventos únicos (deduplicados): {len(df_deduplicado)}")
print(f"Match Score promedio: {df_deduplicado['Data Match Quality'].mean():.2f}")
print(f"Total Gasto (Spend): {df_deduplicado['Spend (€)'].sum():.2f}")
print(f"Total Ingresos (Value): {df_deduplicado['Revenue (€)'].sum():.2f}")
print(f"ROAS Global: {df_deduplicado['Revenue (€)'].sum() / df_deduplicado['Spend (€)'].sum():.2f}")
print(f"CPA Global: {df_deduplicado['Spend (€)'].sum() / len(df_deduplicado):.2f}")