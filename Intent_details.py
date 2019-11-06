# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List

class AlarmRequest:
    def __init__(
        self,
        device: str = None,
        severity: str = None,
        fromTime: str = None,
        toTime: str = None,
        location: str = None
    ):
        self.device = device
        self.severity = severity
        self.fromTime = fromTime
        self.toTime = toTime
        self.location = location


class DevicesRequest:
    def __init__(
        self,
        location: str = None,
        type: str = None
    ):
        self.location = location
        self.type = type

class MeasurementRequest:
    def __init__(
        self,
        deviceId: str = None,
        type: str = None,
        unsupported_str: List[str] = [],
    ):
        self.deviceId = deviceId
        self.type = type
        self.unsupported_str = unsupported_str

class OnOperation:
    def __init__(
        self,
        deviceId: str = None,
        operationType: str = None,
        message: str = None,
        unsupported_str: List[str] = []
    ):
        self.deviceId = deviceId
        self.operationType = operationType
        self.message = message
        self.unsupported_str = unsupported_str
