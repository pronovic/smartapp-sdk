# vim: set ft=python ts=4 sw=4 expandtab:

"""
Classes that are part of the SmartApp interface.
"""

# For lifecycle class definitions, see:
#
#   https://developer-preview.smartthings.com/docs/connected-services/lifecycles/
#   https://developer-preview.smartthings.com/docs/connected-services/configuration/
#
# There is not any public documentation about event structure, only the Javascript
# reference implementation here:
#
#   https://github.com/SmartThingsCommunity/smartapp-sdk-nodejs/blob/f1ef97ec9c6dc270ba744197b842c6632c778987/lib/lifecycle-events.d.ts
#
# However, as of this writitng, even that reference implementation is not fully up-to-date
# with the JSON that is being returned for some events I have examined in my testing.
#
# I have access to private documentation that shows all of the attributes.  However, that
# documentation doesn't always make it clear which attributes will always be included and
# which are optional.  As compromise, I have decided to maintain the actual events as
# dicts rather than true objects.  See further discussion below by the Event class.

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from enum import Enum, StrEnum
from typing import Any, assert_never

from arrow import Arrow
from attrs import field, frozen

AUTHORIZATION_HEADER = "authorization"
CORRELATION_ID_HEADER = "x-st-correlation"
DATE_HEADER = "date"


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

    DEVICE_COMMANDS_EVENT = "DEVICE_COMMANDS_EVENT"
    DEVICE_EVENT = "DEVICE_EVENT"
    DEVICE_HEALTH_EVENT = "DEVICE_HEALTH_EVENT"
    DEVICE_LIFECYCLE_EVENT = "DEVICE_LIFECYCLE_EVENT"
    HUB_HEALTH_EVENT = "HUB_HEALTH_EVENT"
    INSTALLED_APP_LIFECYCLE_EVENT = "INSTALLED_APP_LIFECYCLE_EVENT"
    MODE_EVENT = "MODE_EVENT"
    SCENE_LIFECYCLE_EVENT = "SCENE_LIFECYCLE_EVENT"
    SECURITY_ARM_STATE_EVENT = "SECURITY_ARM_STATE_EVENT"
    TIMER_EVENT = "TIMER_EVENT"
    WEATHER_EVENT = "WEATHER_EVENT"


class SubscriptionType(Enum):
    """Supported subscription types."""

    DEVICE = "DEVICE"
    CAPABILITY = "CAPABILITY"
    MODE = "MODE"
    DEVICE_LIFECYCLE = "DEVICE_LIFECYCLE"
    DEVICE_HEALTH = "DEVICE_HEALTH"
    SECURITY_ARM_STATE = "SECURITY_ARM_STATE"
    HUB_HEALTH = "HUB_HEALTH"
    SCENE_LIFECYCLE = "SCENE_LIFECYCLE"


class BooleanValue(StrEnum):
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
    required: bool | None = False


@frozen(kw_only=True)
class DeviceSetting(AbstractSetting):
    """A DEVICE setting."""

    type: ConfigSettingType = ConfigSettingType.DEVICE
    multiple: bool
    capabilities: list[str]  # note that this is treated as AND - you'll get devices that have all capabilities
    permissions: list[str]


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
    options: list[EnumOption]


@frozen(kw_only=True)
class EnumSetting(AbstractSetting):
    """An ENUM setting."""

    type: ConfigSettingType = ConfigSettingType.ENUM
    multiple: bool
    options: list[EnumOption] | None = None
    grouped_options: list[EnumOptionGroup] | None = None


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


ConfigSetting = (
    DeviceSetting
    | TextSetting
    | BooleanSetting
    | EnumSetting
    | LinkSetting
    | PageSetting
    | ImageSetting
    | IconSetting
    | TimeSetting
    | ParagraphSetting
    | EmailSetting
    | DecimalSetting
    | NumberSetting
    | PhoneSetting
    | OauthSetting
)


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


ConfigValue = DeviceConfigValue | StringConfigValue


