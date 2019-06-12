import json
import requests
import itertools
import csv
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
s = requests.session()	

class ch:

	def __init__(self, IP,username,password,g ,h, k, l,  *args, **kwargs):
		self.IP = IP
		self.username = username
		self.password = password
		self.g = []
		self.h = []
		self.k = []
		self.l = []


	def get(self):
		try:
			uri = 'https://' + self.IP + '/dataservice/device'  
			response = s.get(uri, auth=HTTPBasicAuth(self.username, self.password), verify=False)
			d = response.json()
			for i in d['data']:
				if i['device-model'] == 'vedge-1000' or i['device-model'] == 'vedge-cloud' and i['reachability'] == 'reachable' and i['personality'] =='vedge':
					self.__h.append(i['local-system-ip'])
					self.__g.append(i['uuid'])
				#elif i['device-model'] =='vedge-cloud' and i['reachability'] == 'reachable' and i['personality'] == 'vedge':
					#self.k.append(i['local-system-ip'])
					#self.l.append(i['uuid'])
		except:
			print 'Cannot Connect'
	def get_bgp(self):
		#s = requests.session()
		urv = 'https://' + self.IP + '/dataservice/device/interface/stats?deviceId='
		for i in self.h:
			urv1 = urv + i + '&&&'
			#print urv1
			response1 = s.get(urv1, auth=HTTPBasicAuth(self.username, self.password), verify=False)
			e = response1.json()
			for i in e['data']:
				print i['vpn-id']

	def get_arp(self):
		urv2 = 'https://' + self.IP + '/dataservice/device/arp?deviceId='
		for i in self.h:
			urv3 = urv2 + i + '&&&'
			response12 = s.get(urv3, auth=HTTPBasicAuth(self.username, self.password), verify=False)
			f = response12.json()
			for i in f['data']:
				print i['if-name'], i['vpn-id'], i['vdevice-host-name'], i['mac'], i['ip']

	def get_software_version(self):
		urv4 = 'https://' + self.IP + '/dataservice/device/software?deviceId='
		count = 0
		for i in self.h:
			urv5 = urv4 + i + '&&&'
			response12 = s.get(urv5, auth=HTTPBasicAuth(self.username, self.password), verify=False)
			g = response12.json()
			for i in g['data']:
				if i['version'] == '18.3.0' and i['active'] == 'true':
					count = count + 1

    #def deactivate_policy(self):
    #	urv4 = 'https://' + self.IP + '/dataservice/template/policy/vsmart/deactivate/da1a9dea-aac7-4171-805a-39c58c51dfdb?confirm=true'
    #	headers={'Content-Type': 'application/json'}
    #	#p = 'da1a9dea-aac7-4171-805a-39c58c51dfdb'
		#q = json.dumps(p)
	#	response1 = s.post(urv4, auth=HTTPBasicAuth(self.username, self.password), headers=headers, verify=False)
	#	print

	def get_running_config(self):
		urv = 'https://' + self.IP + '/dataservice/template/config/running/' 
		for i in self.g:
			urv1 = urv + i
			res = s.get(urv1, auth=HTTPBasicAuth(self.username, self.password), verify=False)
			e = res.json()


	def get_templates(self):
		urv = 'https://' + self.IP + '/dataservice/template/device'
		res = s.get(urv, auth=HTTPBasicAuth(self.username, self.password), verify=False)
		e = res.json()
		for i in e['data']:
			print i['templateName'], i['deviceType'], i['templateId'], i['templateDescription']

	def attach_feature_template(self):
		urv = 'https://' + self.IP + '/dataservice/template/device/config/attachfeature'
		headers={'Content-Type': 'application/json'}
		payload = {"deviceTemplateList":[{"templateId":"b64eb57f-57de-404d-9d8c-1a83209d12de",
		"device":[{"csv-status":"complete","csv-deviceId":"8e897e63-7b79-4622-8040-6aab57fab89e","csv-deviceIP":"1.1.1.222","csv-host-name":"",
		"//system/host-name":"","//system/system-ip":"","//system/site-id":"","csv-templateId":"b64eb57f-57de-404d-9d8c-1a83209d12de"}],
		"isEdited":"false","isMasterEdited":"false"}]}
		with open('DC_vEDGE-CLOUD.csv', 'rU') as f:
			reader = csv.DictReader(f)
			data ={}
			for row in reader:
				for header , value in row.items():
					try:
						data[header].append(value)
					except KeyError:
						data[header] = [value]

		payload['deviceTemplateList'][0]['device'][0]['csv-host-name'] = data['csv-host-name'][0]
		payload['deviceTemplateList'][0]['device'][0]['//system/host-name'] = data['//system/host-name'][0]
		payload['deviceTemplateList'][0]['device'][0]['//system/system-ip'] = data['//system/system-ip'][0]
		payload['deviceTemplateList'][0]['device'][0]['//system/site-id'] = data['//system/site-id'][0]
		q = json.dumps(payload)
		response1 = s.post(urv, auth=HTTPBasicAuth(self.username, self.password), data= q, headers=headers, verify=False)
		print response1, response1.content


	

    








t = []
u = []
v = []
l = []
a = ch('10.195.168.110', 'deepesh', 'deepesh4321!',t,u,v,l)

a.get()
#a.get_software_version()
#a.deactivate_policy()
a.get_software_version()
#a.attach_feature_template()












