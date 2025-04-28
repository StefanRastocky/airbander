#!/usr/bin/env python3

from airbander_lib import Transcriber

writer = Transcriber()
text = writer.transcribe("data/tmp/denoised.wav")
print(text)
