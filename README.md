# Airbander

## Description  
Airbander is an **educational, experimental** toolkit for fusing air-band voice with ADS-B position data into a unified **operational picture** of nearby air traffic for situational awareness.

## First milestone achieved
![screenshot of airband message transcription](docs/screenshot.png)
Continuous stream is now segmented into individual transmissions in real time and transcribed into text using parallel processing. See src/pipeline.py for example implementation.

## Features  
- **Voice Segmentation**: Split live air-band streams into individual WAV clips. (✔️ Done)  
- **ADS-B Ingestion**: Parse live ADS-B feeds (dump1090 or similar).  
- **Call-Sign Extraction**: Transcribe clips and extract call-signs. (partially implemented)
- **Data Fusion**: Align voice events with ADS-B tracks.  
- **Visualization**: Show fused data on a simple map.

## Roadmap  
1. **Segmentation Module**  
   - [✔️] Chunk continuous audio into per-transmission WAVs  
2. **ADS-B Receiver**  
   - [ ] Ingest and parse position reports  
3. **Call-Sign Extraction**  
   - [✔️,x] Transcribe audio and tag call-signs  
4. **Fusion Engine**  
   - [ ] Correlate voice and ADS-B data  
5. **UI Dashboard**  
   - [ ] Build a basic map-based visualization  

## Quick Start
```bash
# Clone and enter project
cd ~/src
git clone https://github.com/yourname/airbander.git
cd airbander

# Create & activate Python venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
pip install -r requirements.txt

# To run a real time transcriber do:
./src/pipeline.py https://some.atc.stream.provider.url


# Test the voice segmenter, preprocessing and transcription
# IN HOME OF THE PROJECT RUN in python console:
>>> from airbander_lib import Chunker AudioProcessing Transcriber 
>>> stream_chunking = Chunker("https://SomeATCstream.mp3")
>>> stream_chunking.start()
# wait for some transmissions to be captured and written to data/tmp
>>> stream_chunking.stop()
>>> denoise = AudioProcessing()
>>> denoise.preprocess("data/tmp/timestamped.wav")
# the .wav will be normalised and written to timestamp_DENOISED.wav in data/tmp
# now to run voice recognition on the wav:
>>> text = Transcriber()
>>> text.transcribe("path/to/.wav")
```

## License  
This project is released under the **MIT License**. You may copy, modify, merge, publish, distribute, and sublicense copies of the Software under the following conditions:

```
MIT License

Copyright (c) 2025 Airbander Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

> **Note:** This project is purely educational and experimental. It is not intended for operational or commercial use and carries no warranty of accuracy.
