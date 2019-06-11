
import json
import requests
import itertools
import sys
import csv
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
session = requests.session()	

class device_audit:

	def __init__(self, IP,username,password):
		self.IP = IP
		self.username = username
		self.password = password


	def get_device_chassis_details(self):
		api_call = 'https://' + self.IP + '/dataservice/system/device/management/systemip'
		response = session.get(urv, auth=HTTPBasicAuth(self.username, self.password), verify=False)
		js_response = response.json()
		for data in js_response['data']:
			if data['deviceType'] == 'vedge':
				print ( i['serialNumber'], i['chasisNumber'])



def main(args):
	vmanage_ip = args[0]
	obj = device_audit(vmanage_ip, 'devuser', 'clus19')
	result = obj.get_device_chassis_details()


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))


