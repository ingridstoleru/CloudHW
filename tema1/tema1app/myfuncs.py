from __future__ import print_function

import httplib2
import os
import base64
import quopri
import json
import dateutil.parser as parser
import sys
import dropbox
import urllib, urllib2, hashlib
import time
import logging

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from os.path import normpath, basename

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'D:\\work\\Anul3\\SEM2\\CLOUD\\TEMA1\\SERVER\\tema1\\tema1app\\client_secret.json'
APPLICATION_NAME = 'MyHomework'
STORE_DIR_ATTACH = 'D:\\work\\Anul3\\SEM2\\CLOUD\\TEMA1\\SERVER\\tema1\\tema1app\\__attachements'
DROPBOX_TOKEN = '7zqg9DxBRuAAAAAAAAAAcUYqgF1hXKUiJfmvG9EzpzV2lf_PmnvUhjKa1_zQ9aXj'
API_URL_VT = 'https://www.virustotal.com/vtapi/v2/'
API_KEY_VT = 'fa339e242582366186ae4cb433cb69d2a413d1821e0a1ad621cc94be70f5edf1'


flags = None
logging.basicConfig(filename='req&&resp.log', level=logging.DEBUG)

try:
    import requests
except:
    print('[Warning] request module is missing!')

def get_credentials():
    logging.info('Started to get credentials!\n')
    """Gets valid user credentials from storage."""
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'hack-my-mails.json')

    store = Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        logging.warning('Invalid credentials!\n')
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        logging.info('Storing credentials to: {0}\n'.format(credential_path))
    return credentials

def backup(path, dbx):
    with open(path, 'rb') as f:
        backUpPath = '/' + basename(normpath(path))
        logging.info("Uploading " + path + " to Dropbox as " + backUpPath + "...")
        try:
            dbx.files_upload(f.read(), backUpPath, mode=WriteMode('overwrite'))
        except ApiError as err:
            # This checks for the specific error where a user doesn't have enough Dropbox space quota to upload this file
            if (err.error.is_path() and
                    err.error.get_path().error.is_insufficient_space()):
                logging.warning("ERROR: Cannot back up; insufficient space.")
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                logging.warning(err.user_message_text)
                sys.exit()
            else:
                logging.warning(err)
                sys.exit()

def uploadFileToDropbox(path):
    # Check for an access token
    if (len(DROPBOX_TOKEN) == 0):
        logging.warning("ERROR: It looks like you didn't add your access token!")
        sys.exit("ERROR: It looks like you didn't add your access token!")
        # Create an instance of a Dropbox class, which can make requests to the API.
    print("Creating a Dropbox object...")
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    # Check that the access token is valid
    try:
        dbx.users_get_current_account()
    except AuthError as err:
        logging.warning("ERROR: Invalid access token; try re-generating an access token from the app console on the web.")
        sys.exit("ERROR: Invalid access token; try re-generating an access token from the app console on the web.")

    logging.info("Creating backup...")
    print("Creating backup...")
    # Create the backup
    backup(path, dbx)

    logging.info("Done with: {0}!".format(basename(normpath(path))))
    #print("Done with: {0}!".format(basename(normpath(path))))

# Sending and scanning files
def scanfile(file):
    url = API_URL_VT + "file/scan"
    files = {'file': open(file, 'rb')}
    headers = {"apikey": API_KEY_VT}
    try:
        response = requests.post(url, files=files, data=headers)
        xjson = response.json()
        response_code = xjson['response_code']
        verbose_msg = xjson['verbose_msg']
        if response_code == 1:
            logging.info("Managed to scan file!")
            return xjson
        else:
            logging.warning(verbose_msg)
            #print(verbose_msg)
    except Exception as e:
        loggin(e)
        #print(e)
        sys.exit()

