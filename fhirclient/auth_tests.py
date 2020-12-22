import re
import unittest

from auth import FHIROAuth2Auth
from server_tests import MockServer

mock_token = {'token': 'unittest'}


class TestAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fhir_auth = MockFHIROAuth2Auth()
        cls.server = MockServer(is_backend_service=True)

    def test__code_exchange_params(self):
        params = self.fhir_auth._code_exchange_params('some_code')
        assert params['grant_type'] == 'authorization_code'
        assert not params['scope']

    def test__code_exchange_params_backend_service(self):
        params = self.fhir_auth._code_exchange_params('some_code', is_backend_service=True, scope='read/Patient.read')
        assert params['grant_type'] == 'client_credentials'
        assert params['scope']

    def test__get_jwt(self):
        jwt_params = {
            'client_id': 'some_client',
            'private_key_file': 'tests_private_key.pem',
            'headers': {
                'alg': 'RS384',
                'typ': 'JWT'
            }
        }
        jwt = self.fhir_auth._get_jwt(jwt_params)
        result = re.match('eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzM4NCJ9\..*\..*', jwt.decode('utf-8'))
        assert result

    def test_handle_callback(self):
        token = self.fhir_auth.handle_callback('some_url', self.server)
        assert token == mock_token


if __name__ == '__main__':
    unittest.main()


class MockFHIROAuth2Auth(FHIROAuth2Auth):
    """ Reads local files.
    """

    def _request_access_token(self, mock_server, params):
        return mock_token
