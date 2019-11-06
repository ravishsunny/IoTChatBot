# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog

from datatypes_date_time.timex import Timex
from helpers.CumulocityHelper import CumulocityConnector

class MeasurementDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(MeasurementDialog, self).__init__(dialog_id or MeasurementDialog.__name__)

        self.c8yConnector=CumulocityConnector()
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        #self.add_dialog(DateResolverDialog(DateResolverDialog.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.device_step,
                    #self.confirm_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    """
    If a destination city has not been provided, prompt for one.
    :param step_context:
    :return DialogTurnResult:
    """

    async def device_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        ms_details = step_context.options

        if ms_details.deviceId is None:
            message_text = "Enter Device ID to know the measurements?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(ms_details.deviceId)

  
    """
    Confirm the information the user has provided.
    :param step_context:
    :return DialogTurnResult:
    """

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        ms_details = step_context.options

        ms_details.deviceId = step_context.result

        message_text =  f"Please confirm, You want to know the measurement for device : { ms_details.deviceId } "
        if not ms_details.type is None:
            message_text = message_text + f" and type : { ms_details.type }"

        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    """
    Complete the interaction and end the dialog.
    :param step_context:
    :return DialogTurnResult:
    """

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        if step_context.result:
            ms_details = step_context.options
            ms_details.deviceId = step_context.result
            result = self.c8yConnector.getMeasurements(ms_details.deviceId, ms_details.type)
            print("output %s" %result)
            
            if len(result) != 0:
                message_text = (
                    f"%s" %self.prettyPrinter.prettyPrintFromDict(result)
                )
                message = MessageFactory.text(
                    message_text, message_text, InputHints.ignoring_input
                )
                
                await step_context.prompt(
                    TextPrompt.__name__, PromptOptions(prompt=message)
                )
                return await step_context.end_dialog(ms_details)
            else:
                prompt_message = "Sorry, I could not find any measurements."
                message = MessageFactory.text(
                    prompt_message, prompt_message, InputHints.ignoring_input
                )
                await step_context.prompt(
                    TextPrompt.__name__, PromptOptions(prompt=message)
                )
                return await step_context.end_dialog(step_context.options)

    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
