import os
from sys import exc_info
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from flasgger import Swagger

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
Swagger(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} 
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    """
    This is the end point that fetches all available drinks
    ---
    tags:
      - Drinks
    responses:
      422:
        description: Error Unable to fetch drinks!
      200:
        description: Drinks fetched succesfully

    """

    try:
        drinks = Drink.query.all()
        if len(drinks) == 0:
            return abort(404, 'Drinks not found')
        return jsonify({
            "success": True,
            'drinks': [d.short() for d in drinks]
        }), 200
    except:
        abort(422)


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
def get_drinks_detail(jwt):
    try:
        drinks = Drink.query.all()
        if len(drinks) == 0:
            return abort(404, 'Drinks not found')
        drink_detail = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drink_detail
        }), 200
    except:
        print(exc_info())
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):
    """
    This is the end point that fetches all available drinks
    ---
    tags:
      - Drinks
    parameters:
        - in: header
          name: authorization
          description: access token
          default: serial eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfdXNlclR5cGUiOiJzY2hvb2wiLCJfZW1haWwiOiJzcGNzQGdtYWlsLmNvbSIsImlhdCI6MTY0Nzk3NTk5NiwiZXhwIjoxNjQ3OTkzOTk2fQ.c-p5B34vPn6jYgtKNOF88eGy3AwkOQXPmFhfIW9ZU8w
          required: true
        - in: body
          name: create drinks
          in: path
          type: string
          description: It enables a manager create drink
          required: true
    responses:
      422:
        description: Error Unable to create drink!
      200:
        description: Drink created succesfully
        schema:
          id: drink
          properties:
            title:
              type: string
              description: Name of drink
              default: Orange juice
            recipe:
              type: string
              description: A dictionary of the drinks recipe
              
    """
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
    except Exception:
        return abort(422)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


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
def edit_drink(jwt, drink_id):
    """
    This endpoint updates a drink 
    ---
    tags:
      - Drinks
    parameters:
        - in: header
          name: authorization
          description: access token
          default: serial eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfdXNlclR5cGUiOiJzY2hvb2wiLCJfZW1haWwiOiJzcGNzQGdtYWlsLmNvbSIsImlhdCI6MTY0Nzk3NTk5NiwiZXhwIjoxNjQ3OTkzOTk2fQ.c-p5B34vPn6jYgtKNOF88eGy3AwkOQXPmFhfIW9ZU8w
          required: true
        - in: body
          name: update drink
          in: path
          type: string
          description: It enables a manager to update a drink
          required: true
    responses:
      422:
        description: Error Unable to update drink!
      200:
        description: Drink updated succesfully
        schema:
          type: object
          properties:
            drink_id:
                type: Integer
                default: 1
            title:
              type: string
              description: Name of drink
              default: Orange juice
            recipe:
              type: string
              description: A dictionary of the drinks recipe
    """
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one()
        if drink is None:
            abort(404)
        if title:
            drink.title = title
        if recipe:
            drink.recipe = recipe if type(recipe) == str else json.dumps(recipe)
        drink.update()
        return jsonify({
        'success': True,
        'drinks': [drink.long()]
        }), 200
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
def delete_drink(jwt, drink_id):
    """
    This endpoint deletes a drink 
    ---
    tags:
      - Drinks
    parameters:
        - in: header
          name: authorization
          description: access token
          default: serial eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfdXNlclR5cGUiOiJzY2hvb2wiLCJfZW1haWwiOiJzcGNzQGdtYWlsLmNvbSIsImlhdCI6MTY0Nzk3NTk5NiwiZXhwIjoxNjQ3OTkzOTk2fQ.c-p5B34vPn6jYgtKNOF88eGy3AwkOQXPmFhfIW9ZU8w
          required: true
        - in: body
          name: delete drink
          in: path
          type: string
          description: It enables a manager to delete a drink
          required: true
    responses:
      422:
        description: Error Unable to delete drink!
      200:
        description: Drink deleted succesfully
        schema:
          type: object
          properties:
            drink_id:
                type: Integer
                default: 1
    """
    try:
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
        "success": True,
        "delete": drink_id
        }), 200
    except:
        print(exc_info())
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
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource no found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def process_AuthError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code

    return response