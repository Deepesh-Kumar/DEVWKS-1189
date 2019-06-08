import json
import requests
import itertools
import csv
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  
import sys 
s = requests.session()  

class push_device_template:

    def __init__(self, IP,username,password):
        self.IP = IP
        self.username = username
        self.password = password


    def push_template(self):
    	uri =  'https://' + self.IP + '/j_security_check'
    	headers1 = {'Content-Type': 'application/x-www-form-urlencoded'}
    	payload1 = {}
    	q1 = json.dumps(payload1)
    	response = s.post(uri, auth=HTTPBasicAuth(self.username, self.password), data= q1, headers=headers1, verify=False)
    	cook = response.cookies	
    	urv = 'https://' + self.IP + '/dataservice/template/device/config/attachcli'
    	headers = {'Content-Type': 'application/json'}
    	payload = {"deviceTemplateList":[{"templateId":"880dcd05-750e-4382-a192-9fda8f0881cd","device":[{"csv-status":"complete","csv-deviceId":"11OD141140055","csv-deviceIP":"1.1.1.14","csv-host-name":"Site15-vE14","csv-templateId":"880dcd05-750e-4382-a192-9fda8f0881cd"}],"isEdited":"false"}]}
    	q = json.dumps(payload)
    	response1 = s.post(urv, auth=HTTPBasicAuth(self.username, self.password), data= q, headers=headers, cookies=cook, verify=False)
    	print (response1, response1.content)




def main(args):
    vmanage_ip = args[0]
    obj = push_device_template(vmanage_ip, 'admin', 'v1ptela0212')
    result = obj.push_template()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
