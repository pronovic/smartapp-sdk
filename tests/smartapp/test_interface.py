# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
# pylint: disable=redefined-outer-name,invalid-name,wildcard-import:
import os

import pytest

from smartapp.converter import CONVERTER
from smartapp.interface import *
from tests.testutil import load_file

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

DEVICE_EVENT = {
    "subscriptionName": "motion_sensors",
    "eventId": "736e3903-001c-4d40-b408-ff40d162a06b",
    "locationId": "499e28ba-b33b-49c9-a5a1-cce40e41f8a6",
    "deviceId": "6f5ea629-4c05-4a90-a244-cc129b0a80c3",
    "componentId": "main",
    "capability": "motionSensor",
    "attribute": "motion",
    "value": "active",
    "stateChange": True,
}

TIMER_EVENT = {
    "eventId": "string",
    "name": "lights_off_timeout",
    "type": "CRON",
    "time": "2017-09-13T04:18:12.469Z",
    "expression": "string",
}


class TestExceptions:
    @pytest.mark.parametrize(
        "exception",
        [
            SmartAppError,
            InternalError,
            BadRequestError,
            SignatureError,
        ],
    )
    def test_exceptions(self, exception):
        e = exception("message")
        assert e.message == "message"
        assert e.correlation_id is None
        assert isinstance(e, SmartAppError)
        e = exception("message", "id")
        assert e.message == "message"
        assert e.correlation_id == "id"
        assert isinstance(e, SmartAppError)


class TestSmartAppRequestContext:
    def test_context(self):
        headers = {
            "Date": "the-date",
            "Authorization": "signature",
            "X-ST-Correlation": "correlation",
            "empty": "",
            "whitespace": "\t\n",
            "none": None,
        }
        context = SmartAppRequestContext(
            headers=headers,
            body="thebody",
        )
        assert context.correlation_id == "correlation"
        assert context.signature == "signature"
        assert context.date == "the-date"
        for header in ["DATE", "Date", "date"]:
            assert context.header(header) == "the-date"
        for header in ["AUTHORIZATION", "Authorization", "authorization"]:
            assert context.header(header) == "signature"
        for header in ["missing", "empty", "whitespace", "none"]:
            assert context.header(header) is None


class TestEvent:
    @pytest.mark.parametrize(
        "event_type,attribute",
        [
            (EventType.DEVICE_COMMANDS_EVENT, "device_commands_event"),
            (EventType.DEVICE_EVENT, "device_event"),
            (EventType.DEVICE_HEALTH_EVENT, "device_health_event"),
            (EventType.DEVICE_LIFECYCLE_EVENT, "device_lifecycle_event"),
            (EventType.HUB_HEALTH_EVENT, "hub_health_event"),
            (EventType.INSTALLED_APP_LIFECYCLE_EVENT, "installed_app_lifecycle_event"),
            (EventType.MODE_EVENT, "mode_event"),
            (EventType.SCENE_LIFECYCLE_EVENT, "scene_lifecycle_event"),
            (EventType.SECURITY_ARM_STATE_EVENT, "security_arm_state_event"),
            (EventType.TIMER_EVENT, "timer_event"),
            (EventType.WEATHER_EVENT, "weather_event"),
        ],
    )
    def test_for_type(self, event_type, attribute):
        value = {"k": "v"}
        args = {"event_type": event_type, attribute: value}
        assert (Event(**args).for_type(event_type)) is value


class TestInstallRequest:
    def test_config_convenience_methods(self):
        path = os.path.join("live", "request", "INSTALL.1.json")
        data = load_file(os.path.join(FIXTURE_DIR, path))
        request = CONVERTER.from_json(data, InstallRequest)
        assert request.as_str("retrieve-weather-enabled") == "true"
        assert request.as_bool("retrieve-weather-enabled") is True
        assert request.as_str("retrieve-weather-frequency") == "15"
        assert request.as_int("retrieve-weather-frequency") == 15
        assert request.as_float("retrieve-weather-frequency") == 15.0
        assert request.as_devices("humidity-devices") == [
            DeviceValue(device_id="3ac74985-XXXX-XXXX-XXXX-ea9623be6a7b", component_id="main"),
            DeviceValue(device_id="0ff440ec-XXXX-XXXX-XXXX-a39e189b8cc9", component_id="main"),
        ]


