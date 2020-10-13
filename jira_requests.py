import requests, json
from requests.auth import HTTPBasicAuth
from requests_toolbelt import MultipartEncoder
import pprint

# Class for making requests to JIRA w/ Asset tracker addon, post and get calls and reads username/password from jira_creds.txt
class jira_requests:

    def __init__(self, username=None, password=None, password_file="jira_creds.txt"):
        # self.asset_tracker_url = 'http://45.56.82.161:8080/rest/com-spartez-ephor/1.0/'  # Change me when appropriate!
        self.asset_tracker_url = 'http://45.56.82.161:8080/rest/insight/1.0/'  # Change me when appropriate!
        self.headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        self.username = username
        self.password = password
        if None in (username, password):
            print("WARNING! Reading username & passowrd from file.")
            self.username, self.password = self.read_username_password_from_file(password_file)

    def return_code_handler(self, return_code):
        return 0

    def post_file_upload(self, operator, myfiles, comment):
        request_url = self.asset_tracker_url + operator
        fileName = myfiles.filename
        attachmentType = myfiles.mimetype
        m = MultipartEncoder(fields={'encodedComment': comment.encode('utf-8'), 'file': (fileName.replace('\\',''), myfiles, attachmentType)})
        headers = {'Content-Type': m.content_type}
        returned_value = requests.post(request_url, data=m, headers=headers,  auth=HTTPBasicAuth(self.username, self.password))
        return returned_value

    def post_data(self, operator, json_dict):
        request_url = self.asset_tracker_url + operator
#        print("Request URL: %s" % request_url)
#        pprint.pprint(json_dict)
        returned_value = requests.post(request_url, json=json_dict, headers=self.headers, auth=HTTPBasicAuth(self.username, self.password))
        return returned_value

    def put_data(self, operator, json_dict):
        request_url = self.asset_tracker_url + operator
#        print("Request URL: %s" % request_url)
#        pprint.pprint(json_dict)
        returned_value = requests.put(request_url, json=json_dict, headers=self.headers, auth=HTTPBasicAuth(self.username, self.password))
        return returned_value

    def get_data(self, operator, params_dict=''):
        request_url = self.asset_tracker_url + operator
        returned_value = requests.get(request_url, params=params_dict, auth=HTTPBasicAuth(self.username, self.password))
        if returned_value:
            return returned_value
        else:
            print("Could not retrieve data")
            return 0

    def get_data_file_url(self, file_url):
        returned_value = requests.get(file_url, auth=HTTPBasicAuth(self.username, self.password))
        if returned_value:
            return returned_value
        else:
            return 0

    def verify_auth(self):
        returned_value = requests.get(self.asset_tracker_url + "object", params='', auth=HTTPBasicAuth(self.username, self.password))
        if returned_value:   # This is not a great way to do this..
            return 0
        else:
            return 1

    def read_username_password_from_file(self, password_file):
        #  You can not have :'s in your password, I'm sorry.  Feel free to fix this if you feel strongly about that.
        username = ""
        password = ""
        try:
            with open(password_file) as userpass_file:
                username, password = userpass_file.readline().rstrip().split(':')
        except IOError:
            print("Could not open password file. %s" % password_file)
            return -1
        return username, password

    # this does not work yet
    def upload_file(self, item_id, myfile):
        files = {'file': open(myfile, 'rb')}
        myurl = self.asset_tracker_url
        r = requests.post(myurl, files=files)
        return