@frozen(kw_only=True)
class InstalledApp:
    """Installed application."""

    installed_app_id: str
    location_id: str
    config: dict[str, list[ConfigValue]]
    permissions: list[str] = field(factory=list)

    def as_devices(self, key: str) -> list[DeviceValue]:
        """Return a list of devices for a named configuration value."""
        return [item.device_config for item in self.config[key]]  # type: ignore[union-attr]

    def as_str(self, key: str) -> str:
        """Return a named configuration value, interpreted as a string"""
        return self.config[key][0].string_config.value  # type: ignore[union-attr]

    def as_bool(self, key: str) -> bool:
        """Return a named configuration value, interpreted as a boolean"""
        return bool(self.as_str(key))

    def as_int(self, key: str) -> int:
        """Return a named configuration value, interpreted as an integer"""
        return int(self.as_str(key))

    def as_float(self, key: str) -> float:
        """Return a named configuration value, interpreted as a float"""
        return float(self.as_str(key))


@frozen(kw_only=True)
class Event:
    """Holds the triggered event, one of several different attributes depending on event type."""

    event_time: Arrow | None = None
    event_type: EventType
    device_event: dict[str, Any] | None = None
    device_lifecycle_event: dict[str, Any] | None = None
    device_health_event: dict[str, Any] | None = None
    device_commands_event: dict[str, Any] | None = None
    mode_event: dict[str, Any] | None = None
    timer_event: dict[str, Any] | None = None
    scene_lifecycle_event: dict[str, Any] | None = None
    security_arm_state_event: dict[str, Any] | None = None
    hub_health_event: dict[str, Any] | None = None
    installed_app_lifecycle_event: dict[str, Any] | None = None
    weather_event: dict[str, Any] | None = None
    weather_data: dict[str, Any] | None = None
    air_quality_data: dict[str, Any] | None = None

    # noinspection PyUnreachableCode
    def for_type(self, event_type: EventType) -> dict[str, Any] | None:  # noqa: PLR0911
        """Return the attribute associated with an event type."""
        if event_type == EventType.DEVICE_COMMANDS_EVENT:
            return self.device_commands_event
        if event_type == EventType.DEVICE_EVENT:
            return self.device_event
        if event_type == EventType.DEVICE_HEALTH_EVENT:
            return self.device_health_event
        if event_type == EventType.DEVICE_LIFECYCLE_EVENT:
            return self.device_lifecycle_event
        if event_type == EventType.HUB_HEALTH_EVENT:
            return self.hub_health_event
        if event_type == EventType.INSTALLED_APP_LIFECYCLE_EVENT:
            return self.installed_app_lifecycle_event
        if event_type == EventType.MODE_EVENT:
            return self.mode_event
        if event_type == EventType.SCENE_LIFECYCLE_EVENT:
            return self.scene_lifecycle_event
        if event_type == EventType.SECURITY_ARM_STATE_EVENT:
            return self.security_arm_state_event
        if event_type == EventType.TIMER_EVENT:
            return self.timer_event
        if event_type == EventType.WEATHER_EVENT:
            return self.weather_event
        assert_never(event_type)


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
    permissions: list[str]
    first_page_id: str


@frozen(kw_only=True)
class ConfigRequestData:
    """Configuration data provided on the request."""

    installed_app_id: str
    phase: ConfigPhase
    page_id: str
    previous_page_id: str
    config: dict[str, list[ConfigValue]]


@frozen(kw_only=True)
class ConfigInitData:
    """Configuration data provided in an INITIALIZATION response."""

    initialize: ConfigInit


@frozen(kw_only=True)
class ConfigSection:
    """A section within a configuration page."""

    name: str
    settings: list[ConfigSetting]


