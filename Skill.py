# -*- coding: utf-8 -*-
"""Simple Solax app."""

import random
import logging
import json
import prompts
import os
import boto3
from requests import Request, Session

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Persistence
ddb_region = os.environ.get('DYNAMODB_PERSISTENCE_REGION')
ddb_table_name = os.environ.get('DYNAMODB_PERSISTENCE_TABLE_NAME')

ddb_resource = boto3.resource('dynamodb', region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource)


# Rest API Client
class Client:
    session = Session()

    @staticmethod
    def send_request(method, adress, **kwargs):
        request = Request(method, adress, params=kwargs)
        prepared = request.prepare()
        return Client.session.send(prepared)

    @staticmethod
    def process_request(response):
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                return None
            return data['result']

    @staticmethod
    def request(method, adress, **kwargs):
        response = Client.send_request(method, adress, **kwargs)
        content = Client.process_request(response)
        return content


# Built-in Intent Handlers
class LaunchHandler(AbstractRequestHandler):
    """Handler for Skill Launch"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("LaunchRequest")(handler_input)) or (is_intent_name("InformationIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchHandler")

        # Persistence
        attr = handler_input.attributes_manager.persistent_attributes

        user_id = handler_input.request_envelope.session.user.user_id

        if not attr:
            attr['token_id'] = 0
            attr['site_id'] = 0
            handler_input.attributes_manager.session_attributes = attr
            handler_input.attributes_manager.save_persistent_attributes()
            speech = 'Please enter token identification and site identification, by saying login. If you need help check the Skill Description in the Skill Store.'
            handler_input.response_builder.speak(speech).ask('')
            return handler_input.response_builder.response
        elif attr['token_id'] == 0:
            speech = 'Please enter token identification and site identification, by saying login. If you need help check the Skill Description in the Skill Store.'
            handler_input.response_builder.speak(speech).ask('')
            return handler_input.response_builder.response
        else:

            # Get Personal data
            attr = handler_input.attributes_manager.persistent_attributes
            token_id = attr['token_id']
            site_id = attr['site_id']

            ENDPOINT = r'https://www.solaxcloud.com:9443/proxy/api/getRealtimeInfo.do'
            kwargs = {'tokenId': token_id, 'sn': site_id}
            data = Client.request('GET', ENDPOINT, **kwargs)

            # Check if Succesfully received
            if data is None:
                speech = 'Wrong token data entered. At least did not receive a valid response from Solax Server. Please try again!'
            acpower = data['acpower']
            today_kwh = data['yieldtoday']
            total_kwh = data['yieldtotal']
            bat_pow = data['batPower']
            speech = 'Total Yield today is: ' + str(int(today_kwh)) + 'kwh. Total Yield is: ' + str(
                int(total_kwh)) + 'kwh. Current Battery Power is: ' + str(int(bat_pow))

            handler_input.response_builder.speak(speech).ask('')
            return handler_input.response_builder.response


class AnswerHandler(AbstractRequestHandler):
    """Handler for Skill Launch and GetNewFact Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AnswerIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In AnswerIntent")
        slots = handler_input.request_envelope.request.intent.slots

        # Input data from user to persistence
        attr = handler_input.attributes_manager.persistent_attributes
        unfiltered_token_id = slots['tokenid'].value
        unfiltered_site_id = slots['siteid'].value
        token_id = ''.join(filter(str.isdigit, str(unfiltered_token_id)))
        site_id = ''.join(filter(str.isalpha, str(unfiltered_site_id)))
        attr['token_id'] = token_id
        attr['site_id'] = site_id
        handler_input.attributes_manager.session_attributes = attr
        handler_input.attributes_manager.save_persistent_attributes()

        # Test if data is correct
        ENDPOINT = r'https://www.solaxcloud.com:9443/proxy/api/getRealtimeInfo.do'
        kwargs = {'tokenId': token_id, 'sn': site_id}
        data = Client.request('GET', ENDPOINT, **kwargs)

        # Output result if correct, else exception is thrown
        if data is None:
            speech = 'Wrong token data entered. At least did not receive a valid response from Solax Server. Please try again!'
        else:
            speech = 'Succesfully saved your input data!'
        handler_input.response_builder.speak(speech).ask('')
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.HELP_MESSAGE]
        reprompt = data[prompts.HELP_REPROMPT]
        handler_input.response_builder.speak(speech).ask(
            reprompt).set_card(SimpleCard(
            data[prompts.SKILL_NAME], speech))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.STOP_MESSAGE]
        handler_input.response_builder.speak(speech)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent.

    AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.FALLBACK_MESSAGE]
        reprompt = data[prompts.FALLBACK_REPROMPT]
        handler_input.response_builder.speak(speech).ask(
            reprompt)
        return handler_input.response_builder.response


class LocalizationInterceptor(AbstractRequestInterceptor):
    """
    Add function to request attributes, that can load locale specific data.
    """

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))

        # localized strings stored in language_strings.json
        with open("language_strings.json") as language_prompts:
            language_data = json.load(language_prompts)
        # set default translation data to broader translation
        if locale[:2] in language_data:
            data = language_data[locale[:2]]
            # if a more specialized translation exists, then select it instead
            # example: "fr-CA" will pick "fr" translations first, but if "fr-CA" translation exists,
            # then pick that instead
            if locale in language_data:
                data.update(language_data[locale])
        else:
            data = language_data[locale]
        handler_input.attributes_manager.request_attributes["_"] = data


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(
            HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb = CustomSkillBuilder(persistence_adapter=dynamodb_adapter)

sb.add_request_handler(AnswerHandler())
sb.add_request_handler(LaunchHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# Register request and response interceptors
sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
