import cv2
import requests
import json
import pprint

pp = pprint.PrettyPrinter()
debug_mode = True

# Translating the HTTP response codes to make the status messages easier to read
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

session = requests.session()

# load api key
f = open("apiKey.json", 'r')
data = json.loads(f.read())

username = data["username"]
password = data["password"]
api_key = data["api"]

###
# Step 1: login (part 1)
# make sure put in valid credentials
###

url = "https://login.eagleeyenetworks.com/g/aaa/authenticate"

payload = json.dumps({'username': username, 'password': password})
headers = {'content-type': 'application/json', 'authorization': api_key}

response = session.request("POST", url, data=payload, headers=headers)

print("Step 1: %s" % HTTP_STATUS_CODE[response.status_code])
token = response.json()['token']

###
# Step 2: login (part 2)
###

url = "https://login.eagleeyenetworks.com/g/aaa/authorize"

querystring = {"token": token}

payload = json.dumps({'token': token})
headers = {'content-type': 'application/json', 'authorization': api_key}

response = session.request("POST", url, data=payload, headers=headers)

print("Step 2: %s" % HTTP_STATUS_CODE[response.status_code])

current_user = response.json()

###
# Step 3: get list of devices
###

url = f"https://{current_user['active_brand_subdomain']}.eagleeyenetworks.com/g/device/list"
if debug_mode:
    url = f"http://localhost:3000/g/device/list"

payload = ""
headers = {'authorization': api_key}
response = session.request("GET", url, data=payload, headers=headers)

print("Step 3: %s" % HTTP_STATUS_CODE[response.status_code])

device_list = response.json()

# filter everything but the cameras
camera_list = [i for i in device_list if i[3] == 'camera']

# Step 4: Select the camera

camera_id = camera_list[0][1]


###
# Step 5: get the stream url
###

url = f"https://{current_user['active_brand_subdomain']}.eagleeyenetworks.com/api/v2/media/cameras/{camera_id}/streams?A={session.cookies['auth_key']} "
if debug_mode:
    url = f"http://localhost:3000/stream"

payload = ""
headers = {'authorization': api_key}
response = session.request("GET", url, data=payload, headers=headers)

print("Step 5: %s" % HTTP_STATUS_CODE[response.status_code])

response_object = response.json()

###
# Step 6: Get video url and use StackOverflow code
###

rstp_url = response_object["data"]["rtsp"]
cap = cv2.VideoCapture(rstp_url)

while cap.isOpened():
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