class TestUpdateRequest:
    def test_config_convenience_methods(self):
        path = os.path.join("samples", "request", "UPDATE.json")
        data = load_file(os.path.join(FIXTURE_DIR, path))
        request = CONVERTER.from_json(data, UpdateRequest)
        assert request.as_str("minutes") == "5"
        assert request.as_bool("minutes") is True
        assert request.as_int("minutes") == 5
        assert request.as_float("minutes") == 5.0
        assert request.as_devices("contactSensor") == [
            DeviceValue(device_id="e457978e-5e37-43e6-979d-18112e12c961", component_id="main"),
        ]


class TestEventRequest:
    def test_for_type_device(self):
        path = os.path.join("samples", "request", "EVENT-DEVICE.json")
        data = load_file(os.path.join(FIXTURE_DIR, path))
        request = CONVERTER.from_json(data, EventRequest)
        for event_type in [event_type for event_type in EventType if event_type != EventType.DEVICE_EVENT]:
            assert request.event_data.for_type(event_type) == []
        assert request.event_data.for_type(EventType.DEVICE_EVENT) == [DEVICE_EVENT]

    def test_for_type_timer(self):
        path = os.path.join("samples", "request", "EVENT-TIMER.json")
        data = load_file(os.path.join(FIXTURE_DIR, path))
        request = CONVERTER.from_json(data, EventRequest)
        for event_type in [event_type for event_type in EventType if event_type != EventType.TIMER_EVENT]:
            assert request.event_data.for_type(event_type) == []
        assert request.event_data.for_type(EventType.TIMER_EVENT) == [TIMER_EVENT]

    def test_filter_device(self):
        path = os.path.join("samples", "request", "EVENT-DEVICE.json")
        data = load_file(os.path.join(FIXTURE_DIR, path))
        request = CONVERTER.from_json(data, EventRequest)
        for event_type in [event_type for event_type in EventType if event_type != EventType.DEVICE_EVENT]:
            assert request.event_data.filter(event_type) == []
            assert request.event_data.filter(event_type, predicate=lambda x: False) == []
            assert request.event_data.filter(event_type, predicate=lambda x: True) == []
        assert request.event_data.filter(EventType.DEVICE_EVENT) == [DEVICE_EVENT]
        assert request.event_data.filter(EventType.DEVICE_EVENT, predicate=lambda x: False) == []
        assert request.event_data.filter(EventType.DEVICE_EVENT, predicate=lambda x: True) == [DEVICE_EVENT]
        assert request.event_data.filter(
            EventType.DEVICE_EVENT, predicate=lambda x: x["deviceId"] == "6f5ea629-4c05-4a90-a244-cc129b0a80c3"
        ) == [DEVICE_EVENT]

    def test_filter_timer(self):
        path = os.path.join("samples", "request", "EVENT-TIMER.json")
        data = load_file(os.path.join(FIXTURE_DIR, path))
        request = CONVERTER.from_json(data, EventRequest)
        for event_type in [event_type for event_type in EventType if event_type != EventType.TIMER_EVENT]:
            assert request.event_data.filter(event_type) == []
            assert request.event_data.filter(event_type, predicate=lambda x: False) == []
            assert request.event_data.filter(event_type, predicate=lambda x: True) == []
        assert request.event_data.filter(EventType.TIMER_EVENT) == [TIMER_EVENT]
        assert request.event_data.filter(EventType.TIMER_EVENT, predicate=lambda x: False) == []
        assert request.event_data.filter(EventType.TIMER_EVENT, predicate=lambda x: True) == [TIMER_EVENT]
        assert request.event_data.filter(EventType.TIMER_EVENT, predicate=lambda x: x["name"] == "lights_off_timeout") == [
            TIMER_EVENT
        ]
