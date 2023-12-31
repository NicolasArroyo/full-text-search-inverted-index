# Proyecto 2 y 3 - BD II

# Integrantes

| <a href="https://github.com/jmac-94" target="_blank">**Josué Mauricio Arriaga Colchado**</a> | <a href="https://github.com/NicolasArroyo" target="_blank">**Nicolas Mateo Arroyo Chávez**</a> | <a href="https://github.com/Gabrieleeh32159" target="_blank">**Gabriel Espinoza**</a> | <a href="https://github.com/Maxantunez404" target="_blank">**Max Antúnez**</a> |
| :----------------------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------: |
| <img src="https://avatars.githubusercontent.com/u/83974555?v=4" alt="drawing" width="200"/> | <img src="https://avatars.githubusercontent.com/u/83975293?v=4" alt="drawing" width="200"/> | <img src="https://avatars.githubusercontent.com/u/85197211?v=4" alt="drawing" width="200"/> | <img src="https://avatars.githubusercontent.com/u/83974281?v=4" alt="drawing" width="200"/> |

# Introducción
## Objetivo
El objetivo de este proyecto es diseñar e implementar sistemas de indexación eficientes para datos textuales y audios wav relacionados a canciones de Spotify. Buscamos optimizar las consultas y la recuperación de información, superar los retos de la alta dimensionalidad en los datos de audio, y ofrecer una interfaz de usuario amigable. Nuestro enfoque se centra en buscar la precisión y rapidez de las búsquedas, la comparación de diferentes métodos de indexación, y la evaluación de su eficacia mediante análisis comparativos y experimentación.

## Dominio de datos
Para la primera parte del proyecto nos hemos basado en la indexación de canciones de Spotify, de modo que guardamos el nombre de la canción, su autor/a y la letra completa.

Por otro lado, para la segunda parte hemos indexado los propios audios de las canciones de Spotify. Específicamente, dado los .wav de cada canción, hemos calculado los Mel-frequency cepstral coefficients (MFCCs) para guardar las señales de audio en una representación compacta que captura frecuencias importantes a través del tiempo aplicando una transformada de Fourier, dejando de lado a señalos sin importancia como son el ruido de fondo, volumen, tono, etc. Después, se ha aplicado una normalización a cada una de estas representaciones para asegurar una misma cantidad de datos por cada vector representativo y así poder indexarlo con técnicas avanzadas provenientes de librerías de Python. 

## Importancia de la indexación
La indexación de los datos que hemos realizado en el proyecto es importante por las siguientes razones:

1. Permite un manejo mucho más rápido de consultas, pues los registros son mucho más rápidos de encontrar en distintas situaciones donde el índice puede ser aprovechado.
2. Genera acceso a consultas mucho más específicas. Por ejemplo, para poder la canción de Spotify más similar a un audio se puede usar los índices de la segunda parte del proyecto aún cuando solo se tiene una parte de la canción completa como consulta.
3. Facilita el uso de técnicas de retrieval mucho más eficientes y adecuadas para contextos específicos que un cliente puede necesitar, como es el caso de K-NN.

# Backend: Índice Invertido
## Construcción del índice invertido en memoria secundaria usando SPIMI
Para un mejor manejo a la hora de realizar la indexación, se han creado 3 clases: ```InvIndexKey```, ```InvIndexValue``` e ```InvIndex```, donde las dos primeras guardan la información principal de nuestro índice invertido y la tercera las agrupa dentro de una sola estructura, agregando métodos que las combinan y abstrayendo la lógica.

En primer lugar, se crea un nuevo objeto ```InvIndex``` al que se le agregará los documentos a indexar mediante el uso del método ```index_docs```. Por cada documento a procesar, ejecutará el método ```proccess_content``` el cual irá llenando el diccionario de ```InvIndexKey```:```InvIndexValue``` que tiene el objeto principal, haciendo uso de un stemmer y de las stop words que este brinde. 

A la hora de añadir un nuevo objeto al diccionario calculamos si el peso futuro de nuestro objeto sobrepasa los límites dados de memoria total del sistema. En caso sí lo sobrepase, mandamos el diccionario actual a memoria secundaria haciendo uso de JSON, para luego vaciarlo y seguir con el proceso, creando dentro del directorio actual a una serie de bloques ```block_n.json```.

