#!/bin/bash
#
# Setup script for External IP Change Notifier
# This script helps with initial project setup
#

set -e  # Exit on any error

PROJECT_DIR="/Users/villekorhonen/projects/external-ip-change-notifier"
VENV_DIR="$PROJECT_DIR/venv"

echo "🚀 Setting up External IP Change Notifier..."

# Change to project directory
cd "$PROJECT_DIR" || {
    echo "❌ Error: Cannot change to project directory $PROJECT_DIR"
    exit 1
}

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your ntfy configuration"
else
    echo "✅ .env file already exists"
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Make scripts executable
echo "🔐 Setting script permissions..."
chmod +x run_ip_monitor.sh

# Test the script
echo "🧪 Testing the script..."
python main.py --test --ip "192.168.1.100"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your ntfy topic and credentials"
echo "2. Test with: python main.py --test --ip 1.2.3.4"
echo "3. Add to crontab:"
echo "   */15 * * * * $PROJECT_DIR/run_ip_monitor.sh"
echo ""
echo "For detailed instructions, see README.md"
