from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os, sys, requests, binascii, hashlib, hmac

app = Flask(__name__)

# setup db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    name = db.Column(db.String, primary_key=True)
    ip = db.Column(db.String)
    key = db.Column(db.String)

# Route requests
@app.route("/")
def hello():
    return "Hello World!\n"

@app.route("/send_key", methods=["POST"])
def sendKey():
    if({"name", "key"}.issubset(request.form)):
        newUser = User(name=request.form["name"], ip=request.remote_addr, key=request.form["key"])
        # db.session.query(User).filter(User.ip==newUser.ip).delete()
        db.session.merge(newUser)
        db.session.commit();
        return "Key Registration Success<br>\nName: %s<br>\nIP: %s<br>\nKey: %s<br>\n" % (request.form["name"],
                                                                          request.remote_addr,
                                                                          request.form["key"])
    return "Key Registration Failed\n"

@app.route("/get_keys")
def getKeys():
    return jsonify([{"name": u.name, "ip": u.ip} for u in db.session.query(User).all()])

@app.route("/get_temp")
def getTemp():
    if("name" in request.args):
        try:
            user = db.session.query(User).filter(User.name==request.args["name"]).first()
            if(user == None):
                return "User not found"
            generated_challenge = binascii.hexlify(os.urandom(32))
            expected_response = hashlib.sha256(generated_challenge + user.key.encode('utf-8')).hexdigest()
            r = requests.get("http://%s/auth_challenge?name=%s&challenge=%s" % (user.ip, user.name, generated_challenge.decode('utf-8')), timeout=10.0)
            rjson = r.json()
            if(not hmac.compare_digest(expected_response, rjson["response"])):
                return "Cliente Authentication Failed"
            solved_challenge = hashlib.sha256((rjson["challenge"] + "components" + user.key).encode('utf-8')).hexdigest()
            r = requests.get("http://%s/components?name=%s&response=%s" % (user.ip, user.name, solved_challenge), timeout=10.0)
            rjson = r.json()
            return str(rjson["components"]["sensor"]["state"]["sensors"]["temperature"])
        except:
            return "Connection Failed"
    return "Client Error"

@app.route("/update_ip")
def updateIps():
    if "ip" in request.args:
        currentIP = request.args["ip"]
    else:
        currentIP = request.remote_addr

    try:
        generated_challenge = binascii.hexlify(os.urandom(32))
        r = requests.get("http://%s/auth_challenge?challenge=%s" % (currentIP, generated_challenge.decode('utf-8')), timeout=2.0)
        if(r.status_code != 200):
            return r.text
        rjson = r.json()
        user = db.session.query(User).filter(User.name==rjson["name"]).first()
        if(user == None):
            return "User doesn't exist"
        expected_response = hashlib.sha256(generated_challenge + user.key.encode('utf-8')).hexdigest()
        if(not hmac.compare_digest(expected_response, rjson["response"])):
            return "Authentication Failed"
        user = db.session.query(User).filter(User.name==rjson["name"]).first()
        user.ip = currentIP
        db.session.commit()
        print("%s: %s" % (currentIP, user.name))
    except Exception as e:
        print(currentIP)
        print(e)
        return "Connection Failed"
    return "Update success"

if __name__ == "__main__":
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop
    # sys.tracebacklimit = 0

    http_server = HTTPServer(WSGIContainer(app), ssl_options={
        "certfile": os.path.realpath("cert.pem"),
        "keyfile": os.path.realpath("key.pem"),
    })
    http_server.listen(8000)
    IOLoop.instance().start()
