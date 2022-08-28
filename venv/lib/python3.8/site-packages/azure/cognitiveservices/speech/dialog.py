# Copyright (c) Microsoft. All rights reserved.
# See https://aka.ms/csspeech/license201809 for the full license information.
"""
Classes related to dialog service connector.

"""

from typing import Optional

from . import speech_py_impl as impl
from .audio import (AudioConfig, PullAudioOutputStream)
from .speech import (
    EventSignal,
    KeywordRecognitionModel,
    RecognitionEventArgs,
    ResultFuture,
    SessionEventArgs,
    SpeechRecognitionCanceledEventArgs,
    SpeechRecognitionEventArgs,
    SpeechRecognitionResult)
from .speech_py_impl import (
    PropertyId,
    ServicePropertyChannel
)

OptionalStr = Optional[str]


class DialogServiceConfig():
    """
    Class that defines base configurations for the dialog service connector object that can communicate
    with a voice assistant.

    This class is base class for BotFrameworkConfig and CustomCommandsConfig classes.
    Create dialog config instances from specific BotFrameworkConfig or CustomCommandsConfig objects.

    """
    def __init__(self, config_impl):
        self._impl = config_impl
        if type(self) == DialogServiceConfig:
            raise Exception("cannot instantiate DialogServiceConfig directly")

        self._impl.set_property("SPEECHSDK-SPEECH-CONFIG-SYSTEM-LANGUAGE", "Python")

    def get_property(self, property_id: PropertyId) -> str:
        """
        Get a property by id.

        :param property_id: The id of the property to be retrieved.
        :return: The value of the property.
        """
        if not isinstance(property_id, PropertyId):
            raise TypeError('property_id value must be PropertyId instance')
        return impl._speech_py_impl.DialogServiceConfig_get_property(self._impl, property_id.value)

    def get_property_by_name(self, property_name: str) -> str:
        """
        Get a property by name.

        :param property_name: The name of the property to be retrieved.
        :return: The value of the property.
        """
        if not isinstance(property_name, str):
            raise TypeError('property_name value must be str instance')
        return impl._speech_py_impl.DialogServiceConfig_get_property(self._impl, property_name)

    def set_property(self, property_id: PropertyId, value: str):
        """
        Set a property by id.

        :param property_id: The id of the property to be set.
        :param value: The value to be set for the property.
        """
        if not isinstance(property_id, PropertyId):
            raise TypeError('property_id value must be PropertyId instance')
        return impl._speech_py_impl.DialogServiceConfig_set_property(self._impl, property_id.value, value)

    def set_property_by_name(self, property_name: str, value: str):
        """
        Set a property by name.

        :param property_name: The name of the property to be set.
        :param value: The value to be set for the property.
        """
        if not isinstance(property_name, str):
            raise TypeError('property_name value must be str instance')
        return impl._speech_py_impl.DialogServiceConfig_set_property(self._impl, property_name, value)

    def set_service_property(self, name: str, value: str, channel: ServicePropertyChannel):
        """
        Sets a property value that will be passed to service using the specified channel.

        :param name: The property name.
        :param value: The property value.
        :param channel: The channel used to pass the specified property to service.
        """
        if not isinstance(channel, ServicePropertyChannel):
            raise TypeError('wrong channel, must be ServicePropertyChannel')
        self._impl.set_service_property(name, value, channel.value)

    def set_proxy(self, hostname: str, port: str, username: str, password: str):
        """
        Set proxy information.

        .. note::

            Proxy functionality is not available on macOS. This function will have no effect on
            this platform.

        :param hostname: The host name of the proxy server. Do not add protocol information (http)
            to the hostname.
        :param port: The port number of the proxy server.
        :param username: The user name of the proxy server.
        :param password: The password of the proxy server.
        """
        self._impl.set_proxy(hostname, port, username, password)

    @property
    def language(self) -> str:
        """
        The language identifier used for speech-to-text, expressed in BCP-47 format.
        """
        return self._impl.get_language()

    @language.setter
    def language(self, language: str):
        """
        Set the language identifier used for speech-to-text, expressed in BCP-47 format.
        """
        self._impl.set_language(language)


