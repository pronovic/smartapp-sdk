SmartApp SDK
============

Release v\ |version|

.. image:: https://img.shields.io/pypi/v/smartapp-sdk.svg
    :target: https://pypi.org/project/smartapp-sdk/

.. image:: https://img.shields.io/pypi/l/smartapp-sdk.svg
    :target: https://github.com/pronovic/smartapp-sdk/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/wheel/smartapp-sdk.svg
    :target: https://pypi.org/project/smartapp-sdk/

.. image:: https://img.shields.io/pypi/pyversions/smartapp-sdk.svg
    :target: https://pypi.org/project/smartapp-sdk/

.. image:: https://github.com/pronovic/smartapp-sdk/workflows/Test%20Suite/badge.svg
    :target: https://github.com/pronovic/smartapp-sdk/actions?query=workflow%3A%22Test+Suite%22

.. image:: https://readthedocs.org/projects/smartapp-sdk/badge/?version=stable&style=flat
    :target: https://smartapp-sdk.readthedocs.io/en/stable/

.. image:: https://coveralls.io/repos/github/pronovic/smartapp-sdk/badge.svg?branch=master
    :target: https://coveralls.io/github/pronovic/smartapp-sdk?branch=master

smartapp-sdk is a Python library to build a `webhook-based SmartApp <https://developer-preview.smartthings.com/docs/connected-servic
es/smartapp-basics/>`_ for the `SmartThings platform <https://www.smartthings.com/>`_.

The SDK is intended to be easy to use no matter how you choose to structure your code, whether that's a traditional Python webapp (such as FastAPI on Uvicorn) or a serverless application (such as AWS Lambda).

The SDK handles all the mechanics of the `webhook lifecycle interface <https://developer-preview.smartthings.com/docs/connected-serv
ices/lifecycles/>`_ on your behalf.  You just implement a single endpoint to accept the SmartApp webhook requests, and a single callba ck class where you define specialized behavior for the webhook events.  A clean `attrs <https://www.attrs.org/en/stable/>`_ object interface is exposed for use by your callback.


Installation
------------

Install the package with pip::

    $ pip install smartapp-sdk


API Documentation
-----------------

.. toctree::
   :maxdepth: 1


Using the SDK
-------------

Below are some notes on how to use the SDK.  The `smartapp-sensortrack <https://github.com/pronovic/smartapp-sensortrack>`_ repo on GitHub is also a good example of how to use the SDK to build a traditional Python webapp.

Event Handler
~~~~~~~~~~~~~

First, create your event handler class::

    from smartapp.interface import (
        ConfigurationRequest,
        ConfirmationRequest,
        EventRequest,
        EventType,
        InstallRequest,
        OauthCallbackRequest,
        SmartAppEventHandler,
        UninstallRequest,
        UpdateRequest,
    )

    class EventHandler(SmartAppEventHandler):

        """SmartApp event handler."""

        def handle_confirmation(self, correlation_id: Optional[str], request: ConfirmationRequest) -> None:
            """Handle a CONFIRMATION lifecycle request"""

        def handle_configuration(self, correlation_id: Optional[str], request: ConfigurationRequest) -> None:
            """Handle a CONFIGURATION lifecycle request."""

        def handle_install(self, correlation_id: Optional[str], request: InstallRequest) -> None:
            """Handle an INSTALL lifecycle request."""

        def handle_update(self, correlation_id: Optional[str], request: UpdateRequest) -> None:
            """Handle an UPDATE lifecycle request."""

        def handle_uninstall(self, correlation_id: Optional[str], request: UninstallRequest) -> None:
            """Handle an UNINSTALL lifecycle request."""

        def handle_oauth_callback(self, correlation_id: Optional[str], request: OauthCallbackRequest) -> None:
            """Handle an OAUTH_CALLBACK lifecycle request."""

        def handle_event(self, correlation_id: Optional[str], request: EventRequest) -> None:
            """Handle an EVENT lifecycle request."""

This empty event handler is perfectly legal and is good enough for now.


SmartApp Definition
~~~~~~~~~~~~~~~~~~~

