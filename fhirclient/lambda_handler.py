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
RESOURCE_KEY = 'resource'

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
    if 'Procedure' in patient:
        for procedure in patient['Procedure']:
            bundle['entry'].append({'resource': procedure.as_json()})
    if 'Condition' in patient:
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
    resource = event[RESOURCE_KEY] if RESOURCE_KEY in event else []
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

    if len(resource) > 1:
        for patient in patients:
            if 'procedure' in list(map(lambda x: x.lower(), resource)):
                search = px.where(struct={'patient': patient['Patient'].id})
                patient['Procedure'] = search.perform_resources(smart.server)
            if 'condition' in list(map(lambda x: x.lower(), resource)):
                search = cx.where(struct={'patient': patient['Patient'].id})
                patient['Condition'] = search.perform_resources(smart.server)

    bundles = list(map(lambda x: addPatientToBundle(x), patients))
    return bundles
