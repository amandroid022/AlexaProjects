# -*- coding: utf-8 -*-

import json
import logging
from typing import Dict, Any

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import (
    is_request_type, is_intent_name, get_supported_interfaces)
from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, AnimatedOpacityProperty, AnimateItemCommand,
    ExecuteCommandsDirective, UserEvent)
from ask_sdk_model.ui import SimpleCard

# APL Document file paths for use in handlers
hello_world_doc_path = "helloworldDocument.json"
hello_world_button_doc_path = "helloworldWithButtonDocument.json"

# Tokens used when sending the APL directives
HELLO_WORLD_TOKEN = "helloworldToken"
HELLO_WORLD_WITH_BUTTON_TOKEN = "helloworldWithButtonToken"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _load_apl_document(file_path):
    # type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)


class StartOverIntentHandler(AbstractRequestHandler):
    """Handler for StartOverIntent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.StartOverIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = None
        response_builder = handler_input.response_builder

        if get_supported_interfaces(
                handler_input).alexa_presentation_apl is not None:
            # Get the APL visual context information from the JSON request
            # and check that the document identified by the
            # HELLO_WORLD_WITH_BUTTON_TOKEN token ("helloworldWithButtonToken")
            # is currently displayed.
            context_apl = handler_input.request_envelope.context.alexa_presentation_apl
            if (context_apl is not None and
                    context_apl.token == HELLO_WORLD_WITH_BUTTON_TOKEN):
                speak_output = ("OK, I'm going to try to bring that text "
                                "back into view.")
                animate_item_command = AnimateItemCommand(
                    component_id="helloTextComponent",
                    duration=3000,
                    value=[AnimatedOpacityProperty(to=1.0)]
                )
                response_builder.add_directive(
                    ExecuteCommandsDirective(
                        token=HELLO_WORLD_WITH_BUTTON_TOKEN,
                        commands=[animate_item_command]
                    )
                )
            else:
                # Device is NOT displaying the expected document, so provide
                # relevant output speech.
                speak_output = ("Hmm, there isn't anything for me to reset. "
                                "Try invoking the 'hello world with button "
                                "intent', then click the button and see what "
                                "happens!")
        else:
            # User's device does not support APL, so tailor the speech to
            # this situation
            speak_output += ("Hello, this example would be more interesting on "
                             "a device with a screen. Try it on an Echo Show, "
                             "Echo Spot or a Fire TV device.")

        return response_builder.speak(speak_output).response


class HelloWorldButtonEventHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        # Since an APL skill might have multiple buttons that generate
        # UserEvents, use the event source ID to determine the button press
        # that triggered this event and use the correct handler.
        # In this example, the string 'fadeHelloTextButton' is the ID we set
        # on the AlexaButton in the document.

        # The user_event.source is a dict object. We can retrieve the id
        # using the get method on the dictionary.
        if is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input):
            user_event = handler_input.request_envelope.request  # type: UserEvent
            return user_event.source.get("id") == "fadeHelloTextButton"
        else:
            return False

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = ("Thank you for clicking the button! I imagine you "
                       "already noticed that the text faded away. Tell me to "
                       "start over to bring it back!")

        return handler_input.response_builder.speak(speech_text).ask(
            "Tell me to start over if you want me to bring the text back into "
            "view. Or, you can just say hello again.").response


class HelloWorldWithButtonIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("HelloWorldWithButtonIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"
        response_builder = handler_input.response_builder

        if get_supported_interfaces(
                handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_WITH_BUTTON_TOKEN,
                    document=_load_apl_document(hello_world_button_doc_path)
                )
            )
            # Tailor the speech for a device with a screen
            speak_output += (" Welcome to Alexa Presentation Language. "
                             "Click the button to see what happens!")
        else:
            # User's device does not support APL, so tailor the speech to
            # this situation
            speak_output += (" This example would be more interesting on a "
                             "device with a screen, such as an Echo Show or "
                             "Fire TV.")

        return response_builder.speak(speak_output).response


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"
        response_builder = handler_input.response_builder

        if get_supported_interfaces(
                handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                RenderDocumentDirective(
                    token=HELLO_WORLD_TOKEN,
                    document=_load_apl_document(hello_world_doc_path)
                )
            )
            # Tailor the speech for a device with a screen
            speak_output += (" You should now also see my greeting on the "
                             "screen.")
        else:
            # User's device does not support APL, so tailor the speech to
            # this situation
            speak_output += (" This example would be more interesting on a "
                             "device with a screen, such as an Echo Show or "
                             "Fire TV.")

        return response_builder.speak(speak_output).response


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome Aman, you can say Hello or Help. Which would you like to try?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class okIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("okIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello Aman ok!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CardIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CardIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speech_text = "This is the text Alexa speaks. Go to the Alexa app to see the card!"
        card_title = "This is the Title of the Card"
        card_text = "This is the card content. This card just has plain text content.\r\nThe content is formated with line breaks to improve readability."

        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(card_title, card_text)).response


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
                .ask(speak_output)
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

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

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
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelloWorldWithButtonIntentHandler())
sb.add_request_handler(HelloWorldButtonEventHandler())
sb.add_request_handler(StartOverIntentHandler())

sb.add_request_handler(okIntentHandler())
sb.add_request_handler(CardIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(
    IntentReflectorHandler())  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