Finalmente, cuando ya hallamos mandado a memoria secundaria a todos los bloques necesarios para representar los tokens de los documentos actuales, realizamos un merge de los bloques usando el método ```merge_and_save_blocks```, el cual extraerá los bloques iniciales uno a uno para no sobrepasar el límite de memoria e irá llenando un nuevo diccionario ordenado, creando un nuevo bloque final ```merged_block_n.json``` antes de sobrepasar el límite de memoria, para seguir después con el proceso.

![spimi](images/spimi.png)

## Ejecución óptima de consultas aplicando Similitud de Coseno
A la hora de realizar queries, primero tokenizamos todos los elementos de la misma. Después, calculamos los valores necesarios para un correcto retrieval y aplicar la similitud de cosenos. Finalmente, buscamos entre los ```merged_block_n.json``` para calcular los documentos más similares a mostrar. 

## Construcción del índice invertido en PostgreSQL
Primero creamos una tabla donde agregamos las filas del archivo 'spotify.csv', luego para poder crear el índice invertido en PostgreSQL agregamos una columna donde combinaremos todos los atributos en formato texto.

```sql
CREATE INDEX combined_text_idx ON songslist USING gin(to_tsvector('english', combined_text));
```
Este código crea un índice de texto completo donde utilizamos dos funciones principales:

- ```to_tsvector('english',combined_text)```: Convierte combined_text en un vector de términos de búsqueda de texto completo. ```language='english'``` es el parámetro que determina en qué lenguaje se procesan las palabras y sus stopwords.
- ```USING GIN```: Estamos especificando a Postgres que usaremos un índice GIN (Generalized Inverted Index). GIN está optimizado para manejar vectores de texto completo

¿Cómo Funciona?
- Indexación: En un índice GIN, PostgreSQL mapea cada término único (como las palabras en un texto) a los identificadores de las filas en las que aparece.
- Estructura Invertida: Lo que hace que un índice GIN sea "invertido" es que, en lugar de listar los términos en orden y luego buscar las filas correspondientes (como en un índice tradicional), lista los términos y luego apunta directamente a las filas donde estos términos aparecen.

# Backend: Índice Multidimensional
## Técnica de transformación de audio a vector característico usada

Para poder manejar los audios .wav de una mejor manera, hemos decidido convertirlos a vectores característicos. En primer lugar, se ha calculado los Mel-frequency cepstral coefficients (MFCCs) para manejar las características más importantes del audio, ignorando a factores externos como puede ser el ruido de fondo o el volumen del audio, así asemejándose a cómo un humano escucha con normalidad. 

```python
def get_normalized_mfcc(audio_file: str) -> ndarray:
    y, _ = librosa.load(audio_file, sr=None)
    mfcc = librosa.feature.mfcc(y=y)

    return normalize_mfcc(mfcc)
```

Después, aplicamos una normalización a cada uno de los arrays que representan los MFCCs, así teniendo en cada uno un total de 80 elementos. Esto asegura que nuestras librerías puedan trabajar con ellos, pues necesitan tener las mismas dimensiones cada uno de los elementos.

```python
def normalize_mfcc(mfcc: ndarray, num_features: int = 20) -> ndarray:
    num_features = min(mfcc.shape[1], num_features)

    normalized_features = []

    for i in range(num_features):
        coef_features = mfcc[:, i]
        min_val = np.min(coef_features)
        max_val = np.max(coef_features)
        mean_val = np.mean(coef_features)
        std_val = np.std(coef_features)

        normalized_features.extend([min_val, max_val, mean_val, std_val])

    return np.array(normalized_features)
```

![mfccs](images/librosa-mfcc.png)

## Técnica de indexación de las librerías utilizadas
### Rtree
El ```rtree``` es una estructura de datos similar al BTree, pero para más de una dimensión. Es usado ampliamente por su eficiencia en búsquedas espaciales, manejo de datos multidimensionales y escalamiento con gran cantidad de datos.

```python
prop = rtree_index.Property()
prop.dimension = collection.shape[1]
index = rtree_index.Index('rtree_index', properties=prop, interleaved=False)
```

**Pasos de construcción:**
1. Se empieza con una raíz vacía.
2. Se agrega punto por punto al árbol.
3. Eliges un lugar donde haya espacio, si no lo hay creas otro nodo.
4. La lógica del árbol colocará los puntos en MBRs que probablemente estén dentro de otros MBRs y así sucesivamente.

![rtree_build1](images/rtree_build1.png)
![rtree_build2](images/rtree_build2.png)

### Faiss
Usamos el ```Inverted Index File Flat``` el cual consiste en agrupar en n clusters los vectores característicos mediante los diagramas de Voronoi.

