import whisper
import os
import pathlib

# # for some reason, pathing does not work. So my function will cd to related directory, do the transcription, then go back to the program folder
fileName = "records\event18\YOT11052023020940.wav"
# filePath = os.path.join(os.getcwd(), os.path.join(fileName.parts[0], fileName.parts[1]))
# os.chdir(filePath)
# # print("the file name is : ", fileName.parts[-1])

# # result = model.transcribe(fileName.parts[-1], fp16=False, language="Indonesian")
# print(os.listdir())
# two_up = pathlib.Path(__file__).resolve().parents[1]
# os.chdir(two_up)
# print(os.listdir())

# def TranscribeText(fileName, transcribeLang="Indonesian"):
#     model = whisper.load_model("large")
#     filenamePath = pathlib.Path(fileName)
#     filePath = os.path.join(os.getcwd(), os.path.join(filenamePath.parts[0], filenamePath.parts[1]))
#     os.chdir(filePath)
#     result = model.transcribe(filenamePath.parts[-1], fp16=False, language=transcribeLang)
    
#     # go back to the directory
#     os.chdir()
    
#     return result["text"]
print("*" * 80)
print(os.path.join(os.getcwd(), fileName))
model = whisper.load_model("large")
fullPath = os.path.join(os.getcwd(), fileName)
result = model.transcribe(fullPath, fp16=False, language="Indonesian")["text"]
print(result)

