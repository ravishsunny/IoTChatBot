#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    LUIS_APP_ID = os.environ.get("LuisAppId", "f85aaaa8-2ef3-486c-84b8-eff26c2a5b8b")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "663da9472f6e449783aa22ca33004f95")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westus.api.cognitive.microsoft.com")
    BING_SPELL_CHECK_SUB_KEY = os.environ.get("bing_spell_check_subscription_key", "a358b22400554de49228897183ea120c")