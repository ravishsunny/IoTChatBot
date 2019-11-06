import requests
import base64, ssl, json
from datetime import date


class PrettyPrinter:

    def __init__(self):
        pass
    
    def prettyPrintFromList(self, result):
        """
        Helper to print data neatly from list. It will also order the results.
        :param result: list of data.
        :return: a string with proper ordering.
        """
        res = "\n"
        counter = 1
        if isinstance(result, list):
            for item in result:
                res = res + str(counter) + ". " + str(item) + '\n'
                counter = counter + 1
        return res
    
    def prettyPrintFromDict(self, result):
        """
        Helper to print data neatly from dictionary. It will also order the results.
        :param result: list of data.
        :return: a string with proper ordering.
        """
        res = "\n"
        counter = 1
        if isinstance(result, dict):
            for item in result:
                res = res + str(counter) + ". " + str(item) + ": "+ str(result[item]) + '\n'
                counter = counter + 1
        return res
