from flask import Flask, request, make_response
from flask_cors import CORS

from decouple import config
import logging
import requests
from typing import Dict

from nli_python import decode_point, encode_point

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

HERE_API_KEY = config('HERE_API_KEY', cast=str)

# Logging
logFormatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger(__name__)

fileHandler = logging.FileHandler("./logs/nli.log")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def get_raw_geolocation_str(address_line, city, state_prov, zip_code, country):
    """
    Normalized method for normalizing raw address
    """
    return f'{address_line}, {city}, {state_prov} {zip_code}, {country}'


def json_response(data='', status: int = 200, headers: Dict = None):
    headers = headers or {}
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
    return make_response(data, status, headers)


@app.route('/api/encode-point/', methods=['POST'])
def encode_point_view():
    if request.method == 'POST':
        try:
            encoded_point = encode_point(
                latitude=float(request.json.get("latitude")),
                longitude=float(request.json.get("longitude")),
                elevation=int(request.json.get("elevation")),
                elevation_type=request.json.get("elevation_type")
            )
            return json_response(data={"encoded_point": encoded_point}, status=200)
        except Exception:
            logger.error("failed to encode point", exc_info=True)
            return json_response(data={"error": "unable to parse point"}, status=404)

    return json_response(data={'error': f'Request type {request.method} not accepted'}, status=405)


@app.route('/api/encode-address/', methods=['POST'])
def encode_address_view():
    if request.method == 'POST':
        try:
            search_str = get_raw_geolocation_str(   
                address_line=request.json.get("address_line"),
                city=request.json.get("city"),
                state_prov=request.json.get("state_prov"),
                zip_code=request.json.get("zip_code"),
                country=request.json.get("country", "US")

            )
            url = f'https://geocoder.ls.hereapi.com/6.2/geocode.json?apiKey={HERE_API_KEY}&searchtext={search_str}'
            res = requests.get(url)

            # Success
            if res.status_code == 200:    
                response_data = res.json()
                # Check for Result
                views = response_data['Response']['View']
                if len(views) == 1:
                    lat_long = views[0]['Result'][0]['Location']['DisplayPosition']
                    encoded_point = encode_point(
                        latitude=float(lat_long['Latitude']), longitude=float(lat_long['Longitude']),
                        elevation=0, elevation_type="ground_level"
                    )
                    return json_response(data={"encoded_point": encoded_point}, status=200)
            
            return json_response(data={"error": res.reason}, status=404)
        except Exception:
            logger.error("failed to encode point", exc_info=True)
            return json_response(data={"error": "unable to parse point"}, status=404)

    return json_response(data={'error': f'Request type {request.method} not accepted'}, status=405)


@app.route('/api/decode-point/', methods=['POST'])
def decode_point_view():
    if request.method == 'POST':
        try:
            latitude, longitude, elevation, elevation_type = decode_point(
                encoded_val=request.json.get("encoded_point")
            )
            return json_response(data={
                "latitude": latitude,
                "longitude": longitude,
                "elevation": elevation,
                "elevation_type": elevation_type
            }, status=200)
        except Exception:
            logger.error("failed to encode point", exc_info=True)
            return json_response(data={"error": "unable to parse point"}, status=404)
    
    return json_response(data={'error': f'Request type {request.method} not accepted'}, status=405)


@app.route('/api/decode-address/', methods=['POST'])
def decode_address_view():
    if request.method == 'POST':
        try:
            latitude, longitude, elevation, elevation_type = decode_point(
                encoded_val=request.json.get("encoded_point")
            )
            payload = {
                "latitude": latitude,
                "longitude": longitude,
                "elevation": elevation,
                "elevation_type": elevation_type
            }
            url = f'https://discover.search.hereapi.com/v1/revgeocode?apiKey={HERE_API_KEY}&at=39.04886,-94.48405&limit=5'
            res = requests.get(url)

            # Success
            if res.status_code == 200:
                items = res.json()['items']
                if len(items) > 0:
                    payload.update({"place": items[0]['address']})

            return json_response(data=payload, status=200)
        except Exception:
            logger.error("failed to encode point", exc_info=True)
            return json_response(data={"error": "unable to parse point"}, status=404)
    
    return json_response(data={'error': f'Request type {request.method} not accepted'}, status=405)


if __name__ == "__main__":
    app.run(
        host=config("API_HOST", cast=str, default="0.0.0.0"),
        port=config("API_PORT", cast=int, default=80),
        debug=config("DEBUG", cast=bool, default=True)
    )
