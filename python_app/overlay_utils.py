import win32gui
import win32con
import win32api
import pygame


def make_window_overlay(window_caption: str):
    """"Makes the pygame window transparrent frameless and always on the top"""
    hwnd = win32gui.FindWindow(None, window_caption)
    if not hwnd:
        print("⚠️ Could not find the window overlay setup")
        return

    #keep the fucker on the top
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
    )
    
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(
        hwnd,
        win32con.GWL_EXSTYLE,
        ex_style | win32con.WS_EX_LAYERED 
    )
    #| win32con.WS_EX_TRANSPARENT
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)
    
    print("✅ Overlay mode enabled for:", window_caption)