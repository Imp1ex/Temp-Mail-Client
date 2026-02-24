import html
import re
import requests
import urllib.parse
import time

def parse_email_content(content):
    content = html.unescape(content)
    name, from_email, subject, time_str, body = "", "", "", "", ""

    m_from = re.search(r'<b>From:\s*</b>(.*?)<br\s*/?>', content, re.DOTALL | re.IGNORECASE)
    if m_from:
        from_part = m_from.group(1).strip()
        q = re.match(r'"([^"]*)"\s*<([^>]+)>', from_part)
        if q:
            name, from_email = q.group(1).strip(), q.group(2).strip()
        else:
            u = re.match(r'([^<]+)\s*<([^>]+)>', from_part)
            if u:
                name, from_email = u.group(1).strip(), u.group(2).strip()

    m_subj = re.search(r'<b>Subject:\s*</b>([^<]*?)</b>', content, re.DOTALL | re.IGNORECASE)
    if m_subj:
        subject = m_subj.group(1).strip()

    m_time = re.search(r'<b>Time:\s*</b>([^<]+?)<hr', content, re.DOTALL | re.IGNORECASE)
    if m_time:
        time_str = m_time.group(1).strip()

    end_header = re.search(r'<hr\s*/?\s*/>\s*</div>\s*</div>', content, re.DOTALL | re.IGNORECASE)
    if end_header:
        rest = content[end_header.end():].strip()
        body = re.sub(r'<[^>]+>', '\n', rest)
        body = re.sub(r'\n{3,}', '\n\n', body)
        body = html.unescape(body).strip()

    return {
        "name": name,
        "email": from_email,
        "subject": subject,
        "time": time_str,
        "body": body,
    }


def emailnator(proxies=None):
    session = requests.Session()
    session.proxies = proxies
    url = "https://www.emailnator.com/"

    response = session.get(url)
    status_code = response.status_code

    if status_code != 200:
        raise Exception(f"Failed to request emailnator Code: {status_code}")

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
        raise Exception(f"Failed to generate email Code: {response.status_code}")


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
    data = response.json()
    msg_list = data.get('messageData') or []
    data['messageData'] = [m for m in msg_list if m.get('messageID') != 'ADSVPN']
    return data, session


def message_data(email, session, message_id):
    cookies = session.cookies.get_dict()
    xsrf = urllib.parse.unquote(cookies['XSRF-TOKEN'])
    payload = {
        "email": email,
        "messageID": message_id
    }
    
    headers = {
        "X-XSRF-TOKEN": xsrf,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Referer": f"https://www.emailnator.com/mailbox/{email}/{message_id}",
    }

    response = session.post('https://www.emailnator.com/message-list', json=payload, headers=headers)
    status_code = response.status_code

    if status_code != 200:
        raise Exception(f"Failed to request emailnator Code: {status_code}")

    response.encoding = 'utf-8'
    raw_data = response.text
    raw_data = html.unescape(raw_data)
    parsed = parse_email_content(raw_data)
    return {**parsed, "raw_data": raw_data}, session


email, session = emailnator()
print(email)

while True:
    messages, session = message_list(email, session)
    msg_data = messages.get('messageData') or []
    print(msg_data)
    if msg_data:
        message_id = msg_data[0]['messageID']
        print(message_id)
        result, session = message_data(email, session, message_id)
        print("Name:", result["name"])
        print("Email:", result["email"])
        print("Subject:", result["subject"])
        print("Time:", result["time"])
        print("Body:", result["body"])
        print("Raw Data:", result["raw_data"])
        break
    time.sleep(5)
