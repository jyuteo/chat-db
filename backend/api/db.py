import uuid
from typing import Dict
from flask import Blueprint, session, jsonify, request

from db_client import MySQLDBClient

db_conn_cache: Dict[str, MySQLDBClient] = {}

db = Blueprint("db", __name__, url_prefix="/db")


@db.route("/connect", methods=["POST"])
def connect_db():
    data = request.json
    host = data.get("host")
    user = data.get("user")
    password = data.get("password")
    database = data.get("database")
    port = data.get("port", 3306)

    connection_id = session.get("connection_id")

    if not connection_id:
        connection_id = str(uuid.uuid4())
        session["connection_id"] = connection_id

    try:
        db_client = MySQLDBClient(host, user, password, database, port)
        db_conn_cache[connection_id] = db_client
        return jsonify({"message": "Database connected successfully.", "connection_id": connection_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@db.route("/execute_query", methods=["POST"])
def execute_query():
    data = request.json
    query = data.get("query")
    connection_id = session.get("connection_id")

    if not connection_id:
        return jsonify({"error": "No active database connection."}), 400

    try:
        db_client = db_conn_cache.get(connection_id, None)
        if not db_client:
            return jsonify({"error": "No active database connection."}), 400
        result = db_client.execute_query(query)
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
