<!DOCTYPE html>
<?php
function getRandomStr()
 {
     $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
     $randstring = '';
     for ($i = 0; $i < 10; $i++) {
         $randstring = $characters[rand(0, strlen($characters))];
     }
     return $randstring;
 }
?>

<html>
  <head>
    <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
    <meta content="utf-8" http-equiv="encoding">
    <title>Mapa COVID Argentina</title>
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-174571331-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-174571331-1');
</script>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=default"></script>
   <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
   <script
     src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDSgsWTwfNItv9D4ajY6-KNVpbU0AkzM_E&libraries=&v=weekly&sda=<?php echo date('l jS \of F Y h:i:s A'); ?>"
     defer
   ></script>
    <link rel="stylesheet" type="text/css" href="style.css?<?= getRandomStr(); ?>" />
  </head>
  <body>
    <table>
    <div id="map"></div>
    <div id = "botonera"></div>
    <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
    <div style="position: relative;">
        <div id="chart_velas" ></div>
        <div id="chart_curva" ></div>
        <div id="chart_defunciones" >asdadssad</div>
  </div>
    <div id="tests" ></div>
    <div id="fallecidos" ></div>
    <div id="titulo"></div>
    <div id="actualizacion"></div>
    <div id="acercade"><a href = "javascript:acercade();">Acerca de Mapa COVID Argentina</a></div>
    <script src="./app.js?rndstr=<?= getRandomStr(); ?>"></script>
  </body>
</html>
