from server import db, User
import requests, binascii, requests, os, socket, threading, queue, hashlib, hmac

def uptate(currentIP):
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

def scanIP(i, q):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    r = s.connect_ex(("192.168.1.%d" % i, 80))
    if r == 0:
        q.put("192.168.1.%d" % i)
    s.close()
    return r

def scanLan():
    hosts = []
    threads = []
    q = queue.Queue()
    for i in range(1, 255):
        thIP = threading.Thread(target=scanIP, args=(i, q))
        threads.append(thIP)
        thIP.start()
    for i in threads:
        i.join()
    return list(q.queue)


ips = scanLan()
print(ips)
for i in ips:
    uptate(i)
