import os
import logging
import jsonpickle

from fhirclient import client
from models.patient import Patient as p

FHIR_SERVER_SETTINGS_KEY = 'fhir_server_settings'
PATIENT_ID_KEY = 'patient_id'
QUERY_KEY = 'query'

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def addPatientToBundle(patient):
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [{
            "fullUrl": f"urn:uuid:{patient['id']}",
            "resource": patient}]
    }


# event dict: {fhir_server_settings, patient_id, query}
# settings dict: {app_id, api_base, app_secret, is_backend_service, is_jwt,
#                 jwt_params: {client_id, private_key_file, headers, alg, typ}


def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))
    fhir_server_settings = event[FHIR_SERVER_SETTINGS_KEY] if FHIR_SERVER_SETTINGS_KEY in event else None
    patient_id = event[PATIENT_ID_KEY] if PATIENT_ID_KEY in event else None
    query = event[QUERY_KEY] if QUERY_KEY in event else None
    smart = client.FHIRClient(settings=fhir_server_settings)
    if fhir_server_settings.get('app_secret') or \
            fhir_server_settings.get('jwt_params') and fhir_server_settings.get('jwt_params').get('private_key_file'):
        smart.prepare()
        smart.handle_callback('some_url')

    if patient_id:
        patients = [p.read(patient_id, smart.server, False).as_json()]
        if query:
            logger.warning(f'Event query: {query} is ignored because patient_id is set')
    else:
        search = p.where(struct=query)
        patients = search.perform_resources(smart.server)
        patients = list(map(lambda x: x.as_json(), patients))
    return list(map(lambda x: addPatientToBundle(x), patients))
