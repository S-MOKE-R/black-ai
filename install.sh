
---

## 📄 **File 4: `install.sh` 

```bash
#!/bin/bash
# Black AI Installer
# Developer: @S_MOKE_R
# GitHub: https://github.com/S-MOKE-R
# Telegram: https://t.me/S_MOKE_R
# Channel: https://t.me/VOID_SMOKER

echo "🔒 Black AI Installer"
echo "Developer: @S_MOKE_R"
echo "GitHub: https://github.com/S-MOKE-R"
echo "Telegram: https://t.me/S_MOKE_R"
echo "Channel: https://t.me/VOID_SMOKER"
echo ""

# Check dependencies
echo "Checking dependencies..."
if ! command -v jq &> /dev/null; then
    echo "Installing jq..."
    sudo apt update && sudo apt install jq -y
fi

if ! command -v curl &> /dev/null; then
    echo "Installing curl..."
    sudo apt install curl -y
fi

if ! command -v python3 &> /dev/null; then
    echo "Installing python3..."
    sudo apt install python3 python3-tk -y
fi

# Create directory
mkdir -p ~/black
cd ~/black

# Download files from GitHub
echo "Downloading files from GitHub..."
curl -s -O https://raw.githubusercontent.com/S-MOKE-R/black-ai/main/black.sh
curl -s -O https://raw.githubusercontent.com/S-MOKE-R/black-ai/main/black_gui.py
curl -s -O https://raw.githubusercontent.com/S-MOKE-R/black-ai/main/README.md
curl -s -O https://raw.githubusercontent.com/S-MOKE-R/black-ai/main/LICENSE

chmod +x black.sh
chmod +x black_gui.py

# Create desktop shortcut
cat > ~/.local/share/applications/black.desktop << EOF
[Desktop Entry]
Name=Black AI
Comment=Bug Bounty Assistant
Exec=python3 /home/$USER/black/black_gui.py
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;System;
EOF

echo ""
echo "✅ Installation complete!"
echo ""
echo "🔒 Black AI installed successfully!"
echo "Developer: @S_MOKE_R"
echo "GitHub: https://github.com/S-MOKE-R"
echo "Telegram: https://t.me/S_MOKE_R"
echo "Channel: https://t.me/VOID_SMOKER"
echo ""
echo "Launch with: python3 ~/black/black_gui.py"
