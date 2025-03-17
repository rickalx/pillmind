import sqlite3
import logging
import json

#actualizar path
DATABASE_URL = "/home/rick/repos/hackaton/verifica_propuesta/veripro_back/propuestas.db"

async def conectar_bd():
    conn = sqlite3.connect(DATABASE_URL)
    return conn

async def crear_tabla():
    conn = await conectar_bd()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS propuestas_campana (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            resumen TEXT NOT NULL,
            analisis_detallado TEXT NOT NULL,
            conclusiones TEXT NOT NULL,
            factibilidad TEXT NOT NULL,
            recomendaciones TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

async def agregar_datos_desde_json(json_data):
    conn = await conectar_bd()
    cursor = conn.cursor()

    try:
        data = json.loads(json_data)
        nombre_propuesta = data.get("nombre_propuesta", "")
        resumen = data.get("resumen", "")
        analisis_detallado = data.get("analisis_detallado", "")
        conclusiones = data.get("conclusion", "")
        factibilidad = data.get("factibilidad", "")
        recomendaciones = data.get("recomendacion", "")

        cursor.execute("""
            INSERT INTO propuestas_campana (nombre, resumen, analisis_detallado, conclusiones, factibilidad, recomendaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre_propuesta, resumen, analisis_detallado, conclusiones, factibilidad, recomendaciones))

        conn.commit()
        print(f"Datos agregados para '{nombre_propuesta}' desde JSON.")
    except json.JSONDecodeError as e:
        error_message = f"Error al decodificar el JSON: {e}"
        print(error_message)
        logging.error(error_message)
    except Exception as e:
        error_message = f"Error al procesar el JSON: {e}"
        print(error_message)
        logging.error(error_message)
    finally:
        conn.close()