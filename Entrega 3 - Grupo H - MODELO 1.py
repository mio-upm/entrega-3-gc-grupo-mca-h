# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 11:13:02 2024

@author: jaime+aitor+almu+lucia
"""

import pulp as lp
import pandas as pd
import matplotlib.pyplot as plt


""" APARTADO 1 """
datos_operaciones = pd.read_excel('241204_datos_operaciones_programadas.xlsx')
costes = pd.read_excel('241204_costes.xlsx', index_col=0)
coste_list = costes.values.tolist()

# PROBLEMA
problema = lp.LpProblem(name='hospital', sense= lp.LpMinimize)

# CONJUNTOS
I = list(range(0, len(datos_operaciones))) # OPERACIONES
J = list(range(0, len(costes))) # QUIROFANOS

# PARÁMETROS
coste_i_j = {}
for b, i in enumerate(I):  
    coste_i_j[i] = {}
    for a, j in enumerate(J):
        coste_i_j[i][j] = coste_list[a][b]
        
inicio = datos_operaciones['Hora inicio '].tolist()
final = datos_operaciones['Hora fin'].tolist()
nombre_operaciones = datos_operaciones['Código operación'].tolist()


inicio_i = {i: inicio[i] for i in I}
final_i = {i: final[i] for i in I}

#L
L = {}

for i in I:
    L[i] = []
    for h in I:
        if i != h:
            if inicio_i[i] < final_i[h] and inicio_i[h] < final_i[i]:
                L[i].append(h)


# VARIABLES
x_i_j = lp.LpVariable.dicts('asignar', [(i,j) for i in I for j in J], cat = lp.LpBinary) 
x_h_j = lp.LpVariable.dicts('incompatibilidad', [(h,j) for h in I for j in J], cat = lp.LpBinary)

# RESTRICCIONES
for i in I :
    problema += lp.lpSum(x_i_j[(i, j)] for j in J) >= 1
    
for i in I:
    if i in L: 
        for h in L[i]:
            for j in J:
                problema += x_h_j[(i, j)] + x_i_j[(h, j)] <= 1

# FO
problema += lp.lpSum(x_i_j[(i,j)]*coste_i_j[i][j] for i in I for j in J)

# RESOLUCIÓN
problema.solve()

# CARACTERIZACIÓN SOLUCIÓN:

print('El objetivo es', lp.value(problema.objective))

# Operaciones asignadas a cada quirófano
plt.figure(figsize=(50, 20))

for j in J:
    operaciones = [i for i in I if lp.value(x_i_j[(i, j)]) == 1]
    if operaciones:
        plt.bar([j] * len(operaciones), [1] * len(operaciones), bottom=range(len(operaciones)))
        for idx, i in enumerate(operaciones):
            plt.text(j, idx + 0.5, nombre_operaciones[i], ha='center', va='center', 
                     rotation=90, fontsize=20)

plt.xticks(J, [f"Q-{j+1}" for j in J], rotation=45, ha="right", fontsize=20)
plt.xlabel("Quirófanos", fontsize=20)
plt.ylabel("Número de Operaciones", fontsize=20)
plt.title("Asignación de Operaciones a Quirófanos", fontsize=30)
plt.tight_layout()
plt.show()

'''
# Operaciones asignadas a cada quirófano
for j in J:
    operaciones = [nombre_operaciones[i] for i in I if lp.value(x_i_j[(i,j)]) == 1]
    print('Quirófano', j+1, ": Operaciones asignadas:", operaciones)
    
# Quirófano asignado a cada operación
for i in I:
    quirofano_asignado = [j for j in J if lp.value(x_i_j[(i, j)]) == 1]
    if quirofano_asignado:
        print("Operación", nombre_operaciones[i], "asignada al quirófano", quirofano_asignado)
    else:
        print("Operación", nombre_operaciones[i], "No tiene quirófano asignado")

# Contar cuántas operaciones hay en cada quirófano
operaciones_por_quirofano = {j: 0 for j in J}
for j in J:
    operaciones_por_quirofano[j] = sum(1 for i in I if lp.value(x_i_j[(i, j)]) == 1)
print("Número de operaciones por quirófano:")
for j in J:
    print('Quirófano', j + 1,':', operaciones_por_quirofano[j], 'operaciones')
'''

#COMENTARIOS PARA EL INFORME

# 12:06 21/11/2024 - Tenemos duda de si estamos leyendo bien los excel, ya que np
# sabemos si hay que coger la cabezera de estos excel como datos o no
# Los hemos leído así de momento y creemos que está bien pero igual a futuro hay
# que cambiarlos

# 17:24 21/11/2024 - Hemos tenido un problema ya que queríamos asociar los costes 
# leídos del excel a los conjuntos creados, pero no podíamos porque era un dataframe,
# por lo que hemos tenido que convertir este dataframe a lista. Una vez hecho este paso
# hemos asociado los costes a los conjuntos. Al principio, estábamos poniendo los
# índices al revés y no coincidían, que daba error. Pero al cambiarlos se ha solucionado.

# 18:16 21/11/2024 - No éramos capaces de almacenar las horas de inicio, hasta que
# hemos comprobado el nombre y es que cuenta con un espacio después. Por si acaso,
# lo hemos almacenado en una lista que es más cómodo.

# 20:20 - 10:30 21/11/2024 - Tenemos problemas para comprender la segunda restricción. No ha constado entender qué es h y
# Li, pero después de un buen rato lo hemos logrado. También nos ha surgido la duda de si Xhj es una variable o un
# parámetro.Decidimos que es una varibale binaria que adoptará el valor 1 si la operació h está asignada a un quirófajo j, 
# y 0 en caso contrario. Para saber si 2 operaciones son incompatibles de debe cumplir que Inicio_h < Fin_i  y que Inicio_i < Fin_h.
# Coprendiendo esto ya somos capaces de construir el conjunto L con sus subconjuntod Li y la segunda restricción.

# 11:10 - 12:20 22/11/2024 - Resolvemos el modelo y obtenemos que la solución es Óptima y que el valor de la F.O. es de 21375.00. Cuando lo resolvemos, 
# python tarda un poco en resolver el modelo, alrededor de 3-5 minutos.
# Caracterizamos la solución para mostrarla por pantalla. Creeemos que visualizar las operaciones 
# asignadas a cada quirófano es un poco confuso, por lo que proponemos otra forma de visualizar la solución:
# ver qué quirófano es asignado a cada operación. También vamos a contar cuantas veces se usa cada quirófano.

# 11:40 - 12:40 07/12/2024 - Para visualizar de forma más concisa el resultado pensamos que lo mejor es representarlo
# gráficamente. Para ello hemos desarrollado un gáfico de barras en el que en el eje verticar vienen representados 
# todos los quirófanos y en el horizontal el número de operaciones que se realizan en cada quirófano. Dentro de cada una
# de las barras para cada uno de los quirófanos aparecen escritos los nombres de las operaciones que se van a llevar a 
# cabo en cada quirófano. En un principio pensabamos representarlo todo por pantalla, pero nos dio la sensación de que 
# tanto texto podría llegar a ser confuso. Hemos dejado esa parte del código como comentario justo después del código 
# con el que se elabora el gráfico.

#Los textos del print del modelo aparecen tanto con “” como  con ‘’ porque cada uno de los miembros del equipo 
#usa un formato diferente.

#Con esto damos por finalizado el apartado 1 del modelo 1.







""" APARTADO 2 """
import pulp as lp
import pandas as pd

datos_operaciones = pd.read_excel('241204_datos_operaciones_programadas.xlsx')
costes = pd.read_excel('241204_costes.xlsx', index_col=0)

datos_cardiologia = datos_operaciones[datos_operaciones['Especialidad quirúrgica'] == 'Cardiología Pediátrica']
nombre_operaciones_cardiologia = datos_cardiologia['Código operación']
costes_cardiologia = costes[nombre_operaciones_cardiologia]

# PROBLEMA
problema2 = lp.LpProblem(name='Cardiología Pediátrica', sense=lp.LpMinimize)

# CONJUNTOS
I2 = datos_cardiologia.index.tolist()  # ÍNDICES OPERACIONES DE CARDIOLOGÍA PEDIÁTRICA
J2 = list(range(len(costes)))  # QUIROFANOS

# PARÁMETROS
costes_cardiologia_dict = {}
for i, codigo_op in enumerate(nombre_operaciones_cardiologia):
    costes_cardiologia_dict[i] = {}
    for j in range(len(costes_cardiologia)):
        costes_cardiologia_dict[i][j] = costes_cardiologia.iloc[j, i]

inicio2 = datos_cardiologia['Hora inicio ']
final2 = datos_cardiologia['Hora fin']

inicio2_i = {i: inicio2[i] for i in I2}
final2_i = {i: final2[i] for i in I2}

# L
L2 = {}

for i in I2:
    L2[i] = []
    for h in I2:
        if i != h:
            if inicio2_i[i] < final2_i[h] and inicio2_i[h] < final2_i[i]:
                L2[i].append(h)

# VARIABLES
x2_i_j = lp.LpVariable.dicts('asignar', [(i, j) for i in I2 for j in J2], cat=lp.LpBinary)
x2_h_j = lp.LpVariable.dicts('incompatibilidad', [(h,j) for h in I2 for j in J2], cat = lp.LpBinary)

# RESTRICCIONES
# Cada operación debe asignarse a un quirófano
for i in I2:
    problema2 += lp.lpSum(x2_i_j[(i, j)] for j in J2) >= 1

# Restricción de incompatibilidades
for i in I2:
    if i in L2: 
        for h in L2[i]:
            for j in J2:
                problema2 += x2_h_j[(i, j)] + x2_i_j[(i, j)] <= 1

# FUNCIÓN OBJETIVO
problema2 += lp.lpSum(x2_i_j[(i, j)] * costes_cardiologia_dict[i][j] for i in I2 for j in J2)

# RESOLUCIÓN
problema2.solve()

# COMENTARIOS PARA EL INFORME

# 12:40 - 13:20 22/11/2024 - Para aplicar resolver el modelo solo con los datos relativos a  las operaciones del 
# servicio de Cardiología Pediátrica será necesario filtrar los datos y almacenarlos en diferentes parámetros. No 
# hemos tenido problemas con el código, ya que es muy parecido al del apartado 1. Solo hemos tenido que añadir 
# algunas líneas co las que filtrar los datos y cambiar el nombre de los parámetros y las variables.

# 12:30 - 13:30 29/11/2024 - Revisando el código encontramos un error en el bucle en el que creábamos el diccionario de 
# costes asociados a las operaciones de Cardiología Pediátrica. No se filtraban bien los nombres de las operaciones y se asociaban
# costes erróneos. Lo hemos solucionado creando un dataframe llamado "costes_cardiologia" en el que solo se almacenaban los
# costes de cada quirófano asociados a las operaciones de Cardiología Pediátrica. Luego hemos modificado el bucle con el que 
# creábamos el dict y hemos revisado si se almacenaban correctamente. Al ver que sí eran los que necesitábamos hemos ejecutado el 
# problema y hemos vuelto a obtener una solución óptima.







""" APARTADO 3 """

print('El objetivo es', lp.value(problema2.objective))

# Operaciones asignadas a cada quirófano
plt.figure(figsize=(45, 10))

for j in J2:  
    operaciones = [i for i in I2 if lp.value(x2_i_j[(i, j)]) == 1]
    if operaciones:
        plt.bar([j] * len(operaciones), [1] * len(operaciones), bottom=range(len(operaciones)))
        for idx, i in enumerate(operaciones):
            plt.text(j, idx + 0.5, nombre_operaciones_cardiologia.iloc[i], 
                     ha='center', va='center', rotation=90, fontsize=20)

plt.yticks([0, 1], labels=["0", "1"], fontsize=20)
plt.xticks(J2, [f"Q-{j+1}" for j in J2], rotation=45, ha="right", fontsize=20)
plt.xlabel("Quirófanos", fontsize=20)
plt.ylabel("Número de Operaciones", fontsize=20)
plt.title("Asignación de Operaciones de Cardiología Pediátrica a Quirófanos", fontsize=30)
plt.tight_layout()
plt.show()


'''
print('El objetivo es', lp.value(problema2.objective))

# Operaciones asignadas a cada quirófano
for j in J2:
    operaciones2 = [nombre_operaciones_cardiologia[i] for i in I2 if lp.value(x2_i_j[(i, j)]) == 1]
    print('Quirófano', j, ": Operaciones asignadas:", operaciones2)

# Quirófano asignado a cada operación
for i in I2:
    quirofano_asignado2 = [j for j in J2 if lp.value(x2_i_j[(i, j)]) == 1]
    if quirofano_asignado2:
        print("Operación", nombre_operaciones_cardiologia[i], "asignada al quirófano", quirofano_asignado2[0])
    else:
        print("Operación", nombre_operaciones_cardiologia[i], "No tiene quirófano asignado")

# Contar cuántas operaciones hay en cada quirófano
operaciones_por_quirofano2 = {j: 0 for j in J2}
for j in J2:
    operaciones_por_quirofano2[j] = sum(1 for i in I2 if lp.value(x2_i_j[(i, j)]) == 1)
print("Número de operaciones por quirófano:")
for j in J2:
    print('Quirófano', j + 1,':', operaciones_por_quirofano2[j], 'operaciones')
'''    


# COMENTARIOS PARA EL INFORME

# 12:40 - 13:20 22/11/2024 - No hemos tenido ningún problema para hacer que se muestren los datos por pantalla, 
# ya que el código lo teníamos hecho en el apartado 1 y solo hemos tenido que cambiar el nombre de las variables y los parámetros.

## 11:40 - 12:40 07/12/2024 - Para visualizar de forma más concisa el resultado pensamos que lo mejor es representarlo 
# gráficamente. Para ello hemos desarrollado un gáfico de barras en el que en el eje verticar vienen representados 
# todos los quirófanos y en el horizontal el número de operaciones que se realizan en cada quirófano. Dentro de cada una
# de las barras para cada uno de los quirófanos aparecen escritos los nombres de las operaciones que se van a llevar a 
# cabo en cada quirófano. En un principio pensabamos representarlo todo por pantalla, pero nos dio la sensación de que 
# tanto texto podría llegar a ser confuso. Hemos dejado esa parte del código como comentario justo después del código 
# con el que se elabora el gráfico.
