#!/bin/bash

echo "🚀 Deploying PHY64ALL Frontend to Firebase Hosting..."

# Get project ID
export PROJECT_ID=$(gcloud config get-value project)
echo "📋 Project ID: $PROJECT_ID"

# Get backend URL from saved file or prompt
if [ -f "frontend/.env" ]; then
    BACKEND_URL=$(grep "BACKEND_URL" frontend/.env | cut -d '=' -f2)
    echo "🔗 Using backend URL: $BACKEND_URL"
else
    echo "⚠️  No backend URL found. Please enter the backend URL:"
    read -p "Backend URL: " BACKEND_URL
fi

# Get Firebase config from user or environment
echo "📝 Firebase Configuration"
echo "Please enter your Firebase config values:"
read -p "Firebase API Key: " FIREBASE_API_KEY
read -p "Firebase Auth Domain: " FIREBASE_AUTH_DOMAIN
read -p "Firebase Storage Bucket: " FIREBASE_STORAGE_BUCKET
read -p "Firebase Messaging Sender ID: " FIREBASE_MESSAGING_SENDER_ID
read -p "Firebase App ID: " FIREBASE_APP_ID

# Create .env file for frontend
echo "📝 Creating frontend .env file..."
cat > frontend/.env << EOL
VITE_FIREBASE_API_KEY=$FIREBASE_API_KEY
VITE_FIREBASE_AUTH_DOMAIN=$FIREBASE_AUTH_DOMAIN
VITE_FIREBASE_PROJECT_ID=$PROJECT_ID
VITE_FIREBASE_STORAGE_BUCKET=$FIREBASE_STORAGE_BUCKET
VITE_FIREBASE_MESSAGING_SENDER_ID=$FIREBASE_MESSAGING_SENDER_ID
VITE_FIREBASE_APP_ID=$FIREBASE_APP_ID
BACKEND_URL=$BACKEND_URL
EOL

echo "✅ .env file created successfully!"

# Check if firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "📦 Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

# Initialize Firebase Hosting (if not already initialized)
if [ ! -f "firebase.json" ]; then
    echo "🔧 Initializing Firebase Hosting..."
    firebase init hosting --project $PROJECT_ID
else
    echo "✅ Firebase Hosting already initialized"
fi

# Build the frontend (create static files)
echo "🏗️ Building frontend..."
cd frontend

# Create a static build directory
mkdir -p build

# Copy streamlit app to build directory (for Firebase Hosting)
# Note: Since Streamlit requires a server, we'll use Firebase Hosting as a proxy
# For production, you might want to use a different approach

# Create a simple index.html that redirects to Streamlit
cat > build/index.html << EOL
<!DOCTYPE html>
<html>
<head>
    <title>PHY64ALL - Physics Solver</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: white;
        }
        .container {
            text-align: center;
            padding: 40px;
        }
        h1 {
            font-size: 4rem;
            background: linear-gradient(135deg, #6C63FF, #00D4FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .subtitle {
            font-size: 1.2rem;
            color: #A0A0C0;
            margin-bottom: 30px;
        }
        .loading {
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #6C63FF;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .note {
            margin-top: 30px;
            font-size: 0.9rem;
            color: #6C63FF;
        }
        a {
            color: #6C63FF;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚛️ PHY64ALL</h1>
        <p class="subtitle">Multi-Agent Physics Solver</p>
        <div class="loading"></div>
        <p class="note">
            ⏳ Loading the application...<br>
            If you're not redirected automatically, 
            <a href="#" onclick="window.location.href='https://$BACKEND_URL'">click here</a>
        </p>
    </div>
</body>
</html>
EOL

# Copy the app files to build directory
cp streamlit_app.py build/
cp requirements.txt build/
cp -r ../backend build/ 2>/dev/null || true

cd ..

# Create firebase.json for proper hosting configuration
cat > firebase.json << EOL
{
  "hosting": {
    "public": "frontend/build",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**",
        "headers": [
          {
            "key": "Access-Control-Allow-Origin",
            "value": "*"
          },
          {
            "key": "X-Content-Type-Options",
            "value": "nosniff"
          }
        ]
      }
    ]
  }
}
EOL

# Deploy to Firebase Hosting
echo "🚀 Deploying to Firebase Hosting..."
firebase deploy --only hosting --project $PROJECT_ID

# Get the hosting URL
HOSTING_URL=$(firebase hosting:list --project $PROJECT_ID --json | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "✅ Frontend deployed successfully!"
echo "🔗 Frontend URL: $HOSTING_URL"
echo ""
echo "📝 Summary:"
echo "   Backend: $BACKEND_URL"
echo "   Frontend: $HOSTING_URL"
echo ""
echo "⚠️  Note: For Streamlit apps, you might want to use Streamlit Sharing or a different hosting approach."
echo "   The current deployment creates a landing page that links to your backend."
