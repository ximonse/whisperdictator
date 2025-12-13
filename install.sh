#!/bin/bash
echo "==================================="
echo "Installerar Whisperdictator"
echo "==================================="
echo ""

# Kolla om vi kör som root (behövs för apt)
if [ "$EUID" -ne 0 ]; then
    SUDO="sudo"
else
    SUDO=""
fi

echo "Installerar systemberoenden..."
echo ""

# Detektera pakethanterare
if command -v apt &> /dev/null; then
    # Debian/Ubuntu
    $SUDO apt update
    $SUDO apt install -y python3 python3-pip python3-tk ffmpeg portaudio19-dev
elif command -v dnf &> /dev/null; then
    # Fedora
    $SUDO dnf install -y python3 python3-pip python3-tkinter ffmpeg portaudio-devel
elif command -v pacman &> /dev/null; then
    # Arch
    $SUDO pacman -S --noconfirm python python-pip tk ffmpeg portaudio
elif command -v brew &> /dev/null; then
    # macOS
    brew install python ffmpeg portaudio
else
    echo "Okänd pakethanterare. Installera manuellt:"
    echo "- python3, pip, tkinter, ffmpeg, portaudio"
    exit 1
fi

echo ""
echo "Installerar Python-paket..."
pip3 install -r requirements.txt

echo ""
echo "==================================="
echo "Installation klar!"
echo "==================================="
echo ""
echo "Starta appen med:"
echo "  python3 Diktafon.py"
echo ""
echo "Eller gör startskriptet körbart:"
echo "  chmod +x start.sh"
echo "  ./start.sh"
echo ""
