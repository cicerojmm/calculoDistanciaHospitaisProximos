
import numpy as np
import pandas as pd
import math
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Constantes
endereco_idoso = (0, 0)
raio_considerado = 40
quantidade_minima_leitos = 3
estado = 'GO'
quantidade_retorno = 10


def calcular_distancia(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def definir_mais_proximos(row):
    distancia = calcular_distancia(endereco_idoso, (row['lat'], row['long']))
    return distancia < raio_considerado


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/hospitais/lista/lat/<lat>/long/<long>', methods=['get'])
def get_hospitais_proximos(lat, long):
    global endereco_idoso
    endereco_idoso = (float(lat), float(long))
    df = pd.read_csv('data/ubs_funcionamento.csv')
    df_ubs_estado = df#df[df['uf'] == estado]
    filtro = df_ubs_estado.apply(definir_mais_proximos, axis=1)
    df_proximos = df_ubs_estado[filtro]
    df_proximos_filtro =  df_proximos[df_proximos['qtd_leitos'] >= quantidade_minima_leitos]
    df_retorno = df_proximos_filtro[['gid', 'lat', 'long', 'no_fantasia', 'nu_telefone', 'qtd_leitos']]
    df_retorno = df_retorno.sort_values(by='qtd_leitos', ascending=False)[:quantidade_retorno]

    result_list = []
    for index, row in df_retorno.iterrows():
        result_list.append(dict(row))

    return jsonify(result_list)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)