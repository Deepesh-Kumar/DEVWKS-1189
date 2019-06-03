
import json
import requests
import itertools
import sys
import csv
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
s = requests.session()	

class device_audit:

	def __init__(self, IP,username,password):
		self.IP = IP
		self.username = username
		self.password = password


	def get_device_chassis_details(self):
		urv = 'https://' + self.IP + '/dataservice/system/device/management/systemip'
		response = s.get(urv, auth=HTTPBasicAuth(self.username, self.password), verify=False)
		d = response.json()
		for i in d['data']:
			if i['deviceType'] == 'vedge':
				print ( i['serialNumber'], i['chasisNumber'])



def main(args):
	vmanage_ip = args[0]
	obj = device_audit(vmanage_ip, 'admin', 'admin')
	result = obj.get_device_chassis_details()


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))


