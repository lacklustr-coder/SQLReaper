#!/bin/bash

# Aikido Security Scanner for SQLReaper
# Linux/Mac version

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "========================================="
echo "  Aikido Security Scanner for SQLReaper"
echo "========================================="
echo ""

# Check if Aikido CLI is installed
if ! command -v aikido &> /dev/null; then
    echo -e "${RED}[WARN] Aikido CLI not found!${NC}"
    echo ""
    echo "To install Aikido CLI:"
    echo "  npm install -g @aikidosec/cli"
    echo "  OR"
    echo "  pip install aikido-cli"
    echo ""
    echo "After installation, run this script again."
    exit 1
fi

echo -e "${GREEN}[OK] Aikido CLI found${NC}"
echo ""

# Function to display menu
show_menu() {
    echo "========================================="
    echo "  Select Scan Type:"
    echo "========================================="
    echo ""
    echo "  1. Quick Dependency Scan"
    echo "  2. Full Security Scan (All)"
    echo "  3. Secrets Detection Only"
    echo "  4. SAST (Code Analysis) Only"
    echo "  5. View Configuration"
    echo "  6. Exit"
    echo ""
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (1-6): " choice

    case $choice in
        1)
            echo ""
            echo "========================================="
            echo "  Running Dependency Scan..."
            echo "========================================="
            echo ""
            aikido scan dependencies
            echo ""
            echo -e "${GREEN}Scan completed!${NC}"
            read -p "Press Enter to continue..."
            ;;
        2)
            echo ""
            echo "========================================="
            echo "  Running Full Security Scan..."
            echo "========================================="
            echo ""
            aikido scan --all --config aikido.yml
            echo ""
            echo -e "${GREEN}Scan completed!${NC}"
            read -p "Press Enter to continue..."
            ;;
        3)
            echo ""
            echo "========================================="
            echo "  Running Secrets Detection..."
            echo "========================================="
            echo ""
            aikido scan secrets
            echo ""
            echo -e "${GREEN}Scan completed!${NC}"
            read -p "Press Enter to continue..."
            ;;
        4)
            echo ""
            echo "========================================="
            echo "  Running Code Analysis (SAST)..."
            echo "========================================="
            echo ""
            aikido scan sast
            echo ""
            echo -e "${GREEN}Scan completed!${NC}"
            read -p "Press Enter to continue..."
            ;;
        5)
            echo ""
            echo "========================================="
            echo "  Current Aikido Configuration"
            echo "========================================="
            echo ""
            if [ -f "aikido.yml" ]; then
                cat aikido.yml
            else
                echo -e "${RED}[ERROR] aikido.yml not found!${NC}"
            fi
            echo ""
            read -p "Press Enter to continue..."
            ;;
        6)
            echo ""
            echo "Exiting Aikido Scanner. Stay secure!"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}[ERROR] Invalid choice. Please select 1-6.${NC}"
            echo ""
            sleep 2
            ;;
    esac
done
