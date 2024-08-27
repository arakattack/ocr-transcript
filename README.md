# OCR Transcript

## Description

This Flask application utilizes Google Cloud Document AI to process document images (specifically transcripts) and extract relevant information like name, IPK (GPA), university details, etc. It offers a secure API endpoint for uploading images and receiving the extracted data in JSON format.

## Requirements

- Python 3.x
- Flask framework
- Google Cloud Document AI API (`google-cloud-documentai`)
- Service account credentials for Google Cloud Platform (GCP)
- `dotenv` for managing environment variables
- `werkzeug` for secure file handling
- (Optional) Additional libraries based on image processing needs (e.g., `Pillow`)

## Installation

1. Create a virtual environment (recommended) and activate it.

2. Install the required dependencies:

   ```bash
   pip install flask google-cloud-documentai Flask-Cors dotenv werkzeug
   # (Optional) Pillow
   pip install Pillow
   ```

3. Create a file named `.env` in your project directory and add the following environment variables, replacing the placeholders with your actual values:

   ```env
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
   PROJECT_ID=your-project-id
   LOCATION_ID=your-location-id
   PROCESSOR_ID=your-processor-id
   MODEL_VERSION=your-model-version
   API_KEY=your-api-key  # (Optional, for API access control)
   ```

## Configuration

- Update the environment variables in `.env` with your GCP project details and API key (if used).
- You may modify the list of extracted fields ("nim", "nama", "ipk", "univ", etc.) in the `process_document` function to suit your specific needs.
- Consider incorporating additional validations or data cleaning steps as required.

## Usage

1. Start the application:

   ```bash
   python app.py
   ```

   The application runs on `http://0.0.0.0:5000` (localhost) by default in debug mode.

2. Make a POST request to the `/` endpoint with an image file in the `image` field of your multipart form data. The API key needs to be included in the request header (if configured).

### Example Request (using cURL)

```bash
curl -X POST http://localhost:5000/ \
  -H "X-API-KEY: your_api_key" \
  -F "image=@transcript.jpg"
```

### Example Response (JSON)

```json
{
  "error": false,
  "message": "Proses OCR Berhasil",
  "result": {
    "nim": "1234567890",
    "nama": "John Doe",
    "ipk": "3.8",
    "univ": "University of Example",
    "fakultas": "Faculty of Science",
    "program_studi": "Computer Science",
    "pendidikan": "Bachelor",
    "pddikti": "https://pddikti.kemdikbud.go.id/api/pencarian/mhs/1234567890",
    "time_elapsed": "0.123"
  }
}
```

### Testing

Implement unit tests for your functions using a framework like pytest.
Manually test the API endpoint using tools like Postman or cURL as demonstrated in the “Usage” section.

### Deployment (Docker Compose)

```bash
run docker-compose up
```

```yaml
version: "3"

services:
  ocr:
    build:
      context: .
      dockerfile: Dockerfile
    image: ocr
    container_name: ocr
    environment:
      GOOGLE_APPLICATION_CREDENTIALS: "your_value"
      PROJECT_ID: "your_value"
      LOCATION_ID: "your_value"
      PROCESSOR_ID: "your_value"
      MODEL_VERSION: "your_value"
      API_KEY: "your_value"
    restart: unless-stopped
    ports:
      - "8000:8000"
    networks:
      - ocr-network
    command: gunicorn app:app -w 4 -t 90 --log-level=debug -b 0.0.0.0:8000 --reload --threads 2 --worker-class gevent --keep-alive 5 --timeout 60 --worker-connections 1000
networks:
  ocr-network:
    driver: bridge
```
