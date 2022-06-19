# SmartApp SDK

[![pypi](https://img.shields.io/pypi/v/smartapp-sdk.svg)](https://pypi.org/project/smartapp-sdk/)
[![license](https://img.shields.io/pypi/l/smartapp-sdk.svg)](https://github.com/pronovic/smartapp-sdk/blob/master/LICENSE)
[![wheel](https://img.shields.io/pypi/wheel/smartapp-sdk.svg)](https://pypi.org/project/smartapp-sdk/)
[![python](https://img.shields.io/pypi/pyversions/smartapp-sdk.svg)](https://pypi.org/project/smartapp-sdk/)
[![Test Suite](https://github.com/pronovic/smartapp-sdk/workflows/Test%20Suite/badge.svg)](https://github.com/pronovic/smartapp-sdk/actions?query=workflow%3A%22Test+Suite%22)
[![docs](https://readthedocs.org/projects/smartapp-sdk/badge/?version=stable&style=flat)](https://smartapp-sdk.readthedocs.io/en/stable/)
[![coverage](https://coveralls.io/repos/github/pronovic/smartapp-sdk/badge.svg?branch=master)](https://coveralls.io/github/pronovic/smartapp-sdk?branch=master)

smartapp-sdk is a Python library to build a [webhook-based SmartApp](https://developer-preview.smartthings.com/docs/connected-services/smartapp-basics/) for the [SmartThings platform](https://www.smartthings.com/).

The SDK is intended to be easy to use no matter how you choose to structure your code, whether that's a traditional Python webapp (such as FastAPI on Uvicorn) or a serverless application (such as AWS Lambda).

The SDK handles all the mechanics of the [webhook lifecycle interface](https://developer-preview.smartthings.com/docs/connected-services/lifecycles/) on your behalf.  You just implement a single endpoint to accept the SmartApp webhook requests, and a single callback class where you define specialized behavior for the webhook events.  A clean [attrs](https://www.attrs.org/en/stable/) object interface is exposed for use by your callback.

SDK documentation is found at [smartapp-sdk.readthedocs.io](https://smartapp-sdk.readthedocs.io/en/stable/).  Look there for installation instructions, the class model documentation, and example code. The [smartapp-sensortrack](https://github.com/pronovic/smartapp-sensortrack) repo on GitHub is also a good example of how to use this SDK to build a traditional Python webapp.
