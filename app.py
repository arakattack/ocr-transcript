from flask import Flask, request, json, jsonify, make_response
import base64
import os
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from google.oauth2 import service_account
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import imghdr
import time

load_dotenv()
app = Flask(__name__)
app.json.sort_keys = False  # Ensure JSON response keeps order

# Load GCP credentials from .env
google_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
credentials_dict = json.loads(google_credentials)

# Create a Credentials object from the dictionary
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# Replace with your actual project ID, location, processor ID, and model version
project_id =  os.getenv('PROJECT_ID')
location =  os.getenv('LOCATION_ID')
processor_id =  os.getenv('PROCESSOR_ID')
model_version =  os.getenv('MODEL_VERSION')

API_KEY = os.getenv('API_KEY') 

def validate_api_key(api_key):
    return api_key == API_KEY

def api_key_required(f):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key or not validate_api_key(api_key):
            error_response = make_response(jsonify({
                'error': True, 
                'message': 'API key required'
                }), 401)
            return error_response
        return f(*args, **kwargs)
    return decorated_function

# Function to process the document using Document AI
def process_document(image_data, mime_type):
    try:
        start_time = time.time()  # Start time for processing

        # Set client options and create the client
        opts = ClientOptions(api_endpoint="us-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(credentials=credentials, client_options=opts)

        # Build the processor version path
        processor_name = client.processor_version_path(
            project_id, location, processor_id, model_version
        )

        # Convert image data to base64
        base64_encoded_image = base64.b64encode(image_data).decode("utf-8")

        # Create the raw document and request
        raw_document = documentai.RawDocument(
            content=base64_encoded_image, mime_type=mime_type
        )
        request = documentai.ProcessRequest(
            name=processor_name, raw_document=raw_document, field_mask="entities"
        )

        # Process the document
        result = client.process_document(request=request)
        document = result.document

        # Extract and format extracted data
        transcript = {}
        for entity in document.entities or []:
            try:
                transcript[entity.type_] = entity.mention_text
            except AttributeError:
                pass  # Handle potential errors (e.g., missing entity attributes)

        # Replace "0" and "☐" with "O" in the gol_darah field
        if 'ipk' in transcript and transcript['ipk']:
            transcript['ipk'] = transcript['ipk'].replace("-", "").replace("=", "").replace(":", "")
        if 'univ' in transcript and transcript['univ']:
            transcript['univ'] = transcript['univ'].replace("\\", "")
        if 'nim' in transcript and transcript['nim']:
            transcript['nim'] = transcript['nim'].replace("/", "")
        # Extract specific fields and correct potential misspellings
        nim = transcript.get("nim", "")
        nama = transcript.get("nama", "")
        ipk = transcript.get("ipk", "")
        univ = transcript.get("univ", "")
        fakultas = transcript.get("fakultas", "")
        program_studi = transcript.get("program_studi", "")
        pendidikan = transcript.get("pendidikan", "")
        pddikti = 'https://pddikti.kemdikbud.go.id/api/pencarian/mhs/' + transcript.get("nim", "")

        finish_time = time.time() - start_time  # Calculate time elapsed

        response = make_response(jsonify({
            'error': False,
            'message': 'Proses OCR Berhasil',
            'result': {
                'nim': str(nim),
                'nama': str(nama),
                'ipk': str(ipk),
                'univ': str(univ),
                'fakultas': str(fakultas),
                'program_studi': str(program_studi),
                'pendidikan': str(pendidikan),
                'pddikti': str(pddikti),
                'time_elapsed': str(round(finish_time, 3))
            }
        }), 200)
        return response

    except Exception as e:
        # Handle exceptions gracefully
        error_response = make_response(jsonify({
            'error': True, 
            'message': str(e)
            }), 400)
        return error_response

@app.route('/')
def hello():
    if request.method == "GET":
        try:
            return 'System Ready!', 200
        except Exception as e:
            # Handle exceptions gracefully
            error_response = make_response(jsonify({
                'error': True, 
                'message': str(e)
                }), 400)
            return error_response

    error_response =  make_response(jsonify({
        'error': True, 
        'message': 'Method Not Allowed'
        }), 405)
    return error_response

@app.route('/healthz')
def healthz():
    return 'Healthy!', 200

# API endpoint to receive image data and process the document
@app.route("/", methods=["POST"])
@api_key_required
def process_transcript_api():
    if request.method == "POST":
        try:
            if "image" not in request.files:
                error_response = make_response(jsonify({
                    'error': True, 
                    'message': 'Missing image data'
                    }), 400)
                return error_response

            image_file = request.files["image"]

            # Check if the file is empty
            if image_file.filename == '':
                error_response =  make_response(jsonify({
                    'error': True, 
                    'message': 'No file selected'
                }), 400)
                return error_response

            # Secure the filename and check if it's an allowed image type
            filename = secure_filename(image_file.filename)
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.pdf')):
                error_response =  make_response(jsonify({
                    'error': True, 
                    'message': 'Invalid file type'
                }), 400)
                return error_response

            # Check MIME type of the file
            image_data = image_file.read()
            image_file.seek(0)  # Reset file pointer to the beginning after reading

            # Determine mime type
            mime_type = "application/pdf" if filename.lower().endswith('.pdf') else "image/png"

            # Process the document and return the response
            response = process_document(image_data, mime_type)
            return response

        except Exception as e:
            # Handle exceptions gracefully
            error_response = make_response(jsonify({
                'error': True, 
                'message': str(e)
                }), 400)
            return error_response

    error_response =  make_response(jsonify({
        'error': True, 
        'message': 'Method Not Allowed'
        }), 405)
    return error_response

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
