# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog

from datatypes_date_time.timex import Timex
from helpers.CumulocityHelper import CumulocityConnector

class DevicesDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(DevicesDialog, self).__init__(dialog_id or DevicesDialog.__name__)

        self.c8yConnector=CumulocityConnector()
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        #self.add_dialog(DateResolverDialog(DateResolverDialog.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.show_devices,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    """
    Complete the interaction and end the dialog.
    :param step_context:
    :return DialogTurnResult:
    """

    async def show_devices(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        device_details = step_context.options
        result = self.c8yConnector.getDevices(device_details.type,device_details.location)
        
        if len(result) != 0:
            res=self.extractDeviceDetails(result,device_details.location)
            msg = "Sorry, I could not find any devices."
            
            if len(res) != 0:
                msg=self.prettyPrinter.prettyPrintFromList(res)
            
            message_text = (
                f"%s" % msg
            )
            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )

            await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=message)
            )
            
            return await step_context.end_dialog(device_details)
        else:
            prompt_message = "Sorry, I could not find any devices."
            return await step_context.end_dialog(self.id, prompt_message)

    def extractDeviceDetails(self,result,location = None):
        devices = []
        if isinstance(result,dict):
            if "managedObjects" in result.keys():
                m_objs = result.get("managedObjects")
                for device in m_objs:
                    uniqueDevice = {}
                    if "name" in device:
                        uniqueDevice["Name"] = device["name"]
                    if "id" in device:
                        uniqueDevice["id"] = device["id"]
                    if "creationTime" in device:
                        uniqueDevice["creationTime"] = device["creationTime"]
                    if "owner" in device:
                        uniqueDevice["owner"] = device["owner"]
                    if "c8y_Position" in device and location:
                        lng = device["c8y_Position"]["lng"]
                        lat = device["c8y_Position"]["lat"]
                        if not self.isInboundDevice(lng,lat,location): continue
                        uniqueDevice["Position"] = location
                    devices.append(uniqueDevice)
        return devices
    def isInboundDevice(self,devlng,devlat,location):
        location = location.lower()
        if location == "hyd": location ="hyderabad"
        Location_dict = {"hyderabad" : (17.38878595,78.4610647345315),"cambridge" : (52.2338333,0.1528505)}

        loclat = Location_dict[location][0]
        loclng = Location_dict[location][1]

        if loclat-2 <= devlat <= loclat+2 :
            if location == "hyderabad":
                if loclng - 2 <= devlng <= loclng + 2:
                    return True
            else:
                if loclng - 0.02 <= devlng <= loclng + 0.02:
                    return True

        return False