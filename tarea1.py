import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd

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

# Minimizar la funcion objetivo
def min_obj(model):
    return sum(model.c[j, k] * model.x[j, k] for j in model.J for k in model.K)
model.obj = pyo.Objective(rule=min_obj, sense=pyo.minimize)

# Restricciones
def restriccion_recursos(model, i, k):
    return sum(model.a[i, j, k] * model.x[j, k] for j in model.J) <= model.b[i, k]
model.restriccion_recursos = pyo.Constraint(model.I, model.K, rule=restriccion_recursos)

def restriccion_demanda(model, j):
    return sum(model.x[j, k] for k in model.K) >= model.d[j]
model.restriccion_demanda = pyo.Constraint(model.J, rule=restriccion_demanda)

# Resolver el modelo
opt = SolverFactory('glpk')
results = opt.solve(model)

# Imprimir los resultados
print("Costo total de produccion: {:.2f}".format(pyo.value(model.obj)))
print("Cantidad de productos a producir en cada fabrica: ")
for k in model.K:
    for j in model.J:
        print(f"Producto {j} en fabrica {k}: {pyo.value(model.x[j, k]):.1f}")

# Generar un archivo con los resultados obtenidos 

file_path = "resultado.csv"
with open(file_path, 'w') as file:
    file.writelines(";P1;P2;P3;P4;P5;P6;P7;P8;P9;P10;P11;P12\n")

    for k in model.K:
        file.write(f"Fabrica {k};")
        for j in model.J:
            valor = pyo.value(model.x[j, k])
            valor_str = f"{valor:.2f}".replace('.', ',')
            file.write(f"{valor_str};")
            if j == "P12":
                file.write("\n")

    costo_total = pyo.value(model.obj)
    costo_total_str = f"{costo_total:.2f}".replace('.', ',')
    file.writelines(f"\nCosto total de produccion;{costo_total_str}")

print("Archivo " + file_path + " Creado con Exito.")
