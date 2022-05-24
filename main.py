import gc
import imaplib
import email
import config
import make_order
import datetime

host = 'imap.gmail.com'
username = config.email_user
password = config.email_password

mail = imaplib.IMAP4_SSL(host)
df = open("json.txt", "r")
print(df)

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def login():
    mail.login(username, password)

def get_inbox():
    # mail = imaplib.IMAP4_SSL(host)
    # mail.login(username, password)
    mail.select("inbox")
    _, search_data = mail.search(None, 'UNSEEN')
    my_message = []
    for num in search_data[0].split():
        email_data = {}
        _, data = mail.fetch(num, '(RFC822)')
        # print(data[0])
        _, b = data[0]
        email_message = email.message_from_bytes(b)
        for header in ['subject', 'to', 'from', 'date']:
            # print("{}: {}".format(header, email_message[header]))
            email_data[header] = email_message[header]
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                email_data['body'] = body.decode()
            elif part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True)
                email_data['html_body'] = html_body.decode()
        my_message.append(email_data)
        return my_message


if __name__ == "__main__":
    login()
    while True:
        try:
            my_inbox = get_inbox()
            x = gc.get_threshold()
            # print(datetime.datetime.now())
            # print(x)
            # gc.collect()
            y = gc.get_objects()
            print(len(y))
            # z = gc.get_count()
            # print(z)
            # print(gc.collect())
            # print(gc.get_freeze_count())
            gc.collect()
            if my_inbox == None:
                last_mail = my_inbox[0]
                last_mail = str(last_mail)
                from_trview = find_between(last_mail, "'from': '", " <")
                print(from_trview)
                if from_trview == "TradingView":
                    order_contracts = float(find_between(last_mail, '"order_contracts": ', ", "))
                    order_action = find_between(last_mail, 'order_action": "', '",\\r\\n "')
                    position_size = float(find_between(last_mail, '"position_size": ', ", "))
                    print(order_contracts)
                    print(order_action)
                    print(position_size)

                    if order_action == 'buy' and order_contracts == 1.0 and position_size == 1.0:
                        make_order.longEnter()
                        print("Opening the long position")

                    if order_action == 'buy' and order_contracts == 1.0 and position_size == 0.0:
                        make_order.shortExit()
                        print("Closing the short position(tp/sl)")

                    if order_action == 'buy' and order_contracts >= 2.0 and position_size >= 1.0:
                        make_order.shortExit()
                        make_order.longEnter()
                        print("Closing short and opening the long position")

                    if order_action == 'sell' and order_contracts == 1.0 and position_size == -1.0:
                        make_order.shortEnter()
                        print("Opening the short position")

                    if order_action == 'sell' and order_contracts == 1.0 and position_size == 0.0:
                        make_order.longExit()
                        print("Closing the long position(tp/sl)")

                    if order_action == 'sell' and order_contracts >= 2.0 and position_size <= -1.0:
                        make_order.longExit()
                        make_order.shortEnter()
                        print("Closing long and opening the short position")
        except MemoryError as me:
            print(me)
        except Exception as e:
            print(e)

    # print(my_inbox[0])
