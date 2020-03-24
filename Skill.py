# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

import requests
import json
import time
from datetime import datetime
from random import randrange

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import requests
import json
from datetime import datetime


class SolaxCrawler():

    def __init__(self):
        date_today = datetime.now().strftime('%Y-%m-%d')
        self.original_url = 'https://www.solaxcloud.com/i18n/language.do?language=en_US&url=/views/index.jsp'
        self.login_url = 'https://www.solaxcloud.com/login/login.do'
        self.data_url = 'https://www.solaxcloud.com/userIndex/getCurrentData.do?currentTime=' + date_today + '+12%3A01%3A42'
        self.logout_url = 'https://www.solaxcloud.com/login/loginOut.do'

        self.headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.132 Safari/537.36'
        }

    def get_data(self, session):
        data_response = session.post(self.data_url, headers=self.headers, verify=False)
        data = json.loads(data_response.text)

        daily_yield = data['todayYield']
        monthly_yield = data['monthYield']
        yearly_yield = data['yearYield']
        total_yield = data['totalYield']
        current_power = data['gridpower']

        # close session
        requests.get(self.logout_url, verify=False)
        requests.post(self.logout_url, verify=False, headers={'Connection': 'close'})
        return current_power, daily_yield, yearly_yield

    def initiate_login_session(self, username, password):
        login_data = {'roletype': '5'}
        login_data.update({'username': username, 'userpwd': password})

        session = requests.session()
        session.post(self.login_url, data=login_data, headers=self.headers, verify=False)
        session.get(self.original_url, headers=self.headers, verify=False)
        return session


class WeatherDataRetriever():

    def __init__(self):
        self.weatherurl = 'http://api.openweathermap.org/data/2.5/forecast?q=Mumbai&cnt=5&appid=d87a44b604cc9d9b83b00af3ac1ddde8'

    def get_estimated_yield(self):
        cloud_average = self.get_weather_data() / 100
        month = datetime.now().month

        sun_hours = 13 - (13 * cloud_average)
        m = 1.01278225014726
        c = 1.41708226978205
        daily_yield = m * sun_hours + c

        if month < 4 or month > 9:
            return daily_yield
        elif 3 <= month < 6:
            return daily_yield + 1
        else:
            return daily_yield + 2

    def get_weather_data(self):
        response = requests.get(self.weatherurl)
        weather_data = json.loads(response.text)['list']
        cloud_average = self.calculate_average_clouds(weather_data)
        return cloud_average

    def calculate_average_clouds(self, data):
        cloud_percentage_daily_average = counter = 0

        for hourly_data in data:
            timestamp = hourly_data['dt']
            count_until_time = WeatherDataRetriever.convert_timestamp_to_hour(timestamp)
            if count_until_time < 20:
                current_cloud_percentage = hourly_data['clouds']['all']
                cloud_percentage_daily_average += current_cloud_percentage
                counter += 1
            elif counter == 0:
                current_cloud_percentage = hourly_data['clouds']['all']
                cloud_percentage_daily_average += current_cloud_percentage
                counter += 1
            else:
                break
        return cloud_percentage_daily_average / counter

    @staticmethod
    def convert_timestamp_to_hour(timestamp):
        return datetime.fromtimestamp(timestamp).hour - 1


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "Welcome to your solax cloud what would you like to know?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("")
                .response
        )


class PredictionIntentHandler(AbstractRequestHandler):
    """Handler for PredictionIntent"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PredictionIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        dataretriever = WeatherDataRetriever()
        estimated_daily_yield = round(dataretriever.get_estimated_yield(), 2)
        speak_output = "The predicted amount for your farm is " + str(
            estimated_daily_yield) + "  Kilowatt Hours"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("")
                .response
        )


class InformationIntentHandler(AbstractRequestHandler):
    """Handler for InformationIntent"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("InformationIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        username = 'user'
        password = '5f4dcc3b5aa765d61d8327deb882cf99'

        solaxretriever = SolaxCrawler()
        solax_session = solaxretriever.initiate_login_session(username, password)
        data = solaxretriever.get_data(solax_session)

        current_power = int(data[0])
        daily_yield = data[1]
        yearly_yield = int(data[2])

        speak_output = "The Farm is currently producing " + str(current_power) + " Watt and has produced " + str(
            daily_yield) + " Kilowatt Hours already. Total this year : " + str(
            yearly_yield) + " Kilowatt Hours"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Da ist wohl was schiefgelaufen. Pierre hat irgendwie Mist gebaut, bitte eine Nachricht an ihn schreiben was ihr gesagt habt."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PredictionIntentHandler())
sb.add_request_handler(InformationIntentHandler())

sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(
    IntentReflectorHandler())  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