@frozen(kw_only=True)
class ConfigPage:
    """A page of configuration data for the CONFIGURATION phase."""

    page_id: str
    name: str
    previous_page_id: str | None
    next_page_id: str | None
    complete: bool
    sections: list[ConfigSection]


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

    def token(self) -> str:
        """Return the auth token associated with this request."""
        return self.auth_token

    def app_id(self) -> str:
        """Return the installed application id associated with this request."""
        return self.installed_app.installed_app_id

    def location_id(self) -> str:
        """Return the installed location id associated with this request."""
        return self.installed_app.location_id

    def as_devices(self, key: str) -> list[DeviceValue]:
        """Return a list of devices for a named configuration value."""
        return self.installed_app.as_devices(key)

    def as_str(self, key: str) -> str:
        """Return a named configuration value, interpreted as a string"""
        return self.installed_app.as_str(key)

    def as_bool(self, key: str) -> bool:
        """Return a named configuration value, interpreted as a boolean"""
        return self.installed_app.as_bool(key)

    def as_int(self, key: str) -> int:
        """Return a named configuration value, interpreted as an integer"""
        return self.installed_app.as_int(key)

    def as_float(self, key: str) -> float:
        """Return a named configuration value, interpreted as a float"""
        return self.installed_app.as_float(key)


@frozen(kw_only=True)
class UpdateData:
    """Update data."""

    # note: auth_token and refresh_token are secrets, so we don't include them in string output

    auth_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    installed_app: InstalledApp
    previous_config: dict[str, list[ConfigValue]] | None = None
    previous_permissions: list[str] = field(factory=list)

    def token(self) -> str:
        """Return the auth token associated with this request."""
        return self.auth_token

    def app_id(self) -> str:
        """Return the installed application id associated with this request."""
        return self.installed_app.installed_app_id

    def location_id(self) -> str:
        """Return the installed location id associated with this request."""
        return self.installed_app.location_id

    def as_devices(self, key: str) -> list[DeviceValue]:
        """Return a list of devices for a named configuration value."""
        return self.installed_app.as_devices(key)

    def as_str(self, key: str) -> str:
        """Return a named configuration value, interpreted as a string"""
        return self.installed_app.as_str(key)

    def as_bool(self, key: str) -> bool:
        """Return a named configuration value, interpreted as a boolean"""
        return self.installed_app.as_bool(key)

    def as_int(self, key: str) -> int:
        """Return a named configuration value, interpreted as an integer"""
        return self.installed_app.as_int(key)

    def as_float(self, key: str) -> float:
        """Return a named configuration value, interpreted as a float"""
        return self.installed_app.as_float(key)


@frozen(kw_only=True)
class UninstallData:
    """Install data."""

    installed_app: InstalledApp

    def app_id(self) -> str:
        """Return the installed application id associated with this request."""
        return self.installed_app.installed_app_id

    def location_id(self) -> str:
        """Return the installed location id associated with this request."""
        return self.installed_app.location_id


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
    events: list[Event]

    def token(self) -> str:
        """Return the auth token associated with this request."""
        return self.auth_token

    def app_id(self) -> str:
        """Return the installed application id associated with this request."""
        return self.installed_app.installed_app_id

    def location_id(self) -> str:
        """Return the installed location id associated with this request."""
        return self.installed_app.location_id

    def for_type(self, event_type: EventType) -> list[dict[str, Any]]:
        """Get all events for a particular event type, possibly empty."""
        return [
            event.for_type(event_type)  # type: ignore[misc]
            for event in self.events
            if event.event_type == event_type and event.for_type(event_type) is not None
        ]

    def filter(self, event_type: EventType, predicate: Callable[[dict[str, Any]], bool] | None = None) -> list[dict[str, Any]]:
        """Apply a filter to a set of events with a particular event type."""
        return list(filter(predicate, self.for_type(event_type)))


@frozen(kw_only=True)
class ConfirmationRequest(AbstractRequest):
    """Request for CONFIRMATION phase"""

    app_id: str
    confirmation_data: ConfirmationData
    settings: dict[str, Any] = field(factory=dict)


@frozen(kw_only=True)
class ConfirmationResponse:
    """Response for CONFIRMATION phase"""

    target_url: str


