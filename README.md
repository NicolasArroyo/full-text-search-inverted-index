# Proyecto 2 y 3 - BD II

# Integrantes:
- Nicolas Arroyo
- Josué Arriaga
- Max Antunez
- Gabriel Espinoza

# Introducción
## Objetivo
## Dominio de datos
## Importancia de la indexación

# Backend: Índice Invertido
## Construcción del índice invertido en memoria secundaria usando SPIMI
## Ejecución óptima de consultas aplicando Similitud de Coseno
## Construcción del índice invertido en PostgreSQL/MongoDB

# Backend: Índice Multidimensional
## Técnica de indexación de las librerías utilizadas
### Rtree
### Faiss
## Búsquedas
### Sequential
### Rtree
### Faiss
## Maldición de la dimensionalidad
## Mitigar la maldición de la dimensionalidad

# Frontend
## Diseño GUI
### Manual de uso
Primero se debe obtener una Spotify API Key. Para esto se debe hacer la siguiente request con la información correspondiente.

```zsh
curl -X POST "https://accounts.spotify.com/api/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials&client_id=your-client-id&client_secret=your-client-secret"

```

### Screenshots
## Análisis comparativo visual con otras implementaciones

# Experimentación
## Resultados experimentales
## Análisis y discusión
