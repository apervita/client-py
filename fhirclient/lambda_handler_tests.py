import json
import unittest

import lambda_handler


class TestLambdaHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('test_client_cerner_settings.json') as cerner_settings:
            cls.cerner_settings = json.loads(cerner_settings.read())

        with open('test_client_epic_settings.json') as epic_settings:
            cls.epic_settings = json.loads(epic_settings.read())

        cls.no_authorization_settings = {
            'app_id': 'myApp',
            'api_base': 'http://test.fhir.org/r4'
        }

        cls.hapi_fhir_settings = {
            'app_id': 'myApp',
            'api_base': 'http://hapi.fhir.org/baseR4',
        }

        cls.vonk_settings = {
            'app_id': 'myApp',
            'api_base': 'https://vonk.fire.ly/R4'
        }

        cls.apervita_settings = {
            'app_id': 'myApp',
            'api_base': 'http://54.89.162.246:8080/cqf-ruler-r4/fhir/'
        }

    def test_lambda_handler_patient_id(self):
        event = {lambda_handler.FHIR_SERVER_SETTINGS_KEY: self.epic_settings,
                 lambda_handler.PATIENT_ID_KEY: 'eq081-VQEgP8drUUqCWzHfw3'}
        response = lambda_handler.lambda_handler(event, {})
        assert len(response) == 1
        assert len(response[0]['entry']) >= 1
        assert isinstance(response[0]['entry'], list)
        assert isinstance(response[0]['entry'][0], dict)

    def test_lambda_handler_query(self):
        event = {lambda_handler.FHIR_SERVER_SETTINGS_KEY: self.vonk_settings,
                 lambda_handler.QUERY_KEY: {'family': 'Chalmers'}}
        response = lambda_handler.lambda_handler(event, {})
        assert len(response) == 10
        assert len(response[0]['entry']) >= 1
        assert isinstance(response[0]['entry'], list)
        assert isinstance(response[0]['entry'][0], dict)

    def test_lambda_handler_patient_id_apervita(self):
        event = {lambda_handler.FHIR_SERVER_SETTINGS_KEY: self.apervita_settings,
                 lambda_handler.PATIENT_ID_KEY: 'mom-with-anaemia'}
        response = lambda_handler.lambda_handler(event, {})
        assert len(response) == 1
        assert len(response[0]['entry']) >= 1
        assert isinstance(response[0]['entry'], list)
        assert isinstance(response[0]['entry'][0], dict)
