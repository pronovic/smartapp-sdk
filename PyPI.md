# SmartApp SDK

[![pypi](https://img.shields.io/pypi/v/smartapp-sdk.svg)](https://pypi.org/project/smartapp-sdk/)
[![license](https://img.shields.io/github/license/pronovic/smartapp-sdk)](https://github.com/pronovic/smartapp-sdk/blob/main/LICENSE)
[![wheel](https://img.shields.io/pypi/wheel/smartapp-sdk.svg)](https://pypi.org/project/smartapp-sdk/)
[![python](https://img.shields.io/pypi/pyversions/smartapp-sdk.svg)](https://pypi.org/project/smartapp-sdk/)
[![Test Suite](https://github.com/pronovic/smartapp-sdk/workflows/Test%20Suite/badge.svg)](https://github.com/pronovic/smartapp-sdk/actions?query=workflow%3A%22Test+Suite%22)
[![docs](https://readthedocs.org/projects/smartapp-sdk/badge/?version=stable&style=flat)](https://smartapp-sdk.readthedocs.io/en/stable/)
[![coverage](https://coveralls.io/repos/github/pronovic/smartapp-sdk/badge.svg?branch=main)](https://coveralls.io/github/pronovic/smartapp-sdk?branch=main)

_Note: As of January 2025, I have migrated my home automation infrastructure from SmartThings to Home Assistant, so I no longer actively use this software. I will continue to maintain the library, keeping dependencies up-to-date and supporting new Python versions, etc.  Time permitting, I will also continue to accept GitHub issues for bug fixes and enhancement requests.  If you submit an issue, please keep in mind that I no longer have a SmartThings environment to test with, so I will expect you to coordinate with me on testing before I release any changes._

---

smartapp-sdk is a Python library to build a [webhook-based SmartApp](https://developer.smartthings.com/docs/connected-services/smartapp-basics/) for the [SmartThings platform](https://www.smartthings.com/).

The SDK is intended to be easy to use no matter how you choose to structure your code, whether that's a traditional Python webapp (such as FastAPI on Uvicorn) or a serverless application (such as AWS Lambda).

The SDK handles all the mechanics of the [SmartThings webhook lifecycle interface](https://developer.smartthings.com/docs/connected-services/lifecycles/) on your behalf.  You just implement a single endpoint to accept the SmartApp webhook requests, and a single callback class where you define specialized behavior for the webhook events.  A clean [attrs](https://www.attrs.org/en/stable/) object interface is exposed for use by your callback.  The attrs interface has been designed to match the JSON interface documented by SmartThings.  If you have questions about the shape of the data or the way the lifecyle interface works, the SmartThings documentation is your best source of information.

SDK documentation for this library is found at [smartapp-sdk.readthedocs.io](https://smartapp-sdk.readthedocs.io/en/stable/).  Look there for installation instructions, the class model documentation, and example code.
