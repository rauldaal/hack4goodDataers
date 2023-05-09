from flask import Flask, request
import sqlalchemy

app = Flask(__name__)

DATA = {
    '8480000476203':{
        'marca': 'Bosque Verde',
        'nombre': 'Pañuelos Extrasuave'
    },
    '5600854627832':{
        'marca': 'Prozis',
        'nombre': 'Creatina Monohidratada'
    }

}

@app.route('/hello', methods=['POST'])
def call():
    # Conexión de sqlalchemy a la bbdd
    # Buscar información del producto
    # Devolver en formato json
    id = request.get_json()
    
    return DATA[id]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
