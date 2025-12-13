# Whisperdictator

Röstinspelning med automatisk transkribering. Håll inne en knappkombination, prata, släpp - texten hamnar i urklipp.

## Vad gör appen?

- Spelar in din röst när du håller inne **Höger Shift + Högerpil**
- Omvandlar tal till text (fungerar offline, ingen kostnad)
- Kopierar texten till urklipp automatiskt
- Liten genomskinlig widget som alltid ligger överst

---

## Installation (Windows)

### Steg 1: Installera Python

1. Gå till **https://www.python.org/downloads/**
2. Klicka på den stora gula knappen **"Download Python 3.x.x"**
3. Öppna filen som laddades ner
4. **VIKTIGT:** Kryssa i rutan **"Add Python to PATH"** längst ner i installationsfönstret
5. Klicka **"Install Now"**
6. Vänta tills det står "Setup was successful"
7. Stäng installationsfönstret

### Steg 2: Ladda ner Whisperdictator

1. Klicka på den gröna knappen **"Code"** högst upp på denna sida
2. Välj **"Download ZIP"**
3. Öppna ZIP-filen och dra ut mappen till valfri plats (t.ex. Skrivbordet)

### Steg 3: Installera beroenden

1. Öppna mappen du precis packade upp
2. **Dubbelklicka på `Installera_Allt.bat`**
3. Ett svart fönster öppnas - vänta medan saker installeras (kan ta flera minuter)
4. När det står **"Installation klar!"** - tryck valfri tangent för att stänga

### Steg 4: Starta appen

1. **Dubbelklicka på `Starta_Diktafon.bat`**
2. En liten grå ruta dyker upp - det är appen!
3. Första gången tar det ~30 sekunder att ladda (laddar AI-modellen)

---

## Installation (Linux/Ubuntu)

### Steg 1: Ladda ner Whisperdictator

1. Klicka på den gröna knappen **"Code"** högst upp på denna sida
2. Välj **"Download ZIP"**
3. Packa upp ZIP-filen där du vill ha den

Eller via terminal:
```bash
git clone https://github.com/ximonse/whisperdictator.git
cd whisperdictator
```

### Steg 2: Kör installationsskriptet

```bash
chmod +x install.sh
./install.sh
```

Skriptet installerar automatiskt:
- Python 3 och pip
- tkinter (för gränssnittet)
- FFmpeg (för ljudbearbetning)
- portaudio (för mikrofonåtkomst)
- Alla Python-paket från requirements.txt

### Steg 3: Starta appen

```bash
python3 Diktafon.py
```

Eller:
```bash
chmod +x start.sh
./start.sh
```

**Tips:** Första gången tar det ~1-2 minuter att ladda (AI-modellen laddas ner).

---

## Installation (macOS)

Samma som Linux, men du behöver **Homebrew** installerat först:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Sen kör du `./install.sh` som vanligt.

---

## Användning

### Spela in med tangentbord (rekommenderat)
1. Håll inne **Höger Shift + Högerpil** samtidigt
2. Prata
3. Släpp tangenterna
4. Vänta på "KLART" - texten finns nu i urklipp (Ctrl+V för att klistra in)

### Spela in med knappar
1. Klicka **▶** för att starta inspelning
2. Klicka **■** för att stoppa och transkribera
3. Texten kopieras automatiskt till urklipp

### Knappförklaring
- **▶** = Starta/pausa inspelning
- **■** = Stoppa och omvandla till text
- **🗑** = Rensa inspelning
- **★** = Kopiera med AI-prompt (för att bearbeta texten vidare)

---

## Felsökning

### Windows

**"Python hittas inte"**
→ Du glömde kryssa i "Add Python to PATH". Avinstallera Python och installera igen, kryssa i rutan.

**"FFmpeg saknas"**
→ Kör `Installera_Allt.bat` igen, eller installera FFmpeg manuellt från https://ffmpeg.org

### Linux

**"No module named tkinter"**
→ Installera tkinter: `sudo apt install python3-tk`

**"No module named pyaudio" eller "portaudio.h not found"**
→ Installera portaudio: `sudo apt install portaudio19-dev` och sedan `pip3 install pyaudio`

**"ALSA lib" varningar**
→ Ignorera dessa - appen fungerar ändå. Det är bara Linux som klagar på ljudkonfiguration.

### Alla system

**Appen fryser vid start**
→ Normalt första gången! AI-modellen (~500 MB) laddas ner. Vänta 1-2 minuter.

**Ingen text kommer ut**
→ Kolla att mikrofonen fungerar. Prata tydligt och nära mikrofonen.

---

## Teknisk info

- Python 3.7+
- OpenAI Whisper (small-modellen, optimerad för svenska)
- Ljudformat: 16kHz mono WAV
- Inspelningar sparas i `recordings/`
- Transkriptioner sparas i `transcriptions/`

## Licens

MIT License - Simon Zetterberg 2025