@frozen(kw_only=True)
class ConfigurationRequest(AbstractRequest):
    """Request for CONFIGURATION phase"""

    configuration_data: ConfigRequestData
    settings: dict[str, Any] = field(factory=dict)


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
    settings: dict[str, Any] = field(factory=dict)

    def token(self) -> str:
        """Return the auth token associated with this request."""
        return self.install_data.token()

    def app_id(self) -> str:
        """Return the installed application id associated with this request."""
        return self.install_data.app_id()

    def location_id(self) -> str:
        """Return the installed location id associated with this request."""
        return self.install_data.location_id()

    def as_devices(self, key: str) -> list[DeviceValue]:
        """Return a list of devices for a named configuration value."""
        return self.install_data.as_devices(key)

    def as_str(self, key: str) -> str:
        """Return a named configuration value, interpreted as a string"""
        return self.install_data.as_str(key)

    def as_bool(self, key: str) -> bool:
        """Return a named configuration value, interpreted as a boolean"""
        return self.install_data.as_bool(key)

    def as_int(self, key: str) -> int:
        """Return a named configuration value, interpreted as an integer"""
        return self.install_data.as_int(key)

    def as_float(self, key: str) -> float:
        """Return a named configuration value, interpreted as a float"""
        return self.install_data.as_float(key)


@frozen(kw_only=True)
class InstallResponse:
    """Response for INSTALL phase"""

    install_data: dict[str, Any] = field(factory=dict)  # always empty in the response


@frozen(kw_only=True)
class UpdateRequest(AbstractRequest):
    """Request for UPDATE phase"""

    update_data: UpdateData
    settings: dict[str, Any] = field(factory=dict)

    def token(self) -> str:
        """Return the auth token associated with this request."""
        return self.update_data.token()

    def app_id(self) -> str:
        """Return the installed application id associated with this request."""
        return self.update_data.app_id()

    def location_id(self) -> str:
        """Return the installed location id associated with this request."""
        return self.update_data.location_id()

    def as_devices(self, key: str) -> list[DeviceValue]:
        """Return a list of devices for a named configuration value."""
        return self.update_data.as_devices(key)

    def as_str(self, key: str) -> str:
        """Return a named configuration value, interpreted as a string"""
        return self.update_data.as_str(key)

    def as_bool(self, key: str) -> bool:
        """Return a named configuration value, interpreted as a boolean"""
        return self.update_data.as_bool(key)

    def as_int(self, key: str) -> int:
        """Return a named configuration value, interpreted as an integer"""
        return self.update_data.as_int(key)

    def as_float(self, key: str) -> float:
        """Return a named configuration value, interpreted as a float"""
        return self.update_data.as_float(key)


@frozen(kw_only=True)
class UpdateResponse:
    """Response for UPDATE phase"""

    update_data: dict[str, Any] = field(factory=dict)  # always empty in the response


@frozen(kw_only=True)
class UninstallRequest(AbstractRequest):
    """Request for UNINSTALL phase"""

    uninstall_data: UninstallData
    settings: dict[str, Any] = field(factory=dict)

    def app_id(self) -> str:
        """Return the installed application id associated with this request."""
        return self.uninstall_data.app_id()

    def location_id(self) -> str:
        """Return the installed location id associated with this request."""
        return self.uninstall_data.location_id()


@frozen(kw_only=True)
class UninstallResponse:
    """Response for UNINSTALL phase"""

    uninstall_data: dict[str, Any] = field(factory=dict)  # always empty in the response


@frozen(kw_only=True)
class OauthCallbackRequest(AbstractRequest):
    """Request for OAUTH_CALLBACK phase"""

    o_auth_callback_data: OauthCallbackData


@frozen(kw_only=True)
class OauthCallbackResponse:
    """Response for OAUTH_CALLBACK phase"""

    o_auth_callback_data: dict[str, Any] = field(factory=dict)  # always empty in the response


