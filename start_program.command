cd "$(dirname "$0")"
python Scripts/GUI.py &
osascript -e 'tell application "Terminal" to close (every window whose name contains "start.sh")' &
