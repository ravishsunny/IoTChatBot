# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
from botbuilder.core import Recognizer, RecognizerResult, TurnContext


class ChatBotLuisRecognizer(Recognizer):
    def __init__(self, configuration: dict):
        self._recognizer = None

        luis_is_configured = (
            configuration["LUIS_APP_ID"]
            and configuration["LUIS_API_KEY"]
            and configuration["LUIS_API_HOST_NAME"]
        )
        if luis_is_configured:
            luis_application = LuisApplication(
                configuration["LUIS_APP_ID"],
                configuration["LUIS_API_KEY"],
                "https://" + configuration["LUIS_API_HOST_NAME"],
            )
            prediction_options=LuisPredictionOptions(spell_check=True, bing_spell_check_subscription_key=configuration["BING_SPELL_CHECK_SUB_KEY"])
            self._recognizer = LuisRecognizer(application=luis_application, prediction_options=prediction_options)

    @property
    def is_configured(self) -> bool:
        # Returns true if luis is configured in the appsettings.json and initialized.
        return self._recognizer is not None

    async def recognize(self, turn_context: TurnContext) -> RecognizerResult:
        return await self._recognizer.recognize(turn_context)
