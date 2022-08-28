# Copyright (c) Microsoft. All rights reserved.
# See https://aka.ms/csspeech/license201809 for the full license information.
"""
Classes related to conversation transcription.

"""

from . import speech_py_impl as impl
from .audio import (AudioConfig)
from .speech import (
    EventSignal,
    RecognitionResult,
    RecognitionEventArgs,
    Recognizer,
    ResultFuture,
    SpeechConfig,
    SessionEventArgs)
from .speech_py_impl import (
    CancellationDetails,
    PropertyCollection
)
from typing import Optional, Type
OptionalStr = Optional[str]


class ConversationTranscriptionResult(RecognitionResult):
    """
    Defines the conversation transcription result.
    """
    def __init__(self, impl_result: impl.ConversationTranscriptionResult):
        """
        Constructor for internal use.
        """
        super().__init__(impl_result)

        self._user_id = impl_result.user_id
        self._utterance_id = impl_result.utterance_id

    @property
    def user_id(self) -> str:
        """
        Unique speaker id
        """
        return self._user_id

    @property
    def utterance_id(self) -> str:
        """
        Unique id that is consistent across all the intermediates and final speech recognition result from one user.
        """
        return self._utterance_id

    def __str__(self) -> str:
        return u'{}(result_id={}, user_id={}, utterance_id={}, text={}, reason={})'.format(
               type(self).__name__, self.result_id, self.user_id, self.utterance_id, self.text, self.reason)


class ConversationTranscriptionEventArgs(RecognitionEventArgs):
    """
    An object that encapsulates the conversation transcription result.
    """
    def __init__(self, evt_args: impl.ConversationTranscriptionEventArgs):
        """
        Constructor for internal use.
        """
        super().__init__(evt_args)
        self._result = ConversationTranscriptionResult(evt_args.result)

    @property
    def result(self) -> ConversationTranscriptionResult:
        """
        Contains the conversation transcription result.
        """
        return self._result

    def __str__(self) -> str:
        return u'{}(session_id={}, result={})'.format(type(self).__name__, self.session_id, self.result)


class ConversationTranscriptionCanceledEventArgs(ConversationTranscriptionEventArgs):
    """
    An object that encapsulates conversation transcription canceled event arguments.
    """
    def __init__(self, evt_args: impl.ConversationTranscriptionCanceledEventArgs):
        """
        Constructor for internal use.
        """
        super().__init__(evt_args)
        self._cancellation_details = evt_args.cancellation_details

    @property
    def cancellation_details(self) -> "CancellationDetails":
        """
        The reason why transcription was cancelled.

        Returns `None` if there was no cancellation.
        """
        return self._cancellation_details


class Participant():
    """
    An object that represents conversation participant.

    :param user_id: The user identification string.
    :param preferred_language: The preferred language of user in BCP-47 format.
    :param voice_signature: User's voice signature (optional).
    """
    def __init__(self, user_id: str, preferred_language: str, voice_signature: OptionalStr = None):
        self._impl = self._get_impl(impl.Participant, user_id, preferred_language, voice_signature)

    @property
    def participant_id(self) -> str:
        """
        Get the identifier for the participant.
        """
        return self._impl._id

    @property
    def avatar(self) -> str:
        """
        Gets the colour of the user's avatar as an HTML hex string (e.g. FF0000 for red).
        """
        return self._impl._avatar

    @property
    def display_name(self) -> str:
        """
        The participant's display name. Please note that each participant within the same conversation must
        have a different display name. Duplicate names within the same conversation are not allowed. You can
        use the Id property as another way to refer to each participant.
        """
        return self._impl._display_name

    @property
    def is_using_tts(self) -> bool:
        """
        Gets whether or not the participant is using Text To Speech (TTS).
        """
        return self._impl._is_using_tts

    @property
    def is_muted(self) -> bool:
        """
        Gets whether or not the participant is muted.
        """
        return self._impl._is_muted

    @property
    def is_host(self) -> bool:
        """
        Gets whether or not the participant is the host.
        """
        return self._impl._is_host

    def set_preferred_language(self, language: str) -> None:
        """
        Sets the preferred language of the participant

        :param language: The language in BCP-47 format.
        """
        self._impl.set_preferred_language(language)

    def set_voice_signature(self, signature: str) -> None:
        """
        Sets the voice signature of the participant used for identification.

        :param signature: The language in BCP-47 format.
        """
        self._impl.set_voice_signature(signature)

    @property
    def properties(self) -> PropertyCollection:
        """
        A collection of properties and their values defined for this Participant.
        """
        return self._impl.properties

    @staticmethod
    def _get_impl(object_type, user_id, preferred_language, voice_signature):  # noqa: ANN001,ANN205
        if voice_signature is not None:
            return object_type._from(user_id, preferred_language, voice_signature)
        else:
            return object_type._from(user_id, preferred_language)


