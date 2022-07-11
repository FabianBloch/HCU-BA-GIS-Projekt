from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv() # Erforderlich zum Laden der zuvor definierten Umgebungsvariablen

db_login = f"""host={os.environ.get('PG_HOST')} 
                port={os.environ.get('PG_PORT')} 
                dbname={os.environ.get('PG_DATABASE')} 
                user={os.environ.get('PG_USER')} 
                password={os.environ.get('PG_PASSWORD')}"""

db_schema = os.environ.get('PG_SCHEMA')

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False

CORS(app) # Script muss nicht auf demselben Server laufen wie API

@app.route('/')
def index():
    return """<!DOCTPYE html><html><head><title>Straßenbaumkataster</title></head>
            <body><h1>RESTful API Straßenbaumkataster</h1></body></html>"""

@app.route('/tree/<id>')
def get_tree(id):
    try:
        with psycopg2.connect(db_login) as connection:
            cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
            cursor.execute(f"""SELECT baumid, baumnummer, sorte_nr, pflanzjahr, 
                           kronendurchmesser, stammumfang, strasse, hausnummer, 
                           ortsteil_nr, public.ST_AsGeoJSON(public.ST_Transform(geom,4326)) as geojson
                           FROM {db_schema}.strassenbaumkataster 
                           WHERE baumid = {id};""")
            
            row = cursor.fetchone()
            tree = {
                'type':'FeatureCollection',
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
        return {'message': error}
    except Exception as error:
        return {'message': error}


@app.route('/trees')
def get_trees():
    try:
        with psycopg2.connect(db_login) as connection:
            cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
            cursor.execute(f"""SELECT baumid, baumnummer, sorte_nr, pflanzjahr, 
                           kronendurchmesser, stammumfang, strasse, hausnummer, 
                           ortsteil_nr, public.ST_AsGeoJSON(public.ST_Transform(geom,4326)) as geojson
                           FROM {db_schema}.strassenbaumkataster LIMIT 5;""")
            
            rows = cursor.fetchall()
            
            feature_collection = {
                'type':'FeatureCollection'
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
            
            feature_collection.update({'features':features})
                
            
            return jsonify(feature_collection)
        
    except psycopg2.DatabaseError as error:
        return {'message': error}
    except Exception as error:
        return {'message': error}
    
    
@app.route('/create', methods=['POST'])
def create_tree():
    content = request.get_json()
    #print(content)
    #return{'message': 'Datensatz eingefügt'}
    
    try:
        with psycopg2.connect(db_login) as connection:
            cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
            query = f'INSERT INTO {db_schema}.strassenbaumkataster(baumid, baumnummer, sorte_nr, pflanzjahr, kronendurchmesser, stammumfang, strasse, hausnummer, ortsteil_nr, geom) VALUES(%(id)s, %(baum_nr)s, %(sorte_nr)s, %(pflanzjahr)s, %(krone)s, %(stamm)s, %(strasse)s, %(haus_nr)s, %(ortsteil_nr)s, ST_Multi(ST_Transform(ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s),4326),25832)));'
            cursor.execute(query, content)
            connection.commit()
            return{'message': 'Datensatz eingefügt'}
        
    except psycopg2.DatabaseError as error:
        return {'message': error}
    except Exception as error:
        return {'message': error}


@app.route('/update', methods=['PUT'])
def update_tree():
    content = request.get_json()
    #print(content)
    #return{'message': 'Datensatz eingefügt'}
    
    try:
        with psycopg2.connect(db_login) as connection:
            cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
            query = f'UPDATE {db_schema}.strassenbaumkataster SET baumnummer = %(baum_nr)s, sorte_nr = %(sorte_nr)s, pflanzjahr = %(pflanzjahr)s, kronendurchmesser = %(krone)s, stammumfang = %(stamm)s, strasse = %(strasse)s, hausnummer = %(haus_nr)s, ortsteil_nr = %(ortsteil_nr)s, geom = ST_Multi(ST_Transform(ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s),4326),25832)) WHERE baumid = %(id)s;'
            cursor.execute(query, content)
            connection.commit()
            return{'message': 'Datensatz geändert'}
        
    except psycopg2.DatabaseError as error:
        return {'message': error}
    except Exception as error:
        return {'message': error}


@app.route('/remove', methods=['DELETE'])
def remove_tree():
    content = request.get_json()
    #print(content)
    #return{'message': 'Datensatz eingefügt'}
    
    try:
        with psycopg2.connect(db_login) as connection:
            cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
            query = f'DELETE FROM {db_schema}.strassenbaumkataster WHERE baumid = %(id)s;'
            cursor.execute(query, content)
            connection.commit()
            return{'message': 'Datensatz gelöscht'}
        

    except psycopg2.DatabaseError as error:
        return {'message': error}
    except Exception as error:
        return {'message': error}

        

if __name__=='__main__':
    app.run(host='0.0.0.0', port=os.environ.get('API_PORT'))
    
    # REST client bei VS Code installieren
    