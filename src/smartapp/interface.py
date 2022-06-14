# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
# pylint: disable=line-too-long:

"""
Classes that are part of the SmartApp interface.
"""

# For lifecycle class definitions, see:
#
#   https://developer-preview.smartthings.com/docs/connected-services/lifecycles/
#   https://developer-preview.smartthings.com/docs/connected-services/configuration/
#
# I can't find any official documentation about the event structure, only the Javascript code referenced below.
# So, the structure below mostly mirrors the definitions within the AppEvent namespace, except I've excluded most enums.
# Also, there is a scene lifecycle class (but no event id), and an installed app event id (but no class), so I've ignored those.
# See: https://github.com/SmartThingsCommunity/smartapp-sdk-nodejs/blob/f1ef97ec9c6dc270ba744197b842c6632c778987/lib/lifecycle-events.d.ts

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Union

from attrs import field, frozen
from pendulum.datetime import DateTime

AUTHORIZATION_HEADER = "authorization"
CORRELATION_ID_HEADER = "x-st-correlation"


class LifecyclePhase(Enum):
    """Lifecycle phases."""

    CONFIRMATION = "CONFIRMATION"
    CONFIGURATION = "CONFIGURATION"
    INSTALL = "INSTALL"
    UPDATE = "UPDATE"
    UNINSTALL = "UNINSTALL"
    OAUTH_CALLBACK = "OAUTH_CALLBACK"
    EVENT = "EVENT"


class ConfigValueType(Enum):
    """Types of config values."""

    DEVICE = "DEVICE"
    STRING = "STRING"


class ConfigPhase(Enum):
    """Sub-phases within the CONFIGURATION phase."""

    INITIALIZE = "INITIALIZE"
    PAGE = "PAGE"


class ConfigSettingType(Enum):
    """Types of config settings."""

    DEVICE = "DEVICE"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    ENUM = "ENUM"
    LINK = "LINK"
    PAGE = "PAGE"
    IMAGE = "IMAGE"
    ICON = "ICON"
    TIME = "TIME"
    PARAGRAPH = "PARAGRAPH"
    EMAIL = "EMAIL"
    DECIMAL = "DECIMAL"
    NUMBER = "NUMBER"
    PHONE = "PHONE"
    OAUTH = "OAUTH"


class EventType(Enum):
    """Supported event types."""

    DEVICE_EVENT = "DEVICE_EVENT"
    DEVICE_LIFECYCLE_EVENT = "DEVICE_LIFECYCLE_EVENT"
    DEVICE_HEALTH_EVENT = "DEVICE_HEALTH_EVENT"
    HUB_HEALTH_EVENT = "HUB_HEALTH_EVENT"
    DEVICE_COMMANDS_EVENT = "DEVICE_COMMANDS_EVENT"
    MODE_EVENT = "MODE_EVENT"
    TIMER_EVENT = "TIMER_EVENT"
    SECURITY_ARM_STATE_EVENT = "SECURITY_ARM_STATE_EVENT"


class BooleanValue(str, Enum):
    """String boolean values."""

    TRUE = "true"
    FALSE = "false"


@frozen(kw_only=True)
class AbstractRequest(ABC):
    """Abstract parent class for all types of lifecycle requests."""

    lifecycle: LifecyclePhase
    execution_id: str
    locale: str
    version: str


@frozen(kw_only=True)
class AbstractSetting(ABC):
    """Abstract parent class for all types of config settings."""

    id: str
    name: str
    description: str
    required: Optional[bool] = False


@frozen(kw_only=True)
class DeviceSetting(AbstractSetting):
    """A DEVICE setting."""

    type: ConfigSettingType = ConfigSettingType.DEVICE
    multiple: bool
    capabilities: List[str]  # note that this is treated as AND - you'll get devices that have all capabilities
    permissions: List[str]


@frozen(kw_only=True)
class TextSetting(AbstractSetting):
    """A TEXT setting."""

    type: ConfigSettingType = ConfigSettingType.TEXT
    default_value: str


@frozen(kw_only=True)
class BooleanSetting(AbstractSetting):
    """A BOOLEAN setting."""

    type: ConfigSettingType = ConfigSettingType.BOOLEAN
    default_value: BooleanValue


@frozen(kw_only=True)
class EnumOption:
    """An option within an ENUM setting"""

    id: str
    name: str


@frozen(kw_only=True)
class EnumOptionGroup:
    """A group of options within an ENUM setting"""

    name: str
    options: List[EnumOption]