class Conversation():
    """
    An object that performs conversation management related operations.

    :param speech_config: The speech configuration.
    :param conversation_id: The conversation identifier.
    """
    def __init__(self, speech_config: SpeechConfig, conversation_id: OptionalStr = None):
        if not isinstance(speech_config, SpeechConfig):
            raise ValueError('speech_config must be a SpeechConfig instance')

        self._impl = self._get_impl(impl.Conversation, speech_config, conversation_id)

    @property
    def conversation_id(self) -> str:
        """
        Get the conversation id.
        """
        return self._impl._conversation_id

    def add_participant_async(self, participant: Optional[Participant] = None, user_id: OptionalStr = None) -> ResultFuture:
        """
        Asynchronously adds a participant to a conversation using the participant object or user id.

        :param participant: the participant object
        :param user_id: the user identification string
        :return: A future containing the added participant object.
        """
        bad_params_error_message = "bad arguments: pass either participant object or user id string "
        if participant is None and user_id is None:
            raise ValueError(bad_params_error_message)
        if participant is not None and user_id is not None:
            raise ValueError(bad_params_error_message)
        if participant is not None:
            return ResultFuture(self._impl.add_participant_async(participant._impl), Participant)
        elif user_id is not None:
            return ResultFuture(self._impl.add_participant_async(user_id), Participant)

    def remove_participant_async(self, participant: Optional[Participant] = None, user_id: OptionalStr = None) -> ResultFuture:
        """
        Asynchronously removes a participant from a conversation using the participant object or user id.

        :param participant: the participant object
        :param user_id: the user identification string
        :return: A future containing the added participant object.
        """
        bad_params_error_message = "bad arguments: pass either participant object or user id string "
        if participant is None and user_id is None:
            raise ValueError(bad_params_error_message)
        if participant is not None and user_id is not None:
            raise ValueError(bad_params_error_message)
        if participant is not None:
            return ResultFuture(self._impl.remove_participant_async(participant._impl), Participant)
        elif user_id is not None:
            return ResultFuture(self._impl.remove_participant_async(user_id), Participant)

    def end_conversation_async(self) -> ResultFuture:
        """
        Asynchronously ends the current conversation.

        :return: A future that is fulfilled once conversation has been ended.
        """
        return self._impl.end_conversation_async()

    def start_conversation_async(self) -> ResultFuture:
        """
        Asynchronously starts conversation.

        :return: A future that is fulfilled once conversation has been started.
        """
        return self._impl.start_conversation_async()

    def delete_conversation_async(self) -> ResultFuture:
        """
        Asynchronously deletes conversation. Any participants that are still part of the converation
        will be ejected after this call.

        :return: A future that is fulfilled once conversation has been deleted.
        """
        return self._impl.delete_conversation_async()

    def lock_conversation_async(self) -> ResultFuture:
        """
        Asynchronously locks conversation. After this no new participants will be able to join.

        :return: A future that is fulfilled once conversation has been locked.
        """
        return self._impl.lock_conversation_async()

    def unlock_conversation_async(self) -> ResultFuture:
        """
        Asynchronously unlocks conversation.

        :return: A future that is fulfilled once conversation has been unlocked.
        """
        return self._impl.unlock_conversation_async()

    def mute_all_participants_async(self) -> ResultFuture:
        """
        Asynchronously mutes all participants except for the host. This prevents others from generating
        transcriptions, or sending text messages.

        :return: A future that is fulfilled once participants have been muted.
        """
        return self._impl.mute_all_participants_async()

    def unmute_all_participants_async(self) -> ResultFuture:
        """
        Asynchronously unmutes all participants, which allows participants to generate
        transcriptions, or send text messages.

        :return: A future that is fulfilled once participants have been unmuted.
        """
        return self._impl.unmute_all_participants_async()

    def mute_participant_async(self, participant_id: str) -> ResultFuture:
        """
        Asynchronously mutes a particular participant. This will prevent them generating new transcriptions,
        or sending text messages.

        :param participant_id: the participant idnetifier.
        :return: A future that is fulfilled once participant has been muted.
        """
        return self._impl.mute_participant_async(participant_id)

    def unmute_participant_async(self, participant_id: str) -> ResultFuture:
        """
        Asynchronously unmutes a particular participant. This will allow generating new transcriptions,
        or sending text messages.

        :param participant_id: the participant idnetifier.
        :return: A future that is fulfilled once participant has been muted.
        """
        return self._impl.unmute_participant_async(participant_id)

    @property
    def authorization_token(self) -> str:
        """
        The authorization token that will be used for connecting to the service.

        .. note::

          The caller needs to ensure that the authorization token is valid. Before the
          authorization token expires, the caller needs to refresh it by calling this setter with a
          new valid token. As configuration values are copied when creating a new recognizer, the
          new token value will not apply to recognizers that have already been created. For
          recognizers that have been created before, you need to set authorization token of the
          corresponding recognizer to refresh the token. Otherwise, the recognizers will encounter
          errors during transcription.
        """
        return self._impl.get_authorization_token()

    @authorization_token.setter
    def authorization_token(self, authorization_token: str) -> None:
        return self._impl.set_authorization_token(authorization_token)

    @property
    def properties(self) -> PropertyCollection:
        """
        A collection of properties and their values defined for this Participant.
        """
        return self._impl.properties

    @staticmethod
    def _get_impl(object_type, speech_config, conversation_id):  # noqa: ANN001,ANN205
        if conversation_id is not None:
            return object_type.create_conversation_async(speech_config._impl, conversation_id).get()
        else:
            return object_type.create_conversation_async(speech_config._impl, "").get()


