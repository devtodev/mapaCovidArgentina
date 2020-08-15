import mysql.connector
import json
import numpy as np

file_zonas = "/srv/http/data_zonas.json"
file_totales = "/srv/http/data_totales.json"
file_edades = "/srv/http/data_provincias_edades.json"
TAG_COVIDPOSITIVO = "COVID Positivo"
TAG_TESTS = "Tests COVID"

mydb = mysql.connector.connect(
    host="localhost",
    user="USER",
    password="PASSWORD",
    database="mapa"
)


def consulta(query):
    mycursor = mydb.cursor()
    mycursor.execute(query)
    return mycursor.fetchall()


def consultaGeograficaFallecidos(geografia, fallecido, covid, tag):
    query = 'select residencia_provincia_id, residencia_departamento_id, count(*) as cantidad '
    query = query + 'from casos where upper(fallecido) = "'+fallecido+'"  and upper(clasificacion_resumen) = "'+covid+'" '
    query = query + 'group by ' + geografia + ', residencia_provincia_id;'
    respuesta = {}
    for row in consulta(query):
        if geografia == "residencia_provincia_id":
            in1 = row[0]
        else:
            in1 = row[0] + row[1]
        respuesta[in1] = {TAG_COVIDPOSITIVO: { tag: row[2] }}
    return respuesta

def consultaGeograficaCuidados(geografia, cuidado, covid, tag):
    query = 'select residencia_provincia_id, residencia_departamento_id, count(*) as cantidad '
    query = query + 'from casos where upper(fallecido) = "NO" and upper(cuidado_intensivo) = "'+cuidado+'"  and upper(clasificacion_resumen) = "CONFIRMADO" and upper(clasificacion_resumen) = "'+covid+'" '
    query = query + 'group by ' + geografia + ', residencia_provincia_id;'
    respuesta = {}
    for row in consulta(query):
        if geografia == "residencia_provincia_id":
            in1 = row[0]
        else:
            in1 = row[0] + row[1]
        respuesta[in1] = {TAG_COVIDPOSITIVO: { tag: row[2] }}
    return respuesta

def consultaGeograficaCOVIDPositivo(geografia):
    respuesta = {}
    fallecidos = consultaGeograficaFallecidos(geografia, "SI", "CONFIRMADO", "Fallecidos")
    vivos = consultaGeograficaFallecidos(geografia, "NO", "CONFIRMADO", "Vivos")
    cuidados = consultaGeograficaCuidados(geografia, "SI", "CONFIRMADO", "Cuidados")
    respuesta = mergeDics(fallecidos, vivos)
    respuesta = mergeDics(respuesta, cuidados)
    return respuesta

def consultaGeografica(query, geografia, tag, subtag):
    respuesta = {}
    for row in consulta(query):
        if geografia == "residencia_provincia_id":
            in1 = row[0]
        else:
            in1 = row[0] + row[1]
        respuesta[in1] = {tag : {subtag: row[2]} }
    return respuesta

def consultaGeograficaAgrupadaClasificada(geografia, agrupacion, clasificacion):
    query = 'select residencia_provincia_id, residencia_departamento_id, count(*) '
    query = query + 'from casos where ' + agrupacion + ' = "' + clasificacion + '" '
    query = query + 'group by ' + geografia + ',residencia_provincia_id;'
    respuesta = consultaGeografica(query, geografia, TAG_TESTS, clasificacion)
    return respuesta

def consultaGeograficaAsistenciaRespiratoria(geografia):
    query = "select residencia_provincia_id, residencia_departamento_id, count(*)  from casos where asistencia_respiratoria_mecanica = 'SI' and fallecido = 'NO' and clasificacion_resumen = 'Confirmado' group by " + geografia + ",residencia_provincia_id;"
    respuesta = consultaGeografica(query, geografia, "Asistencia respiratoria mecanica" ,"COVID + respirador")
    query = "select residencia_provincia_id, residencia_departamento_id, count(*)  from casos where asistencia_respiratoria_mecanica = 'SI' and fallecido = 'NO' and clasificacion_resumen != 'Confirmado' group by " + geografia + ",residencia_provincia_id;"
    sinCovidSinRespirador = consultaGeografica(query, geografia, "Asistencia respiratoria mecanica", "COVID - respirador")
    respuesta = mergeDics(respuesta, sinCovidSinRespirador)
    return respuesta

