var map, zonas, dataTotal, idprovincias, seleccion = "1";
var queryString = window.location.search, urlParams = new URLSearchParams(queryString);
TOSHOW = "" != urlParams ? "departamentos" : "provincias";
GEOJSONTOSHOW = "departamentos" != TOSHOW ? "departamento.geojson" : "provincia.geojson";
DATAJSONTOSHOW = "data_zonas.json";
DATAJSONTOTALES = "data_totales.json";
var settings;
google.charts.load('current', {'packages':['corechart'], 'callback': cargaTotales   }  );
var chart;
function  drawChart(poblacion, contagiados, ncontagiados, cuidados, ncuidados, fallecidos, nfallecidos, respiradoresp, nrespiradoresp,  respiradoresn, nrespiradoresn) {
        respiradoresp.splice(0,0,nrespiradoresp + "\nRespiradores\nCOVID +");
        respiradoresn.splice(0,0,nrespiradoresn + "\nRespiradores\nCOVID -");
        contagiados.splice(0,0,ncontagiados + "\ncontagiados");
        fallecidos.splice(0,0,nfallecidos +"\nfallecidos");
        cuidados.splice(0,0,ncuidados +"\ncuidados intensivos");
        var dataInfo = [ contagiados, cuidados, fallecidos, respiradoresp, respiradoresn ]
        var data = google.visualization.arrayToDataTable(dataInfo, true);
        var porcien =  ncontagiados*100 ;
        porcien = (porcien / poblacion).toFixed(2);
        var titulo = (poblacion == 0)? '\nEdades min,  max y cuartiles':  formatMoney(poblacion) + ' poblacion total \nEdades min,  max y cuartiles';

        var options = {
          'height':360,
          'width':576,
         'fontSize': 14,
         'title':titulo,
          legend:'none'
        };
       options.chartArea = { left: '5%', top: '20%', width: "95%", height: "66%"};
       chart = new google.visualization.CandlestickChart(document.getElementById('chart_div'));
       chart.draw(data, options);
}

function cargaTotales() {
  $.getJSON(DATAJSONTOTALES, function(a) {
    if (seleccion != "") {
      settings = a;
      document.getElementById("titulo").innerHTML = "Argentina";
      showData(a);
    }
  }).fail(function() {
      console.log("An error has occurred.")
  });
}

function formatMoney(amount, decimalCount = 0, decimal = ".", thousands = ",") {
  try {
    decimalCount = Math.abs(decimalCount);
    decimalCount = isNaN(decimalCount) ? 2 : decimalCount;

    const negativeSign = amount < 0 ? "-" : "";

    let i = parseInt(amount = Math.abs(Number(amount) || 0).toFixed(decimalCount)).toString();
    let j = (i.length > 3) ? i.length % 3 : 0;

    return negativeSign + (j ? i.substr(0, j) + thousands : '') + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + thousands) + (decimalCount ? decimal + Math.abs(amount - i).toFixed(decimalCount).slice(2) : "");
  } catch (e) {
    console.log(e)
  }
};

function getColorByIn1(in1) {
  pormil = 0;
  var pintura = document.getElementById("pintura");
  if ((zonas!= null) && (zonas[in1] != null))  {
    pormil = zonas[in1]["pormil"].Confirmado;
  }

  pormil = 700 < pormil ? 255 : 20 * pormil;

  if (!TOSHOW.localeCompare("departamentos"))
  {
    pormil = 700 < pormil ? 255 : 8 * pormil;
  } else {
     pormil = 700 < pormil ? 255 : 20 * pormil;
  }

  pormil = 700 < pormil ? 255 : pormil;
  r = pormil;
  g = 255 - r;
  b = 255 - r;
  color = "rgb(" + r + "," + g + ", " + b + ")";
  return color;
}

function printData(a) {
    text = "";
    for (var c in a) {
      if ((c != "pormil")&&(c != "nombre"))
      a.hasOwnProperty(c) && ("object" != typeof a[c] ? text = text + "&nbsp;&nbsp;&nbsp;" + c + ": " + a[c] + "<br/>" : (subobj = a[c],
      text = text + "<br/>" + c + "<br/>",
      text += getTextFromJSON(subobj)));
    }
    return text;
}

function acercade() {
  alert('Se muestra en el mapa los datos publicados por el Ministerio de Salud de la Nación Argentia el día ' + settings["Fecha actualización"]["Datos "] + ' y disponibles para descargar en el link de abajo a la derecha. El mapa de COVID Argentina es un desarrollo realizado por Carlos Miguens. cmiguens@gmail.com ');
}

