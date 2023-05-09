import whisper
import os
import pathlib
# this didn't work. CLI worked.
# model = whisper.load_model("base")
# audioPath = os.path.join(os.getcwd(), "test/KNS07052023011554.wav")
# result = model.transcribe(audioPath, fp16=False)
# print(result["text"])


# i have a hunch that this is gonna work if you change the directory.
# fileName = pathlib.Path("records/event17/ZXN08052023180558.wav")

fileName = pathlib.Path("records/event17/SAM08052023180710.wav")
filePath = os.path.join(os.getcwd(), os.path.join(fileName.parts[0], fileName.parts[1]))
os.chdir(filePath)
print("the file name is : ", fileName.parts[-1])
model = whisper.load_model("large")
result = model.transcribe(fileName.parts[-1], fp16=False, language="Indonesian")
print(result["text"])

# rootPath = os.getcwd()
# os.chdir(os.path.join(rootPath, ))
