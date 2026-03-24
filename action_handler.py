import time
import ctypes
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Virtual key codes for media controls (Play/Pause, Next, Previous)
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1

class ActionHandler:
    def __init__(self, debounce_seconds=0.8):
        # Get speaker device
        devices = AudioUtilities.GetSpeakers()
        
        # Activate volume control interface
        interface = devices._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        
        # Cast interface to usable volume object
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Get volume range (min, max)
        self.vol_min, self.vol_max, _ = self.volume.GetVolumeRange()

        # Store last action time for debounce control
        self.last_action_time = {}
        self.debounce_seconds = debounce_seconds

    def _can_fire(self, label):
        # Check if enough time has passed for this action
        now = time.time()
        if now - self.last_action_time.get(label, 0) >= self.debounce_seconds:
            # update last trigger time
            self.last_action_time[label] = now  
            return True
        return False

    def _press_media_key(self, vk_code):
        """Simulate media key press using Windows API"""
        # key press
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)   
        # key release    
        ctypes.windll.user32.keybd_event(vk_code, 0, 0x0002, 0)  

    def handle(self, gesture):
        # Ignore if no gesture detected
        if gesture is None:
            return

        # Handle tuple gesture (label + distance)
        if isinstance(gesture, tuple):
            label, distance = gesture
        else:
            label, distance = gesture, None

        # Volume control using finger distance
        if label == "VOLUME_CONTROL":
            # map distance → volume
            vol = np.interp(distance, [20, 200], [self.vol_min, self.vol_max])  
            self.volume.SetMasterVolumeLevel(vol, None)

        # Play / Pause action
        elif label == "PLAY_PAUSE":
            if self._can_fire("PLAY_PAUSE"):
                self._press_media_key(VK_MEDIA_PLAY_PAUSE)

        # Next track action
        elif label == "NEXT_TRACK":
            if self._can_fire("NEXT_TRACK"):
                self._press_media_key(VK_MEDIA_NEXT_TRACK)

        # Previous track action
        elif label == "PREV_TRACK":
            if self._can_fire("PREV_TRACK"):
                self._press_media_key(VK_MEDIA_PREV_TRACK)

        # Mute / Unmute toggle
        elif label == "MUTE":
            if self._can_fire("MUTE"):
                # get current mute state
                current = self.volume.GetMute()  
                # toggle mute
                self.volume.SetMute(not current, None)  