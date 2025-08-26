#!/bin/bash
set -e

echo "🏗️  Building DocuShield AI Frontend..."

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build frontend
echo "🔨 Building frontend assets..."
npm run build

# Verify build
if [ -d "dist" ]; then
    echo "✅ Frontend build completed successfully!"
    echo "📁 Built assets are available in frontend/dist/"
    
    # Show build size
    echo "📊 Build size:"
    du -sh dist/
else
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "🎉 Frontend ready for offline deployment!"