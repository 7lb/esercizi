#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pylint: disable = missing-docstring, import-error, redefined-outer-name

from datetime import datetime
from flask import Flask, jsonify, request, make_response, url_for
from flask.ext.httpauth import HTTPBasicAuth
app = Flask(__name__)
auth = HTTPBasicAuth()

# Backend
collection = {}

users = {
    "admin": "admin",
    "pippo": "pluto",
    "foo": "bar",
    "paolo": "i<3francesca",
}

@auth.get_password
def get_password(username):
    password = users.get(username)
    if password:
        return password
    return


@auth.error_handler
def unauthorized():
    return make_response(
        jsonify({
            "message": "Unauthorized access"
        }), 401
    )


@app.errorhandler(405)
def method_not_allowed():
    return make_response(
        jsonify({"message": "Method not allowed"}), 405)


@app.errorhandler(500)
def internal_server_error():
    return make_response(
        jsonify({"message": "Internal server error"}), 500)


def check_user(user):
    if user != auth.username() and user is not None:
        return unauthorized()

# Aggiunta di un numero di passi per la giornata in corso
@app.route("/v1/days", methods=["POST"])
@app.route("/v2/users/<user>/days", methods=["POST"])
@auth.login_required
def add_day(user=None):
    check_user(user)

    if not request.json or not "steps" in request.json:
        return make_response(
            jsonify({"message": "Bad Request: missing step number"}), 400
        )

    date = datetime.now().isoformat()[:10]
    day = {
        "date": date,
        "steps": request.json["steps"]
    }

    if day_present(day, collection):
        return make_response(
            jsonify({"message": "Bad Request: item already present"}), 400
        )

    add(day, collection)
    response = {
        "message": "Created",
        "day": day,
    }

    if user is not None:
        response["uri"] = url_for(
            "get_day", date=date, user=user, _external=True)
    else:
        response["uri"] = url_for("get_day", date=date, _external=True)
    return make_response(jsonify(response), 201)


# Modifica del numero di passi per la giornata in corso
@app.route("/v1/days", methods=["PUT"])
@app.route("/v2/users/<user>/days", methods=["PUT"])
@auth.login_required
def change_day(user=None):
    check_user(user)

    if not request.json or not "steps" in request.json:
        make_response(
            jsonify({"message": "Bad Request: missing step number"}), 400
        )

    date = datetime.now().isoformat()[:10]
    day = {
        "date": date,
        "steps": request.json["steps"]
    }

    if not day_present(day, collection):
        return make_response(
            jsonify({"message": "Not Found"}), 404
        )

    # Siccome remove e add usano la data come chiave il seguente codice
    # funziona perché i corpi del giorno rimosso e aggiunto differiscono
    remove(day, collection)
    add(day, collection)
    response = {
        "message": "OK",
        "day": day,
    }

    if user is not None:
        response["uri"] = url_for(
                "get_day", date=date, user=user, _external=True)
    else:
        response["uri"] = url_for("get_day", date=date, _external=True)
    return make_response(jsonify(response), 200)


# Recupero del numero di passi per una data arbitraria
@app.route("/v1/days/<date>", methods=["GET"])
@app.route("/v2/users/<user>/days/<date>", methods=["GET"])
@auth.login_required
def get_day(date, user=None):
    check_user(user)

    day = get_date(date, collection)
    if not day:
        return make_response(
            jsonify({
                "message": "Not Found"
            }), 404
        )

    return make_response(
        jsonify({
            "message": "OK",
            "day": day
        }), 200
    )


# Rimozione dei passi registrati per una data arbitraria
@app.route("/v1/days/<date>", methods=["DELETE"])
@app.route("/v2/users/<user>/days/<date>", methods=["DELETE"])
@auth.login_required
def remove_day(date, user=None):
    check_user(user)

    day = get_date(date, collection)
    if not day:
        return make_response(
            jsonify({
                "message": "Not Found"
            }), 404
        )

    remove(day, collection)
    return make_response(
        jsonify({
            "message": "OK",
            "day" : day
        }), 200
    )


def day_present(day, collection):
    """
    Controlla se il giorno è presente nella collection
    """
    days = collection.get(auth.username())

    if days is None:
        return None

    return days.get(day["date"])


def add(day, collection):
    """
    Aggiunge un giorno alla collection
    """
    days = collection.get(auth.username())

    if days is None:
        days = {}

    days[day["date"]] = day
    collection[auth.username()] = days


def remove(day, collection):
    """
    Rimuove un giorno dalla collection
    """
    days = collection.get(auth.username())

    if days is None:
        return None

    return days.pop(day["date"], None)


def get_date(date, collection):
    """
    Ritorna un giorno dalla collection
    """
    days = collection.get(auth.username())

    if days is None:
        return None

    return days.get(date)


if __name__ == "__main__":
    app.run()
