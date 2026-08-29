RENDER BACKEND SETUP

1. Upload ALL files in this folder to a GitHub repository.
2. Create a Render Web Service.
3. Build command: pip install -r requirements.txt
4. Start command: gunicorn app:app

Required Render environment variables:
MONGO_URI = MongoDB Atlas connection string
MONGO_DB_NAME = photo_portal
ADMIN_USERNAME = your admin username
ADMIN_PASSWORD = your strong password
JWT_SECRET = a long random secret
FRONTEND_ORIGINS = https://YOUR-HOSTINGER-DOMAIN,https://www.YOUR-HOSTINGER-DOMAIN

For the domain currently shown in your screenshot, use the exact site origin in FRONTEND_ORIGINS, for example:
https://gl.blazecorporation.in

Do NOT add a path such as /camera.html.
Do NOT add a trailing slash.

After deployment, open:
https://YOUR-RENDER-SERVICE.onrender.com/api/health

Expected response when MongoDB is connected:
{"database":"connected","status":"ok"}

Then put the exact Render service URL into the Hostinger frontend file:
js/config.js