Parámetros:
- Quantizer: Objeto que divide el espacio en regiones más pequeñas.
- d: Dimensión de los vectores.
- nlists: Cantidad de clusters.
- metric: Metrica usada para la distancia.
- nprobe: Cantidad extra de clusters en los que buscar en una consulta.

```python
dimension = vectors.shape[1]
nlist = n
quantizer = faiss.IndexFlatIP(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
index.nprobe = nprobe
```

**Pasos de construcción:**
1. Datos: Colocar los vectores normalizados como puntos en el espacio.
2. Selección de centroides: Se eligen n centroides (parámetro ```nlist```), que son puntos, al azar o mediante el algoritmo n-means (k-means).

![faiss_step2](images/faiss_step2.png)

3. Clustering: Cada punto se asigna al centroide/cluster más cercano mediante el cálculo de la distancia.

![faiss_step3](images/faiss_step3.png)

4. Creación de listas invertidas: Por cada cluster se crea una lista invertida de los puntos que pertenecen a él.

## Búsquedas
### Sequential
#### KNN-heap
En primer lugar, se itera punto por punto de la colección y se calcula su distancia con el query vector. Después, se crea un heap con la finalidad de mantener siempre los k más cercanos. Finalmente, una vez recorrida toda la colección se ordena el heap y se retorna como una lista.

![knn_sequential_search](images/sequential_knn_search.png)

#### Por rango
En primer lugar, se itera punto por punto de la colección y se calcula su distancia con el query vector. Si la distancia de este punto es menor al radio r dado entonces se agrega al resultado final.

![sequential_range_search](images/sequential_range_search.png)

El radio para la consulta se selecciona mediante el análisis de la distribución de la data, donde a partir de un percentil (% de data que queremos hallar entorno a la query) se calcula un radio. 

El radio de búsqueda se calcula a partir del percentil escogido, reflejando el porcentaje de puntos que deseamos incluir alrededor del punto de consulta. Esto permite que el radio se ajuste a la densidad de nuestro conjunto de datos.

### Rtree
1. Descender en el árbol: Se selecciona el MBR más cercano al punto de la query y al entrar a ese MBR se repite el proceso hasta llegar a un nodo hoja.
2. Verificar hojas: Se compara la query con los puntos en la hoja y se buscan los k más cercanos.
3. Fin de la búsqueda: La búsqueda termina cuando no existan otros puntos más cercanos en otros MBRs.

![rtree_search](images/rtree_search.png)

### Faiss
1. Cluster más cercano: Elegir el cluster a menor distancia del query vector.
2. Búsqueda en el cluster más cercano: Se busca los k vecinos más cercanos dentro de la lista invertida del cluster más cercano.
3. Problema del borde: Si el query vector cerca de otros clusters pueden existir puntos más cercanos a él en esos otros clusters. Por ello, se busca en cierta cantidad de clusters vecinos además del más cercano (parámetro ```nprobe```).

![faiss_step4](images/faiss_step4.png)

## Maldición de la dimensionalidad
Es un fenómeno que ocurre cuando se analizan datos de alta dimensión que afecta a la búsqueda eficiente de los datos. A medida que aumenta la dimensionalidad la separación y volumen de los datos crece tan rápido que los puntos cercanos parecen distantes provocando que las búsquedas sean ineficientes y/o poco precisas.

![curse_of_dimensionality](images/curse_of_dimensionality.png)

## Mitigar la maldición de la dimensionalidad
- PCA: Reducción de dimensionalidad.
![mitigate_curse_of_dimensionality](images/mitigate_curse_of_dimensionality.png)
- Selección de características relevantes.
- Usar un índice para alta dimensionalidad.
![faiss_step3](images/faiss_step3.png)

# Frontend
## Manual de uso
1. Primero se debe obtener una Spotify API Key. Para esto se debe hacer la siguiente request con la información correspondiente requerida, que se saca de la web para desarrolladores de Spotify.

```zsh
curl -X POST "https://accounts.spotify.com/api/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials&client_id=your-client-id&client_secret=your-client-secret"
```

2. Luego se debe ingresar a la carpeta del backend, instalar las dependencias del `requirements.txt` y correr el siguiente comando:
```zsh
uvicorn main:app --reload
```
Este iniciará la API que se conectará con el front end.
3. Luego también instalar las dependencias del `requirements.txt` y correr el siguiente comando en la carpeta del backend del inidice multidimensional:
```zsh
uvicorn main:app --reload -p 8080
```
4.- Finalmente para iniciar la web en la que se mostrará toda la GUI, primero ubicarse en la carpeta de frontend y ejecutar:
```zsh
npm run dev
```
Finalmente dirigirse al link que aparecerá en la terminal.

