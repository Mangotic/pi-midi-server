#!/bin/bash

# Get the current user's home directory
USER_HOME=$(eval echo ~"$USER")
SCRIPT_PATH="$USER_HOME/midi_webserver.py"

# Ensure script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: $SCRIPT_PATH not found! Ensure 'midi_webserver.py' is in your home directory."
    exit 1
fi

# Ensure necessary directories exist
mkdir -p "$USER_HOME/midi_recordings"
mkdir -p "$USER_HOME/templates"

# Modify midi_webserver.py to use dynamic home folder
echo "Modifying midi_webserver.py to use dynamic home directory..."
sed -i "s|midi_dir = \"/home/pi/midi_recordings\"|midi_dir = \"$USER_HOME/midi_recordings\"|" "$SCRIPT_PATH"

# Ask user if they want to start the server on boot
echo "Do you want 'midi_webserver.py' to start automatically on boot? (y/n)"
read -r START_ON_BOOT

if [[ "$START_ON_BOOT" == "y" || "$START_ON_BOOT" == "Y" ]]; then
    echo "Adding to crontab..."
    
    # Remove any existing crontab entry for midi_webserver.py
    crontab -l | grep -v "$SCRIPT_PATH" | crontab -

    # Add new crontab entry
    (crontab -l; echo "@reboot /usr/bin/python3 $SCRIPT_PATH &") | crontab -
    
    echo "✔ MIDI web server will start automatically on boot!"
else
    echo "❌ Skipping autostart setup."
fi

echo "✅ Setup complete! You can start the server manually with:"
echo "   python3 $SCRIPT_PATH"
