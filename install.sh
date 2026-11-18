#!/usr/bin/env bash
# Installs Notepad for the current user: apps-menu entry and `notepad` command.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
APPS="$HOME/.local/share/applications"
BIN="$HOME/.local/bin"

chmod +x "$DIR/notepad.py"
mkdir -p "$APPS" "$BIN"
ln -sf "$DIR/notepad.py" "$BIN/notepad"

cat > "$APPS/io.local.Notepad.desktop" <<EOF
[Desktop Entry]
Name=Notepad
GenericName=Text Editor
Comment=Write notes with Markdown formatting, tabs and session restore
Exec=$DIR/notepad.py %F
Icon=accessories-text-editor
Terminal=false
Type=Application
Categories=Utility;TextEditor;
MimeType=text/plain;text/markdown;text/x-markdown;
Keywords=notepad;text;editor;markdown;notes;
StartupNotify=true
StartupWMClass=io.local.Notepad
Actions=new-window;

[Desktop Action new-window]
Name=New Window
Exec=$DIR/notepad.py
EOF

update-desktop-database "$APPS" 2>/dev/null || true
echo "Installed. Open Notepad from the apps menu or run: notepad"
