import whisper
import googletrans as gt
import pathlib
import os

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
        filenamePath = pathlib.Path(fileName)
        # go to the voice clip's directory
        filePath = os.path.join(os.getcwd(), os.path.join(filenamePath.parts[0], filenamePath.parts[1]))
        os.chdir(filePath)
        result = self.whisperModel.transcribe(filenamePath.parts[-1], fp16=False, language=transcribeLang)
        # go back to the Program's root directory.
        two_up = pathlib.Path(__file__).resolve().parents[1]
        os.chdir(two_up)
        return result["text"]
    
    def TwoForOneSpecial(self, fileName, transcribeLang="id", translateLang="en"):
        text = self.TranscribeText(fileName, transcribeLang)
        return self.TranslateText(text, transcribeLang, translateLang)
    
    def SaySomething(self):
        print("a platypus? PERRY THE PLATYPUS???")
# ttt = TurnToTextinator()
# text = ttt.TranscribeText("records\event17\BH09052023214407.wav", transcribeLang="English")
# tlText = ttt.TranslateText(text, "en", "id")
# print(tlText)