@frozen(kw_only=True)
class EventRequest(AbstractRequest):
    """Request for EVENT phase"""

    event_data: EventData
    settings: dict[str, Any] = field(factory=dict)

    def token(self) -> str:
        """Return the auth token associated with this request."""
        return self.event_data.token()

    def app_id(self) -> str:
        """Return the installed application id associated with this request."""
        return self.event_data.app_id()

    def location_id(self) -> str:
        """Return the installed location id associated with this request."""
        return self.event_data.location_id()


@frozen(kw_only=True)
class EventResponse:
    """Response for EVENT phase"""

    event_data: dict[str, Any] = field(factory=dict)  # always empty in the response


LifecycleRequest = (
    ConfigurationRequest
    | ConfirmationRequest
    | InstallRequest
    | UpdateRequest
    | UninstallRequest
    | OauthCallbackRequest
    | EventRequest
)


LifecycleResponse = (
    ConfigurationInitResponse
    | ConfigurationPageResponse
    | ConfirmationResponse
    | InstallResponse
    | UpdateResponse
    | UninstallResponse
    | OauthCallbackResponse
    | EventResponse
)


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


@frozen
class SmartAppError(Exception):
    """An error tied to the SmartApp implementation."""

    message: str
    correlation_id: str | None = None


@frozen
class InternalError(SmartAppError):
    """An internal error was encountered processing a lifecycle event."""


@frozen
class BadRequestError(SmartAppError):
    """A lifecycle event was invalid."""


@frozen
class SignatureError(SmartAppError):
    """The request signature on a lifecycle event was invalid."""


@frozen(kw_only=True)
class SmartAppDispatcherConfig:
    # noinspection PyUnresolvedReferences
    """
    Configuration for the SmartAppDispatcher.

    Any production SmartApp should always check signatures.  We support disabling that feature
    to make local testing easier during development.

    BEWARE: setting `log_json` to `True` will potentially place secrets (such as authorization
    keys) in your logs.  This is intended for use during development and debugging only.

    Attributes:
        check_signatures(bool): Whether to check the digital signature on lifecycle requests
        clock_skew_sec(int): Amount of clock skew allowed when verifying digital signatures, or None to allow any skew
        keyserver_url(str): The SmartThings keyserver URL, where we retrieve keys for signature checks
        log_json(bool): Whether to log JSON data at DEBUG level when processing requests
    """

    check_signatures: bool = True
    clock_skew_sec: int | None = 300
    keyserver_url: str = "https://key.smartthings.com"
    log_json: bool = False


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
    def handle_confirmation(self, correlation_id: str | None, request: ConfirmationRequest) -> None:
        """Handle a CONFIRMATION lifecycle request"""

    @abstractmethod
    def handle_configuration(self, correlation_id: str | None, request: ConfigurationRequest) -> None:
        """Handle a CONFIGURATION lifecycle request."""

    @abstractmethod
    def handle_install(self, correlation_id: str | None, request: InstallRequest) -> None:
        """Handle an INSTALL lifecycle request."""

    @abstractmethod
    def handle_update(self, correlation_id: str | None, request: UpdateRequest) -> None:
        """Handle an UPDATE lifecycle request."""

    @abstractmethod
    def handle_uninstall(self, correlation_id: str | None, request: UninstallRequest) -> None:
        """Handle an UNINSTALL lifecycle request."""

    @abstractmethod
    def handle_oauth_callback(self, correlation_id: str | None, request: OauthCallbackRequest) -> None:
        """Handle an OAUTH_CALLBACK lifecycle request."""

    @abstractmethod
    def handle_event(self, correlation_id: str | None, request: EventRequest) -> None:
        """Handle an EVENT lifecycle request."""


@frozen(kw_only=True)
class SmartAppConfigPage:
    """
    A page of configuration for the SmartApp.
    """

    page_name: str
    sections: list[ConfigSection]


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
    permissions: list[str]
    config_pages: list[SmartAppConfigPage] | None


