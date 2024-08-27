import os
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, request
from app import app, validate_api_key, api_key_required, process_document

class FlaskTestCase(unittest.TestCase):

    API_KEY = '67BD92FF-9408-43C4-A9F3-8CC942694F1E'
    FILE_PATH = 'tests/test.png'

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

if __name__ == '__main__':
    unittest.main()
