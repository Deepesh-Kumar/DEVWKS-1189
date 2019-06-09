import logging
from datetime import timedelta, datetime, time
from requests import ReadTimeout, ConnectTimeout
from urllib3.exceptions import ConnectTimeoutError
import urllib.parse

import time
from requests import ReadTimeout

from helper.ds_query_time_keeper import DsQueryTimeKeeper

logger = logging.getLogger("SDWAN")


class VipDevices:
    """
    This class is used to get the data from vmanage through API calls.
    """

    def __init__(self, viptela_session, args, vmanage_url):
        self.viptela_session = viptela_session
        self.args = args
        self.query_interval = int(args.vmanage_query_interval)
        self.vmanage_url = vmanage_url
        self.platform_version = None
        self.app_version = None

    '''
    Make request to vmanage API for given path
    '''

    def make_request(self, path):

        try:
            if self.platform_version is None and self.app_version is None:
                self.__get_vmanage_version()

            if int(self.platform_version[0]) >= 18 or int(self.app_version[0]) >= 18:
                if "assembly" in path:
                    id = path.split("/")[-1]
                    path = "/dataservice/template/policy/assembly/vsmart/" + id
            response = self.viptela_session._get(self.viptela_session.session, self.vmanage_url + path, timeout=10)

            if response.status_code == 200:
                if len(response.data) != 0:
                    logger.debug("Successfully retrived data for path {0}".format(path))
                else:
                    logger.debug("No data received for path {0}".format(path))
            elif response.status_code == 403:
                logger.info("vManage session expired recreating the session")
                self.viptela_session.login()
                logger.info("New vManage session created")
                logger.debug("Requesting the API again to retrieve the data {0}".format(path))
                response = self.make_request(path=path)
            else:
                logger.error("Error while retrieving data for path {0}".format(path))

            return response
        except Exception as e:
            logger.error("Error in getting data from vManage during make request")
            logger.error(e)

    def make_bulk_api_request(self, path):

        response = self.viptela_session._get(self.viptela_session.session, self.vmanage_url + path, timeout=10)
        if response.status_code == 200:
            if len(response.data) != 0:
                logger.debug("Successfully retrived data for path {0}".format(path))
            else:
                logger.debug("No data received")
        elif response.status_code == 403:
            logger.info("vManage session expired recreating the session")
            self.viptela_session.login()
            logger.info("New vManage session created")
            logger.debug("Requesting the API again to retrieve the data {0}".format(path))
            self.make_bulk_api_request(path=path)
        else:
            logger.error("Error while retrieving data for path {0}".format(path))
        return response

    def get_component_list(self):
        component_list = []
        raw_component_list = self.make_request("/dataservice/event/component/keyvalue")

        for component in raw_component_list.data:
            component_list.append(component["key"])

        return component_list

    '''
    Getting viptela devices.
    '''

    def get_devices_map(self):

        raw_map_link = self.make_request("/dataservice/group/map/devices/links?groupId=all")

        return raw_map_link.data

    '''#TODO need to remove this when confirmed with other flows.
    def get_devices(self):

        devices = self.viptela_session._get(self.viptela_session.session,
                                            self.vmanage_url + "/dataservice/device?personality=vedge", timeout=10)
        if devices.status_code == 200:
            if len(devices.data) != 0:
                logger.debug("Successfully devices retrived...")
            else:
                logger.debug("Error while retrieving data...")

        return devices.data'''

    '''
    Getting tenant details.
    '''

    def get_org(self):
        org = None
        devices = self.make_request("/dataservice/settings/configuration/organization")
        for device in range(0, len(devices.data)):
            org = devices.data[device]
        return org

    '''
    Getting information about sites for sub group formation.
    '''

    def get_sub_group(self):

        # TODO use bdf session to get device list and site ID

        devices = self.make_request(path="/dataservice/device")

        site_with_no_location = {}
        lst_of_devices = []
        for device in devices.data:
            location_name = self.get_device_location_name(device["uuid"])

            if location_name is None:
                site_with_no_location[device["site-id"]] = {
                                                            "site_id": device["site-id"],
                                                            "latitude": device["latitude"],
                                                            "longitude": device["longitude"],
                                                            "location_name": location_name,
                                                           }
            else:
                device_attr = {
                                "site_id": device["site-id"],
                                "latitude": device["latitude"],
                                "longitude": device["longitude"],
                                "location_name": location_name,
                              }
                lst_of_devices.append(device_attr)
                if device["site-id"] in site_with_no_location:
                    del site_with_no_location[device["site-id"]]

        for site_id in site_with_no_location:
            lst_of_devices.append(site_with_no_location[site_id])
        return lst_of_devices

    def get_site_id_site_name_map(self):
        """
        Get all the sites location names
        :return: the site id and site location map
        """

        # TODO use bdf session to get device list and site ID
        devices = self.make_request(path="/dataservice/device")
        site_with_no_location = {}
        lst_of_sites = {}
        for device in devices.data:
            location_name = self.get_device_location_name(device["uuid"])
            if location_name is None:
                site_with_no_location[device["site-id"]] = None
            else:
                lst_of_sites[device["site-id"]] = location_name
                if device["site-id"] in site_with_no_location:
                    del site_with_no_location[device["site-id"]]
        for site_id in site_with_no_location:
            lst_of_sites[site_id] = site_with_no_location[site_id]
        return lst_of_sites

    def get_site(self):

        devices = self.make_request("/dataservice/device")

        lst_of_sites = []
        for device in devices.data:
            if device["site-id"] not in lst_of_sites:
                lst_of_sites.append(device["site-id"])
        return lst_of_sites

    '''
    Get the interface list
    '''

    def get_interfaces(self, count=5000):

        # Supported keys from API

        # "recordId": "#29:0",
        # "ifindex": 1,
        # "vdevice-name": "172.17.0.10",
        # "if-admin-status": "Up",
        # "createTimeStamp": 1474290841536,
        # "duplex": "full",
        # "vpn-id": "0",
        # "vdevice-host-name": "vmanage",
        # "mtu": "1500",
        # "ip-address": "10.10.1.10/24",
        # "hwaddr": "00:50:56:bc:3e:ec",
        # "speed-mbps": "1000",
        # "vdevice-dataKey": "172.17.0.10-0-eth1",
        # "ifname": "eth1",
        # "lastupdated": 1518225994470,
        # "port-type": "transport",
        # "if-oper-status": "Up",
        # "encap-type": "null"
        raw_interface_list = []
        path = "/dataservice/data/device/state/Interface"
        raw_interface_list += self.__get_paged_interface_response(count=count, path=path)
        path = "/dataservice/data/device/state/CEdgeInterface"
        raw_interface_list += self.__get_paged_interface_response(count=count, path=path)
        return raw_interface_list

    def get_bfd_session(self, start_id=None, count=500, isFirstCall=True):

        """
        Get the BFD Session
        :param start_id: The start ID
        :param count: The Count
        :param isFirstCall: Flag to check is this API call is first
        :return: The BFD session JSON Data
        """

        raw_bfd_sessions = None
        if isFirstCall and count is not None:
            raw_bfd_sessions = self.make_bulk_api_request(
                "/dataservice/data/device/state/BFDSessions?count={}".format(count)
            )
        else:
            if start_id is not None:
                path = "/dataservice/data/device/state/BFDSessions?count={0}&startId={1}".format(count, start_id)
                raw_bfd_sessions = self.make_bulk_api_request(path)
            else:
                logger.error("start_id is None for BFD Session")

        return raw_bfd_sessions

    '''
     Get flow data from VManage.
    '''

    def get_omp(self, device_ip):

        path = "/dataservice/device/omp/routes/received?deviceId=" + device_ip
        ompd = self.make_request(path)

        return ompd.data

    def get_interface_lst(self, scroll_id=None, count=500, isFirstCall=True):
        interface_data = None
        try:
            end_time = datetime.now()
            start_time = DsQueryTimeKeeper.INTERFACE_START_TIMING

            path = None
            if isFirstCall and count is not None:

                path = "/dataservice/data/device/statistics/interfacestatistics" \
                       "?count={0}&startDate={1}&endDate={2}&timeZone={3}".format(
                                                               count,
                                                               start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                                               end_time.strftime("%Y-%m-%dT%H:%M:%S"), "UTC")
                logger.debug(self.vmanage_url + path)
                interface_data = self.make_bulk_api_request(path)
            else:
                if scroll_id is not None:

                    path = "/dataservice/data/device/statistics/interfacestatistics?scrollId={0}".format(scroll_id)
                    logger.debug(self.vmanage_url + path)
                    interface_data = self.make_bulk_api_request(path)
                else:
                    logger.error("scroll_id is None for interface statistics")

        except ReadTimeout:
            logger.error("Error vmanage timeout during interface stats")

        return interface_data

    '''
    Fetches last thirty minutes statistics.
    date.strftime("%Y-%m-%dT%H:%M:%S")
    '''
    def get_approute_statistics(self, scroll_id=None, count=500, isFirstCall=True):
        app_statistics = None

        try:
            end_time = datetime.now()
            # start_time = end_time - timedelta(seconds=self.query_interval)
            start_time = DsQueryTimeKeeper.APPROUTE_START_TIMING

            path = None
            if isFirstCall and count is not None:
                path = "/dataservice/data/device/statistics/approutestatsstatistics?" \
                                         "count={0}&startDate={1}&endDate={2}&timeZone={3}".format(
                    count,
                    start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "UTC"
                )

            else:
                if scroll_id is not None:
                    path = "/dataservice/data/device/statistics/approutestatsstatistics?scrollId={0}".format(scroll_id)
                else:
                    logger.error("scroll_id is None for approutes statistics")

            if path is not None:
                logger.debug(self.vmanage_url + path)
                app_statistics = self.make_bulk_api_request(path)

            if not app_statistics.data:
                logger.debug("Approute statistics data is empty")
            else:
                logger.debug("Successfully devices retrived...")

        except ReadTimeout:
            logger.error("Error vmanage timeout during approute stats")

        return app_statistics

    """
    Getting all devices from VManage including vsmart,vbond,vmanage and vedge.
    """

    def get_all_devices(self):
        path = "/dataservice/device"
        devices = self.make_request(path="/dataservice/device")

        if len(devices.data) != 0:
            logger.debug("Successfully devices retrived for path {0}".format(path))
        else:
            logger.error("Error while retrieving data for path {0}".format(path))

        return devices.data

    def get_alarms(self, scroll_id=None, count=500, isFirstCall=True):

        alarms = None
        try:

            end_time = datetime.now()
            start_time = DsQueryTimeKeeper.ALARMS_COUNT_START_TIMING

            path = "/dataservice/data/device/statistics/alarm?startDate={0}&endDate={1}" \
                                     "&count={2}&timeZone={3}".format(start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                                                      end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                                                      count, "UTC")

            if isFirstCall and count is not None:
                logger.debug(self.vmanage_url + path)
                alarms = self.make_bulk_api_request(path=path)
            else:
                if scroll_id is not None:
                    path = "/dataservice/data/device/statistics/alarm?scrollId={0}".format(scroll_id)
                    alarms = self.make_bulk_api_request(path=path)
                else:
                    logger.error("scroll_id is None for alarm statistics")
        except ReadTimeout:
            logger.error("Error vmanage timeout during alarm stats")

        return alarms

    def get_events(self, scroll_id=None, count=500, isFirstCall=True):
        events = None
        try:

            end_time = datetime.now()
            start_time = DsQueryTimeKeeper.EVENT_START_TIMING

            if isFirstCall and count is not None:
                logger.debug(self.vmanage_url + "/dataservice/data/device/statistics/deviceevents?"
                                                                      "startDate={0}&endDate={1}"
                                                                      "&count={2}&timeZone={3}".format(
                                                       start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                                       end_time.strftime("%Y-%m-%dT%H:%M:%S"), count, "UTC"))
                events = self.make_bulk_api_request(path="/dataservice/data/device/statistics/deviceevents?"
                                                                      "startDate={0}&endDate={1}"
                                                                      "&count={2}&timeZone={3}".format(
                                                       start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                                       end_time.strftime("%Y-%m-%dT%H:%M:%S"), count, "UTC"))

            else:
                if scroll_id is not None:

                    path = "/dataservice/data/device/statistics/deviceevents?scrollId={0}".format(scroll_id)

                    logger.debug(self.vmanage_url + path)

                    events = self.make_bulk_api_request(path=path)
                else:
                    logger.error("scroll_id is None for event statistics")

        except ReadTimeout:
            logger.error("Error vmanage timeout during event stats for path "
                         "/dataservice/data/device/statistics/deviceevents")

        return events

    '''
    Get all the SLA class List
    '''
    def get_sla_class(self):

        raw_sla_class = self.make_request("/dataservice/template/policy/list/sla")

        return raw_sla_class.data

    def check_location_name(self, device_uuid):
        """
        Get the Device Running config details for given device UUID
        :param device_uuid:
        :return: the Device config
        """

        try:
            raw_config = self.make_request("/dataservice/template/config/running/{0}".format(
                device_uuid
            ))
            config_list = [s for s in raw_config.data.splitlines()]
            for config in config_list:
                if "location" in config and "gps" not in config:
                    location = config.replace("location", "").replace('"', '').strip()
                    return location
        except (ConnectTimeout, ConnectTimeoutError, ReadTimeout):
            logger.error("Error in getting the device  configuration for device : {}".format(device_uuid))
            raise Exception("Unable to get the device list from NMS")
        except Exception as ex:
            logger.error("Error in parsing the device  configuration for device : {}".format(device_uuid))
            logger.error(ex)

    def get_device_location_name(self, device_uuid):
        """
        Get the Device Running config details for given device UUID
        :param device_uuid:
        :return: the Device config
        """

        location = None

        """
        device_uuid sometime has '/' character, so we encode the '/' char using url encoder
        """
        encoded_device_uuid = urllib.parse.quote(device_uuid, safe='')
        try:
            raw_config = self.make_request("/dataservice/template/config/running/{0}".format(
                encoded_device_uuid
            ))
            config_list = [s for s in raw_config.data.splitlines()]
            for config in config_list:
                if "location" in config and "gps" not in config:
                    location = config.replace("location", "").replace('"', '').strip()
                    return location
        except Exception as ex:
            logger.error("Error in parsing the device  configuration for device : {}".format(device_uuid))
            logger.error(ex)

        return location

    def get_vsmart_policy(self):

        policies = self.make_request("/dataservice/template/policy/vsmart")
        return policies.data

    def get_vsmart_policy_by_id(self, vsmart_policy_id):

        policies = self.make_request(path="/dataservice/template/policy/vsmart/definition/{0}".format(vsmart_policy_id))
        return policies.data

    def get_approute_definition(self, approute_policy_id):
        policies = self.make_request("/dataservice/template/policy/definition/approute/{0}" .format(approute_policy_id))
        return policies.data

    def find_sla_by_id(self, sla_id):
        raw_sla_class = self.make_request("/dataservice/template/policy/list/sla")
        for sla in raw_sla_class.data:
            if sla["listId"] == sla_id:
                return sla

    def get_app_list_by_id(self, app_list_id):
        app_list = self.make_request("/dataservice/template/policy/list/app")
        for app in app_list.data:
            if app["listId"] == app_list_id:
                return app

    def get_data_prefix_list_by_id(self, data_prefix_id):
        prefix_list = self.make_request("/dataservice/template/policy/list/dataprefix")
        for prefix in prefix_list.data:
            if prefix["listId"] == data_prefix_id:
                return prefix

    # It is only used for policy
    def get_assembly(self, id):
        response = self.make_request("/dataservice/template/policy/assembly/{0}".format(id))
        return response.preview

    def get_device_system_statistics(self, scroll_id=None, count=500, isFirstCall=True):
        device_system_status_data = None
        try:
            end_time = datetime.now()
            start_time = DsQueryTimeKeeper.DEVICE_SUMMARY_START_TIMING

            if isFirstCall and count is not None:

                path = "/dataservice/data/device/statistics/devicesystemstatusstatistics" \
                       "?count={0}&startDate={1}&endDate={2}&timeZone={3}".format(
                                                               count,
                                                               start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                                               end_time.strftime("%Y-%m-%dT%H:%M:%S"), "UTC")
                logger.debug(self.vmanage_url + path)
                device_system_status_data = self.make_bulk_api_request(path)
            else:
                if scroll_id is not None:

                    path = "/dataservice/data/device/statistics/devicesystemstatusstatistics?scrollId={0}".format(
                            scroll_id)
                    logger.debug(self.vmanage_url + path)
                    device_system_status_data = self.make_bulk_api_request(path)
                else:
                    logger.error("scroll_id is None for devicesystemstatusstatistics")

        except ReadTimeout:
            logger.error("Error vmanage timeout during devicesystemstatusstatistics")

        return device_system_status_data

    def get_hardware_env_statistics(self, start_id=None, count=500, isFirstCall=True):
        hardware_env_statistics = None
        try:
            if isFirstCall and count is not None:

                path = "/dataservice/data/device/state/HardwareEnvironment?count={0}".format(count, "UTC")
                logger.debug(self.vmanage_url + path)
                hardware_env_statistics = self.make_bulk_api_request(path)
            else:
                if start_id is not None:

                    path = "/dataservice/data/device/state/HardwareEnvironment?count={0}&startId={1}".format(
                        count, start_id)
                    logger.debug(self.vmanage_url + path)
                    hardware_env_statistics = self.make_bulk_api_request(path)
                else:
                    logger.error("scroll_id is None for Hardware Environment")

        except ReadTimeout:
            logger.error("Error vmanage timeout during Hardware Environment")

        return hardware_env_statistics

    def __get_vmanage_version(self):
        vmanage_about = self.viptela_session.get_vmanage_about()
        platform_key, platform_version = vmanage_about.data['version'].split(":")
        # application_key, app_version = vmanage_about.data['applicationVersion'].split(":")

        if vmanage_about.data['applicationVersion']:
            appversion = vmanage_about.data['applicationVersion'].split(":")
            appversion.pop(0)
            app_version = ''.join(appversion)

        self.platform_version = platform_version.strip().split('.')
        self.app_version = app_version.strip().split('.')

    def get_interface_queue_stats(self, device_id):
        queue_stats = self.make_request("/dataservice/device/interface/queue_stats?deviceId={0}".format(device_id))
        return queue_stats.data

    '''
    Get the colour list.
    '''

    def get_colors(self):
        colors_set = set()
        color_list = list()
        bfd_sessions = self.get_bfd_session(count=int(self.args.data_count_per_request))
        page_info = bfd_sessions.page_info
        try:
            while True:
                for tunnel in bfd_sessions.data:
                    colors_set.add(tunnel["color"])
                    colors_set.add(tunnel["local-color"])
                if page_info is None:
                    logger.error("Page info not available for BFD Session")
                    break
                if page_info["moreEntries"] is False:
                    # TODO add time keeper
                    break
                try:
                    bfd_sessions = self.get_bfd_session(start_id=page_info["startId"], isFirstCall=False)
                    page_info = bfd_sessions.page_info
                except (ConnectTimeout, ConnectTimeoutError, ReadTimeout) as e:
                    logger.error("vManage timeout")
            color_list = list(colors_set)
        except Exception as e:
            logger.error("Exception raised in get_colors: {0}".format(e))

        return color_list

    def get_reboot_history(self):
        reboot_history = self.make_request("/dataservice/device/reboothistory/details")
        return reboot_history.data

    def get_qos_dpi_apps(self):
        applications = self.make_request("/dataservice/device/dpi/qosmos/applications")
        return applications.data

    def __get_paged_interface_response(self, count, path):
        start_id = None
        raw_interface_list = []
        raw_interface_response = self.make_bulk_api_request(
            "{}?count={}".format(path, count)
        )
        if "pageInfo" in raw_interface_response:
            page_info = raw_interface_response.page_info
        else:
            page_info = {"moreEntries": False}
        if "startId" in page_info:
            start_id = page_info["startId"]
        raw_interface_list += raw_interface_response.data

        while page_info["moreEntries"]:
            if start_id is not None:
                path = "{}?count={}&startId={}".format(path, count, start_id)
                raw_interface_response = self.make_bulk_api_request(path)
                page_info = raw_interface_response.page_info
                start_id = page_info["startId"]
                raw_interface_list += raw_interface_response.data
            else:
                logger.error("start_id is None for Interfaces")
        return raw_interface_list
