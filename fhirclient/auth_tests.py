import unittest

from auth import FHIROAuth2Auth


class TestAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fhir_auth = FHIROAuth2Auth()

    def test__code_exchange_params(self):
        params = self.fhir_auth._code_exchange_params('some_code')
        assert params['grant_type'] == 'authorization_code'
        assert not params['scope']

    def test__code_exchange_params_backend_service(self):
        params = self.fhir_auth._code_exchange_params('some_code', is_backend_service=True, scope='read/Patient.read')
        assert params['grant_type'] == 'client_credentials'
        assert params['scope']


if __name__ == '__main__':
    unittest.main()
