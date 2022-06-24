# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:

"""
Manage the requests and responses that are part of the SmartApp lifecycle.
"""
import logging
from json import JSONDecodeError
from typing import Optional, Union

from attr import field, frozen

from .converter import CONVERTER
from .interface import (
    AbstractRequest,
    BadRequestError,
    ConfigPhase,
    ConfigurationInitResponse,
    ConfigurationPageResponse,
    ConfigurationRequest,
    ConfirmationRequest,
    ConfirmationResponse,
    EventRequest,
    EventResponse,
    InstallRequest,
    InstallResponse,
    InternalError,
    LifecycleRequest,
    LifecycleResponse,
    OauthCallbackRequest,
    OauthCallbackResponse,
    SmartAppConfigManager,
    SmartAppDefinition,
    SmartAppDispatcherConfig,
    SmartAppError,
    SmartAppEventHandler,
    SmartAppRequestContext,
    UninstallRequest,
    UninstallResponse,
    UpdateRequest,
    UpdateResponse,
)
from .signature import SignatureVerifier


@frozen(kw_only=True)
class StaticConfigManager(SmartAppConfigManager):

    """
    Configuration manager that operates on static data.

    This is the configuration manager used by default in the dispatcher.  It operates on
    a static set of config pages.  This sort of static definition is adequate for lots of
    SmartApps, but it doesn't work for some types of complex configuration, where the responses
    need to be generated dynamically.  In that case, you can implement your own configuration
    manager with that specialized behavior.
    """

    def handle_page(self, request: ConfigurationRequest, definition: SmartAppDefinition, page_id: int) -> ConfigurationPageResponse:
        """Handle a CONFIGURATION PAGE lifecycle request."""
        if not definition.config_pages:
            raise ValueError("Static configuration manager requires at least one configured page.")
        previous_page_id = None if page_id == 1 else page_id - 1
        next_page_id = None if page_id >= len(definition.config_pages) else page_id + 1
        complete = page_id >= len(definition.config_pages)
        try:
            page = definition.config_pages[page_id - 1]  # page_id is 1-based, but we need 0-based for array
            return self.build_page_response(
                name=page.page_name,
                page_id=page_id,
                previous_page_id=previous_page_id,
                next_page_id=next_page_id,
                complete=complete,
                sections=page.sections,
            )
        except IndexError as e:
            raise ValueError("Page not found: %d" % page_id) from e


@frozen(kw_only=True)
class SmartAppDispatcher:

    # noinspection PyUnresolvedReferences
    """
    Dispatcher to manage the requests and responses that are part of the SmartApp lifecycle.

    You must provide both a definition and an event handler, but in some cases the handler
    methods will probably be no-ops without any custom logic.  For more information, see
    `SmartAppEventHandler`.

    Attributes:
        definition(SmartAppDefinition): The static definition for the SmartApp
        event_handler(SmartAppEventHandler): Application event handler for SmartApp lifecycle events
    """

    definition: SmartAppDefinition
    event_handler: SmartAppEventHandler
    config: SmartAppDispatcherConfig = field(factory=SmartAppDispatcherConfig)
    manager: SmartAppConfigManager = field(factory=StaticConfigManager)

    def dispatch(self, context: SmartAppRequestContext) -> str:
        """
        Dispatch a request, responding to SmartThings and invoking callbacks as needed.

        Args:
            context(SmartAppRequestContext): The request context

        Returns:
            str: Response JSON payload that to be returned to the POST caller

        Raises:
            SmartAppError: If processing fails
        """
        try:
            if self.config.log_json:  # put this right at the top, so we've got an opportunity to debug unexpected data
                logging.debug("[%s] Raw JSON: \n%s", context.correlation_id, context.body)  # note: may contain secrets!
            request: LifecycleRequest = CONVERTER.from_json(context.body, LifecycleRequest)  # type: ignore
            logging.info("[%s] Handling %s request", context.correlation_id, request.lifecycle)
            logging.debug("[%s] Date: %s", context.correlation_id, context.date)
            logging.debug("[%s] Signature: %s", context.correlation_id, context.signature)  # note: signature not confidential
            logging.debug("[%s] Request: %s", context.correlation_id, request)  # note: secrets are not serialized in repr()
            if self.config.check_signatures:
                SignatureVerifier(context=context, config=self.config, definition=self.definition).verify()
            response = self._handle_request(context.correlation_id, request)
            return CONVERTER.to_json(response)
        except SmartAppError as e:
            raise e
        except JSONDecodeError as e:
            raise BadRequestError("Invalid JSON", context.correlation_id) from e
        except ValueError as e:
            raise BadRequestError("%s" % e, context.correlation_id) from e
        except Exception as e:  # pylint: disable=broad-except:
            raise InternalError("%s" % e, context.correlation_id) from e

    def _handle_request(self, correlation_id: Optional[str], request: AbstractRequest) -> LifecycleResponse:
        """Handle a lifecycle request, returning the appropriate response."""
        if isinstance(request, ConfirmationRequest):
            self.event_handler.handle_confirmation(correlation_id, request)
            return self._handle_confirmation_request(request)
        elif isinstance(request, ConfigurationRequest):
            self.event_handler.handle_configuration(correlation_id, request)
            return self._handle_config_request(request)
        elif isinstance(request, InstallRequest):
            self.event_handler.handle_install(correlation_id, request)
            return InstallResponse()
        elif isinstance(request, UpdateRequest):
            self.event_handler.handle_update(correlation_id, request)
            return UpdateResponse()
        elif isinstance(request, UninstallRequest):
            self.event_handler.handle_uninstall(correlation_id, request)
            return UninstallResponse()
        elif isinstance(request, OauthCallbackRequest):
            self.event_handler.handle_oauth_callback(correlation_id, request)
            return OauthCallbackResponse()
        elif isinstance(request, EventRequest):
            self.event_handler.handle_event(correlation_id, request)
            return EventResponse()
        else:
            raise ValueError("Unknown lifecycle event")

    def _handle_confirmation_request(self, request: ConfirmationRequest) -> ConfirmationResponse:
        """Handle a CONFIRMATION lifecycle request, logging data and returning an appropriate response."""
        logging.info("CONFIRMATION [%s]: [%s]", request.app_id, request.confirmation_data.confirmation_url)
        return ConfirmationResponse(target_url=self.definition.target_url)

    def _handle_config_request(self, request: ConfigurationRequest) -> Union[ConfigurationInitResponse, ConfigurationPageResponse]:
        """Handle a CONFIGURATION lifecycle request, returning an appropriate response."""
        if request.configuration_data.phase == ConfigPhase.INITIALIZE:
            return self.manager.handle_initialize(request, self.definition)
        else:  # if request.configuration_data.phase == ConfigPhase.PAGE:
            page_id = int(request.configuration_data.page_id)
            return self.manager.handle_page(request, self.definition, page_id)
