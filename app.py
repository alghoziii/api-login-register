from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
import hashlib
import os
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app
from firebase_config import get_firebase_config

app = Flask(__name__)
load_dotenv()

def generate_token(User_Id):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    
    payload = {
        'exp': expiration_time,
        'iat': datetime.datetime.utcnow(),
        'sub': str(User_Id)
    }
    
    secret_key = os.getenv('SECRET_KEY')
    

    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


cred = credentials.Certificate(get_firebase_config())
initialize_app(cred)

db = firestore.client()

last_User_Id = 0

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers.get('Authorization')

        if not token:
            print("Token is missing!")
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            User_Id = data['sub']
            print(f"Decoded User_Id: {User_Id}")

            current_user_ref = db.collection('users').where('User_Id', '==', int(User_Id)).get()

            if not current_user_ref:
                print(f"User with User_Id {User_Id} not found in Firestore.")
                return jsonify({'message': 'User not found!'}), 401


            current_user = current_user_ref[0].to_dict()
            print(f"Current user data: {current_user}")

        except jwt.ExpiredSignatureError:
            print("Token has expired!")
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            print("Invalid token!")
            return jsonify({'message': 'Invalid token!'}), 401
        else:
            print(f"User {current_user['Email']} successfully authenticated.")

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/', methods=['GET','POST'])
def default_route():
    return jsonify({'message': 'Success fetching the API'}), 200

# API Register
@app.route('/auth/register', methods=['POST'])
def register():
    global last_User_Id

    data = request.get_json()
    Email = data.get('Email')  
    Password = data.get('Password')  
    Address = data.get('Address')  
    Age = data.get('Age')  
    Name = data.get('Name')  

    user_ref = db.collection('users').where('Email', '==', Email).get()
    if len(user_ref) > 0:
        return jsonify({'message': 'Email sudah terdaftar!'}), 400

    if not Email:
        return jsonify({'message': 'Email cannot be empty!'}), 400


    last_User_Id_ref = db.collection('users').order_by('User_Id', direction=firestore.Query.DESCENDING).limit(1).stream()
    last_User_Id = 0
    for doc in last_User_Id_ref:
        last_User_Id = doc.get('User_Id')


    new_User_Id = last_User_Id + 1


    hashed_password = hashlib.sha256(Password.encode()).hexdigest()

    user_data = {
        'Email': Email,
        'Password': hashed_password,
        'Address': Address,
        'Age': Age,
        'Name': Name,
        'User_Id': new_User_Id,
    }

    db.collection('users').add(user_data)
    print(f"User added to Firestore with User_Id: {new_User_Id}")

    return jsonify({'message': 'User registered successfully!'}), 201

# API Login
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    Email = data.get('Email')
    Password = data.get('Password')

    print(f"Received login request with Email: {Email}, Password: {Password}")

    if not Email or not Password:
        return jsonify({'error': 'Invalid Email or Password'}), 400

    user_ref = db.collection('users').where('Email', '==', Email).get()

    print(f"Email: {Email}, User reference: {user_ref}")

    if len(user_ref) == 0:
        print(f"User with Email {Email} not found in Firestore.")
        return jsonify({'error': 'User not found'}), 404

    user_data = user_ref[0].to_dict()

    hashed_password = hashlib.sha256(Password.encode()).hexdigest()
    print(f"Hashed Password from input: {hashed_password}, Hashed Password from database: {user_data.get('Password', '')}")
    
    if hashed_password != user_data.get('Password'):
        return jsonify({'error': 'Invalid Password'}), 401

    User_Id = str(user_data.get('User_Id'))

    token = generate_token(User_Id)

    return jsonify({
        'success': True,
        'message': 'Sukses login',
        'data': {'token': token}
    }), 200

@app.route('/user/details', methods=['GET'])
@token_required
def get_user_details(current_user):
    print("Inside get_user_details")
    print(f"Current user: {current_user}")
    
 
    return jsonify({
        'User_Id': current_user.get('User_Id', ''),
        'Email': current_user.get('Email', ''),
        'Name': current_user.get('Name', ''),
        'Age': current_user.get('Age', 0),
        'Address': current_user.get('Address', '')
    }), 200

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
