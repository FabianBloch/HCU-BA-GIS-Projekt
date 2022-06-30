from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# pip install -U Flask
# pip install -U Flask-Cors
# pip install -U psycopg2
# pip install -U python-dotenv

# https://de.wikipedia.org/wiki/Cross-Origin_Resource_Sharing

# http://localhost:8085/tree/100005870

load_dotenv()  # Erforderlich zum Laden der zuvor definierten Umgebungsvariablen.

db_login = f"""host={os.environ.get('PG_HOST')} port={os.environ.get('PG_PORT')} 
               dbname={os.environ.get('PG_DATABASE')} user={os.environ.get('PG_USER')} 
               password={os.environ.get('PG_PASSWORD')}"""
db_schema = os.environ.get('PG_SCHEMA')
print(f" * DB-Schema: {db_schema}")

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False

CORS(app)

@app.route('/')
def index():
    return """<!DOCTYPE html><html><title>Straßenbaumkataster</title></head>
            <body><h1>RESTful API Straßenbaumkataster</h1></body></html>"""

@app.route('/tree/<id>')
def get_tree(id):
    try:
        with psycopg2.connect(db_login) as connection:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            SQL = f"""SELECT baumid, baumnummer, sorte_nr, pflanzjahr,
                             kronendurchmesser, stammumfang,
                             strasse, hausnummer, ortsteil_nr,
                             public.ST_AsGeoJSON(public.ST_Transform(geom, 4326)) as geojson
                      FROM {db_schema}.strassenbaumkataster WHERE baumid={id};"""
            print(SQL)
            cursor.execute(SQL)
            row = cursor.fetchone()
            tree = {
                'type': 'FeatureCollection',
                'features': [
                    {
                        'type': 'Feature',
                        'id': row['baumid'],
                        'properties': {
                            'baum_nr': row['baumnummer'],
                            'sorte_nr': row['sorte_nr'],
                            'pflanzjahr': row['pflanzjahr'],
                            'krone': row['kronendurchmesser'],
                            'stamm': row['stammumfang'],
                            'strasse': row['strasse'],
                            'haus_nr': row['hausnummer'],
                            'ortsteil_nr': row['ortsteil_nr']
                        },
                        'geometry': json.loads(row['geojson'])
                    }
                ]
            }
            return tree
    except psycopg2.DatabaseError as error:
        return { 'message': error }
    except Exception as error:
        return { 'message': error }

@app.route('/trees')
def get_trees():
    try:
        with psycopg2.connect(db_login) as connection:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            SQL = f"""SELECT baumid, baumnummer, sorte_nr, pflanzjahr,
                             kronendurchmesser, stammumfang,
                             strasse, hausnummer, ortsteil_nr,
                             public.ST_AsGeoJSON(public.ST_Transform(geom, 4326)) as geojson
                      FROM {db_schema}.strassenbaumkataster LIMIT 5;"""
            #print(SQL)
            cursor.execute(SQL)
            rows = cursor.fetchall()

            feature_collection = {
                'type': 'FeatureCollection'
            }
            features = list()
            for row in rows:
                feature = {
                    'type': 'Feature',
                        'id': row['baumid'],
                        'properties': {
                            'baum_nr': row['baumnummer'],
                            'sorte_nr': row['sorte_nr'],
                            'pflanzjahr': row['pflanzjahr'],
                            'krone': row['kronendurchmesser'],
                            'stamm': row['stammumfang'],
                            'strasse': row['strasse'],
                            'haus_nr': row['hausnummer'],
                            'ortsteil_nr': row['ortsteil_nr']
                        },
                        'geometry': json.loads(row['geojson'])
                }
                features.append(feature)
            feature_collection.update({
                'features': features
            })
            return jsonify(feature_collection)
    except psycopg2.DatabaseError as error:
        return { 'message': error }
    except Exception as error:
        return { 'message': error }

@app.route('/create', methods=['POST'])
def create_tree():
    content = request.get_json()
    print(content)   
    try:
        with psycopg2.connect(db_login) as connection:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            #cursor.execute("INSERT INTO straßenbaumkataster VALUES(:id, :baum_nr, :sorte_nr, :pflanzjahr, :krone, :stamm, :strasse, :haus_nr, :ortsteil_nr, );", content)
            return {'message': 'Datensatz eingefügt'}
    except psycopg2.DatabaseError as error:
        return { 'message': error }
    except Exception as error:
        return { 'message': error }
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('API_PORT'))