# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""

# Imports
import sqlite3
import pandas as pd
from collections import Counter

# %% Apertura de la base

# Define the path as a variable for better readability and maintainability


# Use os.path.join to ensure the correct path separator is used


def abrir_excel(ruta):
    '''lee archivos de Excel (1ra pestaña) como data frame de Pandas'''
    base_df = pd.read_excel(ruta)
    return base_df

# %% Creacion de base de datos SQL


def crear_base():
    conn = sqlite3.connect('Ausencias_SJ.db')
    cur = conn.cursor()
    
    # Habilitar claves foráneas
    conn.execute("PRAGMA foreign_keys = ON")

        # Crear tabla de agrupadores
    cur.execute('''CREATE TABLE IF NOT EXISTS agrupadores
                (id_agr        INTEGER PRIMARY KEY,
                 agrupador     TEXT            NOT NULL
              );''')

    # Crear tabla de valores departamentos
    cur.execute('''CREATE TABLE IF NOT EXISTS departamentos
                (id_dep        INTEGER PRIMARY KEY,
                 DEPARTAMENTO  TEXT            NOT NULL
              );''')

    # Crear tabla de tipos de certificado
    cur.execute('''CREATE TABLE IF NOT EXISTS tcd
                (id_tc         INTEGER PRIMARY KEY,
                 tc_detalle    TEXT,
                 id_agr        INT,
                 FOREIGN KEY (id_agr) REFERENCES agrupadores(id_agr)
                 ON DELETE CASCADE
              );''')

    # Crear tabla de empleados
    cur.execute('''CREATE TABLE IF NOT EXISTS empleados
                (nro_legajo    INTEGER PRIMARY KEY,
                 nombre        TEXT            NOT NULL,
                 cuil          INT,
                 id_suc        INT             NOT NULL,
                 id_dep        INT             NOT NULL,
                 id_cat        INT             NOT NULL,
                 FOREIGN KEY (id_DEP) REFERENCES departamentos(id_dep)
                 ON DELETE CASCADE
              );''')

    # Crear tabla sucursales
    cur.execute('''CREATE TABLE IF NOT EXISTS sucursales
                id_suc      INT      INTEGER PRIMARY KEY,
                sucursal   TEXT     NOT NULL
                ''')

    # Crear tabla categorias
    cur.execute('''CREATE TABLE IF NOT EXISTS categorias
                id_cat      INT      INTEGER PRIMARY KEY,
                categoria   TEXT     NOT NULL
                ''')   

    # Crear tabla de certificados
    cur.execute('''CREATE TABLE IF NOT EXISTS certificados
                 (nro_certificado    INTEGER PRIMARY KEY,
                  id_tc              INT             NOT NULL,
                  nro_legajo         INT             NOT NULL,
                  validez_dde        DATE            NOT NULL,
                  validez_hta        DATE            NOT NULL,
                  descripcion        TEXT,
                  obs_general        TEXT
                );''')
    
    # Crear tabla de ausencias
    cur.execute('''CREATE TABLE IF NOT EXISTS ausencias
                 (fecha              DATA            PRIMARY KEY,
                  justificado        INT,
                  no_justificado     INT,
                  no_controlable     INT
                );''')

    # Crear indices
    cur.execute('CREATE INDEX IF NOT EXISTS idx_id_agr ON tcd (id_agr);')

    conn.commit()
    cur.close()
    conn.close()


def abrir_bd():
    global conn
    global cur
    conn = sqlite3.connect('Ausencias_SJ.db')
    cur = conn.cursor()
    return conn, cur


def cerrar_bd():
    conn.commit()
    cur.close()
    conn.close()

# %% Verificaciones de datos de la base
'''
# Agrupa por el nombre y cuenta la cantidad de legajos únicos
inconsistencias = base_df.groupby('Nombre')['Numero_Legajo'].nunique()
inconsistencias_2 = base_df.groupby('Numero_Legajo')['Nombre'].nunique()
# Muestra las filas donde hay más de un legajo para el mismo nombre
inconsistencias_con_legajo_multiple = inconsistencias[inconsistencias > 1]
inconsistencias_c_leg_multiple_2 = inconsistencias_2[inconsistencias_2 > 1]
# Muestra los nombres que tienen más de un número de legajo
print(inconsistencias_con_legajo_multiple)
# Muestra los legajos que tienen más de un nombre
print(inconsistencias_c_leg_multiple_2)

# Verificar si hay números de certificado duplicados
duplicados_certificado = base_df[base_df[
    'Numero_Certificado'].duplicated(keep=False)]
# Muestra los registros donde los números de legajo están repetidos
print(duplicados_certificado)
'''

# %% Limpieza de las bases


