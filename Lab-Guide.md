
## Introduction

Documentation Link for Cisco SD-WAN APIs

https://sdwan-docs.cisco.com/Product_Documentation/Command_Reference/vManage_REST_APIs


## API-Library

- The API library for the vManage can be accesssed at ht<span>tps://{{vmanage-ip}}/apidocs
  
 
  
[![Screen-Shot-2019-06-02-at-10-50-56-PM.png](https://i.postimg.cc/PqhcfRts/Screen-Shot-2019-06-02-at-10-50-56-PM.png)](https://postimg.cc/RWsGXG6X)

## Chrome Developer Tools 

[![Screen-Shot-2019-06-09-at-4-24-37-PM.png](https://i.postimg.cc/Gp4C5fZv/Screen-Shot-2019-06-09-at-4-24-37-PM.png)](https://postimg.cc/kVPzVTM5)

## Use Case-1 -  Device Auditing

#### Run python script to get serial and chassis numbers of devices which are part of the SD-WAN overlay.
- API Used - ht<span>tps://{{vmanage-ip}}/dataservice/system/device/management/systemip
- METHOD - GET 


## Use Case-2 - vSmart Policy Push

#### Run python script to push centralized policy on the vSmart controller.
- API Used  - ht<span>tps://{{vmanage-ip}}/dataservice/template/policy/vsmart
- METHOD - POST
##### Verification Step



## Use Case-3 - Device Template Push
#### Run python script to push configuration on the WAN Edge Device.
- API Used - ht<span>tps://{{vmanage-ip}}/dataservice/template/device/config/attachcli
- METHOD - POST
##### Verification Step


## Use Case-4 - Device Monitoring
#### Leverage Third party tools to look at integrations for monitoring SD-WAN devices.
- Tools Used - LiveAction, SevOne
- APIs Used - ht<span>tps://{{vmanage-ip}}/dataservice/data/device/state/Interface
            - ht<span>tps://{{vmanage-ip}}/dataservice/data/device/state/BFDSessions
- METHOD - GET  