def print_report(jsonx):
    avlist = []
    jsonx = json.loads(jsonx)
    scan_date = jsonx.get('scan_date')
    total = jsonx.get('total')
    positive = jsonx.get('positives')
    print ('Scan date: ' + scan_date)
    logging.info('Scan date: ' + scan_date)
    print ('Detection ratio: ' + str(positive) + "/" + str(total))
    logging.info('Detection ratio: ' + str(positive) + "/" + str(total))
    scans = jsonx.get('scans')
    for av in scans.iterkeys():
        res = scans.get(av)
        if res.get('detected') == True:
            avlist.append('+ ' + av + ':  ' + res.get('result'))
    if positive > 0:
        for res in avlist:
            print (res)

# Retrieve file scan reports
def getfile(file):
    if os.path.isfile(file):
        f = open(file, 'rb')
        file = hashlib.sha256(f.read()).hexdigest()
        f.close()
    url = API_URL_VT + "file/report"
    parameters = {"resource": file, "apikey": API_KEY_VT}
    data = urllib.urlencode(parameters)
    req = urllib2.Request(url, data)
    try:
        response = urllib2.urlopen(req)
        xjson = response.read()
        response_code = json.loads(xjson).get('response_code')
        verbose_msg = json.loads(xjson).get('verbose_msg')
        if response_code == 1:
            logging.info(verbose_msg)
            print(verbose_msg)
            #print_report(xjson)
            return xjson
        else:
            logging.warning(verbose_msg)
            print(verbose_msg)
            return None
    except Exception as e:
        print(e)
        return None

def getAttachments(start, stop):
    """Creates a Gmail API service object and outputs a list of attachments corresponding to the unread messages of the user's Gmail account."""
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    unread_msgs = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
    message_list = unread_msgs['messages']
    count = 0
    message_data = []

    for message in message_list[start:stop]:
        temp_dict = {}
        m_id = message['id']

        attachment = service.users().messages().get(userId='me', id=m_id).execute()
        temp_dict['attachment'] = []

        if "parts" in attachment["payload"]:
            for part in attachment["payload"]["parts"]:
                ok = False
                path = ""
                if "attachmentId" in part['body']:
                    att_id = part['body']['attachmentId']
                    att = service.users().messages().attachments().get(userId='me', messageId=m_id,
                                                                       id=att_id).execute()
                    file_data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))
                    ok = True

                if ok:
                    if count > 5:
                        break
                    path = os.path.join(STORE_DIR_ATTACH, '{0}{1}.txt'.format(part["filename"], count))

                    f = open(path, 'wb')
                    f.write(file_data)
                    f.close()

                    temp_dict['attachment'].append(path)
                    count += 1

                    message = service.users().messages().get(userId='me', id=m_id).execute()  # fetch the message using API
                    payld = message['payload']
                    headr = payld['headers']
                    for hdr in headr:
                        if hdr['name'] == 'Subject':  # getting the subject
                            msg_subject = hdr['value']
                            temp_dict['Subject'] = msg_subject
                        else:
                            pass
                    for hdr in headr:  # getting the sender
                        if hdr['name'] == 'From':
                            msg_from = hdr['value']
                            temp_dict['Sender'] = msg_from
                        else:
                            pass
                    for hdr in headr:  # getting the date
                        if hdr['name'] == 'Date':
                            msg_date = hdr['value']
                            date_parse = (parser.parse(msg_date))
                            m_date = (date_parse.date())
                            temp_dict['Date'] = str(m_date)
                        else:
                            pass

                    """ Scan file and process results """
                    scanfile(path)
                    scan_results = getfile(path)
                    while scan_results is None:
                        time.sleep(10)
                        scan_results = getfile(path)
                    jsonx = json.loads(scan_results)
                    positive = jsonx.get('positives')
                    if positive == 0:
                        print("Attachment from path:{0}, with mail from:{1} and subject:{2}, sent at date:{3} is clean!".format(path, msg_from, msg_subject, msg_date))
                        uploadFileToDropbox(path)
                    else:
                        print("Attachment from path:{0}, with mail from:{1} and subject:{2}, sent at date:{3} is malicious!".format(path, msg_from, msg_subject, msg_date))

                    temp_dict["scan_results"] = scan_results
                    temp_dict["positives"] = positive
                    message_data.append(temp_dict)
    return message_data
