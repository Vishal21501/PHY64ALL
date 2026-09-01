#!/bin/bash

echo "🚀 Deploying PHY64ALL Frontend..."

# Get backend URL
if [ -f "frontend/.env" ]; then
    BACKEND_URL=$(grep "BACKEND_URL" frontend/.env | cut -d '=' -f2)
else
    echo "⚠️  No backend URL found. Please enter it:"
    read -p "Backend URL: " BACKEND_URL
fi

# Get Firebase config
echo "📝 Firebase Configuration"
read -p "Firebase API Key: " FIREBASE_API_KEY
read -p "Firebase Auth Domain: " FIREBASE_AUTH_DOMAIN
read -p "Firebase Project ID: " PROJECT_ID
read -p "Firebase Storage Bucket: " FIREBASE_STORAGE_BUCKET
read -p "Firebase Messaging Sender ID: " FIREBASE_MESSAGING_SENDER_ID
read -p "Firebase App ID: " FIREBASE_APP_ID

# Create .env file
cat > frontend/.env << EOL
VITE_FIREBASE_API_KEY=$FIREBASE_API_KEY
VITE_FIREBASE_AUTH_DOMAIN=$FIREBASE_AUTH_DOMAIN
VITE_FIREBASE_PROJECT_ID=$PROJECT_ID
VITE_FIREBASE_STORAGE_BUCKET=$FIREBASE_STORAGE_BUCKET
VITE_FIREBASE_MESSAGING_SENDER_ID=$FIREBASE_MESSAGING_SENDER_ID
VITE_FIREBASE_APP_ID=$FIREBASE_APP_ID
BACKEND_URL=$BACKEND_URL
EOL

echo "✅ .env file created!"

# Deploy to Streamlit Cloud
echo ""
echo "📤 To deploy to Streamlit Cloud:"
echo "1. Push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Deploy PHY64ALL'"
echo "   git push origin main"
echo ""
echo "2. Go to https://share.streamlit.io"
echo "3. Connect your GitHub repository"
echo "4. Select the frontend/streamlit_app.py file"
echo "5. Add the following secrets:"
echo "   - VITE_FIREBASE_API_KEY"
echo "   - VITE_FIREBASE_AUTH_DOMAIN"
echo "   - VITE_FIREBASE_PROJECT_ID"
echo "   - VITE_FIREBASE_STORAGE_BUCKET"
echo "   - VITE_FIREBASE_MESSAGING_SENDER_ID"
echo "   - VITE_FIREBASE_APP_ID"
echo "   - BACKEND_URL"
echo ""
echo "🔗 Your app will be available at: https://phy64all.streamlit.app"
