"""Test de bout en bout par l Ingress, sans DNS : requetes vers l IP de l ingress avec le bon Host."""
import json, re, sys, urllib.request
IP, HOST = "157.159.11.201", "dbz.grp1.net4255.luxbulb.org"
def req(path, data=None, token=None):
    r = urllib.request.Request(f"http://{IP}{path}", headers={"Host": HOST, "Content-Type": "application/json"},
                               data=json.dumps(data).encode() if data else None)
    if token: r.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(r, timeout=10) as resp: return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e: return e.code, e.read().decode()
s, b = req("/");            print("front /          ", s, re.search(r"<title>(.*?)</title>", b).group(1))
s, b = req("/connexion");   print("SPA /connexion   ", s)
s, b = req("/api/health/"); print("api health       ", s, b)
s, b = req("/api/auth/login/", {"username": "admin", "password": open(sys.argv[1]).read().strip()})
tok = json.loads(b).get("token");   print("login admin      ", s, json.loads(b).get("user"))
s, b = req("/api/attractions/", token=tok); print("attractions      ", s, [a.get("name") for a in json.loads(b)][:4])