@frozen(kw_only=True)
class EnumSetting(AbstractSetting):
    """An ENUM setting."""

    type: ConfigSettingType = ConfigSettingType.ENUM
    multiple: bool
    options: Optional[List[EnumOption]] = None
    grouped_options: Optional[List[EnumOptionGroup]] = None


@frozen(kw_only=True)
class LinkSetting(AbstractSetting):
    """A LINK setting."""

    type: ConfigSettingType = ConfigSettingType.LINK
    url: str
    image: str


@frozen(kw_only=True)
class PageSetting(AbstractSetting):
    """A PAGE setting."""

    type: ConfigSettingType = ConfigSettingType.PAGE
    page: str
    image: str


@frozen(kw_only=True)
class ImageSetting(AbstractSetting):
    """An IMAGE setting."""

    type: ConfigSettingType = ConfigSettingType.IMAGE
    image: str


@frozen(kw_only=True)
class IconSetting(AbstractSetting):
    """An ICON setting."""

    type: ConfigSettingType = ConfigSettingType.ICON
    image: str


@frozen(kw_only=True)
class TimeSetting(AbstractSetting):
    """A TIME setting."""

    type: ConfigSettingType = ConfigSettingType.TIME


@frozen(kw_only=True)
class ParagraphSetting(AbstractSetting):
    """A PARAGRAPH setting."""

    type: ConfigSettingType = ConfigSettingType.PARAGRAPH
    default_value: str


@frozen(kw_only=True)
class EmailSetting(AbstractSetting):
    """An EMAIL setting."""

    type: ConfigSettingType = ConfigSettingType.EMAIL


@frozen(kw_only=True)
class DecimalSetting(AbstractSetting):
    """A DECIMAL setting."""

    type: ConfigSettingType = ConfigSettingType.DECIMAL


@frozen(kw_only=True)
class NumberSetting(AbstractSetting):
    """A NUMBER setting."""

    type: ConfigSettingType = ConfigSettingType.NUMBER


@frozen(kw_only=True)
class PhoneSetting(AbstractSetting):
    """A PHONE setting."""

    type: ConfigSettingType = ConfigSettingType.PHONE


@frozen(kw_only=True)
class OauthSetting(AbstractSetting):
    """An OAUTH setting."""

    type: ConfigSettingType = ConfigSettingType.OAUTH
    browser: bool
    url_template: str


ConfigSetting = Union[
    DeviceSetting,
    TextSetting,
    BooleanSetting,
    EnumSetting,
    LinkSetting,
    PageSetting,
    ImageSetting,
    IconSetting,
    TimeSetting,
    ParagraphSetting,
    EmailSetting,
    DecimalSetting,
    NumberSetting,
    PhoneSetting,
    OauthSetting,
]


@frozen(kw_only=True)
class DeviceValue:
    device_id: str
    component_id: str


@frozen(kw_only=True)
class DeviceConfigValue:
    """DEVICE configuration value."""

    device_config: DeviceValue
    value_type: ConfigValueType = ConfigValueType.DEVICE


@frozen(kw_only=True)
class StringValue:
    value: str


@frozen(kw_only=True)
class StringConfigValue:
    """STRING configuration value."""

    string_config: StringValue
    value_type: ConfigValueType = ConfigValueType.STRING


ConfigValue = Union[
    DeviceConfigValue,
    StringConfigValue,
]


@frozen(kw_only=True)
class InstalledApp:
    """Installed application."""

    installed_app_id: str
    location_id: str
    config: Dict[str, List[ConfigValue]]
    permissions: List[str] = field(factory=list)


@frozen(kw_only=True)
class DeviceEvent:
    """A device event."""

    subscription_name: str
    event_id: str
    location_id: str
    device_id: str
    component_id: str
    capability: str
    attribute: str
    value: str
    state_change: bool
    data: Optional[Dict[str, Any]] = None


class DeviceLifecycleEvent:
    """A device lifecycle event."""

    lifecycle: str
    event_id: str
    location_id: str
    device_id: str
    device_name: str
    principal: str


@frozen(kw_only=True)
class DeviceHealthEvent:
    event_id: str
    location_id: str
    device_id: str
    hub_id: str
    status: str
    reason: str


@frozen(kw_only=True)
class HubHealthEvent:
    event_id: str
    location_id: str
    hub_id: str
    status: str
    reason: str


@frozen(kw_only=True)
class DeviceCommand:
    component_id: str
    capability: str
    command: str
    arguments: List[Any]  # TODO: exactly what do we get here?  Seems like this is too generic?


@frozen(kw_only=True)
class DeviceCommandsEvent:
    event_id: str
    device_id: str
    profile_id: str
    external_id: str
    commands: List[DeviceCommand]


