from flask import Flask, request, jsonify
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash
import traceback

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "mysql"),
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        database=os.environ['MYSQL_DATABASE']
    )

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if not username:
        return jsonify({"error": "Username cannot be empty"}), 400

    hashed_password = generate_password_hash(password)

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        db.commit()
    except mysql.connector.Error as err:
        print(f"MySQL Error {err.errno}: {err.msg}")
        traceback.print_exc()

        if err.errno == 1062:  # Duplicate entry
            return jsonify({"error": "Username already exists"}), 400
        return jsonify({"error": f"Database error: {err.msg}"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()

    return '', 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    try:
        db = get_db_connection()
        cursor = db.cursor(buffered=True)
        cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
        record = cursor.fetchone()
    except Exception as e:
        print(f"Login DB error: {e}")
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()

    if record and check_password_hash(record[0], password):
        return '', 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
