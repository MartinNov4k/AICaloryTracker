import requests
def get_Meal(url, user, day):
    url = "https://marty1888.pythonanywhere.com/meals/"
    response = requests.get(url, params={"user": user, "day":day})
    print(response.status_code)   # 200 když OK
    return response.json()      # vrácený JSON


def post_meal(API_URL,payload):
    response = requests.post(API_URL, json=payload) ## payload je dict
    if response.status_code == 201:
        message = "uloženo"
    else:
        message = response.status_code

    return message


def get_Targets(url,user):
    url = "https://marty1888.pythonanywhere.com/targets/"
    response = requests.get(url, params={"user": user})
    print(response.status_code)   
    return response.json()     


def post_target(API_URL,payload, user):

    r = requests.get(API_URL+ f"?user={user}")
    existing = r.json()
    if existing:
        target_id = str(existing[0]["id"])    
        response = requests.put(API_URL+target_id+ "/", json=payload) ## payload je dict
    else:
        response = requests.post(API_URL, json=payload) ## payload je dict
        
    if response.status_code == 201 or response.status_code == 200:
        message = "uloženo"
    else:
        message = response.status_code

    return message


def get_history(API_URL, user, day):
    response = requests.get(API_URL, params={"user": user,"day" : day })
    print(response.status_code)   # 200 když OK
    if response.status_code:
        return response.json()  