class BotFrameworkConfig(DialogServiceConfig):
    """
    Class that is used to initialize a DialogServiceConnector that will connect to a Bot Framework
    bot using the Direct Line Speech channel.

    See also the `direct line speech page <https://docs.microsoft.com/azure/cognitive-services/speech-service/direct-line-speech>`.

    The configuration can be initialized in following ways:

    - from subscription: pass a subscription key, a region and a bot_id (optional)
    - from authorization token: pass an authorization token, a region and a bot_id (optional)

    :param subscription: The subscription key.
    :param auth_token: The authorization token.
    :param region: The region name (see the `region page <https://aka.ms/csspeech/region>`_).
    :param bot_id: The identifier of a specific bot resource to request.
    """

    def __init__(self, subscription: OptionalStr = None, auth_token: OptionalStr = None,
                 region: OptionalStr = None, bot_id: OptionalStr = ''):
        bad_params_error_message = "bad arguments: either pass subscription key with region and optional bot_id " \
                                   "or authorization token with region and optional bot_id"
        if subscription is None and region is None and auth_token is None:
            raise ValueError(bad_params_error_message)

        if (subscription is not None and region is None):
            raise ValueError("both subscription key and region must be given to "
                             "initialize from subscription")

        if (auth_token is not None and region is None):
            raise ValueError("both authorization token and region must be given to "
                             "initialize from authorization token")

        if (subscription is not None and auth_token is not None):
            raise ValueError("pass either subscription key with region or authorization "
                             "token with region in initialization")

        if subscription is not None:
            self._impl = impl.BotFrameworkConfig._from_subscription(subscription, region, bot_id)
        elif auth_token is not None:
            self._impl = impl.BotFrameworkConfig._from_authorization_token(auth_token, region, bot_id)
        else:
            raise ValueError('cannot construct BotFrameworkConfig with the given parameters')

        super().__init__(self._impl)


class CustomCommandsConfig(DialogServiceConfig):
    """
    Class used to initialize a DialogServiceConnector that will connect to a Custom Commands
    application as published from Speech Studio for a speech service resource.

    See also the `custom commands page <https://docs.microsoft.com/azure/cognitive-services/speech-service/custom-commands>`.

    The configuration can be initialized in following ways:

    - from subscription: pass an application id, a subscription key and a region
    - from authorization token: pass an application id, an authorization token and a region

    :param app_id: The Custom Commands application id.
    :param subscription: The subscription key.
    :param auth_token: The authorization token.
    :param region: The region name (see the `region page <https://aka.ms/csspeech/region>`_).
    """

    def __init__(self, app_id: OptionalStr = None, subscription: OptionalStr = None,
                 auth_token: OptionalStr = None, region: OptionalStr = None):
        bad_params_error_message = "bad arguments: either pass application id and subscription key with region " \
                                   "or application id and authorization token with region"
        if subscription is None and region is None and auth_token is None and app_id is None:
            raise ValueError(bad_params_error_message)

        if (app_id is None):
            raise ValueError("valid application id must be given to the initializer")

        if (subscription is not None and region is None):
            raise ValueError("both subscription key and region must be given to "
                             "initialize from subscription")

        if (auth_token is not None and region is None):
            raise ValueError("both authorization token and region must be given to "
                             "initialize from authorization token")

        if (subscription is not None and auth_token is not None):
            raise ValueError("pass either subscription key with region or authorization "
                             "token with region in initialization")

        if subscription is not None:
            self._impl = impl.CustomCommandsConfig._from_subscription(app_id, subscription, region)
        elif auth_token is not None:
            self._impl = impl.CustomCommandsConfig._from_authorization_token(app_id, auth_token, region)
        else:
            raise ValueError('cannot construct CustomCommandsConfig with the given parameters')

        super().__init__(self._impl)

    @property
    def application_id(self) -> str:
        """
        Get the identifier for the Custom Commands application to use, as selected from the subscription.
        """
        return self._impl.get_application_id()

    @application_id.setter
    def application_id(self, app_id: str):
        """
        Set the identifier for the Custom Commands application to use, as selected from the subscription.
        """
        self._impl.set_application_id(app_id)


