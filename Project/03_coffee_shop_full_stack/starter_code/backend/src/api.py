import os
from tkinter.messagebox import NO
from urllib import response
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

def get_success_response_template():
    return {
        'success': True
    }

def get_formatted_short_drinks(drinks):
    return [drink.short() for drink in drinks]

def get_formatted_long_drinks(drinks):
    return [drink.long() for drink in drinks]

# ROUTES
'''
@Done implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = get_formatted_short_drinks(drinks)
    if len(formatted_drinks) == 0:
        abort(404)
    response = get_success_response_template()
    response["drinks"] = formatted_drinks
    return jsonify(response)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = get_formatted_long_drinks(drinks)
    if len(formatted_drinks) == 0:
        abort(404)
    response = get_success_response_template()
    response["drinks"] = formatted_drinks
    return jsonify(response)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    request_body = request.get_json()

    if not ('title' in request_body and 'recipe' in request_body):
        abort(400)
    title = request_body.get("title")
    recipe = json.dumps(request_body.get("recipe"))
    try:
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()
        drinks = []
        drinks.append(new_drink)
        
        response = get_success_response_template()
        response['drinks'] = get_formatted_long_drinks(drinks)[0]
        return jsonify(response)

    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    drink_to_update = Drink.query.get(drink_id).one_or_none()
    if drink_to_update is None:
        abort(404)
    try:
        request_body = request.get_json()
        drink_to_update.title = request_body.get("title")
        drink_to_update.recipe = json.dumps(request_body.get("recipe"))
        drink_to_update.update()
        drinks = []
        drinks.append(drink_to_update)
        response = get_success_response_template()
        response['drinks'] = get_formatted_long_drinks(drinks)[0]
        return jsonify(response)

    except:
        abort(422)



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload,drink_id):
    drink_to_delete = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink_to_delete is None:
        abort(404)
    try:
        drink_to_delete.delete()
        response = get_success_response_template()
        response['delete'] = drink_to_delete.id
        return jsonify(response)

    except Exception:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(401)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
        }), 401