def limpieza_db(ruta):
    base_df = abrir_excel(ruta)
    # Convertir las fechas al formato correcto
    base_df['Validez_Desde'] = pd.to_datetime(base_df['Validez_Desde'],
                                            dayfirst=True, errors='coerce')

    # Eliminar certificados de duracion menor a 1 (dias)
    base_df = base_df[base_df['Dias'] >= 1]

    # Eliminar la columna de fecha de fin de certificado
    base_df= base_df.drop('Dias', axis=1)

    # Eliminar filas con NaN en nro legajo o en fecha
    base_df = base_df.dropna(
        subset=[base_df.columns[3], base_df.columns[9]])

    # Convertir la columna "Validez_Desde" a un formato correcto para SQL
    base_df['Validez_desde'] = pd.to_datetime(
        base_df['Validez_Desde']).dt.date

    # Convertir la columna "Validez_Hasta" a un formato correcto para SQL
    base_df['Validez_hasta'] = pd.to_datetime(
        base_df['Validez_Hasta']).dt.date
    return base_df


def limpieza_db_empleados(ruta):
    '''Limpia la base de datos de empleados'''
    base_df = abrir_excel(ruta)

    # Eliminar las filas 1 a 3
    base_df = base_df.drop(base_df.index[0:2])

    # Conservar las primeras 6 filas
    base_df = base_df.iloc[0:6]
# %% Agregado de columnas de ID


def agregar_ID(ruta):
    base_df_limpia = limpieza_db(ruta)
    # Agregar ID_TC (ID para cada tipo de certificado).
    base_df_limpia.loc[:, 'ID_TC'] = pd.factorize(base_df_limpia['TCDetalle'])[0]
    # Agregar ID_Dep (ID para cada departamento)
    base_df_limpia.loc[:, 'ID_Dep'] = pd.factorize(base_df_limpia['Departamento'])[0]
    # Agregar ID_Agr (ID para cada tipo de agrupador)
    base_df_limpia.loc[:, 'ID_Agr'] = pd.factorize(base_df_limpia['Agrupador'])[0]
    return base_df_limpia


def agregar_ID_empleados(ruta):
    base_df_limpia = limpieza_db_empleados(ruta)
    # Agregar ID_suc (ID para cada sucursal)
    base_df_limpia.loc[:, 'ID_Suc'] = pd.factorize(base_df_limpia['Sucursal'])[0]
    # Agregar ID_cat (ID para cada categoria de empleado)
    base_df_limpia.loc[:, 'ID_cat'] = pd.factorize(base_df_limpia['Categoria'])[0]

# %% Dividir las tablas en sub tablas para SQL

# Tabla T_TCD (Detalle de tipo de certificado)
def dividir_tabla(ruta):
    base_df_limpia = agregar_ID(ruta)
    T_TCD = base_df_limpia[['ID_TC', 'TCDetalle', 'ID_Agr']].drop_duplicates()
    # Tabla T_Dep (Departamentos)
    T_Dep = base_df_limpia[['ID_Dep', 'Departamento']].drop_duplicates()
    # Tabla T_Agr (Agrupadores)
    T_Agr = base_df_limpia[['ID_Agr', 'Agrupador']].drop_duplicates()
    # Tabla T_Emp (Empleados)
    T_Emp = base_df_limpia[['Numero_Legajo', 'Nombre',
                            'ID_Dep']].drop_duplicates()
    # Tabla T_Cer (Certificados, tabla central)
    T_Cer = base_df_limpia[['Numero_Certificado', 'ID_TC', 'Numero_Legajo',
                            'Validez_desde', 'Validez_hasta', 'Descripcion',
                            'Observacion_General']].drop_duplicates()

    listado_databases = ((T_TCD, 'TCD'), (T_Dep, 'departamentos'),
                         (T_Agr, 'agrupadores'), (T_Emp, 'empleados'),
                         (T_Cer, 'certificados'))
    return listado_databases


def dividir_tabla_empleados(ruta):
    base_df_limpia = agregar_ID_empleados(ruta)
    # Tabla T_Suc (Sucursales)
    T_Suc = base_df_limpia[['ID_Suc', 'Sucursal']].drop_duplicates()
    # Tabla T_Cat (Categorias de empleados)
    T_Cat = base_df_limpia[['ID_cat', 'Categoria']].drop_duplicates()
    # Tabla T_Emp (Empleados)
    T_Emp = base_df_limpia[['Numero_Legajo', 'Nombre', 'CUIL', 'ID_cat',
                            'ID_Suc', 'ID_Dep']].drop_duplicates()
    listado_databases = ((T_Suc, 'sucursales'), (T_Cat, 'categorias'),
                         (T_Emp, 'empleados'))
    return listado_databases

# %% Organizar los datos para la tabla de ausencias


def organizar_ausencias():
    datos = sql_ausencias()
    df = pd.DataFrame(datos, columns=[
        'validez_dde', 'validez_hta', 'agrupadores', 'tipo_cert'])
    contador_fechas = crear_dic_fechas(df)

    # Insertar los resultados en la tabla de ausencias
    insertar_ausencias(contador_fechas['justificado'], 'justificado')
    insertar_ausencias(contador_fechas['no_justificado'], 'no_justificado')
    insertar_ausencias(contador_fechas['no_controlable'], 'no_controlable')