class ActivityReceivedEventArgs:
    """
    An object that encapsulates the response data that originates from the dialog implementation used by a
    DialogServiceConnector. Activities may be sent by a dialog implementation at any time during a connection
    and there may be a many-to-one relationship between activities received and input utterances.

    """

    def __init__(self, evt_args):
        """
        Constructor for internal use.
        """
        self._activity = evt_args.activity
        self._has_audio = evt_args.has_audio
        self._audio = None
        if self._has_audio is True:
            self._audio = PullAudioOutputStream(stream_impl=evt_args.audio)

    @property
    def activity(self) -> str:
        """
        Gets a serialized JSON string that represents the activity payload sent by the dialog implementation that
        a DialogServiceConnector communicates with. This data is originated from the dialog implementation and both
        the schema and contents of the document are determined by the sender.
        """
        return self._activity

    @property
    def audio(self) -> PullAudioOutputStream:
        """
        Gets a PullAudioOutputStream associated with this activity, as produced by the text-to-speech service.
        This streamis populated as data arrives and may not contain all synthesized audio when the activity arrives.
        If there is no audio data associated with this activity payload, has_audio will be False and audio will be None.
        """
        return self._audio

    @property
    def has_audio(self) -> bool:
        """
        Gets a value indicating whether this activity payload includes an audio stream from the text-to-speech service.
        If such a stream is present, it can be retrieved via the audio property.

        If there is no audio data associated with this activity payload, has_audio will be False and audio will be None.
        """
        return self._has_audio

    def __str__(self):
        return u'{}(activity={}, audio={}, has_audio={})'.format(
            type(self).__name__, self._activity, self._audio, self._has_audio)


class TurnStatusReceivedEventArgs:
    """
    An object that encapsulates turn status information as received from the dialog implementation that a DialogServiceConnector
    communicates with. A turn is a single execution session within the dialog implementation that may generate any number of
    activities over its course. The information in this payload represents success or failure conditions encountered by the
    dialog implementation over the course of this execution. This data facilitates the indication of completion or error conditions
    within the dialog implementation even when no explicit activity data is produced as part of a turn.
    """

    def __init__(self, evt_args):
        """
        Constructor for internal use.
        """
        self._interaction_id = evt_args.interaction_id
        self._conversation_id = evt_args.conversation_id
        self._status_code = evt_args.status_code

    @property
    def interaction_id(self) -> str:
        """
        The interaction identifier associated with this turn status event. Interaction identifiers generally correspond to a
        single input signal (e.g. a voice utterance or sent activity payload) and will correlate to replyTo fields within Bot
        Framework activities.
        """
        return self._interaction_id

    @property
    def conversation_id(self) -> str:
        """
        The conversation identifier associated with this turn status event. Conversations are logical groupings of turns that
        may span multiple interactions. A client can use a conversation identifier to resume or retry a conversation if such
        a capability is supported by the backing dialog implementation.
        """
        return self._conversation_id

    @property
    def status_code(self) -> int:
        """
        The numeric status code associated with this turn status event. These generally correspond to standard HTTP status
        codes such as 200 (OK), 400 (Failure/Bad Request), and 429 (Timeout/Throttled).
        """
        return self._status_code

    def __str__(self):
        return u'{}(interaction_id={}, conversation_id={}, status_code={})'.format(
            type(self).__name__, self._interaction_id, self._conversation_id, self._status_code)


