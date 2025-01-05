import time

import requests_unixsocket
import logging


class WolfAPI:
    def __init__(self, socket_path: str, twitch_stream_key: str):
        self.session = requests_unixsocket.Session()
        self.socket_path = "http+unix://" + socket_path.replace('/', "%2F") + "/api/v1"
        logging.debug("Using socket path: " + self.socket_path)
        self.twitch_stream_key = twitch_stream_key
        self.wolf_session_id = None

    def add_app(self, docker_image: str):
        twitch_app_req = {
            "title": "Twitch Plays Wolf",
            "id": "twitch-plays-wolf",
            "support_hdr": False,
            # TODO: HW encoders
            "h264_gst_pipeline": "",
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
        self.wolf_session_id = resp.json()["session_id"]
        time.sleep(1)  # Wait for the session to be created

    def start_session(self):
        twitch_stream_endpoint = "rtmp://ingest.global-contribute.live-video.net/app/" + self.twitch_stream_key
        session_req = {
            "session_id": self.wolf_session_id,
            "video_session": {
                "display_mode": {
                    "width": 1920,
                    "height": 1080,
                    "refreshRate": 30,
                },
                "gst_pipeline": "interpipesrc listen-to={session_id}_video is-live=true stream-sync=restart-ts max-bytes=0 max-buffers=3 block=false ! "
                                "video/x-raw, width={width}, height={height}, format=RGBx ! "
                                "queue ! "
                                "videoconvertscale ! "
                                "x264enc pass=cbr tune=zerolatency key-int-max=60 bitrate=4500 ! "
                                "video/x-h264, profile=high ! "
                                "flvmux ! "
                                "rtmp2sink location=\"" + twitch_stream_endpoint + "\"",
                "session_id": -1,  # Will be replaced by the server
                "port": 9999,
                "wait_for_ping": False,
                "timeout_ms": 999999999,
                "packet_size": -1,
                "frames_with_invalid_ref_threshold": -1,
                "fec_percentage": -1,
                "min_required_fec_packets": -1,
                "bitrate_kbps": -1,
                "slices_per_frame": -1,
                "color_range": "JPEG",
                "color_space": "BT601",
                "client_ip": "0.0.0.0"
            },
            "audio_session": {
                "gst_pipeline": "",
                "session_id": -1,  # Will be replaced by the server
                "encrypt_audio": False,
                "aes_key": "",
                "aes_iv": "",
                "wait_for_ping": False,
                "port": 9999,
                "client_ip": "0.0.0.0",
                "packet_duration": -1,
                "audio_mode": {
                    "channels": 2,
                    "streams": 1,
                    "coupled_streams": 1,
                    "speakers": ["FRONT_LEFT", "FRONT_RIGHT"],
                    "bitrate": 96000,
                    "sample_rate": 48000,
                }
            }
        }
        resp = self.session.post(self.socket_path + "/sessions/start", json=session_req)
        logging.debug(resp.json())
