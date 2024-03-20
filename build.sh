#!/bin/bash

# Define colors for logging
GREEN='\033[1;32m' # Bold green
CYAN='\033[1;36m' # Bold cyan
RED='\033[1;31m' # Bold red
NC='\033[0m' # No Color

# Function to log messages with color and bold text
log() {
    echo -e "${CYAN}[INFO] \033[1m$1${NC}"
}

# Function to log errors with color and bold text
error() {
    echo -e "${RED}[ERROR] \033[1m$1${NC}"
    exit 1
}

# Main build process
main() {
    log "Starting build process..."

    log "Checking prerequisites..."
    command -v python3 >/dev/null 2>&1 || error "Python3 is not installed"
    command -v pip >/dev/null 2>&1 || error "pip is not installed"

    log "Installing lolcat..."
    sudo apt-get install lolcat -y > /dev/null 2>&1 || error "Failed to install lolcat"
    log "lolcat installed successfully"

    log "Installing Tor..."
    sudo apt-get install tor -y > /dev/null 2>&1 || error "Failed to install Tor"
    log "Tor installed successfully"

    log "Creating Python virtual environment..."
    VENV_NAME="OnyForce_venv"
    python3 -m venv "$VENV_NAME" || error "Failed to create Python virtual environment"
    log "Python virtual environment created successfully"

    log "Sourcing into Python virtual environment..."
    source "$VENV_NAME/bin/activate" || error "Failed to source into Python virtual environment"
    log "Sourced into Python virtual environment successfully"

    log "Installing Python requirements..."
    REQUIREMENTS_FILE="requirements.txt"
    pip install -r "$REQUIREMENTS_FILE" > /dev/null 2>&1 || error "Failed to install Python requirements"
    log "Python requirements installed successfully"

    log "Build completed successfully"
}

# Start the build process
main

# Clear the screen
clear

# Run main.py script
#log "Running main.py script..."
python3 main.py
#log "main.py script execution completed"

# Exit
#log "Exiting..."
