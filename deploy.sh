#!/bin/bash
zip -r -u fhir-client-py.zip fhirclient && aws --profile dev s3 cp fhir-client-py.zip s3://sandbox-fhir-cql/lambda/ && aws --profile dev lambda update-function-code --function-name fhir-client-py --s3-bucket sandbox-fhir-cql --s3-key lambda/fhir-client-py.zip
