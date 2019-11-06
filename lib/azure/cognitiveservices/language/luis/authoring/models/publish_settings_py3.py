# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class PublishSettings(Model):
    """The application publish settings.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. The application ID.
    :type id: str
    :param is_sentiment_analysis_enabled: Required. Setting sentiment analysis
     as true returns the sentiment of the input utterance along with the
     response
    :type is_sentiment_analysis_enabled: bool
    :param is_speech_enabled: Required. Enables speech priming in your app
    :type is_speech_enabled: bool
    :param is_spell_checker_enabled: Required. Enables spell checking of the
     utterance.
    :type is_spell_checker_enabled: bool
    """

    _validation = {
        'id': {'required': True},
        'is_sentiment_analysis_enabled': {'required': True},
        'is_speech_enabled': {'required': True},
        'is_spell_checker_enabled': {'required': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'is_sentiment_analysis_enabled': {'key': 'sentimentAnalysis', 'type': 'bool'},
        'is_speech_enabled': {'key': 'speech', 'type': 'bool'},
        'is_spell_checker_enabled': {'key': 'spellChecker', 'type': 'bool'},
    }

    def __init__(self, *, id: str, is_sentiment_analysis_enabled: bool, is_speech_enabled: bool, is_spell_checker_enabled: bool, **kwargs) -> None:
        super(PublishSettings, self).__init__(**kwargs)
        self.id = id
        self.is_sentiment_analysis_enabled = is_sentiment_analysis_enabled
        self.is_speech_enabled = is_speech_enabled
        self.is_spell_checker_enabled = is_spell_checker_enabled
