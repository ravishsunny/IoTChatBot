# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
import datetime
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from botbuilder.core.recognizer_result import RecognizerResult
from Intent_details import AlarmRequest, DevicesRequest, MeasurementRequest, OnOperation
from helpers.CumulocityHelper import CumulocityConnector


class Intent(Enum):
    GET_ALARM = "GetAlarm"
    GET_DEVICES = "GetDevices"
    GET_MEASUREMENT = "GetMeasurement"
    DO_OPERATION = "PerformOperation"
    NONE_INTENT = "NoneIntent"

class GetAlarmHelper:
    @staticmethod
    def execute_alarmluis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext, _intent: Intent, recognizer_result: RecognizerResult
    ) -> (object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = _intent

        try:

            print('entities: ', recognizer_result.entities)
            result = AlarmRequest()

            severity  = recognizer_result.entities.get("$instance", {}).get(
                    "alarmType", []
                )
            if len(severity) > 0:
                if recognizer_result.entities.get("alarmType", [{"$instance": {}}])[0]:
                    result.severity = severity[0]["text"]

            device  = recognizer_result.entities.get("$instance", {}).get(
                    "c8y_Device", []
                )
            if len(device) > 0:
                if recognizer_result.entities.get("c8y_Device", [{"$instance": {}}])[0]:
                    result.device = getDeviceId(recognizer_result, device[0])
                    print('quering for deviceId: ', result.device)

            ret = parseTime(recognizer_result)
            if ret['from']:
                result.fromTime = ret['from']
            if ret['to']:
                result.toTime = ret['to']

            # print('alarm:', result)
            # extract details

        except Exception as e:
            print(e)

        return result


class GetDeviceHelper:
    @staticmethod
    def execute_deviceluis_query(recognizer_result):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        try:
            
            device = DevicesRequest()

            # extract type if provided
            typeEntity = recognizer_result.entities.get("$instance", {}).get("c8y_DeviceType", [])

            if len(typeEntity) > 0:
                if "type" in typeEntity:
                    device.type = typeEntity["text"]

            # extract type if provided
            locationEntity = recognizer_result.entities.get("$instance", {}).get("geographyV2_city", [])

            if len(locationEntity) > 0:
                if "text" in locationEntity[0]:
                    device.location = locationEntity[0]["text"]

        except Exception as e:
            print(e)

        return device

class GetMeasurementHelper:
    @staticmethod
    def execute_measurementluis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext, _intent: Intent, recognizer_result: RecognizerResult
    ) -> (object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = _intent

        try:
            
            result = MeasurementRequest()

            # extract details
            device_entities = recognizer_result.entities.get("$instance", {}).get(
                    "c8y_Device", []
                )
            if len(device_entities) > 0:
                #print(recognizer_result.entities.get("device", [{"$instance": {}}])[0])
                if recognizer_result.entities.get("c8y_Device", [{"$instance": {}}])[0]:
                    result.deviceId = device_entities[0]["text"]
                    print("device result.deviceId =%s" %result.deviceId)
                else:
                    result.unsupported_str.append(
                        to_entities[0]["text"]
                    )

            type_entities = recognizer_result.entities.get("$instance", {}).get(
                "c8y_DeviceType", []
            )
            if len(type_entities) > 0:
                if recognizer_result.entities.get("c8y_DeviceType", [{"$instance": {}}])[0]:
                    result.type = type_entities[0]["text"].capitalize()
                else:
                    result.unsupported_airports.append(
                        type_entities[0]["text"].capitalize()
                    )
        except Exception as e:
            print(e)

        return result

class OnOperationHelper:
    @staticmethod
    def execute_operationluis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext, _intent: Intent, recognizer_result: RecognizerResult
    ) -> (object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = _intent

        try:

            result = OnOperation()

            # extract details
            operations = recognizer_result.entities.get("$instance", {}).get(
                "Operation_Name", []
            )
            if len(operations) > 0:
                if recognizer_result.entities.get("Operation_Name", [{"$instance": {}}])[0]:
                    result.operationType = operations[0]["text"]
                    if "message" in result.operationType or "send" in result.operationType :
                        if len(recognizer_result.entities.get("$instance", {}).get("Operation_Message", [])) > 0:
                            result.message = recognizer_result.entities.get("$instance", {}).get("Operation_Message", [])[0]["text"]
                        else:
                            result.message = None
                else:
                    result.unsupported_str.append(
                        operations[0]["text"]
                    )

            device_entities = recognizer_result.entities.get("$instance", {}).get(
                "c8y_Device", []
            )
            if len(device_entities) > 0:
                if recognizer_result.entities.get("c8y_Device", [{"$instance": {}}])[0]:
                    result.deviceId = device_entities[0]["text"]
                else:
                    result.unsupported_str.append(
                        device_entities[0]["text"]
                    )

            # extract details

        except Exception as e:
            print(e)

        return result

def getDeviceId(recognizer, device):

    deviceName = device['text']

    try:
        return int(deviceName)
    except ValueError:
        conn = CumulocityConnector()

        queryText = recognizer.text
        startIndex = int(device['startIndex'])
        endIndex = int(device['endIndex'])

        res = conn.getDeviceWithName(queryText[startIndex:endIndex])
        objs = res['managedObjects']
        if len(objs) == 1:
            return objs[0]['id']

def parseTime(recognizer):
    dt = recognizer.entities.get("$instance", {}).get(
                "datetime", []
    )

    if len(dt) > 0:
        if recognizer.entities.get("datetime", [{"$instance": {}}])[0]:
            print(dt)
            dt2 = recognizer.entities.get("datetime", {})[0]
            timexDate = str(dt2['timex'][0])

            if timexDate.startswith('('):
                # Got range
                dates = timexDate.split(',')
                fromDate = dates[0][1:]
                toDate = dates[1]

                print('from:', fromDate, 'to:', toDate)
                return {'from': parseDateTime(fromDate), 'to': parseDateTime(toDate)}
            else:
                fromDate = timexDate

                print('from:', fromDate)
                return {'from': parseDateTime(fromDate)}

def parseDateTime(date: str):
    current = datetime.datetime.now()
    y, m, d, h, M, s = '', '', '', '', '', ''

    split = date.split('T')
    datePart = split[0]
    timePart = split[1] if len(split) > 1 else ''

    if len(datePart) > 0:
        # Contains date
        date = datePart.split('-')
        if len(date) == 1:
            # Contains only year
            y = date[0]
            m = current.month
            d = current.day
        elif len(date) == 2:
            # Contains year and month
            y = date[0] if not isAmbiguous(date[0]) else current.year
            m = date[1]
            d = current.day
        elif len(date) == 3:
            # Conatains year, month and day
            y = date[0] if not isAmbiguous(date[0]) else current.year
            m = date[1] if not isAmbiguous(date[1]) else current.month
            d = date[2]
    else:
        y = current.year
        m = current.month
        d = current.day


    if len(timePart) > 0:
        # Contains time
        time = timePart.split(':')
        if len(time) == 1:
            # Contains only hours
            h = time[0]
            M = current.minute
            s = current.second
        elif len(time) == 2:
            # Contains hours and minutes
            h = time[0] if not isAmbiguous(time[0]) else current.hour
            M = time[1]
            s = current.second
        elif len(time) == 3:
            # Contains hours, minutes and seconds
            h = time[0] if not isAmbiguous(time[0]) else current.hour
            M = time[1] if not isAmbiguous(time[1]) else current.minute
            s = time[2]
    else:
        h = current.hour
        M = current.minute
        s = current.second

    return '%s-%s-%sT%s:%s:%sZ'%(y,m,d,h,M,s)


def isAmbiguous(field: str):
    try:
        int(field)
        return False
    except ValueError:
        return True
