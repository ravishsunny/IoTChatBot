# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, TurnContext
from botbuilder.schema import InputHints

from .measurement_dialog import MeasurementDialog
from .operation_dialog import OperationDialog
from .alarms_dialog import AlarmsDialog
from .ManagedObject import DevicesDialog
from chatbot_luis_recognizer import ChatBotLuisRecognizer
from helpers.luis_helper import LuisHelper
from helpers.intent_extract_helper import Intent
from Intent_details import AlarmRequest, DevicesRequest, MeasurementRequest, OnOperation
from helpers.CumulocityHelper import CumulocityConnector

class MainDialog(ComponentDialog):
    def __init__(
        self, luis_recognizer: ChatBotLuisRecognizer, measurement_dialog: MeasurementDialog, operation_dialog: OperationDialog,
            alarms_dialog: AlarmsDialog, deviceDialog: DevicesDialog
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self._luis_recognizer = luis_recognizer
        self._measurement_dialog_id = measurement_dialog.id
        self._operation_dialog_id = operation_dialog.id
        self._alarm_dialog_id = alarms_dialog.id;
        self._device_dialog_id = deviceDialog.id

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(measurement_dialog)
        self.add_dialog(operation_dialog)
        self.add_dialog(alarms_dialog)
        self.add_dialog(deviceDialog)

        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.intro_step, self.act_step, self.final_step]
            )
        )

        self.initial_dialog_id = "WFDialog"

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )

            return await step_context.next(None)
        message_text = (
            str(step_context.options)
            if step_context.options
            else "What can I help you with today?"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            raise Exception("Luis not configured")
            # LUIS is not configured, we just run the BookingDialog path with an empty BookingDetailsInstance.

        # Call LUIS and gather any potential booking details. (Note the TurnContext has the response to the prompt.)
        intent, luis_result = await LuisHelper.execute_luis_query(
            self._luis_recognizer, step_context.context
        )
        print("Got Intent " + intent)
        if intent == Intent.GET_DEVICES.value:
            # Run device dialog
            return await step_context.begin_dialog(self._device_dialog_id, luis_result)

        if intent == Intent.GET_MEASUREMENT.value:
            print("getting measurement_dialog")
            # Show a warning for Origin and Destination if we can't resolve them.
            await MainDialog._show_warning_for_unsupported_entities(
                step_context.context, luis_result
            )

            # Run the BookingDialog giving it whatever details we have from the LUIS call.
            return await step_context.begin_dialog(self._measurement_dialog_id, luis_result)
        elif intent == Intent.DO_OPERATION.value:
            # Show a warning for Origin and Destination if we can't resolve them.
            await MainDialog._show_warning_for_unsupported_entities(
                step_context.context, luis_result
            )

            # Run the OperationDialog giving it whatever details we have from the LUIS call.
            return await step_context.begin_dialog(self._operation_dialog_id, luis_result)
        elif intent == Intent.GET_ALARM.value:
            return await step_context.begin_dialog(self._alarm_dialog_id, luis_result)
        else:
            didnt_understand_text = (
                "Sorry, I didn't get that. Please try asking in a different way"
            )
            didnt_understand_message = MessageFactory.text(
                didnt_understand_text, didnt_understand_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(didnt_understand_message)

        return await step_context.next(None)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # If the child dialog ("BookingDialog") was cancelled or the user failed to confirm,
        # the Result here will be null.
        if step_context.result is not None:
            result = step_context.result

            # Now we have all the booking details call the booking service.

            # If the call to the booking service was successful tell the user.
            # time_property = Timex(result.travel_date)
            # travel_date_msg = time_property.to_natural_language(datetime.now())
            msg_txt = f"Previous query finished."
            message = MessageFactory.text(msg_txt, msg_txt, InputHints.ignoring_input)
            await step_context.context.send_activity(message)

        prompt_message = "What else can I do for you?"
        return await step_context.replace_dialog(self.id, prompt_message)

    @staticmethod
    async def _show_warning_for_unsupported_entities(
        context: TurnContext, luis_result: object
    ) -> None:
        print(luis_result)
        if luis_result.unsupported_str:
            message_text = (
                f"Sorry its are not supported:"
                f" {', '.join(luis_result.unsupported_str)}"
            )
            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )
            await context.send_activity(message)