function showData(a) {
     if ((a != null) && (a[ "Tests COVID"] != null)) {
        var text = "<u>Resultados tests</u><br />"   + printData(a["Tests COVID"]) +"<u>Financiamiento</u> <br /> "+ printData(a["Financiamiento"]) ;
        document.getElementById("fallecidos").innerHTML = text;
      } else {
        document.getElementById("fallecidos").innerHTML = "";
      }
      if ((a != null) && (a["edad"]!=null)) {
        nvivos = (a["COVID Positivo"]==null)||(a["COVID Positivo"]["Vivos"]==null) ?0:a["COVID Positivo"]["Vivos"];
        ncuidados = (a["COVID Positivo"]==null)||(a["COVID Positivo"]["Cuidados"]==null) ?0:a["COVID Positivo"]["Cuidados"];
        nfallecidos = (a["COVID Positivo"]==null)||(a["COVID Positivo"]["Fallecidos"]==null) ?0:a["COVID Positivo"]["Fallecidos"];

        nrespiradoresp =(a["Asistencia respiratoria mecanica"]==null)||(a["Asistencia respiratoria mecanica"]["COVID + respirador"]==null) ?0:a["Asistencia respiratoria mecanica"]["COVID + respirador"];
        nrespiradoresn = (a["Asistencia respiratoria mecanica"]==null)||(a["Asistencia respiratoria mecanica"]["COVID - respirador"]==null) ?0:a["Asistencia respiratoria mecanica"]["COVID - respirador"];

        var contagiados =  [a["edad"]["contagiados"].min, a["edad"]["contagiados"].q1, a["edad"]["contagiados"].q2, a["edad"]["contagiados"].max];
        var cuidados =  [a["edad"]["cuidados"].min, a["edad"]["cuidados"].q1, a["edad"]["cuidados"].q2, a["edad"]["cuidados"].max];
        var fallecidos = [a["edad"]["fallecidos"].min, a["edad"]["fallecidos"].q1, a["edad"]["fallecidos"].q2, a["edad"]["fallecidos"].max];

        var respiradoresp =  0;
        var respiradoresn =  0;
        if (a["edad"]["respirador+"] != null) {
          respiradoresp =  [a["edad"]["respirador+"].min, a["edad"]["respirador+"].q1, a["edad"]["respirador+"].q2, a["edad"]["respirador+"].max];
          respiradoresn =  [a["edad"]["respirador-"].min, a["edad"]["respirador-"].q1, a["edad"]["respirador-"].q2, a["edad"]["respirador-"].max];
        }
        poblacion = 0;
        if (a["poblacion"] != null)
        {
          poblacion =a["poblacion"]["T"];
        }
        drawChart(poblacion, contagiados, nvivos, cuidados, ncuidados, fallecidos, nfallecidos, respiradoresp, nrespiradoresp,  respiradoresn, nrespiradoresn);
      }
      if ((settings != null) && (settings["Fecha actualización"] != null)) {
          fecha = (settings["Fecha actualización"]["Datos "] != null) ? "<a href='https://sisa.msal.gov.ar/datos/descargas/covid-19/files/Covid19Casos.csv'>Datos actualizados al " + settings["Fecha actualización"]["Datos "] + "</a>" : "";
          document.getElementById("actualizacion").innerHTML = fecha
      }
}

function resolverNombre(a) {
    nombreKey = a;
    "Tierra del Fuego, Ant\u00e1rtida e Islas del Atl\u00e1ntico Sur" === a && (nombreKey = "Tierra del Fuego");
    "Ciudad Aut\u00f3noma de Buenos Aires" === a && (nombreKey = "CABA");
    return nombreKey
}
$(document).ready(function() {
    $.getJSON(DATAJSONTOSHOW, function(a) {
        zonas = a
        initMap();
        //showData(zonas);
    }).fail(function() {
        console.log("An error has occurred.")
    })
});
var getCircularReplacer = function() {
    var a = new WeakSet;
    return function(c, d) {
        if ("object" === typeof d && null !== d) {
            if (a.has(d))
                return;
            a.add(d)
        }
        return d
    }
};
function reselecciona(a) {
    map.data.revertStyle();
    map.data.overrideStyle(a.feature, {
        strokeWeight: 5
    });
    nombre = a.feature.getProperty("nam");
    in1 = a.feature.getProperty("in1");
    document.getElementById("titulo").innerHTML = nombre;
    if(zonas[in1] == null) {
      document.getElementById("fallecidos").innerHTML = "sin datos";
        drawChart(0,[0, 0, 0, 0], 0, [0, 0, 0, 0], 0, [0, 0, 0, 0], 0, [0, 0, 0, 0], 0, [0, 0, 0, 0], 0);
      } else {
      showData(zonas[in1]);
    }
}
function initMap() {
    map = new google.maps.Map(document.getElementById("map"),{
        center: {
            lat: -40,
            lng: -55
        },
        zoom: 4
    });
    map.data.loadGeoJson(GEOJSONTOSHOW);
    map.data.setStyle(function(a) {
        try {
          in1 = a.getProperty("in1");
          nombre = a.getProperty("nam");
          color = getColorByIn1(in1);
        } catch(e) {color = 0}
        return {
            fillColor: color,
            strokeWeight: 1
        }
    });

    map.data.addListener("click", function(a) {
      seleccion =  (seleccion == "") ?"1":"";
      if (seleccion == "1") reselecciona(a);
    });

    map.data.addListener("mouseover", function(a) {
      if (seleccion == "1") {
          reselecciona(a);
      }
    });
    map.data.addListener("mouseout", function(a) {
        if (seleccion != "") {
          map.data.revertStyle();
          document.getElementById("titulo").innerHTML = "Argentina";
          showData(settings);
        }
    });
}

botonera = "departamentos" == TOSHOW ?  ' <a href="https://www.elestadodelclima.com/mapa/index.php">Ver departamentos</a> ' : '<a href = "https://www.elestadodelclima.com/mapa/index.php?mostrar=provincias">Ver provincias</a>';
document.getElementById("botonera").innerHTML = botonera;

function myPeriodicMethod() {
  $.ajax({
    success: function(data) {
      for (i = 0; i < 33;i++)
         console.log(i%2 == 0 ? ".: CmIgUeNs :. " : ".: cMiGuEnS :. ");
    },
    complete: function() {
      // schedule the next request *only* when the current one is complete:
      setTimeout(myPeriodicMethod, 1000);
    }
  });
}

// schedule the first invocation:
// setTimeout(myPeriodicMethod, 1500);
