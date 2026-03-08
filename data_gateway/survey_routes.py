# data_gateway/survey_routes.py

from flask import Blueprint, request, jsonify, Response
import os
import requests
import jwt

# 1. Create a Blueprint object. 'survey_api' is the name of this blueprint.
survey_bp = Blueprint('survey_api', __name__)

# 2. Define configuration specific to this blueprint.
SURVEY_SERVICE_BASE_URL = "http://survey_service:8000"
PUBLIC_SUBPATHS = ['/initial_submit']

# 3. Define a generic forwarding route to handle all requests under this blueprint.
@survey_bp.route('/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def forward(subpath):
    """
    This function handles all requests registered under this blueprint's prefix.
    """
    user_id = None
    request_subpath = f"/{subpath}"

    # 4. Security Check: Determine if the requested subpath is in the public list.
    if request_subpath not in PUBLIC_SUBPATHS:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"message": "Authentication Token is missing or has an incorrect format"}), 401

        token = auth_header.split(" ")[1]
        try:
            # Decode the JWT using the secret key from environment variables.
            secret_key = os.getenv("SECRET_KEY")
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid"}), 401

    # 5. Prepare the payload for forwarding.
    original_payload = request.get_json(silent=True) or {}
    if user_id:
        original_payload['userId'] = str(user_id)

    print(f"--- Data Gateway forwarding the following data to Survey Service ---")
    print(original_payload)
    print(f"------------------------------------------------------------------")

    # 6. Construct the full internal URL and forward the request.
    forward_url = f"{SURVEY_SERVICE_BASE_URL}/{subpath}"
    try:
        resp = requests.request(
            method=request.method,
            url=forward_url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            json=original_payload,
            timeout=10.0
        )
        return Response(resp.content, resp.status_code, resp.headers.items())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"The Survey Service is currently unavailable: {e}"}), 503