def consultaGeograficaOrigenFinanciamiento(geografia):
    respuesta = {}
    query = "select residencia_provincia_id, residencia_departamento_id, count(*) from casos where origen_financiamiento = 'Privado' group by " + geografia + ",residencia_provincia_id;"
    privado = consultaGeografica(query, geografia, "Financiamiento" ,"Privado")
    query = "select residencia_provincia_id, residencia_departamento_id, count(*) from casos where origen_financiamiento != 'Privado' group by " + geografia + ",residencia_provincia_id;"
    respuesta = mergeDics(privado, consultaGeografica(query, geografia, "Financiamiento" ,"Público"))
    return respuesta

def consultaPoblacion():
    respuesta = {}
    query = "  select provincia_id, departamento_id, sexo, a2020 from poblacion group by provincia_id, departamento_id, sexo;"
    for row in consulta(query):
        in1 = row[0] + row[1]
        if not in1 in respuesta:
            respuesta[in1] = {}
            respuesta[in1]["poblacion"]  = {}
        respuesta[in1]["poblacion"][row[2]] = row[3]
    return respuesta

def consultaTotalAgrupadaClasificada(agrupacion, clasificacion):
    query = 'select count(*) as "' + clasificacion + '" '
    query = query + 'from casos where ' + agrupacion + ' = "' + clasificacion + '"; '
    row = consulta(query)
    respuesta = {clasificacion: row[0][0]}
    return respuesta

