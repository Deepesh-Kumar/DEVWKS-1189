import json
import requests
import itertools
import csv
import sys 
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  
session = requests.session()  
 

class activate_vsmart_policy:

    def __init__(self, IP,username,password):
        self.IP = IP
        self.username = username
        self.password = password


    def activate_policy(self):
        uri = 'https://' + self.IP + '/dataservice/template/policy/vsmart'
        response = session.get(uri, auth=HTTPBasicAuth(self.username, self.password), verify=False)
        response_js = response.json()
        for data in response_js['data']:
                if data['policyName'] == 'SLA-Policy':
                    policy_id = data['policyId']
        urv = 'https://' + self.IP +  '/dataservice/template/policy/vsmart/activate/' + policy_id
        headers={'Content-Type': 'application/json'}
        payload = {}
        payload = json.dumps(payload)
        response_new = session.post(url=urv, auth=HTTPBasicAuth(self.username, self.password), data=payload, headers=headers, verify=False)
        print (response_new, response_new.content)




def main(args):
    vmanage_ip = args[0]
    obj = activate_vsmart_policy(vmanage_ip, 'devuser', 'clus19')
    result = obj.activate_policy()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))












			



