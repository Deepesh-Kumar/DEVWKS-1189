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
    	urv = 'https://' + self.IP + '/dataservice/template/device/config/attachfeature'
    	headers = {'Content-Type': 'application/json'}
    	payload = {"deviceTemplateList":{"deviceTemplateList":[{"templateId":"6b985229-0ff8-4cde-b5e3-8d05a518007d","device":[{"csv-status":"complete","csv-deviceId":"0f500217-8dac-45d2-14a7-c19120a25af7","csv-deviceIP":"1.10.1.2","csv-host-name":"dc10-vedge2","/0/ge0/0/interface/if-name":"ge0/0","/512/ge0/6/interface/if-name":"ge0/6","//system/site-id":"10","/0/ge0/1/interface/if-name":"ge0/1","/512/ge0/6/interface/ip/address":"192.168.150.10/24","//system/host-name":"dc10-vedge2","//system/system-ip":"1.10.1.2","/10/ge0/2/interface/if-name":"ge0/2","/512/eth0/interface/if-name":"eth0","/512/vpn-instance/ip/route/0.0.0.0/0/prefix":"0.0.0.0/0","/10/ge0/2/interface/ip/address":"10.10.1.3/24","/0/ge0/1/interface/ip/address":"10.10.2.2/30","/512/vpn-instance/ip/route/0.0.0.0/0/next-hop/192.168.150.1/address":"192.168.150.1","/0/vpn-instance/ip/route/0.0.0.0/0/prefix":"0.0.0.0/0","/0/vpn-instance/ip/route/0.0.0.0/0/next-hop/10.10.2.1/address":"10.10.2.1","/0/vpn-instance/ip/route/0.0.0.0/0/next-hop/19.10.2.1/address":"19.10.2.1","csv-templateId":"6b985229-0ff8-4cde-b5e3-8d05a518007d"}],"isEdited":false,"isMasterEdited":false}]}
    	q = json.dumps(payload)
    	response1 = s.post(urv, auth=HTTPBasicAuth(self.username, self.password), data= q, headers=headers, cookies=cook, verify=False)
    	print (response1, response1.content)




def main(args):
    vmanage_ip = args[0]
    obj = push_device_template(vmanage_ip, 'admin', 'v1ptela0212')
    result = obj.push_template()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
