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
Para un mejor manejo a la hora de realizar la indexación, se han creado 3 clases: ```InvIndexKey```, ```InvIndexValue``` e ```InvIndex```, donde las dos primeras guardan la información principal de nuestro índice invertido y la tercera las agrupa dentro de una sola estructura, agregando métodos que las combinan y abstrayendo la lógica.

En primer lugar, se crea un nuevo objeto ```InvIndex``` al que se le agregará los documentos a indexar mediante el uso del método ```index_docs```. Por cada documento a procesar, ejecutará el método ```proccess_content``` el cual irá llenando el diccionario de ```InvIndexKey```:```InvIndexValue``` que tiene el objeto principal, haciendo uso de un stemmer y de las stop words que este brinde. 

A la hora de añadir un nuevo objeto al diccionario calculamos si el peso futuro de nuestro objeto sobrepasa los límites dados de memoria total del sistema. En caso sí lo sobrepase, mandamos el diccionario actual a memoria secundaria haciendo uso de JSON, para luego vaciarlo y seguir con el proceso, creando dentro del directorio actual a una serie de bloques ```block_n.json```.

Finalmente, cuando ya hallamos mandado a memoria secundaria a todos los bloques necesarios para representar los tokens de los documentos actuales, realizamos un merge de los bloques usando el método ```merge_and_save_blocks```, el cual extraerá los bloques iniciales uno a uno para no sobrepasar el límite de memoria e irá llenando un nuevo diccionario ordenado, creando un nuevo bloque final ```merged_block_n.json``` antes de sobrepasar el límite de memoria, para seguir después con el proceso.

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
