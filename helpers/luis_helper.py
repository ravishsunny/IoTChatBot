# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from .intent_extract_helper import GetAlarmHelper, GetDeviceHelper, GetMeasurementHelper, OnOperationHelper, Intent


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )
            print("LuisHelper recognizer_result = %s" %recognizer_result)
            if intent == Intent.GET_ALARM.value:
                result = GetAlarmHelper.execute_alarmluis_query(luis_recognizer, turn_context, intent, recognizer_result)
            elif intent == Intent.GET_DEVICES.value:
                result = GetDeviceHelper.execute_deviceluis_query(recognizer_result)
            elif intent == Intent.GET_MEASUREMENT.value:
                result = GetMeasurementHelper.execute_measurementluis_query(luis_recognizer, turn_context, intent, recognizer_result)
            elif intent == Intent.DO_OPERATION.value:
                result = OnOperationHelper.execute_operationluis_query(luis_recognizer, turn_context, intent, recognizer_result)
                
        except Exception as e:
            print(e)

        return intent, result
        