class DialogServiceConnector():
    """
    An object that communicates with a speech-enabled dialog system using either the Bot Framework or Custom Commands.
    This type receives speech-to-text results and also facilitates the asynchronous sending and receiving of non-speech
    dialog activity data.

    :param dialog_service_config: The config for the dialog service, either for bot framework or custom commands.
    :param audio_config: The config for the audio input.
    """

    def __init__(self, dialog_service_config: DialogServiceConfig, audio_config: Optional[AudioConfig] = None):

        if not isinstance(dialog_service_config, DialogServiceConfig):
            raise ValueError('dialog_service_config must be a DialogServiceConfig instance')

        self._impl = self._get_impl(impl.DialogServiceConnector, dialog_service_config, audio_config)

    def connect(self):
        """
        Synchronously establishes a connection with the service. Connection is automatically performed when needed,
        but this manual call can be useful to make sure the connection is active before its first use to help reduce
        inital latency.

        On return, the connection might not be ready yet. Please subscribe to the `connected` event
        of the `Connection` instance to be notified when the connection to service is established.
        Please use :class:`.Connection` to retrieve instance by using :py:meth:`.from_dialog_service_connector`
        method.
        """
        return self._impl.connect_async().get()

    def connect_async(self):
        """
        Asynchronously establishes a connection with the service. Connection is automatically performed when needed,
        but this manual call can be useful to make sure the connection is active before its first use to help reduce
        inital latency.

        :return: A future that is fulfilled once connection has been initialized.
        """
        return self._impl.connect_async()

    def disconnect(self):
        """
        Synchronously disconnects from the service. Subsequent calls that require a connection will still automatically
        reconnect after manual disconnection.

        """
        return self._impl.disconnect_async().get()

    def disconnect_async(self):
        """
        Asynchronously disconnects from the service. Subsequent calls that require a connection will still automatically
        reconnect after manual disconnection.

        :return: A future that is fulfilled when disconnected.
        """
        return self._impl.disconnect_async()

    def send_activity(self, activity: str) -> str:
        """
        Synchronously sends a data payload to dialog backend service that this DialogServiceConnector instance is
        connected to. This is usually a JSON document with its schema determined by the dialog implementation in
        the service and the contents of a sent activity should be populated with knowledge about the format and
        content expectations of the dialog system. Sent activities are not associated with any other interaction
        and will generate their own standalone interaction identifier when processed by the service. Correlation of
        conversations and other interactions should be accomplished via the activity payload itself using the
        capabilities of the dialog implementation used.

        :param activity: the serialized payload of an activity to send.
        :return: an interaction identifier acquired when the activity is acknowledged by the service. This may occur
            before the activity is processed and evaluated by the dialog implementation and the receipt of an interaction
            identifier does not indicate any success or failure in processing the activity. Information about success or failure
            may be obtained via response activities with correlation data or with TurnStatusReceived events that correlate to
            this interaction identifier.
        """
        return self._impl.send_activity_async(activity).get()

    def send_activity_async(self, activity: str) -> ResultFuture:
        """
        Asynchronously sends an activity to the backing dialog, see description details at :py:meth:`.send_activity`

        :param activity: the serialized payload of an activity to send.
        :return: A future containing the result value of the asynchronous activity sending operation.
        """
        return ResultFuture(self._impl.send_activity_async(activity), str)

    def start_keyword_recognition(self, model: KeywordRecognitionModel):
        """
        Synchronously starts a speech-to-text interaction with this connector using a keyword. This interaction will use
        the provided keyword model to listen for a keyword indefinitely, during which audio is not sent to the speech service
        and all processing is performed locally. When a keyword is recognized, the DialogServiceConnector will automatically
        connect to the speech service and begin sending audio data from just before the keyword as if
        :py:meth:`.listen_once_async` were invoked. When received, speech-to-text results may be processed by the provided
        result handler or retrieved via a subscription to the recognized event. The speech-to-text result produced by this
        operation is also provided to the configured dialog implementation and that dialog system may produce any number of
        activity payloads in response to the speech interaction. Speech interactions may be correlated with activities via
        dialog-specific data in the activity payload.

        Call :py:meth:`.stop_keyword_recognition_async` to stop the keyword initiated recognition.

        :param model: the keyword recognition model that specifies the keyword to be recognized.
        """
        return self._impl.start_keyword_recognition_async(model._impl).get()

    def start_keyword_recognition_async(self, model: KeywordRecognitionModel):
        """
        Asynchronously configures the dialog service connector with the given keyword model. After calling this method,
        the connector is listening for the keyword to start the recognition. Call
        :py:meth:`.stop_keyword_recognition_async` to stop the keyword initiated recognition.

        See :py:meth:`.start_keyword_recognition` for detailed description of the functionality.

        :param model: the keyword recognition model that specifies the keyword to be recognized.

        :return: A future that is fulfilled once recognition has been initialized.
        """
        return self._impl.start_keyword_recognition_async(model._impl)

    def stop_keyword_recognition(self):
        """
        Synchronously stops the keyword initiated recognition.

        """
        return self._impl.stop_keyword_recognition_async().get()

    def stop_keyword_recognition_async(self):
        """
        Asynchronously stops the keyword initiated recognition.

        :return: A future that is fulfilled once recognition has been stopped.
        """
        return self._impl.stop_keyword_recognition_async()

    def listen_once(self) -> SpeechRecognitionResult:
        """
        Synchronously starts a speech-to-text interaction with this connector and blocks until a single speech-to-text
        final result is received. The speech-to-text result received is also provided to the configured dialog implementation
        and that dialog system may produce any number of activity payloads in response to the speech interaction.
        Speech interactions may be correlated with activities via dialog-specific data in the activity payload.

        :return: the speech-to-text result from the speech recognition.
        """
        return SpeechRecognitionResult(self._impl.listen_once_async().get())

    def listen_once_async(self) -> ResultFuture:
        """
        Asynchronously starts a speech-to-text interaction with this connector and blocks until a single speech-to-text
        final result is received. The speech-to-text result received is also provided to the configured dialog implementation
        and that dialog system may produce any number of activity payloads in response to the speech interaction.
        Speech interactions may be correlated with activities via dialog-specific data in the activity payload.

        :return: A future containing the speech-to-text result value of the asynchronous recognition.
        """
        return ResultFuture(self._impl.listen_once_async(), SpeechRecognitionResult)

    def stop_listening(self):
        """
        Requests an immediate stop to any active listening operation. This may interrupt a speech-to-text interaction
        in progress and any speech-to-text result received may represent an incomplete speech input.

        Synchronous methods should not be called when handling an event. Use :py:meth:`.stop_listening_async` if a stop
        is desired in response to an event.

        :return: A future that is fulfilled once listening has been stopped.
        """
        return self._impl.stop_listening_async().get()

    def stop_listening_async(self):
        """
        Requests an immediate stop to any active listening operation. This may interrupt a speech-to-text interaction
        in progress and any speech-to-text result received may represent an incomplete speech input.

        :return: A future that is fulfilled once listening has been stopped.
        """
        return self._impl.stop_listening_async()

    @property
    def authorization_token(self) -> str:
        """
        The authorization token that will be used for connecting to the service.

        .. note::
          The caller needs to ensure that the authorization token is valid. Before the
          authorization token expires, the caller needs to refresh it by calling this setter with a
          new valid token. Otherwise, the recognizer will encounter errors during recognition.
        """
        return self._impl.get_authorization_token()

    @authorization_token.setter
    def authorization_token(self, authorization_token: str):
        """
        Sets the authorization token that will be used for connecting to the service.
        Note: The caller needs to ensure that the authorization token is valid. Before the authorization token
        expires, the caller needs to refresh it by calling this setter with a new valid token.
        Otherwise, the connector will encounter errors during its operation.
        """
        self._impl.set_authorization_token(authorization_token)

    @property
    def speech_activity_template(self) -> str:
        """
        Gets the JSON template that will be provided to the speech service for the next conversation. The service will
        attempt to merge this template into all activities sent to the dialog backend, whether originated by the
        client with SendActivityAsync or generated by the service, as is the case with speech-to-text results.
        """
        return self._impl.get_speech_activity_template()

    @speech_activity_template.setter
    def speech_activity_template(self, speech_activity_template: str):
        """
        Sets a JSON template that will be provided to the speech service for the next conversation. The service will
        attempt to merge this template into all activities sent to the dialog backend, whether originated by the
        client with SendActivityAsync or generated by the service, as is the case with speech-to-text results.
        """
        self._impl.set_speech_activity_template(speech_activity_template)

    @property
    def session_started(self) -> EventSignal:
        """
        Signal for events indicating the start of a recognition session (operation).

        Callbacks connected to this signal are called with a :class:`.SessionEventArgs` instance as
        the single argument.
        """
        return EventSignal(self._impl.session_started, SessionEventArgs)

    @property
    def session_stopped(self) -> EventSignal:
        """
        Signal for events indicating the end of a recognition session (operation).

        Callbacks connected to this signal are called with a :class:`.SessionEventArgs` instance as
        the single argument.
        """
        return EventSignal(self._impl.session_stopped, SessionEventArgs)

    @property
    def speech_start_detected(self) -> EventSignal:
        """
        Signal for events indicating the start of speech.

        Callbacks connected to this signal are called with a :class:`.RecognitionEventArgs`
        instance as the single argument.
        """
        return EventSignal(self._impl.speech_start_detected, RecognitionEventArgs)

    @property
    def speech_end_detected(self) -> EventSignal:
        """
        Signal for events indicating the end of speech.

        Callbacks connected to this signal are called with a :class:`.RecognitionEventArgs`
        instance as the single argument.
        """
        return EventSignal(self._impl.speech_end_detected, RecognitionEventArgs)

    @property
    def recognizing(self) -> EventSignal:
        """
        Signal for events containing intermediate recognition results.

        Callbacks connected to this signal are called with a :class:`.SpeechRecognitionEventArgs`,
        instance as the single argument.
        """
        return EventSignal(self._impl.recognizing, SpeechRecognitionEventArgs)

    @property
    def recognized(self) -> EventSignal:
        """
        Signal for events containing final recognition results (indicating a successful
        recognition attempt).

        Callbacks connected to this signal are called with a :class:`.SpeechRecognitionEventArgs`,
        instance as the single argument, dependent on the type of recognizer.
        """
        return EventSignal(self._impl.recognized, SpeechRecognitionEventArgs)

    @property
    def canceled(self) -> EventSignal:
        """
        Signal for events containing canceled recognition results (indicating a recognition attempt
        that was canceled as a result or a direct cancellation request or, alternatively, a
        transport or protocol failure).

        Callbacks connected to this signal are called with a
        :class:`.SpeechRecognitionCanceledEventArgs`, instance as the single argument.
        """
        return EventSignal(self._impl.canceled, SpeechRecognitionCanceledEventArgs)

    @property
    def activity_received(self) -> EventSignal:
        """
        Signals that an activity was received from the backend.

        Callbacks connected to this signal are called with a :class:`.ActivityReceivedEventArgs`,
        instance as the single argument, dependent on the type of recognizer.
        """
        return EventSignal(self._impl.activity_received, ActivityReceivedEventArgs)

    @property
    def turn_status_received(self) -> EventSignal:
        """
        Signals that a turn status update was received from the backend.

        Callbacks connected to this signal are called with a
        :class:`.TurnStatusReceivedEventArgs`, instance as the single argument.
        """
        return EventSignal(self._impl.turn_status_received, TurnStatusReceivedEventArgs)

    @staticmethod
    def _get_impl(reco_type, dialog_service_config, audio_config):
        if audio_config is not None:
            _impl = reco_type._from_config(dialog_service_config._impl, audio_config._impl)
        else:
            _impl = reco_type._from_config(dialog_service_config._impl, None)

        return _impl
