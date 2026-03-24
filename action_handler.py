import time
import ctypes
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Windows media key virtual codes — no library needed
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1

class ActionHandler:
    def __init__(self, debounce_seconds=0.8):
        devices = AudioUtilities.GetSpeakers()
        interface = devices._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.vol_min, self.vol_max, _ = self.volume.GetVolumeRange()

        self.last_action_time = {}
        self.debounce_seconds = debounce_seconds

    def _can_fire(self, label):
        now = time.time()
        if now - self.last_action_time.get(label, 0) >= self.debounce_seconds:
            self.last_action_time[label] = now
            return True
        return False

    def _press_media_key(self, vk_code):
        """Send media key directly via Windows API — no library needed."""
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)       # key down
        ctypes.windll.user32.keybd_event(vk_code, 0, 0x0002, 0)  # key up

    def handle(self, gesture):
        if gesture is None:
            return

        if isinstance(gesture, tuple):
            label, distance = gesture
        else:
            label, distance = gesture, None

        if label == "VOLUME_CONTROL":
            vol = np.interp(distance, [20, 200], [self.vol_min, self.vol_max])
            self.volume.SetMasterVolumeLevel(vol, None)

        elif label == "PLAY_PAUSE":
            if self._can_fire("PLAY_PAUSE"):
                self._press_media_key(VK_MEDIA_PLAY_PAUSE)

        elif label == "NEXT_TRACK":
            if self._can_fire("NEXT_TRACK"):
                self._press_media_key(VK_MEDIA_NEXT_TRACK)

        elif label == "PREV_TRACK":
            if self._can_fire("PREV_TRACK"):
                self._press_media_key(VK_MEDIA_PREV_TRACK)

        elif label == "MUTE":
            if self._can_fire("MUTE"):
                current = self.volume.GetMute()
                self.volume.SetMute(not current, None)