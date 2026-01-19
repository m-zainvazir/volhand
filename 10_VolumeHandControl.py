import cv2  
import time
import numpy as np
import HandTracking_Module as htm
import os
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from comtypes import client
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

######
wCam, hCam = 640, 480
######

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)
# Get default audio device
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

vol = 0
volBar = 400
volPer = 0
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
print(f"Volume range: {minVol} to {maxVol}")

# --- NEW: Toggle lock state variables ---
volume_locked = False
prev_pinky_state = "down"  # Track previous state: "up" or "down"
pinky_up_threshold = 30    # How many pixels above PIP to count as "up"
# --- END NEW ---

volume.SetMasterVolumeLevel(0.0, None)


while True:
    success, img = cap.read()
    img = detector.findHands(img) #Detect Hands
    lmList = detector.findPosition(img, draw=False) #Get Location of landmarks
    
    if len(lmList) != 0:
        # --- NEW: Pinky toggle logic ---
        # Get pinky tip (landmark 20) and pinky PIP (landmark 18)
        pinky_tip_y = lmList[20][2]  # y-coordinate of pinky tip (landmark 20)
        pinky_pip_y = lmList[18][2]   # y-coordinate of pinky PIP (landmark 18)
        
        # Determine current pinky state
        current_pinky_state = "down"
        if pinky_tip_y < pinky_pip_y - pinky_up_threshold:  # Pinky up (tip significantly above PIP)
            current_pinky_state = "up"
        # Note: We don't need to check "down" precisely - anything not "up" is "down"
        
        # --- Toggle lock when pinky goes from down to up ---
        # Only toggle when pinky was down and now is up (lifting motion)
        if prev_pinky_state == "down" and current_pinky_state == "up":
            volume_locked = not volume_locked  # Toggle lock state
            print(f"Lock toggled: {'LOCKED' if volume_locked else 'UNLOCKED'}")
        
        # Update previous state
        prev_pinky_state = current_pinky_state
        
        # Set display colors and status text
        if volume_locked:
            lock_status = "LOCKED"
            lock_color = (0, 0, 255)  # Red
        else:
            lock_status = "UNLOCKED"
            lock_color = (0, 255, 0)  # Green
        
        # Draw pinky landmarks with state indicator
        pinky_tip_x, pinky_tip_y = lmList[20][1], lmList[20][2]
        pinky_pip_x, pinky_pip_y = lmList[18][1], lmList[18][2]
        
        # Draw pinky tip with color based on its current position
        pinky_tip_color = (0, 255, 255) if current_pinky_state == "up" else (255, 255, 0)
        cv2.circle(img, (pinky_tip_x, pinky_tip_y), 12, pinky_tip_color, cv2.FILLED)
        cv2.circle(img, (pinky_pip_x, pinky_pip_y), 8, (200, 200, 200), cv2.FILLED)
        
        # Draw line between tip and PIP for visual reference
        cv2.line(img, (pinky_tip_x, pinky_tip_y), (pinky_pip_x, pinky_pip_y), (255, 255, 255), 2)
        
        # Draw indicator showing if pinky is currently up or down
        pinky_state_text = "Pinky: UP" if current_pinky_state == "up" else "Pinky: DOWN"
       # cv2.putText(img, pinky_state_text, (pinky_tip_x - 50, pinky_tip_y - 20), 
       #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, pinky_tip_color, 2)
        # --- END NEW ---

        # --- MODIFIED: Only adjust volume if NOT locked ---
        if not volume_locked:
            x1, y1 = lmList[4][1], lmList[4][2] #Thumb tip
            x2, y2 = lmList[8][1], lmList[8][2] #Index tip
            cx, cy = (x1 + x2)//2, (y1 + y2)//2 #Center point

            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3) 
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            length = np.hypot(x2 - x1, y2 - y1)
            print(f"Distance: {length:.1f}, Status: {lock_status}")

            #Hand range 50 - 300
            hi = 200
            lo = 50

            vol = np.interp(length, [lo, hi], [0, 1])
            volBar = np.interp(length, [lo, hi], [400, 150])
            volPer = np.interp(length, [lo, hi], [0, 100])
            volume.SetMasterVolumeLevelScalar(vol, None)

            if length < 50:
                cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
            if length > 200:
                cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
        else:
            # --- NEW: Show lock indicator on thumb-index line ---
            x1, y1 = lmList[4][1], lmList[4][2] #Thumb tip
            x2, y2 = lmList[8][1], lmList[8][2] #Index tip
            cx, cy = (x1 + x2)//2, (y1 + y2)//2 #Center point
            
            # Draw grayed out line to show volume control is inactive
            cv2.circle(img, (x1, y1), 15, (100, 100, 100), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (100, 100, 100), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (100, 100, 100), 3)
            
            # Show "LOCKED" text and a lock icon
            cv2.putText(img, "LOCKED", (cx-40, cy-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Draw a small lock icon
            lock_rect_start = (cx-15, cy+10)
            lock_rect_end = (cx+15, cy+40)
            cv2.rectangle(img, lock_rect_start, lock_rect_end, (0, 0, 255), 2)
            cv2.circle(img, (cx, cy+10), 10, (0, 0, 255), 2)
            # --- END NEW ---

    # --- MODIFIED: Draw lock status and instructions ---
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    
    # Draw lock status box
    cv2.rectangle(img, (wCam-200, 10), (wCam-10, 60), lock_color if len(lmList) != 0 else (100, 100, 100), -1)
    cv2.putText(img, f'Status: {lock_status if len(lmList) != 0 else "NO HAND"}', 
                (wCam-190, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Draw toggle instructions
    cv2.putText(img, "Lift Pinky to TOGGLE lock", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(img, "Lift again to unlock", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    # --- END MODIFIED ---

    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
            
    #cv2.putText(img, f'FPS:{int(fps)}', (20, 90), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    cv2.imshow("Image", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()