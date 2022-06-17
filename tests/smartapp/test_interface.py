# -*- coding: utf-8 -*-
# vim: set ft=python ts=4 sw=4 expandtab:
# pylint: disable=redefined-outer-name,invalid-name,wildcard-import:
import os

import pytest

from smartapp.converter import CONVERTER
from smartapp.interface import *
from tests.testutil import load_file

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


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


class TestConfig:
    def test_config_convenience_methods(self):
        path = os.path.join("live", "request", "INSTALL.1.json")
        data = load_file(os.path.join(FIXTURE_DIR, path))
        request = CONVERTER.from_json(data, InstallRequest)
        assert request.install_data.as_str("retrieve-weather-enabled") == "true"
        assert request.install_data.as_bool("retrieve-weather-enabled") is True
        assert request.install_data.as_str("retrieve-weather-frequency") == "15"
        assert request.install_data.as_int("retrieve-weather-frequency") == 15
        assert request.install_data.as_float("retrieve-weather-frequency") == 15.0
        assert request.install_data.as_devices("humidity-devices") == [
            DeviceValue(device_id="3ac74985-XXXX-XXXX-XXXX-ea9623be6a7b", component_id="main"),
            DeviceValue(device_id="0ff440ec-XXXX-XXXX-XXXX-a39e189b8cc9", component_id="main"),
        ]
