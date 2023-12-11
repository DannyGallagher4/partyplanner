from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    mapbox_access_token = 'pk.eyJ1Ijoia2xvZGFuIiwiYSI6ImNscG16cXFrMjAxaW8ya29pbHM3ejI4bXAifQ.vfQJewHUm3kngAd22BCjoQ'  # Replace with your Mapbox access token
    return render_template('goodindex.html', mapbox_access_token=mapbox_access_token)

if __name__ == '__main__':
    app.run(debug=True)
