import json
import requests_unixsocket
import logging


class WolfAPI:
    def __init__(self, socket_path: str, twitch_stream_key: str):
        self.session = requests_unixsocket.Session()
        self.socket_path = "http+unix://" + socket_path.replace('/', "%2F") + "/api/v1"
        logging.debug("Using socket path: " + self.socket_path)
        self.twitch_stream_key = twitch_stream_key

    def add_app(self, docker_image: str):
        twitch_stream_endpoint = "rtmp://ingest.global-contribute.live-video.net/app/" + self.twitch_stream_key
        twitch_app_req = {
            "title": "Twitch Plays Wolf",
            "id": "twitch-plays-wolf",
            "support_hdr": False,
            # TODO: HW encoders
            "h264_gst_pipeline": "interpipesrc listen-to={session_id}_video is-live=true stream-sync=restart-ts max-bytes=0 max-buffers=3 block=false !"
                                 "videoconvertscale ! "
                                 "x264enc tune=zerolatency ! "
                                 "flvmux ! "
                                 "rtmp2sink location=" + twitch_stream_endpoint,
            "hevc_gst_pipeline": "",
            "av1_gst_pipeline": "",
            "render_node": "/dev/dri/renderD128",  # TODO:
            "opus_gst_pipeline": "",  # TODO: Audio
            "start_virtual_compositor": True,
            "start_audio_server": True,
            "runner": {
                "type": "docker",
                "name": "twitch-plays-wolf",
                "image": docker_image,
                "mounts": [],
                "env": [],
                "devices": [],
                "ports": []
            }
        }
        resp = self.session.post(self.socket_path + "/apps/add", json=twitch_app_req)
        logging.debug(resp.json())
        return resp.json()

    def create_session(self):
        session_req = {
            "app_id": "twitch-plays-wolf",
            "client_id": "4135727842959053255",  # TODO
            "client_ip": "127.0.0.1",  # TODO
            "video_width": 1920,  # TODO: config
            "video_height": 1080,
            "video_refresh_rate": 30,
            "audio_channel_count": 2,
            "client_settings": {
                "run_uid": 1000,
                "run_gid": 1000,
                "controllers_override": [],
                "mouse_acceleration": 1.0,
                "v_scroll_acceleration": 1.0,
                "h_scroll_acceleration": 1.0,
            }
        }
        resp = self.session.post(self.socket_path + "/sessions/add", json=session_req)
        logging.debug(resp.json())
        # TODO: get session ID
        return resp.json()

    def start_session(self, session_id: str):
        pass  # TODO: Implement API call in Wolf for events::VideoSession
