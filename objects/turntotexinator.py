import whisper
import os
import googletrans as gt

# behold the most critical non-core component: the Turn-to-textinator
# it transcribes an audio file and translates to English if it isn't already.
# takes a .wav and returns a string. The saving will be done in the main app, invoking the db function.

class TurnToTextinator():
    def __init__(self) -> None:
        self.whisperModel = whisper.load_model("large")
        self.translator = gt.Translator()

    def TranslateText(self, text, src="auto", dest="en"):
        return self.translator.translate(text, src=src, dest=dest).text

    def TranscribeText(self, fileName, transcribeLang="id"):
        filenamePath = os.path.join(os.getcwd(), fileName)
        result = self.whisperModel.transcribe(filenamePath, fp16=False, language=transcribeLang)
        return result["text"]
    
    def TwoForOneSpecial(self, fileName, transcribeLang="id", translateLang="en"):
        text = self.TranscribeText(fileName, transcribeLang)
        return self.TranslateText(text, transcribeLang, translateLang)
    
    def SaySomething(self):
        print("a platypus? PERRY THE PLATYPUS???")
        
# ttt = TurnToTextinator()
# text = ttt.TranscribeText("records\event18\YOT11052023020940.wav", transcribeLang="Indonesian")
# tlText = ttt.TranslateText(text, "id", "en")
# print(text)
# print("-" * 80)
# print(tlText)
