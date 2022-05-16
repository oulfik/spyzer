# Spyzer

Spyzer is a speech analysis toolkit. It provides audio analysis, diarization and transcription functionality. All in one package. The GUI was made with [Kivy](https://kivy.org/#home).

## Installation


```bash
pip install -r requirements.txt
```
### Transcription
Spyzer uses [Vosk](https://alphacephei.com/vosk/) under the hood for the transcription feature. You need to install ffmpeg an you machine for the transcription to work. An instruction on how to do it can be found [here](https://windowsloop.com/install-ffmpeg-windows-10/). You also need a model that you can find [here](https://alphacephei.com/vosk/models). Vosk models are language depended so if you want to transcribe english speech files you need to download a model from the english section. Vosk supports more than 20 languages.

## Usage

```python
python main.py
```



## License
[MIT](https://choosealicense.com/licenses/mit/)