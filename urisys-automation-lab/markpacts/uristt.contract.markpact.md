# uristt contract (MVP)

Scheme: `stt://`

## Routes

```txt
stt://local/session/{session}/command/start
stt://local/session/{session}/query/transcript
stt://local/audio/command/transcribe
```

## Engines (planned)

| Engine | Use case |
|--------|----------|
| browser Web Speech API | demo / quick tests |
| Vosk | offline CPU / RPi |
| whisper.cpp | local C++ inference |
| faster-whisper | PC/GPU quality |

## Pipeline

```txt
getUserMedia / MediaRecorder
  → stt://local/audio/command/transcribe
  → transcript
  → chat://local/uri/command/execute
```