@frozen(kw_only=True)
class ModeEvent:
    event_id: str
    location_id: str
    mode_id: str


@frozen(kw_only=True)
class TimerEvent:
    event_id: str
    name: str
    type: str
    time: DateTime
    expression: str


@frozen(kw_only=True)
class SecurityArmStateEvent:
    event_id: str
    location_id: str
    arm_state: str
    optional_arguments: Dict[str, Any]


@frozen(kw_only=True)
class Event:
    """Holds the triggered event, one of several different attributes depending on event type."""

    event_type: EventType
    event_time: Optional[DateTime] = None
    device_event: Optional[DeviceEvent] = None
    device_lifecycle_event: Optional[DeviceLifecycleEvent] = None
    device_health_event: Optional[DeviceHealthEvent] = None
    device_commands_event: Optional[DeviceCommandsEvent] = None
    mode_event: Optional[ModeEvent] = None
    timer_event: Optional[TimerEvent] = None
    security_arm_state_event: Optional[SecurityArmStateEvent] = None


@frozen(kw_only=True)
class ConfirmationData:
    """Confirmation data."""

    app_id: str
    confirmation_url: str


@frozen(kw_only=True)
class ConfigInit:
    """Initialization data."""

    id: str
    name: str
    description: str
    permissions: List[str]
    first_page_id: str


@frozen(kw_only=True)
class ConfigRequestData:
    """Configuration data provided on the request."""

    installed_app_id: str
    phase: ConfigPhase
    page_id: str
    previous_page_id: str
    config: Dict[str, List[ConfigValue]]


@frozen(kw_only=True)
class ConfigInitData:
    """Configuration data provided in an INITIALIZATION response."""

    initialize: ConfigInit


@frozen(kw_only=True)
class ConfigSection:
    """A section within a configuration page."""

    name: str
    settings: List[ConfigSetting]


@frozen(kw_only=True)
class ConfigPage:
    """A page of configuration data for the CONFIGURATION phase."""

    page_id: str
    name: str
    previous_page_id: Optional[str]
    next_page_id: Optional[str]
    complete: bool
    sections: List[ConfigSection]


@frozen(kw_only=True)
class ConfigPageData:
    """Configuration data provided in an PAGE response."""

    page: ConfigPage


@frozen(kw_only=True)
class InstallData:
    """Install data."""

    # note: auth_token and refresh_token are secrets, so we don't include them in string output

    auth_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    installed_app: InstalledApp


@frozen(kw_only=True)
class UpdateData:
    """Update data."""

    # note: auth_token and refresh_token are secrets, so we don't include them in string output

    auth_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    installed_app: InstalledApp
    previous_config: Optional[Dict[str, List[ConfigValue]]] = None
    previous_permissions: List[str] = field(factory=list)


@frozen(kw_only=True)
class UninstallData:
    """Install data."""

    installed_app: InstalledApp


@frozen(kw_only=True)
class OauthCallbackData:
    installed_app_id: str
    url_path: str


@frozen(kw_only=True)
class EventData:
    """Event data."""

    # note: auth_token is a secret, so we don't include it in string output

    auth_token: str = field(repr=False)
    installed_app: InstalledApp
    events: List[Event]


@frozen(kw_only=True)
class ConfirmationRequest(AbstractRequest):
    """Request for CONFIRMATION phase"""

    app_id: str
    confirmation_data: ConfirmationData
    settings: Dict[str, Any] = field(factory=dict)


@frozen(kw_only=True)
class ConfirmationResponse:
    """Response for CONFIRMATION phase"""

    target_url: str


@frozen(kw_only=True)
class ConfigurationRequest(AbstractRequest):
    """Request for CONFIGURATION phase"""

    configuration_data: ConfigRequestData
    settings: Dict[str, Any] = field(factory=dict)


@frozen(kw_only=True)
class ConfigurationInitResponse:
    """Response for CONFIGURATION/INITIALIZE phase"""

    configuration_data: ConfigInitData


@frozen(kw_only=True)
class ConfigurationPageResponse:
    """Response for CONFIGURATION/PAGE phase"""

    configuration_data: ConfigPageData


@frozen(kw_only=True)
class InstallRequest(AbstractRequest):
    """Request for INSTALL phase"""

    install_data: InstallData
    settings: Dict[str, Any] = field(factory=dict)


@frozen(kw_only=True)
class InstallResponse:
    """Response for INSTALL phase"""

    install_data: Dict[str, Any] = field(factory=dict)  # always empty in the response


@frozen(kw_only=True)
class UpdateRequest(AbstractRequest):
    """Request for UPDATE phase"""

    update_data: UpdateData
    settings: Dict[str, Any] = field(factory=dict)


