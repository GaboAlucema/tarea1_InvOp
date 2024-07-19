Instalar:
    anaconda para glpk o scip (con su entorno nuevo pyomo_env),
    pyomo,
    pandas

Extras:
    modificar:
        dependencies.py entre los archivos de librerias de python:
            linea 1002: _floats = [np.float64, np.float16, np.float32, np.float64],
            linea 1016: _complex = [np.complex128, np.complex64, np.complex128]
