import json
import requests
import itertools
import csv
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  
import sys 
session = requests.session()  

class push_device_template:

    def __init__(self, IP,username,password):
        self.IP = IP
        self.username = username
        self.password = password

    def push_template(self):
        api_call_first =  'https://' + self.IP + '/j_security_check'
        headers1 = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload1 = {}
        payload_js = json.dumps(payload1)
        response_js = session.post(api_call_first, auth=HTTPBasicAuth(self.username, self.password), data= payload_js, headers=headers1, verify=False)
        cookie = response_js.cookies 
        api_call = 'https://' + self.IP + '/dataservice/template/device/config/attachcli'
        headers = {'Content-Type': 'application/json'}
        payload = {"deviceTemplateList":[{"templateId":"42d40990-8c65-43f7-ba42-1d91fbc8fa3c","device":[{"csv-status":"complete","csv-deviceId":"0f500217-8dac-45d2-14a7-c19120a25af7","csv-deviceIP":"1.10.1.2","csv-host-name":"dc10-vedge2","csv-templateId":"42d40990-8c65-43f7-ba42-1d91fbc8fa3c"}],"isEdited":"false"}]}
        data = json.dumps(payload)
        response_js_final = session.post(api_call, auth=HTTPBasicAuth(self.username, self.password), data= data, headers=headers, cookies=cookie, verify=False)
        print (response_js_final, response_js_final.content)



def main(args):
    vmanage_ip = args[0]
    obj = push_device_template(vmanage_ip, 'devuser', 'clus19')
    result = obj.push_template()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
