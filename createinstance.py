import random
import string

from googleapiclient.discovery import build
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file('service-account.json')
compute = build('compute','v1',credentials = creds)

l = string.ascii_lowercase
name = "sf-crawl-" + ''.join(random.choice(l) for i in range(4))
machine = "zones/us-central1-a/machineTypes/n1-standard-2"
snapshot = "global/snapshots/sf-cli-api"
startupscript = "bash /home/****/bin/cloudcrawlclose example.com"

config = {
        'name': name,
        'machineType': machine,
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceSnapshot': snapshot,
                }
            }
        ],
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],
        'serviceAccounts': [{
            "email": "***************@developer.gserviceaccount.com",
            "scopes": [
              "https://www.googleapis.com/auth/bigquery",
              "https://www.googleapis.com/auth/datastore",
              "https://www.googleapis.com/auth/devstorage.full_control",
              "https://www.googleapis.com/auth/logging.write",
              "https://www.googleapis.com/auth/monitoring.write",
              "https://www.googleapis.com/auth/service.management.readonly",
              "https://www.googleapis.com/auth/servicecontrol",
              "https://www.googleapis.com/auth/sqlservice.admin",
              "https://www.googleapis.com/auth/trace.append"
            ]
        }],
        'metadata': {
            'items': [{
                'key': 'startup-script',
                'value': startupscript
            }]
        }
    }
instance = compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()
print(instance)