@frozen(kw_only=True)
class UpdateResponse:
    """Response for UPDATE phase"""

    update_data: Dict[str, Any] = field(factory=dict)  # always empty in the response


@frozen(kw_only=True)
class UninstallRequest(AbstractRequest):
    """Request for UNINSTALL phase"""

    uninstall_data: UninstallData
    settings: Dict[str, Any] = field(factory=dict)


@frozen(kw_only=True)
class UninstallResponse:
    """Response for UNINSTALL phase"""

    uninstall_data: Dict[str, Any] = field(factory=dict)  # always empty in the response


@frozen(kw_only=True)
class OauthCallbackRequest(AbstractRequest):
    """Request for OAUTH_CALLBACK phase"""

    o_auth_callback_data: OauthCallbackData


@frozen(kw_only=True)
class OauthCallbackResponse:
    """Response for OAUTH_CALLBACK phase"""

    o_auth_callback_data: Dict[str, Any] = field(factory=dict)  # always empty in the response


@frozen(kw_only=True)
class EventRequest(AbstractRequest):
    """Request for EVENT phase"""

    event_data: EventData
    settings: Dict[str, Any] = field(factory=dict)


@frozen(kw_only=True)
class EventResponse:
    """Response for EVENT phase"""

    event_data: Dict[str, Any] = field(factory=dict)  # always empty in the response


LifecycleRequest = Union[
    ConfigurationRequest,
    ConfirmationRequest,
    InstallRequest,
    UpdateRequest,
    UninstallRequest,
    OauthCallbackRequest,
    EventRequest,
]

LifecycleResponse = Union[
    ConfigurationInitResponse,
    ConfigurationPageResponse,
    ConfirmationResponse,
    InstallResponse,
    UpdateResponse,
    UninstallResponse,
    OauthCallbackResponse,
    EventResponse,
]

REQUEST_BY_PHASE = {
    LifecyclePhase.CONFIGURATION: ConfigurationRequest,
    LifecyclePhase.CONFIRMATION: ConfirmationRequest,
    LifecyclePhase.INSTALL: InstallRequest,
    LifecyclePhase.UPDATE: UpdateRequest,
    LifecyclePhase.UNINSTALL: UninstallRequest,
    LifecyclePhase.OAUTH_CALLBACK: OauthCallbackRequest,
    LifecyclePhase.EVENT: EventRequest,
}

CONFIG_VALUE_BY_TYPE = {
    ConfigValueType.DEVICE: DeviceConfigValue,
    ConfigValueType.STRING: StringConfigValue,
}

CONFIG_SETTING_BY_TYPE = {
    ConfigSettingType.DEVICE: DeviceSetting,
    ConfigSettingType.TEXT: TextSetting,
    ConfigSettingType.BOOLEAN: BooleanSetting,
    ConfigSettingType.ENUM: EnumSetting,
    ConfigSettingType.LINK: LinkSetting,
    ConfigSettingType.PAGE: PageSetting,
    ConfigSettingType.IMAGE: ImageSetting,
    ConfigSettingType.ICON: IconSetting,
    ConfigSettingType.TIME: TimeSetting,
    ConfigSettingType.PARAGRAPH: ParagraphSetting,
    ConfigSettingType.EMAIL: EmailSetting,
    ConfigSettingType.DECIMAL: DecimalSetting,
    ConfigSettingType.NUMBER: NumberSetting,
    ConfigSettingType.PHONE: PhoneSetting,
    ConfigSettingType.OAUTH: OauthSetting,
}