# noinspection PyShadowingBuiltins,PyMethodMayBeStatic
class SmartAppConfigManager(ABC):
    """
    Configuration manager, used by the dispatcher to respond to CONFIGURATION events.

    The dispatcher has a default configuration manager.  However, you can implement your
    own if that default behavior does not meet your needs.  For instance, a static config
    definition is adequate for lots of SmartApps, but it doesn't work for some types of
    complex configuration, where the responses need to be generated dynamically.  In that
    case, you can implement your own configuration manager with that specialized behavior.

    This abstract class also includes several convenience methods to make it easier to
    build responses.
    """

    def handle_initialize(self, _request: ConfigurationRequest, definition: SmartAppDefinition) -> ConfigurationInitResponse:
        """Handle a CONFIGURATION INITIALIZE lifecycle request."""
        return self.build_init_response(
            id=definition.id,
            name=definition.name,
            description=definition.description,
            permissions=definition.permissions,
            first_page_id=1,
        )

    @abstractmethod
    def handle_page(self, request: ConfigurationRequest, definition: SmartAppDefinition, page_id: int) -> ConfigurationPageResponse:
        """Handle a CONFIGURATION PAGE lifecycle request."""

    def build_init_response(  # noqa: PLR6301
        self,
        id: str,  # noqa: A002
        name: str,
        description: str,
        permissions: list[str],
        first_page_id: int,
    ) -> ConfigurationInitResponse:
        """Build a ConfigurationInitResponse."""
        return ConfigurationInitResponse(
            configuration_data=ConfigInitData(
                initialize=ConfigInit(
                    id=id,
                    name=name,
                    description=description,
                    permissions=permissions,
                    first_page_id=str(first_page_id),
                )
            )
        )

    def build_page_response(  # noqa: PLR0913,PLR0917,PLR6301
        self,
        page_id: int,
        name: str,
        previous_page_id: int | None,
        next_page_id: int | None,
        complete: bool,  # noqa: FBT001
        sections: list[ConfigSection],
    ) -> ConfigurationPageResponse:
        """Build a ConfigurationPageResponse."""
        return ConfigurationPageResponse(
            configuration_data=ConfigPageData(
                page=ConfigPage(
                    name=name,
                    page_id=str(page_id),
                    previous_page_id=str(previous_page_id) if previous_page_id else None,
                    next_page_id=str(next_page_id) if next_page_id else None,
                    complete=complete,
                    sections=sections,
                )
            )
        )


# noinspection PyUnresolvedReferences
@frozen(kw_only=True)
class SmartAppRequestContext:
    """
    The context for a SmartApp lifecycle request.

    Attributes:
        headers(Mapping[str, str]): The request headers
        body(str): The body of the request as string
    """

    # I'm pulling out the correlation id, signature, and date because they are 3 specific
    # headers that I know the SmartThings API always provides.  Others can be pulled out
    # using header().

    headers: Mapping[str, str] = field(factory=dict)
    body: str = ""
    normalized: Mapping[str, str] = field(init=False)
    correlation_id: str = field(init=False)
    signature: str = field(init=False)
    date: str = field(init=False)

    @normalized.default
    def _default_normalized(self) -> Mapping[str, str]:
        # in conjunction with header(), this gives us a case-insensitive dictionary
        return {key.lower(): value for (key, value) in self.headers.items()} if self.headers else {}

    @correlation_id.default
    def _default_correlation_id(self) -> str | None:
        return self.header(CORRELATION_ID_HEADER)

    @signature.default
    def _default_signature(self) -> str | None:
        return self.header(AUTHORIZATION_HEADER)

    @date.default
    def _default_date(self) -> str | None:
        return self.header(DATE_HEADER)

    def header(self, name: str) -> str | None:
        """Return the named header case-insensitively, or None if not found."""
        if name.lower() not in self.normalized:
            return None
        value = self.normalized[name.lower()]
        if not value or not value.strip():
            return None
        return value