Every SmartApp needs a definition, which provides an id, name, description,
target URL, and usually at least one configuration page::

    from smartapp.interface import ConfigSection, DeviceSetting, SmartAppConfigPage, SmartAppDefinition

    definition = SmartAppDefinition(
        id="example",
        name="Example App",
        description="Example SmartApp with temperature sensor",
        target_url="https://example.com/smartapp",
        permissions=["r:devices:*", "r:locations:*"],
        config_pages=[
            SmartAppConfigPage(
                page_name="Configuration",
                sections=[
                    ConfigSection(
                        name="Devices",
                        settings=[
                            DeviceSetting(
                                id="temperature-devices",
                                name="Temperature Devices",
                                description="Sensor devices to track temperature for",
                                required=False,
                                multiple=True,
                                capabilities=["temperatureMeasurement"],
                                permissions=["r"],
                            ),
                        ],
                    )
                ],
            )
        ],
    )

You can also use ``smartapp.converter.CONVERTER`` to round-trip between object
representation and YAML or JSON representation.  The YAML format looks like
this::

    id: example
    name: Example App
    description: Example SmartApp with temperature sensor
    targetUrl: https://example.com/smartapp
    permissions:
    - r:devices:*
    - r:locations:*
    configPages:
    - pageName: Configuration
      sections:
      - name: Devices
        settings:
        - id: temperature-devices
          name: Temperature Devices
          description: Sensor devices to track temperature for
          type: DEVICE
          required: false
          multiple: true
          capabilities:
          - temperatureMeasurement
          permissions:
          - r

One convenient option is to keep the SmartApp YAML definition somewhere in your
source tree::

    with importlib.resources.open_text("myapp.data", "definition.yaml") as f:
        definition = CONVERTER.from_yaml(f.read(), SmartAppDefinition)

It's often easier to maintain the definition in YAML rather than in code, and
it's also somewhat more legible.


Dispatcher
~~~~~~~~~~

Once you have an event handler and a SmartApp definition, you can create your
dispatcher::

    dispatcher = SmartAppDispatcher(definition=definition, event_handler=EventHandler())

There's also an optional ``config`` parameter, but you probably don't need to
change any of the default configuration.


POST Endpoint
~~~~~~~~~~~~~

Finally, handle all SmartApp ``POST`` requests with just two lines of code::

    context = SmartAppRequestContext(headers=request_headers, body=request_body)
    response_body = dispatcher.dispatch(context=context)

Source the request headers and JSON request body in any way that makes
sense for the web application framework you are using. For instance, with
FastAPI, this is one way to do it (although in a real application, you'd also
want some exception handlers, etc.)::

    @API.post("/smartapp")
    async def smartapp(request: Request) -> Response:
        headers = request.headers
        body = codecs.decode(await request.body(), "UTF-8")
        context = SmartAppRequestContext(headers=headers, body=body)
        content = dispatcher.dispatch(context=context)
        return Response(status_code=200, content=content, media_type="application/json")

Then, make sure your web application is exposed on the public internet via
https, and you are ready to follow the remaining setup steps in the
`SmartThings documentation <https://developer-preview.smartthings.com/docs/connected-services/hosting/webhook-smartapp/>`_.


More Implementation Notes
~~~~~~~~~~~~~~~~~~~~~~~~~

The guts of your SmartApp will be in your event handler. 

The event handler is a synchronous and single-threaded interface.  The
assumption is that if you need high-volume asynchronous or multi-threaded
processing, you will implement that at the calling tier (as shown in the
FastAPI example above).

Some lifecycle events do not require you to implement any custom event handler
logic:

- ``CONFIRMATION``: normally no callback needed, since the dispatcher logs the app id and confirmation URL
- ``CONFIGURATION``: normally no callback needed, since the dispatcher has the information it needs to respond
- ``INSTALL``/``UPDATE``: set up or replace subscriptions and schedules and persist required data, if any
- ``UNINSTALL``: remove persisted data, if any
- ``OAUTH_CALLBACK``: coordinate with your oauth provider as needed
- ``EVENT``: handle SmartThings events or scheduled triggers

The ``EventRequest`` object that you receive in the ``handle_event()`` callback
method includes an authorization token and also the entire configuration bundle
for the installed application.  So, if your SmartApp is built around event
handling and scheduled actions triggered by SmartThings, your handler can
probably be stateless.  There is probably is not any need to persist any of the
data returned in the ``INSTALL`` or ``UPDATE`` lifecycle events into your own
data store.  This is the model folowed in the `smartapp-sensortrack <https://github.com/pronovic/smartapp-sensortrack>`_ example.
