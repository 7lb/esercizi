#! /usr/bin/env python
#-*- coding: utf-8 -*-

# pylint: disable = missing-docstring, import-error, redefined-outer-name

from datetime import datetime
from flask import Flask, jsonify, request, make_response, url_for
from flask.ext.httpauth import HTTPBasicAuth
app = Flask(__name__)
auth = HTTPBasicAuth()

# Backend
days = {}

users = {
    "admin": "admin",
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


# Aggiunta di un numero di passi per la giornata in corso
@app.route("/v1/days", methods=["POST"])
@auth.login_required
def add_day():
    if not request.json or not "steps" in request.json:
        return make_response(
            jsonify({"message": "Bad Request: missing step number"}), 400
        )

    date = datetime.now().isoformat()[:10]
    day = {
        "date": date,
        "steps": request.json["steps"]
    }

    if day_present(day, days):
        return make_response(
            jsonify({"message": "Bad Request: item already present"}), 400
        )

    add(day, days)
    return make_response(
        jsonify({
            "message": "Created",
            "day": day,
            "uri": url_for("get_day", date=date, _external=True)
        }), 201
    )


# Modifica del numero di passi per la giornata in corso
@app.route("/v1/days", methods=["PUT"])
@auth.login_required
def change_day():
    if not request.json or not "steps" in request.json:
        make_response(
            jsonify({"message": "Bad Request: missing step number"}), 400
        )

    date = datetime.now().isoformat()[:10]
    day = {
        "date": date,
        "steps": request.json["steps"]
    }

    if not day_present(day, days):
        return make_response(
            jsonify({"message": "Not Found"}), 404
        )

    # Siccome remove e add usano la data come chiave il seguente codice
    # funziona perché i corpi del giorno rimosso e aggiunto differiscono
    remove(day, days)
    add(day, days)
    return make_response(
        jsonify({
            "message": "OK",
            "day": day,
            "uri": url_for("get_day", date=date, _external=True)
        }), 200
    )


# Recupero del numero di passi per una data arbitraria
@app.route("/v1/days/<date>", methods=["GET"])
@auth.login_required
def get_day(date):
    day = days.get(date)
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
@auth.login_required
def remove_day(date):
    day = days.get(date)
    if not day:
        return make_response(
            jsonify({
                "message": "Not Found"
            }), 404
        )

    remove(day, days)
    return make_response(
        jsonify({
            "message": "OK",
            "day" : day
        }), 200
    )

def day_present(day, days):
    """
    Controlla se il giorno è presente nella collection
    """
    return days.get(day["date"])


def add(day, days):
    """
    Aggiunge un giorno alla collection
    """
    days[day["date"]] = day


def remove(day, days):
    """
    Rimuove un giorno dalla collection
    """
    return days.pop(day["date"], None)

if __name__ == "__main__":
    app.run()
