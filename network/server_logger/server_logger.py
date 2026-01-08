from flask import Flask, request, jsonify
import os

app = Flask(__name__)

os.makedirs("/home/MrAG/shader_server/data", exist_ok=True)

servers_data = {}


@app.route('/')
def home():
    return "Server logger is working."


@app.route('/add_server', methods=['POST'])
def add_server():
    """
    server_data -> {
        "server_name": str,
        "max_players": int,
        "has_password": bool,
        "ip_address": str,
        "port": int,
        "players": int
    }
    """
    server_data = request.get_json()

    if not server_data:
        return jsonify({"error": "There is no server data"}), 400
    try:
        if server_data["ip_address"] in servers_data:
            return jsonify({"error": "This server already exists"}), 400
        servers_data[server_data["ip_address"]] = server_data

        return jsonify({"message": "Server added successfully"}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route('/update_server', methods=['POST'])
def update_server():
    """
    server_data -> {
        Optional["server_name"]: str,
        Optional["max_players"]: int,
        Optional["has_password"]: bool,
        "ip_address": str,
        Optional["port"]: int,
        Optional["players"]: int
    }
    """
    server_data = request.get_json()

    if not server_data:
        return jsonify({"error": "There is no server data"}), 400
    try:
        if server_data["ip_address"] in servers_data:
            servers_data[server_data["ip_address"]] |= server_data
            return jsonify({"message": "Server updated successfully"}), 201
        else:
            return jsonify({"error": "There is no such server"}), 400
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route('/delete_server', methods=['POST'])
def delete_server():
    """
    server_data -> {
        "ip_address": str
    }
    """
    server_data = request.get_json()

    if not server_data:
        return jsonify({"error": "There is no server data"}), 400
    try:
        if server_data["ip_address"] in servers_data:
            del servers_data[server_data["ip_address"]]
            return jsonify({"message": "Server deleted successfully"}), 201
        else:
            return jsonify({"error": "There is no such server"}), 400

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route('/get_servers_list', methods=['GET'])
def get_servers_list():
    try:
        return jsonify({"data": servers_data}), 200
    except Exception as error:
        return jsonify({"error": str(error), "data": []}), 500


if __name__ == "__main__":
    app.run(debug=True)
