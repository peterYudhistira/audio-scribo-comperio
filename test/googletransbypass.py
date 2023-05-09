from googletrans import Translator

tl = Translator()

textInput = input("Say something : ")
textOutput = tl.translate(textInput, src="ja", dest="en")
print(textOutput.text)


