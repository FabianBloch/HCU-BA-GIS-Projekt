from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

db_login = f"host={os.environ.get('PG_HOST')} port={os.environ.get('PG_PORT')} dbname={os.environ.get('PG_DATABASE')} user={os.environ.get('PG_USSER')} password={os.environ.get('PG_PASSWORD')}"

db_schema = os.environ.get('PG_SCHEMA')

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False

CORS(app)

@app.route('/')
def index():
    return """<!DOCTYPE html><html>
            <head>
                <title>Straßenbaumkataster</title>
            </head>
            <body>
                <h1>RESTFUL API Straßenbaumkataster</h1>
            </body></html>"""

@app.route('/tree/<id>')
def get_tree(id):
    try:
        with psycopg2.connect(db_login) as connection:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(f"""SELECT baumid, 
                                        baumnummer, 
                                        sorte_nr, 
                                        pflanzjahr, 
                                        kronendurchmesser,
                                        stammumfang,
                                        strasse,
                                        hausnummer,
                                        ortsteil_nr,
                                        public.ST_AsGeoJSON(public.ST_Transorm(geom, 4326)) as geojson
                                FROM {db_schema}.strassenbaumkataster WHERE baumid={id};""")
            row = cursor.fetchone
            tree = {
                'type': 'FeutureCollection',
                'feutures': [
                    {
                        'type': 'Feuture',
                        'if': row['baumid'],
                        'properties': {
                            'baum_nr': row['baumnummer'],
                            'sorte_nr': row['sorte_nr'],
                            'pflanzjahr': row['pflanzjahr'],
                            'krone': row['kronendurchmesser'],
                            'strasse': row['strasse'],
                            'haus_nr': row['hausnummer'],
                            'ortsteil_nr': row['ortsteil_nr'],
                        },
                        'geometry': json.loads('geojson')
                    }
                ]
            }
            return tree
    except psycopg2.DatabaseError as error:
        return {'message': error }
    except Exception as error:
        return {'message': error }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('API_PORT'))