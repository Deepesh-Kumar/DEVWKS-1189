import json
import requests
import itertools
import csv
import sys 
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  
s = requests.session()  
 

class activate_vsmart_policy:

    def __init__(self, IP,username,password):
        self.IP = IP
        self.username = username
        self.password = password


    def activate_policy(self):
        uri = 'https://' + self.IP + '/dataservice/template/policy/vsmart'
        response = s.get(uri, auth=HTTPBasicAuth(self.username, self.password), verify=False)
        d = response.json()
        for i in d['data']:
                if i['policyName'] == 'Policy-DC-Prefrence':
                    a = i['policyId']
        urv = 'https://' + self.IP +  '/dataservice/template/policy/vsmart/activate/' + a 
        headers={'Content-Type': 'application/json'}
        payload = {}
        payload = json.dumps(payload)
        response1 = s.post(url=urv, auth=HTTPBasicAuth(self.username, self.password), data=payload, headers=headers, verify=False)
        print (response1, response1.content)




def main(args):
    vmanage_ip = args[0]
    obj = activate_vsmart_policy(vmanage_ip, 'admin', 'v1ptela0212')
    result = obj.activate_policy()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))












			



