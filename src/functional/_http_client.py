import requests
def sendHttpRequest(url):
    response = requests.get(url) 
    status = response.status_code 
    return response