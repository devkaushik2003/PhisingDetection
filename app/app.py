from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
from urllib.parse import urlparse
import re
import os  # For OS-independent paths
from flask_cors import CORS  # Enable CORS for debugging

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/predict": {"origins": "*"}})
 # Enable CORS support

# Load the saved model and Label Encoder
model_path = os.path.join('app', 'models', 'model.pkl')
encoder_path = os.path.join('app', 'models', 'label_encoder.pkl')

try:
    model = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)
except Exception as e:
    print(f"Error loading model or encoder: {e}")
    model = None
    label_encoder = None

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Preprocessing functions
def having_ip_address(url):
    match = re.search(
        r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.'
        r'([01]?\d\d?|2[0-4]\d|25[0-5])\/)|'
        r'((0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\/)' 
        r'(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}', url)
    return 1 if match else 0

def abnormal_url(url):
    hostname = urlparse(url).hostname
    hostname = str(hostname)
    match = re.search(hostname, url)
    return 1 if match else 0

def count_dot(url):
    return url.count('.')

def count_www(url):
    return url.count('www')

def count_atrate(url):
    return url.count('@')

def count_dir(url):
    return urlparse(url).path.count('/')

def shortening_service(url):
    match = re.search(r'bit\.ly|goo\.gl|tinyurl|t\.co', url)
    return 1 if match else 0

def url_length(url):
    return len(str(url))

def hostname_length(url):
    return len(urlparse(url).netloc)

def suspicious_words(url):
    match = re.search(r'PayPal|login|signin|bank|account|update|free|bonus|ebay', url)
    return 1 if match else 0

# Additional feature extraction functions
def count_percent(url):
    return url.count('%')

def count_hyphen(url):
    return url.count('-')

def count_digits(url):
    return sum(c.isdigit() for c in url)

def count_http(url):
    return url.count('http')

def count_https(url):
    return url.count('https')

def count_question(url):
    return url.count('?')

def count_equal(url):
    return url.count('=')

def count_embed_domain(url):
    return urlparse(url).path.count('//')

def fd_length(url):
    urlpath = urlparse(url).path
    try:
        return len(urlpath.split('/')[1])
    except:
        return 0

def tld_length(url):
    try:
        tld = url.split('.')[-1]
        return len(tld)
    except:
        return 0

def count_letters(url):
    return sum(c.isalpha() for c in url)

# Updated feature extraction function
def extract_features(url):
    features = []
    features.append(having_ip_address(url))
    features.append(abnormal_url(url))
    features.append(count_dot(url))
    features.append(count_www(url))
    features.append(count_atrate(url))
    features.append(count_dir(url))
    features.append(count_embed_domain(url))
    features.append(shortening_service(url))
    features.append(count_https(url))
    features.append(count_http(url))
    features.append(count_percent(url))
    features.append(count_question(url))
    features.append(count_hyphen(url))
    features.append(count_equal(url))
    features.append(url_length(url))
    features.append(hostname_length(url))
    features.append(suspicious_words(url))
    features.append(fd_length(url))
    features.append(tld_length(url))
    features.append(count_digits(url))
    features.append(count_letters(url))

    return pd.DataFrame([features], columns=[
        'use_of_ip', 'abnormal_url', 'count.', 'count-www', 'count@',
        'count_dir', 'count_embed_domian', 'short_url', 'count-https', 'count-http',
        'count%', 'count?', 'count-', 'count=', 'url_length',
        'hostname_length', 'sus_url', 'fd_length', 'tld_length',
        'count-digits', 'count-letters'
    ])

# Route for prediction
@app.route('/predict', methods=['POST'])
def predict():
    try:
        print("Request Headers:", request.headers)
        print("Received Request Body:", request.json)

        if not request.is_json:
            print("Invalid Content-Type!")
            return jsonify({'error': 'Invalid Content-Type. Expected application/json'}), 400

        data = request.json
        url = data.get('url')

        if not url:
            print("No URL provided!")
            return jsonify({'error': 'No URL provided'}), 400

        print("Processing URL:", url)

        features = extract_features(url)
        print("Extracted Features:", features)

        prediction = model.predict(features)
        prediction_label = label_encoder.inverse_transform(prediction)[0]

        print("Prediction:", prediction_label)

        return jsonify({'url': url, 'prediction': prediction_label})

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)