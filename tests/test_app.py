import os
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, request
from app import app, validate_api_key, api_key_required, process_document

class FlaskTestCase(unittest.TestCase):

    API_KEY = '67BD92FF-9408-43C4-A9F3-8CC942694F1E'
    FILE_PATH = 'tests/sample_ktp.png'

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def test_validate_api_key(self):
        self.assertTrue(validate_api_key(self.API_KEY))
        self.assertFalse(validate_api_key('wrong_key'))

    def test_api_key_required(self):
        response = self.client.post('/', headers={'X-API-KEY': self.API_KEY})
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/', headers={'X-API-KEY': 'wrong_key'})
        self.assertEqual(response.status_code, 401)

    def test_process_document(self):
        with self.app.app_context():
            with open(self.FILE_PATH, 'rb') as f:
                image = f.read()
            response = process_document(image)
            print(response.data)

    def test_process_ktp_api(self):
        with self.app.app_context():
            response = self.client.post('/', headers={'X-API-KEY': self.API_KEY})
            print(response.data)
            self.assertEqual(response.status_code, 400)
            response = self.client.post('/', headers={'X-API-KEY': 'wrong_key'})
            print(response.data)
            self.assertEqual(response.status_code, 401)
            with open(self.FILE_PATH, 'rb') as f:
                response = self.client.post('/', headers={'X-API-KEY': self.API_KEY}, data={'image': f})
                print(response.data)
                self.assertEqual(response.status_code, 200)

    @patch('app.process_document')
    def test_process_document(self, mock_process_document):
        with self.app.app_context():
            # Mock the response from process_document()
            mock_response = {
                "error": False,
                "message": "Proses OCR Berhasil",
                "result": {
                    "nik": "3175070101909999",
                    "nama": "BILLY BUMBLEBEE SIFULAN",
                    "tempat_lahir": "SURABAYA",
                    "tgl_lahir": " 01-01-1990",
                    "gol_darah": "AB",
                    "jenis_kelamin": "LAKI-LAKI",
                    "agama": "ISLAM",
                    "status_perkawinan": "KAWIN",
                    "pekerjaan": "KARYAWAN SWASTA",
                    "kewarganegaraan": "WNI",
                    "alamat": {
                        "name": "JL DIMANA NO 100",
                        "rt_rw": "001/001",
                        "kel_desa": "",
                        "kecamatan": "DUREN SAWIT",
                        "kabupaten": "JAKARTA TIMUR",
                        "provinsi": "DKI JAKARTA"
                    }
                }
            }
            mock_process_document.return_value = mock_response

            with open(self.FILE_PATH, 'rb') as f:
                image = f.read()
            response = process_document(image)
            # Convert the response data to a dictionary
            response_data = response.get_json()
            # Exclude time_elapsed from the comparison
            response_data['result'].pop('time_elapsed', None)
            print(response_data)

            self.assertEqual(response_data, mock_response)

if __name__ == '__main__':
    unittest.main()
