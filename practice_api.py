import requests
import json

def api_request(input):
    url = "https://api.darksky.net/forecast/37f3f52d76a1699428512298c4ec2055/" + input
    req = requests.get(url)
    if not req:
        page_not_found()
    json_data = json.loads(req.text)
    response = json_data#['results']
    temp = response["currently"]["temperature"]
    return temp

def call_api(location):
    temp = api_request(location)
    if temp > 60:
        return "Get supplies from farmers market"
    else:
        return "Get supplies from the supermarket"

"""if __name__ == "__main__":
    print("Detroit:")
    call_api("44.761527,-69.322662")
    print("Antarctica:")
    call_api("-82.4,-33.7")
    print("Egypt:")
    call_api("23.0,26.7")"""