#!/usr/bin/env python
#
# WARNING This code is still under development
#
__author__ = 'Kim Hagen'

DOCUMENTATION = '''
---
module: els_file_upload

dependencies:
    requests cbor2 urllib3 datetime json
    To pip install requests cbor2 urllib3 datetime json

'''
import json
from datetime import date
import requests
import urllib3
from requests.auth import HTTPBasicAuth
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cbor2

class ElsUploadFile():
    def __init__(self, module):
        self.module = module
        # Assign Parms.
        self.server = module.params["server"]
        self.verify_certificate = module.params["verify_certificate"]
        self.els_file = module.params["els_file"]
        self.els_id = module.params["els_id"]

    def put_pipeline(self):
        headers = {'content-type': 'application/json'}
        data = {
            "description": "Extract attachment information",
            "processors": [
                {
                    "attachment": {
                        "field": "data"
                    }
                }
            ]
        }
        try:
            p = requests.put(
                self.server + "/_ingest/pipeline/attachment?pretty",
                data=json.dumps(data),
                headers=headers,
                verify=self.verify_certificate
            )
            p.raise_for_status()
        except requests.exceptions.HTTPError as err:
            self.module.fail_json(msg="elastic post: Failure %s" % (err))
            return False


    def put_file(self):
        today = date.today()
        index_date = today.strftime("%Y-%m-%d")
        headers = {'content-type': 'application/cbor'}
        changed = self.put_pipeline()

        if changed:
            return False

        with open(self.els_file, 'rb') as f:
            doc = {
                'data': f.read()
            }
            try:
                p = requests.put(
                    self.server + "/logstash-%s/_doc/%s?pipeline=attachment&pretty" % (index_date, self.els_id),
                    data=cbor2.dumps(doc),
                    headers=headers,
                    verify=self.verify_certificate
                )
                p.raise_for_status()
            except requests.exceptions.HTTPError as err:
                self.module.fail_json(msg="elastic post: Failure %s" % (err))
                return False


        cb_dec = cbor2.loads(p.content)
        self.upload_info = cb_dec


    def main(self):
        changed = self.put_file()
        self.module.exit_json(changed=changed, msg=self.upload_info)

def main():
        module = AnsibleModule(
            argument_spec=dict(
                server=dict(type='str', required=True),
                verify_certificate=dict(type='bool', required=False, default=True),
                els_file=dict(type='str', required=True),
                els_id=dict(type='int', required=True),
            ),
            supports_check_mode=True
        )
        ElsUploadFile(module).main()

# import module snippets
from ansible.module_utils.basic import *
main()
