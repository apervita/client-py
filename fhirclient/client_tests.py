import unittest

import client
import json
from models.patient import Patient as p
from models.fhirabstractbase import FHIRValidationError


class TestClient(unittest.TestCase):
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

    #  This test will fail if test_client_cerner_settings.json is not configured correctly.
    def test_client_cerner(self):
        smart = client.FHIRClient(settings=self.cerner_settings)
        smart.prepare()
        smart.handle_callback('some_url')
        assert smart.ready
        patient = p.read('12742400', smart.server, False)
        assert patient.id == '12742400'

    #  This test will fail if test_client_epic_settings.json is not configured correctly.
    def test_client_epic(self):
        smart = client.FHIRClient(settings=self.epic_settings)
        smart.prepare()
        smart.handle_callback('some_url')
        assert smart.ready
        patient = p.read('eq081-VQEgP8drUUqCWzHfw3', smart.server)
        assert patient.id == 'eq081-VQEgP8drUUqCWzHfw3'

    def test_client_no_authorization(self):
        smart = client.FHIRClient(settings=self.no_authorization_settings)
        search = p.where(struct={'family': 'Chalmers'})
        patients = search.perform_resources(smart.server)
        assert patients
        assert len(patients) > 0

    # HAPI FHIR does not strictly adhere to FHIR spec
    # Specific issues:
    #   Patient.communication.language is omitted but required
    def test_client_hapi_fhir(self):
        smart = client.FHIRClient(settings=self.hapi_fhir_settings)
        search = p.where(struct={'family': 'Smith'})
        try:
            search.perform_resources(smart.server)
            assert False
        except FHIRValidationError as e:
            assert True

    def test_client_vonk(self):
        smart = client.FHIRClient(settings=self.vonk_settings)
        search = p.where(struct={'family': 'Chalmers'})
        patients = search.perform_resources(smart.server)
        assert patients
        assert len(patients) > 0


if __name__ == '__main__':
    unittest.main()
