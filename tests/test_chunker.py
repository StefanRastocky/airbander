#!/usr/bin/env python3

from airbander_lib import Chunker
from time import time, sleep

EMPYR_url = "http://d.liveatc.net/kewr_klga_app_empyr"

empChunker = Chunker(EMPYR_url)
empChunker.start()
sleep(30)
empChunker.stop()

