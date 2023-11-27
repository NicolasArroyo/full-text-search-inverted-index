import time
import psycopg2

# Datos de conexion
host = "localhost"
dbname = ""
user = ""
password = ""

langs = {
    "ar" : "arabic",
    "da" : "danish",
    "nl" : "dutch",
    "en" : "english",
    "fi" : "finnish",
    "fr" : "french",
    "de" : "german",
    "hu" : "hungarian",
    "it" : "italian",
    "no" : "norwegian",
    "pt" : "portuguese",
    "ro" : "romanian",
    "ru" : "russian",
    "es" : "spanish",
    "sv" : "swedish",
}

def query_my_index(query : str, language : str, k : int) -> list:
    conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password)
    cursor = conn.cursor()

    sql_query = """
        SELECT *
        FROM songslist
        WHERE to_tsvector(%s, combined_text)
        @@ plainto_tsquery(%s, %s)
        LIMIT %s
    """

    start_time = time.time()
    cursor.execute(sql_query, (langs[language], langs[language], query, k,))

    result = []
    for row in cursor.fetchall():
        track_id = row[0]
        result.append(track_id)
    elapsed_time = time.time() - start_time
    cursor.close()
    conn.close()

    return [result, elapsed_time]
