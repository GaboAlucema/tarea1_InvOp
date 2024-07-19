import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd
import numpy as np

# Importar los datos
df_F1 = pd.read_csv('F1.csv',skiprows=1,delimiter=';',index_col=0)
df_F2 = pd.read_csv('F2.csv',skiprows=1,delimiter=';',index_col=0)
df_F3 = pd.read_csv('F3.csv',skiprows=1,delimiter=';',index_col=0)
df_F4 = pd.read_csv('F4.csv',skiprows=1,delimiter=';',index_col=0)
df_F5 = pd.read_csv('F5.csv',skiprows=1,delimiter=';',index_col=0)
df_general = pd.read_csv('General.csv', delimiter=';')

dfs = {'F1': df_F1, 'F2': df_F2, 'F3': df_F3, 'F4': df_F4, 'F5': df_F5}

#print("Contenido de la fila 7 de General.csv: ", df_general.iloc[5].values)
#print("Contenido completo del DataFrame F1: ", df_F1)
#print("Etiquetas de las filas de F1.csv: ", df_F1.index)

demanda = df_general.iloc[5].values.astype(float)

# Crear el modelo
model = pyo.ConcreteModel('Produccion en fabricas')

# Listas de productos, fabricas y recursos
lista_fabricas = ['F{}'.format(i) for i in range(1, 6)]
lista_productos = ['P{}'.format(i) for i in range(1, 13)]
lista_recursos = ['R{}'.format(i) for i in range(1, 8)]

# Conjuntos de indices para fabricas, productos y recursos
model.K = pyo.Set(initialize=lista_fabricas)
model.J = pyo.Set(initialize=lista_productos)
model.I = pyo.Set(initialize=lista_recursos)

# a_ijk
model.a = pyo.Param(model.I, model.J, model.K, within=pyo.NonNegativeReals, mutable=True)
for k in model.K:
    unidades_recurso = dfs[k].iloc[0:7,1:-1].values
    for i, fila in enumerate(unidades_recurso):
        for j, valor in enumerate(fila):
            valor_float = float(str(valor).replace(',', '.'))
            model.a[f'R{i+1}', f'P{j+1}', k] = valor_float
'''
for k in model.K:
    for i in model.I:
        for j in model.J:
            print(f"Unidades del recurso {i} para producir el producto {j} en la fabrica {k}: {pyo.value(model.a[i, j, k])}")
'''

# b_ik
model.b = pyo.Param(model.I, model.K, within=pyo.NonNegativeReals, mutable=True)
for k in model.K:
    disponibilidad_recursos = dfs[k].iloc[:,-1].dropna().values
    disponibilidad_recursos = [float(str(valor).replace(',', '.')) for valor in disponibilidad_recursos]
    for i, valor in zip(model.I, disponibilidad_recursos):
        model.b[i, k] = valor
'''
for k in model.K:
    for i in model.I:
        print(f"Disponibilidad del recurso {i} en la fabrica {k}: {pyo.value(model.b[i, k])}")
'''

# c_jk
model.c = pyo.Param(model.J, model.K, within=pyo.NonNegativeReals, mutable=True)
for k in model.K:
    costos_produccion = dfs[k].iloc[-1].values[1:]
    costos_produccion = [valor.replace(',', '.') for valor in costos_produccion if pd.notna(valor) and valor.strip()]
    for j, valor in zip(model.J, costos_produccion):
        float_valor = float(valor)
        model.c[j, k] = float_valor
'''
for k in model.K:
    for j in model.J:
        print(f"Costo de produccion del producto {j} en la fabrica {k}: {pyo.value(model.c[j, k])}")
'''

# d_j
model.d = pyo.Param(model.J, within=pyo.NonNegativeReals, mutable=True)
for j, valor in zip(model.J, demanda):
    model.d[j] = valor
'''
for j in model.J:
    print(f"Producto {j}: {pyo.value(model.d[j])}")
'''

# x_jk
model.x = pyo.Var(model.J, model.K, within=pyo.NonNegativeReals)