class ConversationTranscriber(Recognizer):
    """
    On object that performs conversation transcription operations.

    :param audio_config: The configuration for the audio input.
    """

    def __init__(self, audio_config: Optional[AudioConfig] = None):
        self._impl = self._get_impl(impl.ConversationTranscriber, audio_config)
        self._audio_keep_alive = audio_config

    def join_conversation_async(self, conversation: Conversation) -> ResultFuture:
        """
        Asynchronously joins to a conversation.

        :return: A future that is fulfilled once joined the conversation.
        """
        return self._impl.join_conversation_async(conversation._impl)

    def leave_conversation_async(self) -> ResultFuture:
        """
        Asynchronously leaves a conversation. After leaving a conversation, no transcribing or transcribed
        events will be sent to end users. End users need to join a conversation to get the events again.

        :return: A future that is fulfilled once left the conversation.
        """
        return self._impl.leave_conversation_async()

    def start_transcribing_async(self) -> ResultFuture:
        """
        Asynchronously starts conversation transcribing.

        :return: A future that is fulfilled once conversation transcription is started.
        """
        return self._impl.start_transcribing_async()

    def stop_transcribing_async(self) -> ResultFuture:
        """
        Asynchronously stops conversation transcribing.

        :return: A future that is fulfilled once conversation transcription is stopped.
        """
        return self._impl.stop_transcribing_async()

    @property
    def properties(self) -> PropertyCollection:
        """
        A collection of properties and their values defined for this Participant.
        """
        return self._impl.properties

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
    def transcribing(self) -> EventSignal:
        """
        Signal for events containing intermediate transcription results.

        Callbacks connected to this signal are called with a :class:`.ConversationTranscriptionEventArgs`,
        instance as the single argument.
        """
        return EventSignal(self._impl.transcribing, ConversationTranscriptionEventArgs)

    @property
    def transcribed(self) -> EventSignal:
        """
        Signal for events containing final transcription results (indicating a successful
        transcription attempt).

        Callbacks connected to this signal are called with a :class:`.ConversationTranscriptionEventArgs`,
        instance as the single argument.
        """
        return EventSignal(self._impl.transcribed, ConversationTranscriptionEventArgs)

    @property
    def canceled(self) -> EventSignal:
        """
        Signal for events containing canceled transcription results (indicating a transcription attempt
        that was canceled as a result or a direct cancellation request or, alternatively, a
        transport or protocol failure).

        Callbacks connected to this signal are called with a
        :class:`.ConversationTranscriptionCanceledEventArgs`, instance as the single argument.
        """
        return EventSignal(self._impl.canceled, ConversationTranscriptionCanceledEventArgs)

    @property
    def authorization_token(self) -> str:
        """
        The authorization token that will be used for connecting to the service.

        .. note::

          The caller needs to ensure that the authorization token is valid. Before the
          authorization token expires, the caller needs to refresh it by calling this setter with a
          new valid token. As configuration values are copied when creating a new recognizer, the
          new token value will not apply to recognizers that have already been created. For
          recognizers that have been created before, you need to set authorization token of the
          corresponding recognizer to refresh the token. Otherwise, the recognizers will encounter
          errors during transcription.
        """
        return self._impl.get_authorization_token()

    @authorization_token.setter
    def authorization_token(self, authorization_token: str) -> None:
        return self._impl.set_authorization_token(authorization_token)

    @staticmethod
    def _get_impl(object_type: Type[impl.ConversationTranscriber],
                  audio_config: Optional[AudioConfig]) -> impl.ConversationTranscriber:
        if audio_config is not None:
            return object_type._from_config(audio_config._impl)
        else:
            return object_type._from_config(None)
