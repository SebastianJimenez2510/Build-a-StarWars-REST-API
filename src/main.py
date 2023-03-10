"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Characters, Favorite_planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#Planetas#
@app.route('/planets', methods=['GET']) #Get all planets 
def get_planets():
     planets = Planets.query.filter().all()
     result = list(map(lambda planet: planet.serialize(), planets))
     #print(planets)
     return jsonify(result), 200

@app.route('/planets/<int:planet_id>', methods=['GET']) #Get planets by Id
def get_planet_by_id(planet_id):
    planet = Planets.query.get(planet_id)
    if planet == None:
        return jsonify(f"Planet {planet_id} does not exist"), 400
    return jsonify(planet.serialize()), 200

#-------------------------------------------


#Personajes#
@app.route("/characters", methods=["GET"])
def get_character():
    characters = Characters.query.all()
    result = list(map(lambda char: char.serialize(), characters))
    return jsonify(result), 200


@app.route("/characters/<int:char_id>", methods=["GET"])
def get_character_by_id(char_id):
    character = Characters.query.get(char_id)
    if character == None:
        raise APIException("Character does not exit", status_code=400)
    else:
        return jsonify(character.serialize()), 200

#-------------------------------------------


#Users#
@app.route('/users', methods=['GET']) #Get all users
def get_users():
     users = User.query.filter().all()
     result = list(map(lambda user: user.serialize(), users))
     return jsonify(result.serialize), 200

@app.route('/users/<int:user_id>', methods=['GET']) #Get users by id
    def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if user == None:
        raise APIException("User does not exist", status_code=400)
    else:
        return jsonify(user.serialize), 200



#-------------------------------------------

#Personajes#
@app.route("/characters", methods=["POST"])
def add_character():
    body = request.get_json()
    add_char = Characters(character_name=body["character_name"], 
        skin_color=body["skin_color"], 
        eye_color=body["eye_color"])
    db.session.add(add_char)
    db.session.commit()
    return jsonify("El planeta fue a??adido correctamente"), 200 

    @app.route('/addfavoritecharacter/<int:id>/usuario/<int:id_usuario>', methods=['POST'])
def add_favorite_character(id, id_usuario):
    character_query = Characters.query.get(id)
    usuario_query = Usuario.query.get(id_usuario)
    favorite_character = Favorite_characters(
        character_name=character_query.character_name, user_id=usuario_query.id)
    db.session.add(favorite_character)
    db.session.commit()

    return jsonify("El personaje fue a??adido de forma correcta"), 200

#----------------------------------

#Planetas#
@app.route('/planets', methods=['POST']) #Add new planet
def add_planets():
    body = request.get_json()
    #print(body)
    add_planet = Planets(planet_name=body["planet_name"], terrain=body["terrain"])
    db.session.add(add_planet)
    db.session.commit()
    return jsonify("El Planeta fue a??adido correctamente"), 200


@app.route('/addfavoriteplanet/<int:planet_id>/usuario/<int:user_id>', methods=['POST'])
def add_favorite_planet(planet_id,user_id):
    planet_q = Planets.query.get(planet_id)
    user_q = User.query.get(user_id)
    add_fav_planet = Favorite_planets(user_id=user_q.id, planet_id=planet_q.id, planet_name=planet_q.planet_name)
    db.session.add(add_fav_planet)
    db.session.commit()
    return jsonify("El planeta fue a??adido correctamente"), 200


#----------------------------------

#Deletes#
@app.route('/deletefavoriteplanet/<int:id>/usuario/<int:user_id>', methods=['DELETE'])
def delete_favorite_planet(id, user_id):
    delete_planet= Favorite_planets.query.filter_by(id=id, user_id=user_id).first()
    print(delete_planet)
    if delete_planet is None:
        return jsonify("No existe el planeta favorito")
    db.session.delete(delete_planet)
    db.session.commit()
    res = {
        "message": "El planeta favorito fue eliminado exitosamente"
    }
    return res,200

@app.route('/deletefavoritecharacter/<int:id>/usuario/<int:user_id>', methods=['DELETE'])
def delete_favorite_character(id, user_id):
    delete_character= Favorite_characters.query.filter_by(id=id, user_id=user_id).first()
    print(delete_character)
    if delete_character is None:
        return jsonify("No existe el personaje favorito")
    db.session.delete(delete_character)
    db.session.commit()
    res = {
        "message": "El personaje favorito fue eliminado exitosamente"
    }
    return res,200

#----------------------------------

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
