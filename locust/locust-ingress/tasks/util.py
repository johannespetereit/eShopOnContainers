import json, os
from datetime import datetime
def dump(name,response):
    dict = {
        'url': response.url, 
        'status_code': response.status_code, 
        'text': response.text,
        'method': response.request.method
    }
    json_string = json.dumps(dict, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else 'not serializable', indent=4)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H_%M_%S")  
    dir = os.path.dirname(os.path.realpath(__file__))
    # request_file = os.path.join(dir, 'out', timestamp + "_" + str(response.status_code) + "_" + response.request.method + ".json")
    # with open(r'D:\tmp.html','w+') as f: f.write(response.text)
    # with open(request_file, 'w+') as file:
    #     file.write(json_string)


def guard_response(response):
    dump(response.url, response)
    if (response.status_code > 299):
        short_text = response.text if len(response.text) < 200 else response.text[0:200]
        print('error', response.status_code,response.request.method, response.url, short_text)
        raise Exception(response.status_code, short_text, response)