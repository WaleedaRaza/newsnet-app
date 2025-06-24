#!/bin/bash

echo "🚀 Setting up NewsNet - AI-Powered News Analysis App"
echo "=================================================="

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed. Please install Flutter first:"
    echo "   https://flutter.dev/docs/get-started/install"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Frontend setup
echo ""
echo "📱 Setting up Flutter frontend..."
cd "$(dirname "$0")"

# Get Flutter dependencies
echo "Installing Flutter dependencies..."
flutter pub get

# Generate code
echo "Generating code..."
flutter packages pub run build_runner build --delete-conflicting-outputs

echo "✅ Frontend setup complete"

# Backend setup
echo ""
echo "🔧 Setting up Python backend..."
cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit backend/.env with your API keys and database configuration"
fi

echo "✅ Backend setup complete"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your API keys"
echo "2. Set up PostgreSQL database"
echo "3. Start the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "4. Start the frontend: flutter run"
echo ""
echo "For detailed instructions, see README.md" 