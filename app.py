import os, base64, uuid
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient, DESCENDING
from gridfs import GridFS
from bson import ObjectId
from werkzeug.security import check_password_hash
import jwt

app=Flask(__name__)
MONGO_URI=os.environ.get('MONGO_URI')
DB_NAME=os.environ.get('MONGO_DB_NAME','photo_portal')
ADMIN_USERNAME=os.environ.get('ADMIN_USERNAME','admin')
ADMIN_PASSWORD=os.environ.get('ADMIN_PASSWORD')
JWT_SECRET=os.environ.get('JWT_SECRET')
if not MONGO_URI or not ADMIN_PASSWORD or not JWT_SECRET: raise RuntimeError('Set MONGO_URI, ADMIN_PASSWORD and JWT_SECRET environment variables.')
origins=[x.strip() for x in os.environ.get('FRONTEND_ORIGINS','http://localhost').split(',')]
CORS(app, resources={r'/api/*':{'origins':origins}})
client=MongoClient(MONGO_URI)
db=client[DB_NAME]; inquiries=db.inquiries; fs=GridFS(db)

def verify_password(password):
    stored=ADMIN_PASSWORD
    return check_password_hash(stored,password) if stored.startswith(('pbkdf2:','scrypt:')) else password==stored

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args,**kwargs):
        header=request.headers.get('Authorization','')
        if not header.startswith('Bearer '): return jsonify(message='Unauthorized'),401
        try: jwt.decode(header[7:],JWT_SECRET,algorithms=['HS256'])
        except Exception: return jsonify(message='Unauthorized'),401
        return fn(*args,**kwargs)
    return wrapper

def serialize(doc):
    return {'id':str(doc['_id']),'name':doc.get('name',''),'mobile':doc.get('mobile',''),'city':doc.get('city',''),'looking_for_home_loan':doc.get('looking_for_home_loan',''),'loan_purpose':doc.get('loan_purpose',''),'loan_amount':doc.get('loan_amount',''),'occupation':doc.get('occupation',''),'selected_frame':doc.get('selected_frame',''),'created_at':doc.get('created_at'),'has_photo':bool(doc.get('photo_file_id'))}

@app.get('/api/health')
def health(): return jsonify(status='ok')

@app.post('/api/inquiries')
def create_inquiry():
    data=request.get_json(silent=True) or {}
    required=['name','mobile','city','looking_for_home_loan','image']
    if any(not str(data.get(k,'')).strip() for k in required): return jsonify(message='Missing required fields'),400
    if data['looking_for_home_loan'] not in ('Yes','No'): return jsonify(message='Invalid home loan choice'),400
    if data['looking_for_home_loan']=='Yes' and any(not str(data.get(k,'')).strip() for k in ['loan_purpose','loan_amount','occupation']): return jsonify(message='Complete all home loan fields'),400
    image=data['image']
    try:
        raw=base64.b64decode(image.split(',',1)[1] if ',' in image else image)
    except Exception: return jsonify(message='Invalid image'),400
    if len(raw)>12*1024*1024: return jsonify(message='Image is too large'),400
    fid=fs.put(raw,filename=f'{uuid.uuid4().hex}.png',content_type='image/png')
    doc={k:data.get(k,'') for k in ['name','mobile','city','looking_for_home_loan','loan_purpose','loan_amount','occupation','selected_frame']}
    if doc['looking_for_home_loan']=='No': doc.update(loan_purpose='',loan_amount='',occupation='')
    doc.update(photo_file_id=fid,created_at=datetime.now(timezone.utc).isoformat())
    result=inquiries.insert_one(doc)
    return jsonify(success=True,id=str(result.inserted_id)),201

@app.post('/api/admin/login')
def login():
    data=request.get_json(silent=True) or {}
    if data.get('username')!=ADMIN_USERNAME or not verify_password(data.get('password','')): return jsonify(message='Invalid username or password'),401
    token=jwt.encode({'sub':ADMIN_USERNAME,'iat':datetime.now(timezone.utc),'exp':datetime.now(timezone.utc).timestamp()+60*60*12},JWT_SECRET,algorithm='HS256')
    return jsonify(token=token)

@app.get('/api/admin/stats')
@admin_required
def stats():
    today=datetime.now(timezone.utc).date().isoformat()
    return jsonify(total_inquiries=inquiries.count_documents({}),today_inquiries=inquiries.count_documents({'created_at':{'$regex':'^'+today}}),total_photos=inquiries.count_documents({'photo_file_id':{'$exists':True}}))

@app.get('/api/admin/inquiries')
@admin_required
def list_inquiries(): return jsonify([serialize(x) for x in inquiries.find().sort('created_at',DESCENDING)])

@app.get('/api/admin/photos/<inquiry_id>')
@admin_required
def photo(inquiry_id):
    try: doc=inquiries.find_one({'_id':ObjectId(inquiry_id)})
    except Exception: doc=None
    if not doc or not doc.get('photo_file_id'): return jsonify(message='Not found'),404
    f=fs.get(doc['photo_file_id']); from io import BytesIO
    return send_file(BytesIO(f.read()),mimetype=f.content_type or 'image/png')

@app.delete('/api/admin/inquiries/<inquiry_id>')
@admin_required
def delete(inquiry_id):
    try: doc=inquiries.find_one({'_id':ObjectId(inquiry_id)})
    except Exception: doc=None
    if not doc:return jsonify(message='Not found'),404
    if doc.get('photo_file_id'): fs.delete(doc['photo_file_id'])
    inquiries.delete_one({'_id':doc['_id']})
    return jsonify(success=True)

if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
