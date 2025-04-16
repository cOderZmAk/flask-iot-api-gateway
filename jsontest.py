from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from datetime import timedelta, datetime

app = Flask(__name__)

# Configure the Flask app for JWT
app.config["JWT_SECRET_KEY"] = "your_secret_key_here"  # Change this secret in production!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# In-memory database for sensor data
sensor_data_db = []

# Dummy user store for demonstration purposes
USER_DATA = {
    "admin": "password123"
}

@app.route('/login', methods=['POST'])
def login():
    """
    Login endpoint.
    Request should include JSON data with 'username' and 'password'.
    Returns a JWT access token upon successful authentication.
    """
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    # Verify the user credentials
    if username not in USER_DATA or USER_DATA[username] != password:
        return jsonify({"msg": "Bad username or password"}), 401

    # Create and return a new access token
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@app.route('/sensor', methods=['POST'])
@jwt_required()
def add_sensor_data():
    """
    Protected endpoint to receive sensor data.
    Expected JSON payload:
      {
          "sensor_id": "sensor_1",
          "value": <numeric_value>,
          "timestamp": "2023-01-01T10:00:00" (optional)
      }
    If the timestamp is not provided, the current UTC time is used.
    """
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400

    sensor_id = data.get('sensor_id')
    value = data.get('value')
    timestamp = data.get('timestamp', datetime.utcnow().isoformat())

    # Basic validation to ensure required fields are provided
    if sensor_id is None or value is None:
        return jsonify({"msg": "Missing sensor_id or value"}), 400

    try:
        # Ensure the value is numeric
        numeric_value = float(value)
    except (ValueError, TypeError):
        return jsonify({"msg": "Value must be numeric"}), 400

    # Create a record for the sensor data including the submitting user
    sensor_entry = {
        "sensor_id": sensor_id,
        "value": numeric_value,
        "timestamp": timestamp,
        "submitted_by": get_jwt_identity()
    }
    sensor_data_db.append(sensor_entry)

    return jsonify({"msg": "Sensor data added successfully", "data": sensor_entry}), 201

@app.route('/data', methods=['GET'])
@jwt_required()
def get_sensor_data():
    """
    Protected endpoint to retrieve all sensor data.
    Returns a list of sensor records.
    """
    return jsonify(sensor_data_db), 200

if __name__ == '__main__':
    app.run(debug=True)
