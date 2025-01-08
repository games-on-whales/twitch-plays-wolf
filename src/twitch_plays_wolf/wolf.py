import time
from time import sleep

from aioemit import Emitter, Event
import requests_unixsocket
import logging
import struct

from twitch_plays_wolf.data import MessageEvent


class WolfAPI:
    def __init__(self, event_bus: Emitter, socket_path: str):
        self.session = requests_unixsocket.Session()
        self.socket_path = "http+unix://" + socket_path.replace('/', "%2F") + "/api/v1"
        logging.debug("Using socket path: " + self.socket_path)
        self.event_bus = event_bus

    def add_app(self, docker_image: str):
        twitch_app_req = {
            "title": "Twitch Plays Wolf",
            "id": "twitch-plays-wolf",
            "support_hdr": False,
            # TODO: HW encoders
            "h264_gst_pipeline": "",
            "hevc_gst_pipeline": "",
            "av1_gst_pipeline": "",
            "render_node": "/dev/dri/renderD129",  # TODO:
            "opus_gst_pipeline": "",  # TODO: Audio
            "start_virtual_compositor": True,
            "start_audio_server": True,
            "runner": {
                "type": "docker",
                "name": "twitch-plays-wolf",
                "image": docker_image,
                "mounts": [],
                "env": ["RUN_SWAY=1"],
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
        time.sleep(1)  # Wait for the session to be created
        return resp.json()["session_id"]

    def start_session(self, session_id: str, twitch_stream_key: str):
        twitch_stream_endpoint = "rtmp://ingest.global-contribute.live-video.net/app/" + twitch_stream_key
        session_req = {
            "session_id": session_id,
            "video_session": {
                "display_mode": {
                    "width": 1920,
                    "height": 1080,
                    "refreshRate": 30,
                },
                "gst_pipeline": "interpipesrc listen-to={session_id}_video is-live=true stream-sync=restart-ts max-bytes=0 max-buffers=3 block=false ! "
                                "video/x-raw, width={width}, height={height}, format=RGBx ! "
                                "queue max-size-buffers=0 max-size-bytes=0 max-size-time=0 ! "
                                "cudaupload ! "
                                "cudaconvertscale ! "
                                "nvh264enc rc-mode=cbr tune=high-quality min-force-key-unit-interval=2000000000 bitrate=4500 ! "
                                "h264parse ! "
                                "flvmux streamable=true ! "
                                "rtmp2sink max-lateness=1000 location=\"" + twitch_stream_endpoint + "\"",
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

    @staticmethod
    def encode_keyboard_input(key_code, is_press=True, modifiers=0):
        """
        Creates a KEYBOARD_PACKET structure and returns it as a base64 encoded string.

        Args:
            key_code (int): The key code to send
            is_press (bool): True for key press, False for key release
            modifiers (int): Keyboard modifiers (shift, ctrl, etc.)

        Returns:
            str: The HEX encoded packet
        """
        # Constants
        PACKET_TYPE_INPUT = 0x0206  # Little endian INPUT_DATA
        KEY_PRESS = 0x00000003  # Little endian KEY_PRESS value
        KEY_RELEASE = 0x00000004  # Little endian KEY_RELEASE value

        # Calculate sizes
        base_struct_size = 12  # Size of INPUT_PKT (2 + 2 + 4 + 4)
        keyboard_data_size = 6  # Size of additional KEYBOARD_PACKET data
        total_packet_size = base_struct_size + keyboard_data_size

        # Create the packet
        packet = struct.pack('<H', PACKET_TYPE_INPUT)  # packet_type (2 bytes, little endian)
        packet += struct.pack('<H', total_packet_size)  # packet_len (2 bytes, little endian)
        packet += struct.pack('<I', keyboard_data_size)  # data_size (4 bytes, little endian)
        packet += struct.pack('<I', KEY_PRESS if is_press else KEY_RELEASE)  # INPUT_TYPE (4 bytes, little endian)

        # Add KEYBOARD_PACKET specific fields
        packet += struct.pack('B', 0)  # flags (1 byte)
        packet += struct.pack('<h', key_code)  # key_code (2 bytes, little endian)
        packet += struct.pack('B', modifiers)  # modifiers (1 byte)
        packet += struct.pack('<h', 0)  # zero1 (2 bytes, little endian)

        return packet.hex().upper()

    async def send_input(self, event: Event):
        available_inputs = {
            "up": 0x26,
            "down": 0x28,
            "left": 0x25,
            "right": 0x27,
            "enter": 0x0D,
            "delete": 0x08,
        }

        message_ev: MessageEvent = event.data
        selected_input = available_inputs[message_ev.msg.split(" ")[0].lower()]
        logging.debug(f"Sending input: {selected_input}")
        if selected_input:
            # Press key
            input_req = {
                "session_id": "4135727842959053255",  # TODO: pass this
                "input_packet_hex": WolfAPI.encode_keyboard_input(selected_input)
            }
            resp = self.session.post(self.socket_path + "/sessions/input", json=input_req)
            logging.debug(resp.json())

            sleep(0.1)

            # Release key
            input_req = {
                "session_id": "4135727842959053255",  # TODO: pass this
                "input_packet_hex": WolfAPI.encode_keyboard_input(selected_input, False)
            }
            resp = self.session.post(self.socket_path + "/sessions/input", json=input_req)
            logging.debug(resp.json())

    def listen_for_input(self, session_id: str):
        self.event_bus.subscribe("chat_message", self.send_input)
