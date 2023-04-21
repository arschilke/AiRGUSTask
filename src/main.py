import argparse
import cv2
import eagleEyeClient

def get_image_from_camera(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)

    while cap.isOpened():
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def main(debug_mode):
    eagle_eye_client = eagleEyeClient.EagleEyeApiClient("apiKey.json", debug_mode)
    current_user = eagle_eye_client.login()

    device_list = eagle_eye_client.get_devices(current_user)

    camera_list = [i for i in device_list if i[3] == 'camera']

    if len(camera_list) <= 0:
        print("No cameras found on this account.")
        return;

    camera_id = camera_list[0][1]
    stream_urls = eagle_eye_client.get_stream_urls(current_user, camera_id)
    rtsp_url = stream_urls["data"]["rtsp"]
    get_image_from_camera(rtsp_url)

parser = argparse.ArgumentParser()
parser.add_argument('--debug', default=False, action='store_true')
args = parser.parse_args()
main(args.debug)
