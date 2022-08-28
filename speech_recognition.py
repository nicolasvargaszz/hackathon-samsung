import azure.cognitiveservices.speech as speechsdk
from datetime import datetime
#    return render_template("nombre.html",datos=datos)
def voice_to_text(audiofile):
    speech_config = speechsdk.SpeechConfig(subscription="9f0e9105b01446e9a97f495cf1404ff2", region="westus2")
    speech_config.speech_recognition_language="es-ES"

    audio_config = speechsdk.audio.AudioConfig(filename=audiofile)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Que te gustaria pedir?.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    #resultado_usuario = speech_recognition_result
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Errtranscripcionor details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    return speech_recognition_result

#with open("sintomas.wav",'r')as f:
# result_voice = voice_to_text("sintomas.wav")


# save_to_txt(result_voice)

if __name__ == "__main__":
    voice_to_text()