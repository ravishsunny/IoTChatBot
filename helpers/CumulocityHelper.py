import requests
import base64, ssl, json
from Intent_details import AlarmRequest
from datetime import date


class CumulocityConnector:

    def __init__(self):
        self.deviceState = 0
        self.CUMULOCITY_USERNAME = 'apamabld'
        self.CUMULOCITY_PASSWORD = 'IfAtFirstYouDon\'tSucceed2'
        self.CUMULOCITY_APPKEY = 'apamaepl-key'
        self.CUMULOCITY_SERVER_URL = "https://sag.cumulocity.com"

    def platformRequest(self, path, method='GET', body=None, params={}):
        """ Performs a REST request against the C8Y platform"""

        headers = {}
        host = self.CUMULOCITY_SERVER_URL
        user = self.CUMULOCITY_USERNAME
        password = self.CUMULOCITY_PASSWORD

        headers["Authorization"] = "Basic " + base64.b64encode(
            bytes(user + ":" + password, "utf8")).decode()
        headers["X-Cumulocity-Application-Key"] = self.CUMULOCITY_APPKEY

        print("Hitting url:", host+path, " Params:", str(params))
        if method == 'GET':
            resp = requests.request(method, host+path, params=params, headers = headers)
        else:
            resp = requests.request(method, host+path, data=body, params=params, headers = headers)

        if not (200 <= resp.status_code < 300):

            e = Exception("Request to %s failed with %i %s" % (path, resp.status_code, resp.reason))
            e.status = resp.status_code
            raise e
        if method == 'POST':
            return ""
        respBody = json.loads(resp.text)
        return respBody


    def getDevices(self,type = None, location = None):

        params = dict()
        params["fragmentType"] = "c8y_IsDevice"
        params["pageSize"] = "20"

        if location is not None:
            params["fragmentType"] = "c8y_Position"

        print("type = %s , location = %s" % (type,location))
        return self.platformRequest("/inventory/managedObjects",params=params)

    def getDeviceWithName(self, deviceName):
        params = {"query": "name eq '%s'" % deviceName}
        return self.platformRequest('/inventory/managedObjects', params=params)

    def getMeasurements (self, deviceId, type=None):
        #{{url}}/measurement/measurements/series?source={{deviceId}}&dateFrom={{dateFrom}}&dateTo={{dateTo}}
        fragmentType = None

        if not type is None:
            if type.upper == "TEMPERATURE":
                fragmentType = "c8y_Temperature"
            elif type.upper == "PRESSURE":
                fragmentType = "c8y_Pressure"
            elif type.upper == "HUMIDITY":
                fragmentType = "c8y_Humidity"

        params = {"source":'%s'% deviceId}
       #pageSize=5&source=226875600&dateFrom=2019-10-24&currentPage=2&revert=true

        params["dateFrom"] = date.today().strftime("%Y-%m-%d")
        params["revert"] = "true"
        params["pageSize"] = 1

        if fragmentType is not None:
            params["fragmentType"] = fragmentType

        results = self.platformRequest('/measurement/measurements', params=params)
        return self.getMeasurementsVal(results)

    def performOperation(self, entities=None):
        # {{url}}/devicecontrol/operations
        print("performOperation calling")
        body = {}
        if "on" in entities.operationType:
            if(self.deviceState == 1):
                return "The Device is already ON"
            body["c8y_Relay"] = {"relayState": "CLOSE"}
            self.deviceState = 1

        if "off" in entities.operationType:
            if(self.deviceState == 0):
                return "The Device is already OFF"
            body["c8y_Relay"] = {"relayState": "OPEN"}
            self.deviceState = 0

        if "message" in entities.operationType or "send" in entities.operationType :
            body["c8y_Message"] = {"text":entities.message}

        body["deviceId"] = entities.deviceId

        body = json.dumps(body)
        print("RRLOG : BODY JSON : %s" %body)

        return self.platformRequest('/devicecontrol/operations', method="POST", body=body)

    def getAlarms(self, alarmRequest: AlarmRequest):
        url = '/alarm/alarms'
        params ={}
        if alarmRequest.device:
            params['source'] = alarmRequest.device

        if alarmRequest.severity:
            params['severity'] = alarmRequest.severity.upper()

        if alarmRequest.fromTime:
            params['dateFrom'] = alarmRequest.fromTime

        if alarmRequest.toTime:
            params['dateTo'] =alarmRequest.toTime

        res = self.platformRequest(url, params=params)
        print(res['self'])
        return res['alarms']

    def getMeasurementsVal(self, result):
        #print(result)
        msVals = {}
        if "measurements" in result.keys():
            measurementslist = result.get("measurements")
            for ms in measurementslist:
                for key in ms.keys():
                    if "c8y" in key :
                        fragment = ms[key]
                        print("fragment = %s" %fragment)
                        msVals[key] = fragment
        return msVals

