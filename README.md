```py
from temp_mail_client import mailbox
import time

def main():
    mb = mailbox()
    
    email = mb.email
    print(email)
    while True:
        messages = mb.get_messages()
        if messages:
            print(f"Message data: {messages}")
            break

        else:
            print("No messages found")
        time.sleep(3)

if __name__ == "__main__":
    main()
```
If you get a 429 error, consider using a proxy.
I do not provide any additional fields or metadata for message data.