## Diseño GUI

1. Cuando entramos en la app sin hacer alguna busqueda.

![gui1](./images/gui1.png)

2. Cuando se hace una busqueda textual.
   
MyIndex:
![gui2_1](./images/gui2_1.png)

Postgres:
![gui2_2](./images/gui2_2.png)

3. Cuando buscamos los 5 mas cercanos usando el indice multidimensional.

![gui3](./images/gui3.png)

# Experimentación
## Resultados experimentales
### Experimento 1
|         | MyIndex (ms)   | PostgreSQL (ms) |
|---------|----------------|-----------------|
| N=1000  |221.944         |974.134          |
| N=2000  |528.335         |2242.100         |
| N=4000  |1034.121        |4498.170         |
| N=8000  |2458.318        |9938.721         |
| N=10000 |2967.021        |11389.978        |
| N=14000 |4882.048        |18326.689        |
| N=18000 |6396.227        |25449.169        |

![experimento1](images/experimento1.png)

### Experimento 2
|         | KNN-Sequential (ms) | KNN-RTree (ms) | KNN-HighD (ms) |
|---------|---------------------|----------------|----------------|
| N=1000  | 6.3                 | 4.1            | 3.6            |
| N=2000  | 13.42               | 7.532          | 0.4            |
| N=4000  | 24.314              | 10.433         | 0.42           |
| N=8000  | 49.3                | 16.561         | 0.59           |
| N=10000 | 58.93               | 26.441         | 0.641          |
| N=12500 | 76.924              | 32.4           | 0.81           |
| N=14944 | 90.1                | 37.001         | 0.9            |

![experimento2](images/experimento2.png)

### Análisis y discusión
#### Experimento 1
Los resultados del Experimento 1 muestran una tendencia clara en la que nuestro índice personalizado, MyIndex, supera en eficiencia al de PostgreSQL en términos de tiempo de respuesta.

Este mejor rendimiento de MyIndex se atribuye a que generalidad que ofrece el índice gist de postgreSQL ya que funciona tanto para datos textuales como para multimedia. Por otro lado, el índice MyIndex está especializado para consultas textuales por lo que funciona mejor.

#### Experimento 2
Se comparan tres variantes del algoritmo KNN: Secuencial, RTree y HighD (Faiss Inverted Index File Flat). Los resultados experimentales revelan una clara ventaja del índice KNN-HighD en términos de velocidad.

Esta superioridad puede atribuirse a la eficacia con la que el índice KNN-HighD gestiona datos en alta dimensión, aprovechando técnicas de clustering y listas invertidas para optimizar la búsqueda. En contraste, el método KNN-Sequential, aunque eficaz en muestras más pequeñas, muestra un aumento significativo en el tiempo de respuesta a medida que el tamaño del conjunto de datos crece. El método RTree, si bien supera al Secuencial en eficiencia, no logra igualar la rapidez y eficacia del HighD por la maldición de la dimensionalidad.

La elección de Faiss para el índice HighD resultó ser una decisión acertada para la interfaz gráfica de la aplicación ya que es el que tiene mayor rapidez y precisión para muchos datos y con altas dimensiones.

# Bibliografía
- An introduction to inverted index. (s/f). Slideshare.net. Recuperado el 27 de noviembre de 2023, de https://es.slideshare.net/weedge/an-introduction-to-inverted-index
- Single-pass in-memory indexing. (s/f). Stanford.edu. Recuperado el 27 de noviembre de 2023, de https://nlp.stanford.edu/IR-book/html/htmledition/single-pass-in-memory-indexing-1.html
- Facebookresearch. (s. f.). Getting started. GitHub. https://github.com/facebookresearch/faiss/wiki/Getting-started
- Nearest Neighbor indexes for similarity search. (s. f.). Pinecone. https://www.pinecone.io/learn/series/faiss/vector-indexes/
- Berchtold, S., Keim, D. A., & Kriegel, H.-P. (s/f). The X-tree: An index structure for high-dimensional data. Dbvis.de. Recuperado el 27 de noviembre de 2023, de https://bib.dbvis.de/uploadedFiles/190.pdf
- Figure 1 The curse of dimensionality (A) 11 objects in one unit bin (B). (s. f.). ResearchGate. https://www.researchgate.net/figure/The-curse-of-dimensionality-a-11-objects-in-one-unit-bin-b-6-objects-in-one-unit-bin_fig1_264823819