def mergeDics(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                mergeDics(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
#                if (key != "nombre"):
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def consultaAgrupadaClasificada(geografia, agrupacion, clasificaciones):
    respuesta = {}
    for clasificacion in clasificaciones:
        if geografia == "":
            newdata = consultaTotalAgrupadaClasificada(agrupacion, clasificacion)
        else:
            newdata = consultaGeograficaAgrupadaClasificada(geografia, agrupacion, clasificacion)
        respuesta = mergeDics(respuesta, newdata)
    return respuesta


def consultaTotales(agrupacion, nombre):
    query = 'select ' + agrupacion + ', count(*) as "cantidad" '
    query = query + ' from casos group by ' + agrupacion + ';'
    respuesta = {}
    for row in consulta(query):
        if nombre != "":
            respuesta[row[0]] = {nombre: row[1]}
        else:
            respuesta[row[0]] = row[1]
    return respuesta


def persistir(nombre, datos):
    f = open(nombre, "w")
    f.write(json.dumps(datos, ensure_ascii=False))
    f.close()
    print("Guardado en ", nombre)
    print('>>> ',datos)

def consultaGeograficaMaximos(geografia, clasificacionCasos):
    query = 'select '+geografia+', count(*) as "cantidad" from casos' \
	+ ' where clasificacion_resumen = "'+clasificacionCasos+'" and '+geografia+' != "SIN ESPECIFICAR" ' \
	+ ' group by '+geografia+', residencia_provincia_id, clasificacion_resumen ' \
    + ' order by cantidad desc limit 1; '
    myquery = consulta(query)[0]
    resultado = {clasificacionCasos: myquery[1]}
    return resultado

def calculaMaximosFacellidosGeografico(geografia):
    query = 'select '+geografia+', count(*) cantidad from casos ' \
    + ' where fallecido = "SI" and '+geografia+' != "SIN ESPECIFICAR" ' \
    + ' group by '+geografia+', residencia_provincia_id order by cantidad desc; '
    myquery = consulta(query)[0]
    resultado = {"Fallecidos": myquery[1]}
    return resultado

def consultaMaximos(clasificacionCasos):
    respuesta = {}
    temp = {}
    for clasificacion in clasificacionCasos:
        temp["departamento"] = consultaGeograficaMaximos("residencia_departamento_nombre", clasificacion)
        temp["provincia"] = consultaGeograficaMaximos("residencia_provincia_nombre", clasificacion)
        respuesta = mergeDics(respuesta, temp)
    temp["departamento"] = calculaMaximosFacellidosGeografico("residencia_departamento_nombre")
    temp["provincia"] = calculaMaximosFacellidosGeografico("residencia_provincia_nombre")
    respuesta = mergeDics(respuesta, temp)
    return respuesta

def calculaPorcentajes(datos, maximos):
    resultado = {}
    for in1 in datos:
        resultado[in1] = {}
        resultado[in1]["pormil"] = {}
        if len(in1) == 2:
            maximosZona = maximos["provincia"]
        else:
            maximosZona = maximos["departamento"]
        for clasificacion in maximosZona:
            if in1 in datos:
                if TAG_TESTS in datos[in1] and clasificacion in datos[in1][TAG_TESTS]:
                    porcentaje = int(datos[in1][TAG_TESTS][clasificacion] * 1000 / (maximosZona[clasificacion]))
                else:
                    porcentaje = 0
            else:
                porcentaje = 0
            resultado[in1]["pormil"][clasificacion] = porcentaje
    return resultado

def consultaActualizacion():
    query = "select ultima_actualizacion from casos order by ultima_actualizacion desc limit 1;"
    return consulta(query)[0][0]

def consultaPositivosTotales():
    respuesta = {}
    query = "select count(*) fallecidos from casos where fallecido = 'SI' and clasificacion_resumen = 'Confirmado';"
    respuesta["Fallecidos"] = consulta(query)[0][0]
    query = "select count(*) fallecidos from casos where fallecido = 'NO' and clasificacion_resumen = 'Confirmado';"
    respuesta["Vivos"] = consulta(query)[0][0]
    query = "select count(*) cuidados from casos where cuidado_intensivo = 'SI' and fallecido = 'NO'  and upper(clasificacion_resumen) = 'CONFIRMADO';"
    respuesta["Cuidados"] = consulta(query)[0][0]
    return respuesta

def consultaAsistenciaRespiratoria():
    respuesta = {}
    query = "select count(*) cantidad from casos where asistencia_respiratoria_mecanica = 'SI' and fallecido = 'NO' and clasificacion_resumen = 'Confirmado';"
    respuesta["COVID + respirador"] = consulta(query)[0][0]
    query = "select count(*) cantidad from casos where asistencia_respiratoria_mecanica = 'SI' and fallecido = 'NO' and clasificacion_resumen != 'Confirmado';"
    respuesta["COVID - respirador"] = consulta(query)[0][0]
    return respuesta

def calculoEdadesTotal():
    # positivos
    respuesta = { "edad": {} }
    queryEdadPorDepartamento = 'select edad from casos where edad_años_meses = "años" and edad != "" and clasificacion_resumen = "Confirmado";'
    edades = [int(i[0], 10) for i in consulta(queryEdadPorDepartamento)]
    if len(edades) == 0:
        edades = [0]
    respuesta["edad"]["contagiados"] = {"min": int(np.min(edades)), "q1": int(np.percentile(edades, 25)), "q2": int(np.percentile(edades, 75)), "max": int(np.max(edades))}
    # fallecidos
    queryEdadPorDepartamento = 'select edad from casos where edad_años_meses = "años" and edad != "" and clasificacion_resumen = "Confirmado" and fallecido = "SI";'
    edades = [int(i[0], 10) for i in consulta(queryEdadPorDepartamento)]
    if len(edades) == 0:
        edades = [0]
    respuesta["edad"]["fallecidos"] = {"min": int(np.min(edades)), "q1": int(np.percentile(edades, 25)), "q2": int(np.percentile(edades, 75)), "max": int(np.max(edades))}
    # cuidados intensivos
    queryEdadPorDepartamento = 'select edad from casos where edad_años_meses = "años" and edad != "" and fallecido = "NO" and cuidado_intensivo = "SI"  and upper(clasificacion_resumen) = "CONFIRMADO";'
    edades = [int(i[0], 10) for i in consulta(queryEdadPorDepartamento)]
    if len(edades) == 0:
        edades = [0]
    respuesta["edad"]["cuidados"] = {"min": int(np.min(edades)), "q1": int(np.percentile(edades, 25)), "q2": int(np.percentile(edades, 75)), "max": int(np.max(edades))}
    # respiradores covid +
    queryEdadCovid = 'select edad from casos where edad_años_meses = "años" and edad != "" and fallecido = "NO" and asistencia_respiratoria_mecanica = "SI"  and upper(clasificacion_resumen) = "CONFIRMADO";'
    edades = [int(i[0], 10) for i in consulta(queryEdadCovid)]
    if len(edades) == 0:
        edades = [0]
    respuesta["edad"]["respirador+"] = {"min": int(np.min(edades)), "q1": int(np.percentile(edades, 25)),
                                        "q2": int(np.percentile(edades, 75)), "max": int(np.max(edades))}
    # respiradores covid +
    queryEdadNoCovid = 'select edad from casos where edad_años_meses = "años" and edad != "" and fallecido = "NO" and asistencia_respiratoria_mecanica = "SI"  and upper(clasificacion_resumen) <> "CONFIRMADO";'
    edades = [int(i[0], 10) for i in consulta(queryEdadNoCovid)]
    if len(edades) == 0:
        edades = [0]    
    respuesta["edad"]["respirador-"] = {"min": int(np.min(edades)), "q1": int(np.percentile(edades, 25)),
                                        "q2": int(np.percentile(edades, 75)), "max": int(np.max(edades))}

    return respuesta

def calculoEdades():
    respuesta = {}
    # traer todas las provincias
    queryProvincias = 'select residencia_provincia_id from casos group by residencia_provincia_id;'
    for provincia in consulta(queryProvincias):
        in1Provincia = provincia[0]
        respuesta[in1Provincia] = {}
        # provincia edades positivo
        queryEdadPorProvincia = 'select edad from casos where edad_años_meses = "años" and edad != "" and clasificacion_resumen = "Confirmado" and residencia_provincia_id = "'+in1Provincia+'";'
        edadesProvincia = [int(i[0], 10) for i in consulta(queryEdadPorProvincia)]
        if len(edadesProvincia) == 0:
            edadesProvincia = [0]
        respuesta[in1Provincia]["edad"] = {"contagiados": {"min": int (np.min(edadesProvincia)), "q1": int(np.percentile(edadesProvincia, 25)), "q2": int(np.percentile(edadesProvincia, 75)), "max": int(np.max(edadesProvincia))}}

        # provincia edades fallecidos
        queryEdadPorProvincia = 'select edad from casos where edad_años_meses = "años" and edad != "" and clasificacion_resumen = "Confirmado" and fallecido = "SI" and residencia_provincia_id = "' + in1Provincia + '";'
        edadesProvincia = [int(i[0], 10) for i in consulta(queryEdadPorProvincia)]
        if len(edadesProvincia) == 0:
            edadesProvincia = [0]
        respuesta[in1Provincia]["edad"]["fallecidos"] = {"min": int(np.min(edadesProvincia)), "q1": int(np.percentile(edadesProvincia, 25)), "q2": int(np.percentile(edadesProvincia, 75)), "max": int(np.max(edadesProvincia))}

        # provincia edades cuidados intensivos
        queryEdadPorProvincia = 'select edad from casos where edad_años_meses = "años" and edad != "" and fallecido = "NO" and cuidado_intensivo = "SI" and upper(clasificacion_resumen) = "CONFIRMADO" and residencia_provincia_id = "' + in1Provincia + '";'
        edadesProvincia = [int(i[0], 10) for i in consulta(queryEdadPorProvincia)]
        if len(edadesProvincia) == 0:
            edadesProvincia = [0]
        respuesta[in1Provincia]["edad"]["cuidados"] = {"min": int(np.min(edadesProvincia)), "q1": int(np.percentile(edadesProvincia, 25)), "q2": int(np.percentile(edadesProvincia, 75)), "max": int(np.max(edadesProvincia))}

        # provincia edades respiradores +
        queryEdadPorProvincia = 'select edad from casos where edad_años_meses = "años" and edad != "" and fallecido = "NO" and asistencia_respiratoria_mecanica = "SI" and upper(clasificacion_resumen) = "CONFIRMADO" and residencia_provincia_id = "' + in1Provincia + '";'
        edadesProvincia = [int(i[0], 10) for i in consulta(queryEdadPorProvincia)]
        if len(edadesProvincia) == 0:
            edadesProvincia = [0]
        respuesta[in1Provincia]["edad"]["respirador+"] = {"min": int(np.min(edadesProvincia)), "q1": int(np.percentile(edadesProvincia, 25)), "q2": int(np.percentile(edadesProvincia, 75)), "max": int(np.max(edadesProvincia))}

        # provincia edades respiradores -
        queryEdadPorProvincia = 'select edad from casos where edad_años_meses = "años" and edad != "" and fallecido = "NO" and asistencia_respiratoria_mecanica = "SI" and upper(clasificacion_resumen) <> "CONFIRMADO" and residencia_provincia_id = "' + in1Provincia + '";'
        edadesProvincia = [int(i[0], 10) for i in consulta(queryEdadPorProvincia)]
        if len(edadesProvincia) == 0:
            edadesProvincia = [0]
        respuesta[in1Provincia]["edad"]["respirador-"] = {"min": int(np.min(edadesProvincia)), "q1": int(np.percentile(edadesProvincia, 25)), "q2": int(np.percentile(edadesProvincia, 75)), "max": int(np.max(edadesProvincia))}

        # obtengo departamentos para el in1 de la provincia
        queryDepartamentos = 'select residencia_departamento_id from casos where residencia_provincia_id = "'+in1Provincia+'" group by residencia_departamento_id;'
        for departamento in consulta(queryDepartamentos):
            in1Departamento = departamento[0]
            in1Unificado = in1Provincia + in1Departamento
            # provincia edades positivo
            queryEdadPorDepartamento = 'select edad from casos where edad_años_meses = "años" and edad != "" and clasificacion_resumen = "Confirmado" and residencia_departamento_id = "'+in1Departamento+'" and residencia_provincia_id = "' + in1Provincia + '";'
            edadesDepartamento = [int(i[0], 10) for i in consulta(queryEdadPorDepartamento)]
            if len(edadesDepartamento) == 0:
                edadesDepartamento = [0]
            respuesta[in1Unificado] = {}
            respuesta[in1Unificado]["edad"] = {"contagiados" : {"min": int(np.min(edadesDepartamento)), "q1": int(np.percentile(edadesDepartamento, 25)), "q2": int(np.percentile(edadesDepartamento, 75)), "max": int(np.max(edadesDepartamento))}}

            # falta fallecidos
            queryEdadPorDepartamento = 'select edad from casos where edad_años_meses = "años" and edad != "" and clasificacion_resumen = "Confirmado" and residencia_departamento_id = "'+in1Departamento+'" and fallecido = "SI" and residencia_provincia_id = "' + in1Provincia + '";'
            edadesDepartamento = [int(i[0], 10) for i in consulta(queryEdadPorDepartamento)]
            if len(edadesDepartamento) == 0:
                edadesDepartamento = [0]
            respuesta[in1Unificado]["edad"]["fallecidos"] = {"min": int(np.min(edadesDepartamento)), "q1": int(np.percentile(edadesDepartamento, 25)), "q2": int(np.percentile(edadesDepartamento, 75)), "max": int(np.max(edadesDepartamento))}

            # cuidados intensivos
            queryEdadPorDepartamento = 'select edad from casos where edad_años_meses = "años" and edad != "" and fallecido = "NO" and residencia_departamento_id = "'+in1Departamento+'" and cuidado_intensivo = "SI" and upper(clasificacion_resumen) = "CONFIRMADO" and residencia_provincia_id = "' + in1Provincia + '";'
            edadesDepartamento = [int(i[0], 10) for i in consulta(queryEdadPorDepartamento)]
            if len(edadesDepartamento) == 0:
                edadesDepartamento = [0]
            respuesta[in1Unificado]["edad"]["cuidados"] = {"min": int(np.min(edadesDepartamento)), "q1": int(np.percentile(edadesDepartamento, 25)), "q2": int(np.percentile(edadesDepartamento, 75)), "max": int(np.max(edadesDepartamento))}

            # Respirador +
            queryEdadPorDepartamento = 'select edad from casos where edad_años_meses = "años" and edad != "" and fallecido = "NO" and residencia_departamento_id = "'+in1Departamento+'" and asistencia_respiratoria_mecanica = "SI" and upper(clasificacion_resumen) = "CONFIRMADO" and residencia_provincia_id = "' + in1Provincia + '";'
            edadesDepartamento = [int(i[0], 10) for i in consulta(queryEdadPorDepartamento)]
            if len(edadesDepartamento) == 0:
                edadesDepartamento = [0]
            respuesta[in1Unificado]["edad"]["respirador+"] = {"min": int(np.min(edadesDepartamento)), "q1": int(np.percentile(edadesDepartamento, 25)), "q2": int(np.percentile(edadesDepartamento, 75)), "max": int(np.max(edadesDepartamento))}

            # Respirador -
            queryEdadPorDepartamento = 'select edad from casos where edad_años_meses = "años" and edad != "" and fallecido = "NO" and residencia_departamento_id = "'+in1Departamento+'" and asistencia_respiratoria_mecanica = "SI" and upper(clasificacion_resumen) <> "CONFIRMADO" and residencia_provincia_id = "' + in1Provincia + '";'
            edadesDepartamento = [int(i[0], 10) for i in consulta(queryEdadPorDepartamento)]
            if len(edadesDepartamento) == 0:
                edadesDepartamento = [0]
            respuesta[in1Unificado]["edad"]["respirador-"] = {"min": int(np.min(edadesDepartamento)), "q1": int(np.percentile(edadesDepartamento, 25)), "q2": int(np.percentile(edadesDepartamento, 75)), "max": int(np.max(edadesDepartamento))}

    return respuesta

def calculaTotales(clasificacionCasos):
    totales = calculoEdadesTotal()
    totales["Tests COVID"] = consultaAgrupadaClasificada("", "clasificacion_resumen", clasificacionCasos)
    totales["COVID Positivo"] = consultaPositivosTotales()
    totales["Asistencia respiratoria mecanica"] = consultaAsistenciaRespiratoria()
    totales["Financiamiento"] = consultaTotales("origen_financiamiento", "")
    totales["Fecha actualización"] = {"Datos ": consultaActualizacion(), "Sistema": "2020-07-28"}
    # totales["Por sexo"] = consultaTotales("sexo", "")
    persistir(file_totales, totales)
    return

def calculaZona(geografia, clasificacionCasos):
    respuesta = {}
    clasificacion = consultaAgrupadaClasificada(geografia, 'clasificacion_resumen', clasificacionCasos)
    positivos = consultaGeograficaCOVIDPositivo(geografia)
    respuesta = mergeDics(clasificacion, positivos)
    respiradores = consultaGeograficaAsistenciaRespiratoria(geografia)
    respuesta = mergeDics(respuesta, respiradores)
    financiamiento = consultaGeograficaOrigenFinanciamiento(geografia)
    respuesta = mergeDics(respuesta, financiamiento)
    # edades = calculoEdadesTotal()
#    respuesta = mergeDics(respuesta, edades)
    # totales["Por sexo"] = consultaTotales("sexo", "")
    return respuesta

def getPeople():
    respuesta = {}
    # cambiar nombre a2020 por el año correspondiente!
    query = 'select provincia_id, provincia_nombre, a2020 from poblacion group by provincia_id, provincia_nombre;'
    for row in consulta(query):
        provincia_id = row[0]
        depto_nombre = row[1]
        habitantes = row[2]

        respuesta[in1] = {TAG_COVIDPOSITIVO: {tag: row[2]}}


    return respuesta;

# totales
clasificacionCasos = consultaTotales("clasificacion_resumen", "")
calculaTotales(clasificacionCasos)

# departamentos
departamentos = calculaZona('residencia_departamento_id', clasificacionCasos)
provincias = calculaZona('residencia_provincia_id', clasificacionCasos)

zonas = mergeDics(departamentos, provincias)
maximos = consultaMaximos(clasificacionCasos)
pormil = calculaPorcentajes(zonas, maximos)
zonas = mergeDics(zonas, pormil)
edades = calculoEdades()
zonas = mergeDics(zonas, edades)
poblaciones = consultaPoblacion()
zonas = mergeDics(zonas, poblaciones)
print("-----")
print(zonas)
print("+++++")
persistir(file_zonas, zonas)