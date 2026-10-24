# Datos y derechos de uso

El manifiesto sources.json enlaza siete PDF oficiales públicos del GLF. El script descarga
los originales a raw y crea pasajes con número de página en processed. Esas carpetas se
excluyen de Git: disponibilidad pública no equivale a una licencia de redistribución.
Los derechos de los PDF pertenecen a sus titulares; MIT cubre el código del equipo.
Los 26 expedientes y sus datos personales no se incluyen. Tampoco el ZIP normativo privado
de 585 fragmentos ni sus traducciones derivadas. Las huellas de originales académicos se
guardan localmente, sin incorporar entregas semanales al repositorio público.
Ejecutar desde la raíz: python -m src.data_processing.
