
import asyncio
import profile
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db,datetime
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash


class ConexionFirebase:

    
    def __init__(self,credencial,ruta) -> None:
        self.credencial = credencial
        self.ruta = ruta
    
    def init_firebase(self):
        firebase_sdk = credentials.Certificate(self.credencial)
        firebase_admin.initialize_app(firebase_sdk,{"databaseURL":self.ruta})

    

    def add_user(self,name,password,img,mail):
        ref = db.reference('User')
        resp = self.login(name,password)
        if (resp["status"] == False):
            print("No existe el usuario")
            nex_box_ref =ref.push({
                    "name": name,
                    "password": generate_password_hash(password),
                    "profile-img": img,
                    "mail": mail
                })
            return {"key":nex_box_ref.key,"profile":img,"name":name}
        else:
            return "ya"

    def get_user(self):
        users = []
        ref = db.reference('User')
        snapshot = ref.order_by_key().get()
        for key, val in snapshot.items():
            users.append({
                "id": key,
                "data": val
            })
        return jsonify(users)
        
    def login(self,name,password):
        ref = db.reference('User')
        snapshot =  ref.order_by_key().get()
        status = False
        keyUser = ""
        profileImg = ""
        nameUser = ""
        if ref.get() != None:
            for key, val in snapshot.items():
                if check_password_hash(val['password'],password):
                    print("entro passwrod")
                    if val['name'] == name:
                        print("entro name")
                        status = True
                        keyUser = key
                        profileImg = val['profile-img']
                        nameUser = val['name']
                        break
                else:
                    status = False
        print(status)
        return {"status": status, "data": keyUser, "profile": profileImg,"name":nameUser}

    def add_img(self,img,key,desp):
        ref =  db.reference('/Photo')
        ref.push({
            "key": key,
            "img": img,
            "descripcion": desp
        })

    def getImageUserKey(self,keyUser):
        photoUser = []
        ref = db.reference("Photo")
        if (ref.get() != None):
            snapshot = ref.order_by_key().get()
            for key, val in snapshot.items():
                if (val['key'] == keyUser):
                    photoUser.append({
                    "id": key,
                    "photo": val['img'],
                    "desp": val['descripcion']
                    })
            return photoUser
        else:
            return []