class SmartAppError(Exception):
    """An error tied to the SmartApp implementation."""

    def __init__(self, message: str, correlation_id: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.correlation_id = correlation_id


class InternalError(SmartAppError):
    """An internal error was encountered processing a lifecycle event."""


class BadRequestError(SmartAppError):
    """A lifecycle event was invalid."""


class SignatureError(SmartAppError):
    """The request signature on a lifecycle event was invalid."""


@frozen(kw_only=True)
class SmartAppDispatcherConfig:

    # noinspection PyUnresolvedReferences
    """
    Configuration for the SmartAppDispatcher.

    Any production SmartApp should always check signatures.  We support disabling that feature
    to make local testing easier during development.

    Attributes:
        check_signatures(bool): Whether to check the digital signature on lifecycle requests
        clock_skew_sec(int): Amount of clock skew allowed when verifying digital signatures, or None to allow any skew
    """

    check_signatures: bool = True
    clock_skew_sec: Optional[int] = 300
    key_server_url: str = "https://key.smartthings.com"


class SmartAppEventHandler(ABC):
    """
    Application event handler for SmartApp lifecycle events.

    Inherit from this class to implement your own application-specific event handler.
    The application-specific event handler is always called first, before any default
    event handler logic in the dispatcher itself.

    The correlation id is an optional value that you can associate with your log messages.
    It may aid in debugging if you need to contact SmartThings for support.

    Some lifecycle events do not require you to implement any custom event handler logic:

    - CONFIRMATION: normally no callback needed, since the dispatcher logs the app id and confirmation URL
    - CONFIGURATION: normally no callback needed, since the dispatcher has the information it needs to respond
    - INSTALL/UPDATE: set up or replace subscriptions and schedules and persist required data, if any
    - UNINSTALL: remove persisted data, if any
    - OAUTH_CALLBACK: coordinate with your oauth provider as needed
    - EVENT: handle SmartThings events or scheduled triggers

    The EventRequest object that you receive for the EVENT callback includes an
    authorization token and also the entire configuration bundle for the installed
    application.  So, if your SmartApp is built around event handling and scheduled
    actions triggered by SmartThings, your handler can probably be stateless.  There is
    probably is not any need to persist any of the data returned in the INSTALL or UPDATE
    lifecycle events into your own data store.

    Note that SmartAppHandler is a synchronous and single-threaded interface.  The
    assumption is that if you need high-volume asynchronous or multi-threaded processing,
    you will implement that at the tier above this where the actual POST requests are
    accepted from remote callers.
    """

    @abstractmethod
    def handle_confirmation(self, correlation_id: Optional[str], request: ConfirmationRequest) -> None:
        """Handle a CONFIRMATION lifecycle request"""

    @abstractmethod
    def handle_configuration(self, correlation_id: Optional[str], request: ConfigurationRequest) -> None:
        """Handle a CONFIGURATION lifecycle request."""

    @abstractmethod
    def handle_install(self, correlation_id: Optional[str], request: InstallRequest) -> None:
        """Handle an INSTALL lifecycle request."""

    @abstractmethod
    def handle_update(self, correlation_id: Optional[str], request: UpdateRequest) -> None:
        """Handle an UPDATE lifecycle request."""

    @abstractmethod
    def handle_uninstall(self, correlation_id: Optional[str], request: UninstallRequest) -> None:
        """Handle an UNINSTALL lifecycle request."""

    @abstractmethod
    def handle_oauth_callback(self, correlation_id: Optional[str], request: OauthCallbackRequest) -> None:
        """Handle an OAUTH_CALLBACK lifecycle request."""

    @abstractmethod
    def handle_event(self, correlation_id: Optional[str], request: EventRequest) -> None:
        """Handle an EVENT lifecycle request."""


@frozen(kw_only=True)
class SmartAppConfigPage:
    """
    A page of configuration for the SmartApp.
    """

    page_name: str
    sections: List[ConfigSection]


@frozen(kw_only=True)
class SmartAppDefinition:

    # noinspection PyUnresolvedReferences
    """
    The definition of the SmartApp.

    All of this data would normally be static for any given version of your application.
    If you wish, you can maintain the definition in YAML or JSON in your source tree
    and parse it with `smartapp.converter.CONVERTER`.

    Keep in mind that the JSON or YAML format on disk will be consistent with the SmartThings
    lifecycle API, so it will use camel case attribute names (like `configPages`) rather than
    the Python attribute names you see in source code (like `config_pages`).

    Attributes:
        id(str): Identifier for this SmartApp
        name(str): Name of the SmartApp
        description(str): Description of the SmartApp
        permissions(List[str]): Permissions that the SmartApp requires
        config_pages(List[SmartAppConfigPage]): Configuration pages that the SmartApp will offer users
    """
    id: str
    name: str
    description: str
    target_url: str
    permissions: List[str]
    config_pages: List[SmartAppConfigPage]


@frozen(kw_only=True)
class SmartAppRequestContext:

    # noinspection PyUnresolvedReferences
    """
    The context for a SmartApp lifecycle request.

    Attributes:
        method(str): The request method, typically "POST"
        path(str): The request path that was used to invoke the endpoint
        headers(Mapping[str, str]): The request headers, assumed to be accessible in case-insenstive fashion
        body(str): The body of the request as string
    """

    headers: Mapping[str, str] = field(factory=dict)
    body: str = ""

    @property
    def correlation_id(self) -> Optional[str]:
        """Return the correlation id, if set."""
        return self.headers[CORRELATION_ID_HEADER] if CORRELATION_ID_HEADER in self.headers else None
