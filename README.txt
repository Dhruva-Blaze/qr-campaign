RENDER BACKEND UPDATED

Required environment variables:
MONGO_URI
MONGO_DB_NAME=photo_portal
ADMIN_USERNAME
ADMIN_PASSWORD
JWT_SECRET
FRONTEND_ORIGINS=https://gl.blazecorporation.in

Important:
1. In MongoDB Atlas -> Network Access, add 0.0.0.0/0 temporarily for testing.
2. Copy a fresh MongoDB driver URI from Atlas -> Connect -> Drivers -> Python.
3. If the password contains special characters, URL-encode it in the URI.
4. This backend uses a lazy MongoClient so it is created after Gunicorn workers start.
5. It pins Python 3.12 via .python-version to avoid the previous Python 3.14 driver/TLS compatibility issue.

Test after deployment:
https://qr-campaign-1.onrender.com/api/health
Expected:
{"status":"ok","database":"connected","database_name":"photo_portal"}
