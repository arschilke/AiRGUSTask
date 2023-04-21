import json
import requests


def load_creds_from_config(filename):
    f = open(filename, 'r')
    return json.loads(f.read())


class EagleEyeApiClient:
    HTTP_STATUS_CODE = {
        200: 'OK',
        202: 'ACCEPTED',
        400: 'Bad Request, please check what you are sending',
        401: 'User needs to Login first',
        403: 'User does not have access to that',
        500: 'API had a problem (500)',
        502: 'API had a problem (502)',
        503: 'API had a problem (503)'
    }

    LOGIN_URL = "https://login.eagleeyenetworks.com/g/aaa/authenticate"
    AUTH_URL = "https://login.eagleeyenetworks.com/g/aaa/authorize"

    def __init__(self, filename, debug_mode):
        self.debug_mode = debug_mode
        self.session = requests.session()
        data = load_creds_from_config(filename)
        self.username = data["username"]
        self.password = data["password"]
        self.api_key = data["api"]
        self.headers = {'content-type': 'application/json', 'authorization': self.api_key}

    def login(self):
        payload = json.dumps({'username': self.username, 'password': self.password})
        login_response = self.session.request("POST",
                                              self.LOGIN_URL,
                                              data=payload,
                                              headers=self.headers)

        print("Login Step 1: %s" % self.HTTP_STATUS_CODE[login_response.status_code])

        token = login_response.json()['token']
        auth_response = self.session.request("POST", self.AUTH_URL, data=json.dumps({'token': token}),
                                             headers=self.headers)

        print("Login Step 2: %s" % self.HTTP_STATUS_CODE[auth_response.status_code])

        return auth_response.json()

    def get_devices(self, current_user):
        if self.debug_mode:
            url = f"http://localhost:3000/g/device/list"
        else:
            url = f"https://{current_user['active_brand_subdomain']}.eagleeyenetworks.com/g/device/list"

        response = self.session.request("GET", url, data="", headers=self.headers)

        print("Get Devices : %s" % self.HTTP_STATUS_CODE[response.status_code])

        return response.json()

    def get_stream_urls(self, current_user, camera_id):
        if self.debug_mode:
            url = f"http://localhost:3000/stream"
        else:
            url = f"https://{current_user['active_brand_subdomain']}.eagleeyenetworks.com/api/v2/media/cameras/{camera_id}/streams?A={self.session.cookies['auth_key']}"

        response = self.session.request("GET", url, data="", headers=self.headers)

        print("Get Stream Urls: %s" % self.HTTP_STATUS_CODE[response.status_code])
        return response.json()
