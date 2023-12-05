from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Replace 'YOUR_MAPBOX_ACCESS_TOKEN' with your actual Mapbox access token
mapbox_access_token = 'pk.eyJ1Ijoia2xvZGFuIiwiYSI6ImNscG16cXFrMjAxaW8ya29pbHM3ejI4bXAifQ.vfQJewHUm3kngAd22BCjoQ'

@app.route('/')
def index():
    return render_template('mapboxinputindex.html', mapbox_access_token=mapbox_access_token)

@app.route('/get_coordinates', methods=['POST'])
def get_coordinates():
    place_name = request.form.get('place_name')
    coordinates = geocode_place(place_name)
    return jsonify(coordinates)

def geocode_place(place_name):
    geocoding_url = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{place_name}.json?access_token={mapbox_access_token}'
    response = requests.get(geocoding_url)
    data = response.json()

    if 'features' in data and data['features']:
        # Extract the coordinates from the first result
        coordinates = data['features'][0]['center']
        name = data['features'][0]['text']
        return {'lng': coordinates[0], 'lat': coordinates[1], 'name': name}
    else:
        return {'error': 'Place not found'}

if __name__ == '__main__':
    app.run(debug=True)
