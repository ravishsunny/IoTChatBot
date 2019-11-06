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


class OperationDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(OperationDialog, self).__init__(dialog_id or OperationDialog.__name__)
        self.c8yConnector = CumulocityConnector()
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        # self.add_dialog(DateResolverDialog(DateResolverDialog.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.device_step,
                    self.confirm_step,
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
            message_text = "Enter Device on which operation needs to be performed?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )

        if ms_details.operationType is None:
            message_text = "Enter Operation which needs to be performed?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        
        # If Operation is of sending message then check that message is provided in double quotes.
        if "message" in ms_details.operationType or "send" in ms_details.operationType :
            if ms_details.message is None:
                message_text = "Could not find any message in the given query. Please make sure that you have provided message in quotes."
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
        message_text = (
            f"Please confirm, You want to perform \"{ms_details.operationType}\" operation on device : "
            f"{ms_details.deviceId}"
        )
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
            result = self.c8yConnector.performOperation(ms_details)
            if result=="":
                result = "Operation successfull"
            message_text = (
                    f"%s" % result
            )
            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )
            await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=message)
            )
            return await step_context.end_dialog(ms_details)
        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
