import requests
import urllib.parse

def emailnator():
    session = requests.Session()
    url = "https://www.emailnator.com/"

    response = session.get(url)
    cookies = response.cookies.get_dict()
    xsrf = urllib.parse.unquote(cookies['XSRF-TOKEN'])

    url = "https://www.emailnator.com/generate-email"

    payload = { "email": ["domain", "plusGmail", "dotGmail", "googleMail"] }
    headers = {
        "X-XSRF-TOKEN": xsrf,
    }

    response = session.post(url, json=payload, headers=headers)

    try:
        data = response.json()
        email = data['email'][0]
        return email, session
    except:
        raise Exception("Failed to generate email")

def message_list(email, session):
    cookies = session.cookies.get_dict()
    xsrf = urllib.parse.unquote(cookies['XSRF-TOKEN'])
    payload = {
        "email": email
    }
    headers = {
        "X-XSRF-TOKEN": xsrf,
    }

    response = session.post('https://www.emailnator.com/message-list', json=payload, headers=headers)
    return response.json()

email, session = emailnator()
message_list = message_list(email, session)
print(message_list)
