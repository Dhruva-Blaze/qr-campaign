RENDER BACKEND

1. Upload these files to a GitHub repository.
2. Create Render Web Service from the repo.
3. Build: pip install -r requirements.txt
4. Start: gunicorn app:app
5. Set environment variables:
   MONGO_URI = your MongoDB Atlas connection string
   MONGO_DB_NAME = photo_portal
   ADMIN_USERNAME = admin (or your choice)
   ADMIN_PASSWORD = choose a strong password (plain password works; a Werkzeug password hash also works)
   JWT_SECRET = long random secret
   FRONTEND_ORIGINS = https://yourdomain.com,https://www.yourdomain.com

MongoDB Atlas: create a database user, add the Render connection as allowed (or temporarily allow access while testing), then copy the mongodb+srv connection string.

After Render gives you a URL, put that URL in Hostinger frontend js/config.js.
