import random
from util import guard_response
import re
from urllib.parse import parse_qs, urlparse
def get_oauth_state():
    state = ""
    for i in range(0,14): state += str(random.randrange(0,10))
    state += "."
    for i in range(0,16): state += str(random.randrange(0,10))
    return state

def get_openid_nonce():
    nonce = ""
    for i in range(0,28): nonce += str(random.randrange(0,10))
    return nonce


def oauth_login(client, username, password):
    state = get_oauth_state()
    nonce = get_openid_nonce()
    authorize_url = "/identity/connect/authorize?response_type=id_token%20token&client_id=js&redirect_uri=" + client.base_url + "/&scope=openid%20profile%20orders%20basket%20marketing%20locations%20webshoppingagg%20orders.signalrhub&nonce=N0." + nonce + "&state=" + state
    resp = client.get(authorize_url, name='/identity/connect/authorize')
    guard_response(resp)
    regex = '__RequestVerificationToken.*?value\=\\"(.*?)\\"'
    token = re.search(regex, resp.text).group(1)
    print(token)
    
    # get returnurl parameter
    parsed = urlparse(resp.url)
    return_url = parse_qs(parsed.query)['ReturnUrl'][0]

    resp = client.post(resp.url, {
        "ReturnUrl": return_url,
        "Email": username,
        "Password": password,
        "__RequestVerificationToken": token,
        "RememberMe": "false",
    }, name='/identity/Account/Login')
    guard_response(resp)

    parsed = urlparse(resp.url)
    access_token = parse_qs(parsed.fragment)["access_token"][0]
    return access_token