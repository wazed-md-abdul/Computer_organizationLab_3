import subprocess, time, ctypes, struct, winreg, os
from ctypes import wintypes
from PIL import Image

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetWindowDC.argtypes = [wintypes.HWND]
user32.GetWindowDC.restype = wintypes.HDC
user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
user32.PrintWindow.restype = wintypes.BOOL

gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
gdi32.CreateCompatibleDC.restype = wintypes.HDC
gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype = wintypes.HGDIOBJ
gdi32.DeleteDC.argtypes = [wintypes.HDC]
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.GetDIBits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT, wintypes.LPVOID, wintypes.LPVOID, wintypes.UINT]
gdi32.GetDIBits.restype = ctypes.c_int

def capture_ripes_gui(source_code, output_png, wait_sec=2.5):
    # Set registry sourcecode
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Ripes\Ripes', 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, 'sourcecode', 0, winreg.REG_SZ, source_code)
    winreg.SetValueEx(key, 'autoclock_interval', 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(key)

    p = subprocess.Popen([r'ripes\Ripes.exe'])
    
    hwnd = None
    for _ in range(20):
        time.sleep(0.5)
        hwnds = []
        def enum_cb(h, extra):
            if user32.IsWindowVisible(h):
                title = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(h, title, 256)
                if title.value == 'Ripes':
                    hwnds.append(h)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
        if hwnds:
            hwnd = hwnds[0]
            break

    if not hwnd:
        p.terminate()
        raise RuntimeError('Ripes window not found')

    time.sleep(1.0)

    # Click Run button (client coords: x=151, y=28)
    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202
    WM_MOUSEMOVE = 0x0200

    cx, cy = 151, 28
    lParam = (cy << 16) | (cx & 0xFFFF)
    user32.SendMessageW(hwnd, WM_MOUSEMOVE, 0, lParam)
    time.sleep(0.05)
    user32.SendMessageW(hwnd, WM_LBUTTONDOWN, 1, lParam)
    time.sleep(0.05)
    user32.SendMessageW(hwnd, WM_LBUTTONUP, 0, lParam)

    time.sleep(wait_sec)

    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top

    hdc_win = user32.GetWindowDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_win)
    hbm = gdi32.CreateCompatibleBitmap(hdc_win, w, h)
    gdi32.SelectObject(hdc_mem, hbm)

    user32.PrintWindow(hwnd, hdc_mem, 2)

    buf_size = w * h * 4
    dib_header = struct.pack('<IIIHHIIIIII', 40, w, h, 1, 32, 0, buf_size, 2835, 2835, 0, 0)
    buf = ctypes.create_string_buffer(buf_size)
    gdi32.GetDIBits(hdc_mem, hbm, 0, h, buf, dib_header, 0)

    user32.ReleaseDC(hwnd, hdc_win)
    gdi32.DeleteDC(hdc_mem)
    gdi32.DeleteObject(hbm)
    p.terminate()
    try:
        p.wait(timeout=2)
    except:
        pass

    # Save PNG
    img = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, -1)
    img.save(output_png)
    print(f'Saved: {output_png}')

tasks = []

# 1. Task A
with open('01_register_trace.s', 'r') as f:
    tasks.append((f.read(), 'screenshot_task_a.png', 1.5))

# 2. Task B
with open('02_memory_bytes.s', 'r') as f:
    tasks.append((f.read(), 'screenshot_task_b.png', 1.5))

# 3. Task C (n=3)
with open('03_array_sum.s', 'r') as f:
    c_n3 = f.read()
tasks.append((c_n3, 'screenshot_task_c_n3.png', 2.0))

# 4. Task C (n=0)
c_n0 = c_n3.replace('addi x11, x0, 3', 'addi x11, x0, 0')
tasks.append((c_n0, 'screenshot_task_c_n0.png', 1.5))

# 5. Task D1 (stride = 1)
d1_code = c_n3.replace('addi x7, x7, 4', 'addi x7, x7, 1')
tasks.append((d1_code, 'screenshot_task_d1_stride_error.png', 2.0))

# 6. Task D2 (lw before beq, n=0)
d2_code = c_n0.replace('loop:\n    beq  x6, x11, end\n    lw   x8, 0(x7)', 'loop:\n    lw   x8, 0(x7)\n    beq  x6, x11, end')
tasks.append((d2_code, 'screenshot_task_d2_read_before_check.png', 1.5))

# 7. Task E (n=3)
with open('04_sum_function.s', 'r') as f:
    e_n3 = f.read()
tasks.append((e_n3, 'screenshot_task_e_function_n3.png', 2.0))

# 8. Task E (n=0)
e_n0 = e_n3.replace('addi a1, x0, 3', 'addi a1, x0, 0')
tasks.append((e_n0, 'screenshot_task_e_function_n0.png', 1.5))

for code, fname, wait_t in tasks:
    capture_ripes_gui(code, fname, wait_sec=wait_t)
    time.sleep(1.0)

print('All screenshots generated successfully!')
