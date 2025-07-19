# Whisperdictator

A compact floating dictaphone with Whisper (prepared) transcription and push-to-talk functionality.

What started as a quick escape from studying turned into the familiar slippery slope of coding... "just a little voice recorder," I said. "It'll only take a minute," I said. Several hours later, here we are with push-to-talk, Whisper transcription, and way too many features for what was supposed to be a simple houer distraction.

## Quick Start

1. Double-click `Installera_Allt.bat` (installs all dependencies)
2. Double-click `Starta_Diktafon.bat` (starts the app)
3. A small transparent window appears floating above all other programs

## Usage

### Basic Recording
- Click ▶ to start recording
- Click ⏸ to pause recording
- Click ■ to stop and start automatic transcription
- Click 🗑 to clear everything and start over

### Push-to-Talk (Recommended)
- Hold down `Right Shift + Right Arrow` to record
- Release keys to pause
- Collect multiple recording segments this way
- Click ■ when finished to transcribe everything at once

### After Transcription
- Text is automatically copied to clipboard
- ★ button turns green and becomes active
- Click ★ to copy text with additional AI prompt for further processing

## AI Prompt Customization
- Edit `ai-prompt.txt` to change the AI prompt used with the ★ button
- The prompt is automatically added before your transcribed text
- **Default**: "Rewrite and organize the text clearly. Summarize the text. Convert events with dates to Google calendar events, convert tasks to task items, convert notes to Google Keep objects."

**Examples of custom prompts:**
- "Translate to English and format as bullet points"
- "Extract action items and create a todo list"
- "Summarize in 3 sentences and highlight key points"
- "Format as professional email and correct grammar"

The AI prompt file allows non-technical users to customize behavior without touching code. If the file is missing, a simple fallback prompt is used.

## File Management
- Audio files saved in `recordings/` folder with timestamp
- Transcriptions saved in `transcriptions/` folder with timestamp
- Both files are kept for future reference

## Features
- Transparent floating widget (60% transparency)
- Hover over window for full visibility
- 90s-style gray tkinter design
- Always stays on top of screen
- Compact 200x50px size
- Timer shows total recording time
- Progress bar during transcription

## Technical Details
- Uses OpenAI Whisper (small model) for Swedish transcription
- Saves audio as 16kHz mono WAV (optimized for Whisper)
- Push-to-talk collects multiple segments before transcription
- Global hotkey works across all programs
- Automatic clipboard copying when finished

## Requirements
- Python 3.7+
- Microphone
- Windows (for .bat files, but code works on Linux/Mac with `pip install -r requirements.txt`)

## Troubleshooting
- **Global hotkey doesn't work**: Reinstall with `pip install pynput`
- **Microphone doesn't work**: Check Windows microphone settings
- **Whisper is slow**: First time loads the model (may take 1-2 minutes)

## License

MIT License - feel free to use, modify, and distribute as you wish.

---
*Built with Python, tkinter, Code Claude and a little help from my friends*
