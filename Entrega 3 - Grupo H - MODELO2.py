# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 11:13:02 2024

@author: jaime+aitor+almu+lucia
"""
import pandas as pd
import pulp as lp

# LEER DATOS
datos_operaciones = pd.read_excel('241204_datos_operaciones_programadas.xlsx', sheet_name='operaciones')
especialidades = [
    'Cardiología Pediátrica',
    'Cirugía Cardíaca Pediátrica',
    'Cirugía Cardiovascular',
    'Cirugía General y del Aparato Digestivo'
]
costes = pd.read_excel('241204_costes.xlsx', sheet_name='costes')

# FILTRAR OPERACIONES POR ESPECIALIDADES
operaciones_filtradas = datos_operaciones[datos_operaciones['Especialidad quirúrgica'].isin(especialidades)]

# PROBLEMA
problema = lp.LpProblem(name="Asignación_Quirófanos", sense=lp.LpMinimize)

# CONJUNTOS
quirofanos = costes['Unnamed: 0'].tolist()
operaciones = operaciones_filtradas['Código operación'].tolist()

# CALCULAR COSTE MEDIO DE CADA OPERACION
costes_medios = {}
for op in operaciones:
    costes_medios[op] = costes[op].mean()

# VARIABLE
yk = lp.LpVariable.dicts("y", (quirofanos, operaciones), cat=lp.LpBinary)

# CALCULAR COSTE TOTAL DE CADA QUIRÓFANO
costes_quir = {}
for q in quirofanos:
    costes_quir[q] = lp.lpSum(yk[q][op] * costes_medios[op] for op in operaciones)

# FUNCION OBJETIVO
problema += lp.lpSum(costes_quir[q] for q in quirofanos)

# RESTRICCION UNA OPERACIÓN POR QUIRÓFANO
for op in operaciones:
    problema += lp.lpSum(yk[q][op] for q in quirofanos) == 1

# SIN SOLAPAMIENTOS
for q in quirofanos:
    operaciones_quir = operaciones_filtradas[operaciones_filtradas['Código operación'].isin(operaciones)]
    for i, op_i in operaciones_quir.iterrows():
        for j, op_j in operaciones_quir.iterrows():
            if op_i['Código operación'] != op_j['Código operación']:
                inicio_i = op_i['Hora inicio ']
                fin_i = op_i['Hora fin']
                inicio_j = op_j['Hora inicio ']
                fin_j = op_j['Hora fin']

                if inicio_i < fin_j and inicio_j < fin_i:
                    # Asegurar no asignación simultánea en el mismo quirófano
                    problema += yk[q][op_i['Código operación']] + yk[q][op_j['Código operación']] <= 1

# RESOLVER
problema.solve()

# ASIGNACIONES DE OPERACIONES POR QUIROFANO
asignaciones = []
for q in quirofanos:
    quir_of_operations = []
    coste_total = 0
    for op in operaciones:
        if yk[q][op].value() == 1:
            coste_op = costes_medios[op]
            quir_of_operations.append({
                "Quirófano": q,
                "Operación": op,
                "Hora inicio":
                    operaciones_filtradas.loc[operaciones_filtradas['Código operación'] == op, 'Hora inicio '].values[
                        0],
                "Hora fin":
                    operaciones_filtradas.loc[operaciones_filtradas['Código operación'] == op, 'Hora fin'].values[0],
                "Coste Medio": coste_op
            })
            coste_total += coste_op
    asignaciones.extend(quir_of_operations)
    if quir_of_operations:
        print(f"Quirófano {q}:")
        print("-" * 30)
        for op in quir_of_operations:
            print(f"Operación: {op['Operación']} | Coste medio: {op['Coste Medio']:.2f}")
        print(f"Coste total de la planificación: {coste_total:.2f}\n")

# CONVERTIR LAS ASIGNACIONES EN DATAFRAME
asignaciones_df = pd.DataFrame(asignaciones)

# VERFICAR SOLAPAMIENTOS POR QUIROFANO
solapamientos = []
for q in quirofanos:
    operaciones_quir = asignaciones_df[asignaciones_df["Quirófano"] == q].sort_values(by="Hora inicio")
    for i in range(len(operaciones_quir) - 1):
        op_actual = operaciones_quir.iloc[i]
        op_siguiente = operaciones_quir.iloc[i + 1]
        if op_actual["Hora fin"] > op_siguiente["Hora inicio"]:
            solapamientos.append({
                "Quirófano": q,
                "Operación Actual": op_actual["Operación"],
                "Operación Siguiente": op_siguiente["Operación"]
            })

# MOSTRAR RESULTADOS
if not solapamientos:
    print("\nValidación exitosa: Todas las planificaciones seleccionadas no tienen solapamientos.")
else:
    print("\nSe encontraron solapamientos:")
    for s in solapamientos:
        print(f"Quirófano {s['Quirófano']}: Operación {s['Operación Actual']} se solapa con {s['Operación Siguiente']}")
