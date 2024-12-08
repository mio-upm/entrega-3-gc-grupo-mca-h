# -*- coding: utf-8 -*-
"""
Created on Wed Dec  1 11:45:49 2024

@author: jaime+aitor+almu+lucia
"""

import pulp as lp
import pandas as pd

# Datos iniciales
operaciones = pd.read_excel('241204_datos_operaciones_programadas.xlsx')
costes = pd.read_excel('241204_costes.xlsx', index_col=0)

# Definir los conjuntos
I = list(range(0, len(operaciones)))  # Conjunto de operaciones
J = list(range(0, len(costes)))  # Conjunto de quirófanos

# Definir parámetros
inicio = operaciones['Hora inicio '].tolist()
final = operaciones['Hora fin'].tolist()
nombre_operaciones = operaciones['Código operación'].tolist()

# Inicialización del problema maestro
problema_generador_patrones = lp.LpProblem(name="Generacion_Columnas_Quirófanos", sense=lp.LpMinimize)

# Patrones iniciales: agrupar las operaciones que no se solapan en un mismo quirófano
patrones = []
utilizadas = set()
for i in I:
    if i not in utilizadas:
        patron = [0] * len(I)
        patron[i] = 1
        utilizadas.add(i)
        for h in I:
            if h not in utilizadas and inicio[h] >= final[i]:
                patron[h] = 1
                utilizadas.add(h)
        patrones.append(patron)

# Variables y función objetivo inicial del problema maestro
y = lp.LpVariable.dicts("Patron", list(range(len(patrones))), cat=lp.LpBinary)
problema_generador_patrones += lp.lpSum(y[k] for k in range(len(patrones)))  # Minimizar el número de quirófanos

# Restricciones iniciales: cada operación debe estar cubierta por al menos un patrón
for i in I:
    problema_generador_patrones += lp.lpSum(patrones[k][i] * y[k] for k in range(len(patrones))) >= 1

# Resolución iterativa mediante generación de columnas
while True:
    # Resolver el problema maestro actual
    problema_generador_patrones.solve()
    
    # Obtener los precios sombra de las restricciones
    precios_sombra = {i: problema_generador_patrones.constraints[f"_C{i}"].pi for i in I}
    
    # Resolver el problema auxiliar (problema tipo knapsack) para generar una nueva columna
    problema_corte_unidimensional = lp.LpProblem(name="Problema_Auxiliar", sense=lp.LpMaximize)
    x = lp.LpVariable.dicts("x", I, cat=lp.LpBinary)
    
    # Función objetivo del problema auxiliar: maximizar la reducción de coste
    problema_corte_unidimensional += lp.lpSum(precios_sombra[i] * x[i] for i in I)
    
    # Restricción de compatibilidad: las operaciones no deben solaparse
    for i in I:
        for h in I:
            if i != h and inicio[i] < final[h] and inicio[h] < final[i]:
                problema_corte_unidimensional += x[i] + x[h] <= 1
    
    # Resolver el problema de corte unidimensional
    problema_corte_unidimensional.solve()
    
    # Comprobar si el valor objetivo del problema auxiliar es positivo
    if lp.value(problema_corte_unidimensional.objective) <= 1e-6:
        # Si no hay mejora, detener el algoritmo
        break
    
    # Crear un nuevo patrón a partir de la solución del problema auxiliar
    nuevo_patron = [int(lp.value(x[i])) for i in I]
    patrones.append(nuevo_patron)
    
    # Añadir la nueva variable al problema maestro
    nueva_variable = lp.LpVariable(f"Patron_{len(patrones) - 1}", cat=lp.LpBinary)
    y[len(patrones) - 1] = nueva_variable
    problema_generador_patrones += nueva_variable
    
    # Añadir la nueva restricción al problema maestro
    for i in I:
        problema_generador_patrones.constraints[f"_C{i}"].addterm(nuevo_patron[i], nueva_variable)

# Mostrar la solución óptima
print('Número mínimo de quirófanos necesarios:', lp.value(problema_generador_patrones.objective))
for k in range(len(patrones)):
    if lp.value(y[k]) == 1:
        operaciones_asignadas = [nombre_operaciones[i] for i in I if patrones[k][i] == 1]
        print(f'Quirófano {k + 1}: Operaciones asignadas: {operaciones_asignadas}')
        
#%%

# CARACTERIZACIÓN SOLUCIÓN: Visualización del número de operaciones en cada quirófano

import matplotlib.pyplot as plt


quirófanos_utilizados = [k for k in range(len(patrones)) if lp.value(y[k]) == 1]
operaciones_por_quirófano = {k: [i for i in I if patrones[k][i] == 1] for k in quirófanos_utilizados}

plt.figure(figsize=(15, 8))
for k, operaciones in operaciones_por_quirófano.items():
    plt.bar([k] * len(operaciones), [1] * len(operaciones), bottom=range(len(operaciones)))
    for idx, i in enumerate(operaciones):
        plt.text(k, idx + 0.5, nombre_operaciones[i], ha='center', va='center', rotation=90, fontsize=8)

plt.xticks(quirófanos_utilizados, [f"Q-{k+1}" for k in quirófanos_utilizados], rotation=45, ha="right", fontsize=10)
plt.xlabel("Quirófanos", fontsize=12)
plt.ylabel("Número de Operaciones", fontsize=12)
plt.title("Asignación de Operaciones a Quirófanos", fontsize=1)
plt.tight_layout()
plt.show()

# Como es un poco ilegible voy a hacerlo mostrando el número total de operaciones por quirófano y ya

#%%
quirófanos_utilizados = [k for k in range(len(patrones)) if lp.value(y[k]) == 1]
operaciones_por_quirófano = {k: [i for i in I if patrones[k][i] == 1] for k in quirófanos_utilizados}

plt.figure(figsize=(15, 8))
for k, operaciones in operaciones_por_quirófano.items():
    plt.bar(k, len(operaciones))
    plt.text(k, len(operaciones) + 0.5, str(len(operaciones)), ha='center', va='bottom', fontsize=10)
plt.xticks(quirófanos_utilizados, [f"Q-{k+1}" for k in quirófanos_utilizados], rotation=45, ha="right", fontsize=10)
plt.xlabel("Quirófanos", fontsize=12)
plt.ylabel("Número de Operaciones", fontsize=12)
plt.title("Número de Operaciones por Quirófano", fontsize=14)
plt.tight_layout()
plt.show()


