"""Drive the Windows VOYO debug app: login -> Explore -> tap POI -> capture.
Detects elements by image analysis (robust to DPI/resize), clicks at screen coords.
Reads any PDIAG exception from the debug log afterwards.
"""
import ctypes, ctypes.wintypes, time, os, subprocess, sys
from dotenv import load_dotenv; load_dotenv('.env')
from PIL import ImageGrab
import numpy as np
import pyautogui

pyautogui.FAILSAFE = False
user32 = ctypes.windll.user32
EMAIL = os.getenv('VOYO_TEST_EMAIL')
PWD = os.getenv('VOYO_TEST_PASSWORD')

def find_window(title):
    hwnd = None
    def cb(h, l):
        nonlocal hwnd
        if user32.IsWindowVisible(h):
            b = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(h, b, 256)
            if b.value == title: hwnd = h
        return True
    user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)(cb), 0)
    return hwnd

def focus(hwnd):
    user32.ShowWindow(hwnd, 9); time.sleep(0.3)
    user32.SetForegroundWindow(hwnd); time.sleep(0.8)

def grab(hwnd):
    rect = ctypes.wintypes.RECT(); user32.GetWindowRect(hwnd, ctypes.byref(rect))
    img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom), all_screens=True)
    return img, (rect.left, rect.top)

def click_at(hwnd, img_x, img_y, delay=0.3):
    rect = ctypes.wintypes.RECT(); user32.GetWindowRect(hwnd, ctypes.byref(rect))
    pyautogui.click(rect.left + img_x, rect.top + img_y)
    time.sleep(delay)

def type_clip(text):
    subprocess.run(['clip.exe'], input=text.encode(), check=True)
    pyautogui.hotkey('ctrl', 'v'); time.sleep(0.3)

def find_orange(img):
    arr = np.array(img.convert("RGB"))
    om = (arr[:,:,0].astype(int)>180)&(arr[:,:,1].astype(int)>60)&(arr[:,:,1].astype(int)<150)&(arr[:,:,2].astype(int)<100)
    ys, xs = np.where(om)
    if len(ys) < 30: return None
    return int(np.median(xs)), int(np.median(ys))

hwnd = find_window('flutter_app')
if not hwnd:
    print("NO flutter_app window"); sys.exit(1)
focus(hwnd)
img, _ = grab(hwnd)
print(f"window grabbed: {img.size}")

# Step 1: login. Find the email field — it's the first text input.
# Login forms: email field is typically in the vertical center-upper area.
# Strategy: click email field area, clear, type email; tab to password; type; find orange button; click.
w, h = img.size
# email field ~ 45% height
click_at(hwnd, w//2, int(h*0.45), 0.4)
pyautogui.hotkey('ctrl','a'); time.sleep(0.1)
type_clip(EMAIL)
time.sleep(0.3)
pyautogui.press('tab'); time.sleep(0.3)
type_clip(PWD)
time.sleep(0.3)
# find orange Sign In button
img2, _ = grab(hwnd)
btn = find_orange(img2)
if btn:
    print(f"Sign In button found at image {btn}")
    click_at(hwnd, btn[0], btn[1], 0.5)
    pyautogui.press('enter')
else:
    print("no orange button, pressing Tab+Enter")
    pyautogui.press('tab'); time.sleep(0.2); pyautogui.press('enter')

print("waiting 16s for Explore...")
time.sleep(16)
img3, _ = grab(hwnd)
img3.save("work/_win3_explore.png")
arr = np.array(img3.convert("RGB"))
content = 100*(arr.mean(axis=2)<230).mean()
green = 100*((arr[:,:,1].astype(int)>arr[:,:,0].astype(int)+5)&(arr[:,:,1].astype(int)>arr[:,:,2].astype(int)+5)).mean()
print(f"after login: content={content:.1f}%  green(map)={green:.1f}%")

if content < 25 and green < 1:
    print("LOGIN LIKELY FAILED — staying on login screen")
    sys.exit(2)

print("\nLOGIN OK — now tapping a POI in the Explore list...")
# The explore screen has POI cards in a list. Tap the first POI card ~30% down.
click_at(hwnd, int(w*0.5), int(h*0.35), 1.0)
# capture the sheet
time.sleep(6)
img4, _ = grab(hwnd)
img4.save("work/_win3_poi_sheet.png")
arr4 = np.array(img4.convert("RGB"))
# the sheet is a bottom panel; measure its body (below hero)
sheet_body = arr4[int(h*0.45):int(h*0.95), int(w*0.05):int(w*0.95)]
m = sheet_body.reshape(-1,3).mean(axis=0).astype(int)
flat_grey = (np.abs(sheet_body.astype(int).mean(axis=2) - int(m.mean())) < 8).mean()*100
uniq = len(np.unique((sheet_body[::8,::8]).reshape(-1,3), axis=0))
print(f"POI sheet body: mean=#{'%02x%02x%02x'%tuple(m)} flat_grey={flat_grey:.1f}% uniq_colors={uniq}")
print("DONE — check work/_win_debug3.log for VOYO-PDIAG lines")
