import os
import logging
import jsonpickle

from fhirclient import client
from models.patient import Patient as p
from models.procedure import Procedure as px
from models.condition import Condition as cx


FHIR_SERVER_SETTINGS_KEY = 'fhir_server_settings'
PATIENT_ID_KEY = 'patient_id'
QUERY_KEY = 'query'

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def addPatientToBundle(patient):
    bundle = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [{
            "fullUrl": f"urn:uuid:{patient['Patient'].id}",
            "resource": patient['Patient'].as_json()}]
    }
    for procedure in patient['Procedure']:
        bundle['entry'].append({'resource': procedure.as_json()})
    for condition in patient['Condition']:
        bundle['entry'].append({'resource': condition.as_json()})

    return bundle


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
        patients = [{'Patient': p.read(patient_id, smart.server, False)}]
        if query:
            logger.warning(f'Event query: {query} is ignored because patient_id is set')
    else:
        search = p.where(struct=query)
        patients = search.perform_resources(smart.server)
        patients = list(map(lambda x: {'Patient': x}, patients))

    for patient in patients:
        search = px.where(struct={'subject': patient['Patient'].id, 'status': 'completed'})
        patient['Procedure'] = search.perform_resources(smart.server)
        search = cx.where(struct={'subject': patient['Patient'].id})
        patient['Condition'] = search.perform_resources(smart.server)

    bundles = list(map(lambda x: addPatientToBundle(x), patients))
    return bundles
