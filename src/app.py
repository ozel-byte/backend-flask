
import base64
import threading
import os
from click import File
from flask import Flask,jsonify,request
import asyncio

from conexiondb import ConexionFirebase

import cloudinary
import cloudinary.uploader


app = Flask(__name__)

conexion_firebase = ConexionFirebase(
        "src/tokkioedit-firebase-adminsdk-x4apd-2678ed0d77.json",
        "https://tokkioedit-default-rtdb.firebaseio.com/"
    )
conexion_firebase.init_firebase()

@app.route("/")
def raiz():
    return jsonify({
        "status":"raiz"
    })

@app.route("/add-user",methods=["POST"])
def user_add():
    json_response = request.get_json(force=True)
    print(json_response);
    nombre = json_response['name']
    password = json_response['password']
    img_base64 = json_response['img']
    mail = json_response['mail']

    img = base64.b64decode(img_base64)
    key_user = cargarImgProfile(img,nombre,password,mail)
    
    return jsonify({
        "status": "ok",
        "data": key_user
    })

def cargarImgProfile(img_url,nombre,password,mail):
    cloudinary.config(
        cloud_name="dv5fwf13g",
        api_key="296484175841721",
        api_secret="DJIqJ_Wi_Qg4jgSKlNVvZGPnQqU"
    )
    img_url_s = cloudinary.uploader.upload(img_url)
    print(img_url_s['secure_url'])
    key = conexion_firebase.add_user(nombre,password,img_url_s['secure_url'],mail)
    return key

@app.route("/get-user")
def get_user():
    return jsonify({
        "status": "Ok",
        "data": conexion_firebase.get_user()
    })


@app.route("/login")
def login():
    name = request.args['name']
    password = request.args['password']
    resp = conexion_firebase.login(name,password)
    print(resp['status'])
    if resp['status']:
        return jsonify({
            "status": "ok",
            "data": resp['data']
        })
    else:
        return jsonify({
            "status": "error"
        })


@app.route("/set-img-profile-user",methods=["POST"])
def setImageProfileUser():
    response_json = request.get_json(force=True)
    
    img_string = response_json['img']
    key = response_json['key']

    img = base64.b64decode(img_string)
    hilo_img = threading.Thread(target=main,kwargs={
        "img_url": img,
        "key": key
    })
    # base = base64.decodestring(img['img'])
    hilo_img.start()
    return jsonify({
        "status": "ok",
    })


def main(img_url,key):
    asyncio.run(cargarImgCloudinary(img_url,key))


async def cargarImgCloudinary(img_url,key):
    cloudinary.config(
        cloud_name="dv5fwf13g",
        api_key="296484175841721",
        api_secret="DJIqJ_Wi_Qg4jgSKlNVvZGPnQqU"
    )
    img_url_s = cloudinary.uploader.upload(img_url)
    print(img_url_s['secure_url'])
    await conexion_firebase.add_img(img_url_s['secure_url'],key)
#https://pub.dev/packages/shared_preferences/install
#https://medium.flutterdevs.com/using-sharedpreferences-in-flutter-251755f07127
#https://blog.logrocket.com/using-sharedpreferences-in-flutter-to-store-data-locally/
#https://blog.logrocket.com/building-an-image-picker-in-flutter/

@app.route("/get-image-user")
def getImageUserKey():
    key_user = request.args['key']
    return jsonify({
        "status": "ok",
        "arrayPhoto": conexion_firebase.getImageUserKey(key_user)
    })

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")  