def sql_ausencias():
    sql = '''SELECT c.validez_dde, c.validez_hta, t.id_agr,
            t.id_tc AS Tipo_cert
            FROM certificados AS c
            JOIN tcd AS t ON c.id_tc = t.id_tc
            WHERE t.id_agr = 0 OR t.id_agr = 3'''
    return sql_con_ausencias(sql)


def sql_con_ausencias(consulta):
    '''Ejecuta la consulta sql que se indique
    Input: consulta sql escrita correctamente
    Output: Lo que devuelva la base de datos'''
    abrir_bd()
    cur.execute(consulta)
    fechas_certificados = cur.fetchall()
    cerrar_bd()
    return fechas_certificados

# Función para crear diccionarios de fechas clasificadas
def crear_dic_fechas(df):
    contador_fechas = { 'justificado': Counter(),
                   'no_justificado': Counter(),
                   'no_controlable': Counter() 
    }

    for _, row in df.iterrows():
        rango_fechas = pd.date_range(start=row['validez_dde'], end=row['validez_hta'])
        if row['tipo_cert'] == 4:
            contador_fechas['no_justificado'].update(rango_fechas)
        elif row['agrupadores'] == 0:
            contador_fechas['justificado'].update(rango_fechas)
        elif row['agrupadores'] == 3:
            contador_fechas['no_controlable'].update(rango_fechas)
    return contador_fechas

# Función para insertar las ausencias en la tabla SQL
def insertar_ausencias(contador_fechas, categoria):
    abrir_bd()
    for fecha, cantidad in contador_fechas.items():
        fecha_str = fecha.strftime('%Y-%m-%d')
        if categoria == 'justificado':
            cur.execute('''INSERT INTO ausencias (fecha, justificado)
                        VALUES (?, ?) ON CONFLICT(fecha)
                        DO UPDATE SET justificado=excluded.justificado''',
                        (fecha_str, cantidad))
        elif categoria == 'no_justificado':
            cur.execute('''INSERT INTO ausencias (fecha, no_justificado)
                        VALUES (?, ?) ON CONFLICT(fecha)
                        DO UPDATE SET no_justificado=excluded.no_justificado''',
                        (fecha_str, cantidad))
        elif categoria == 'no_controlable':
            cur.execute('''INSERT INTO ausencias (fecha, no_controlable)
                        VALUES (?, ?) ON CONFLICT(fecha)
                        DO UPDATE SET no_controlable=excluded.no_controlable''',
                        (fecha_str, cantidad))
    cerrar_bd()

# %% Cargar los sub data frames en SQLITE


def cargar_df_en_db(dataf, tablaSQL):
    # Crear placeholders para los valores
    placeholders = ', '.join('?' * len(dataf.columns))
    # Convertir los datos del DataFrame a una lista de tuplas
    valores = dataf.to_records(index=False).tolist()

    abrir_bd()
    # Crear la consulta SQL para insertar los datos
    query = f"INSERT INTO {tablaSQL} VALUES ({placeholders})"
    # Insertar los datos en la tabla existente
    conn.executemany(query, valores)
    cerrar_bd()

def pasar_a_db(ruta):
    listado_databases = dividir_tabla(ruta)
    for tabla in listado_databases:
        cargar_df_en_db(tabla[0], tabla[1])


def pasar_a_db_empleados(ruta):
    listado_databases = dividir_tabla_empleados(ruta)
    # Borrar la tabla de empleados preexistente de la bd
    abrir_bd()
    cur.execute("DROP TABLE IF EXISTS empleados")
    cerrar_bd()
    for tabla in listado_databases:
        cargar_df_en_db(tabla[0], tabla[1])


# %% Contar las faltas por dia de la semana

'''
# Función para contar los días de la semana
def contar_dias_semana(fecha_inicio, duracion):
    if pd.isna(fecha_inicio) or duracion <= 0:  # Verifica fechas no válidas o duraciones incorrectas
        return pd.Series([0]*7)  # Retorna cero para cada día si hay un error
    dias = pd.date_range(fecha_inicio, periods=duracion)
    return dias.weekday.value_counts().reindex(range(7), fill_value=0)

# Aplicar la función a cada fila y expandir los resultados en columnas
dias_semana = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
conteo_dias = df.apply(lambda row: contar_dias_semana(row['Validez_Desde'], row['Dias']), axis=1)

# Ya que 'conteo_dias' es un DataFrame, lo concatenamos directamente con 'df'
df_con_dias = pd.concat([df, conteo_dias.set_axis(dias_semana, axis=1)], axis=1)


df_con_dias.to_csv('ausencias_por_día.csv', index=False, sep = ';')
'''

def crear_db_cert(ruta):
    crear_base()
    pasar_a_db(ruta)
    organizar_ausencias()


def crear_db_empleados(ruta):
    pasar_a_db_empleados(ruta)