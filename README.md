# Dron
Códigos de todo

## [Complementos](./complementos/)
Archivos complementarios

## [Pruebas](./pruebas/)
Script de pruebas para crear el final

## [src](./src/)
Código final

El dockerfile ya sirve, ejecutar con

docker run -it --rm \
  --device=/dev/video0 \
  -p 5000:5000 \
  -p 5001:5001 \
  reco-fac

Construido con
docker build -t reco-fac .

http://192.168.68.96:5001/
