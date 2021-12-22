import base64
import email
import os.path
import pickle
from re import S
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
user_id = 'me' # change 'me' with email address for commercial use.

def list_to_dict(keys,values):
    # using dictionary comprehension
    # to convert lists to dictionary
    res = {keys[i]: values[i] for i in range(len(keys))}
    return res # print(list_to_dict(['one','two'],['1','2']))
def get_service():
    """
    Authenticate the google api client and return the service object 
    to make further calls
    PARAMS
        None
    RETURNS
        service api object from gmail for making calls
    """
    creds = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)


    service = build('gmail', 'v1', credentials=creds)

    return service

service = get_service()

def get_message_id(service, user_id):

    message_ids = service.users().messages().list(userId=user_id,q='to:'+user_id).execute()
    return message_ids['messages']

def get_all_emails(service,user_id):
    msg_ids = get_message_id(service,user_id)
    emails = []
    for id in msg_ids: # iterate through message id and get individual email
        emails.append(get_email(service,user_id,id['id']))
    return emails
def get_all_senders_data(service, user_id):
    msg_ids = get_message_id(service, user_id)
    senders_data = []
    for id in msg_ids:
        senders_data.append(get_sender_data(get_service(),user_id,id['id']))
    return senders_data
def get_sender_data(service, user_id, msg_id):
    # get senders data for automation
    try:
        # grab the message instance
        # but format as default
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        # seperate individual data from json data
        from_data = message['payload']['headers'][16]['value']
        to_data = message['payload']['headers'][20]['value']
        sent_data = message['payload']['headers'][17]['value']
        subject_data = message['payload']['headers'][19]['value']
        sender_name = from_data.split('<')[0]
        sender_email = from_data.split('<')[1].split('>')[0]
    
        return list_to_dict(['sender_name','sender_email','to_data','sent_data','subject_data'],[sender_name,sender_email,to_data,sent_data,subject_data])
    except Exception:
        print("An error occured",message) 

def get_email(service, user_id, msg_id):
    try:
        # grab the message instance
        message = service.users().messages().get(userId=user_id, id=msg_id,format='raw').execute()
        # decode the raw string, ASCII works pretty well here
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        # grab the string from the byte object
        mime_data = email.message_from_bytes(msg_str)
        emails = []
        email_data = {}
        for header in ['to', 'from', 'date','subject']:
            # print("{}: {}".format(header, mime_data[header]))
            email_data[header] = mime_data[header]
        for part in mime_data.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                email_data['body'] = body.decode()
                body = email_data['body']
        emails.append(email_data)
        return emails

    except Exception:
        print("An error occured")

# # Examples for debugging
# print("\nService info : ",get_service())
# print("\nMessage ID :",get_message_id(service, user_id))
# print("\nGet All Emails :",get_all_emails(service, user_id))
# # msg_id of recent email for POC
# msg_id = get_message_id(service,user_id)[0]['id']
# print("\nAll Senders Data :",get_all_senders_data(service,user_id))
# # Gets Senders info of recent email for POC
# print("\nSenders Data :",get_sender_data(service,user_id,msg_id))
# # Gets recent email for POC
# print("\nGet specific email :",get_email(service, user_id,msg_id))


