# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, CardFactory
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog

from datatypes_date_time.timex import Timex
from helpers.CumulocityHelper import CumulocityConnector


class AlarmsDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(AlarmsDialog, self).__init__(dialog_id or AlarmsDialog.__name__)

        self.c8yConnector = CumulocityConnector()
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        # self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        # self.add_dialog(DateResolverDialog(DateResolverDialog.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    # self.confirm_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    """
    Complete the interaction and end the dialog.
    :param step_context:
    :return DialogTurnResult:
    """
    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result = self.c8yConnector.getAlarms(step_context.options)
        
        if result:
            message_text = (
                f"%s" % self.prettyPrinter.prettyPrintFromList(self.fineTuneAlarms(result))
            )

            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )

            await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=message)
            )
            return await step_context.end_dialog(step_context.options)
        else:
            prompt_message = "Sorry, I could not find any alarms."
            message = MessageFactory.text(
                prompt_message, prompt_message, InputHints.ignoring_input
            )
            await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=message)
            )
            return await step_context.end_dialog(step_context.options)
        
    def fineTuneAlarms(self, result):
        alarms = []
        if isinstance(result, list):
            for alarm in result:
                if alarm.get('history') != None:
                    alarm.pop('history')
                if alarm.get('self') != None:
                    alarm.pop('self')
                if alarm.get('source') != None and alarm.get('source').get('self') != None:
                    alarm.get('source').pop('self')
                alarms.append(alarm)
        return alarms

    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types