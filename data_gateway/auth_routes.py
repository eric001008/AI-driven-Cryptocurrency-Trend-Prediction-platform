# data_gateway/auth_routes.py

from flask import Blueprint, request, Response, jsonify
import requests

"""
This script defines the authentication routes for the API Gateway.

As part of the gateway, this module does not contain any business logic

It exposes two main endpoints:
- /register: Forwards user registration requests.
- /login: Forwards user login requests.

This pattern decouples the gateway's routing function from the core
authentication logic, allowing services to be developed and scaled independently.
"""

auth_bp = Blueprint('auth_api', __name__)
LOGIN_SERVICE_URL = "http://login_service:5001"

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def forward_register():
    if request.method == 'OPTIONS':
        return Response(status=200)

    payload = request.get_json()
    try:
        #Forward to /api/register inside login_service
        response = requests.post(f"{LOGIN_SERVICE_URL}/api/register", json=payload, timeout=10.0)
        return Response(response.content, response.status_code, response.headers.items())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"The registration service is currently unavailable: {e}"}), 503

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def forward_login():
    """Responsible for forwarding login requests"""
    if request.method == 'OPTIONS':
        return Response(status=200)

    payload = request.get_json()
    try:
        # Similarly, forward the request to /api/login inside login_service
        response = requests.post(f"{LOGIN_SERVICE_URL}/api/login", json=payload, timeout=10.0)
        return Response(response.content, response.status_code, response.headers.items())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"The login service is currently unavailable: {e}"}), 503