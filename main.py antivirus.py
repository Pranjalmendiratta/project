from glob import glob
from tkinter import*
from tkinter import ttk
import psutil
import pystray
import PIL.Image
from screeninfo import get_monitors
import random
import math
import json
import os
from src.scanner import SystemScanner

# Create scanner instance
scanner = SystemScanner()

#--------------------Global Variable ---------------------# 
global winFrame, homeButtonImg, footerImg, logoLabelImg
#--------------------Global Variable End ---------------------# 

# Custom styles and colors
COLORS = {
    'bg_dark': "#1E1E2E",
    'bg_darker': "#181825",
    'bg_lighter': "#252538",
    'accent': "#7AA2F7",
    'accent_hover': "#8AB2FF",
    'text': "#FFFFFF",
    'text_secondary': "#A9B1D6",
    'success': "#9ECE6A",
    'success_hover': "#ABD873",
    'warning': "#E0AF68",
    'card_bg': "#1F1F2F"
}

def create_hover_effect(widget, normal_bg, hover_bg, duration_ms=150):
    """Enhanced hover effect with smooth transition"""
    steps = 10
    step_time = duration_ms // steps
    
    def interpolate_color(start, end, step, total_steps):
        """Interpolate between two hex colors"""
        start = tuple(int(start[i:i+2], 16) for i in (1, 3, 5))
        end = tuple(int(end[i:i+2], 16) for i in (1, 3, 5))
        
        r = start[0] + (end[0] - start[0]) * step // total_steps
        g = start[1] + (end[1] - start[1]) * step // total_steps
        b = start[2] + (end[2] - start[2]) * step // total_steps
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def animate_hover(start_color, end_color, step=0):
        if step <= steps:
            color = interpolate_color(start_color, end_color, step, steps)
            widget.configure(bg=color)
            widget.after(step_time, lambda: animate_hover(start_color, end_color, step + 1))
    
    def on_enter(e):
        animate_hover(normal_bg, hover_bg)
    
    def on_leave(e):
        animate_hover(hover_bg, normal_bg)
    
    widget.bind('<Enter>', on_enter)
    widget.bind('<Leave>', on_leave)

def create_card(parent, title, **kwargs):
    """Create a modern card widget with consistent styling"""
    card = Frame(parent, bg=COLORS['card_bg'], relief='flat', **kwargs)
    card.pack(fill=X, pady=(0, 15), padx=20)
    
    # Add subtle border radius effect with inner highlight
    canvas = Canvas(card, height=2, bg=COLORS['card_bg'], highlightthickness=0)
    canvas.pack(fill=X)
    canvas.create_line(0, 0, card.winfo_reqwidth(), 0, 
                      fill=COLORS['accent'], width=2)
    
    if title:
        Label(card, text=title, font=("Helvetica", 12, "bold"),
              bg=COLORS['card_bg'], fg=COLORS['text_secondary']).pack(
                  anchor=W, padx=15, pady=(10, 5))
    
    return card

def create_modern_button(text, y_pos, command=None):
    btn = Label(main_container, text=text, font=("Helvetica", 12, "bold"),
               bg=COLORS['bg_lighter'], fg=COLORS['text'],
               padx=25, pady=12, cursor="hand2", width=20)
    btn.place(x=160, y=y_pos)
    create_hover_effect(btn, COLORS['bg_lighter'], COLORS['accent'])
    if command:
        btn.bind('<Button-1>', command)
    return btn

def CloseWindow(event):
    save_window_settings()
    window.withdraw()

    def OpenWindow():
        window.deiconify()
        window.lift()
        window.focus_force()
        iconIo.stop()

    ioIconImange = PIL.Image.open("res\\Logo\\logo.png")
    iconIo = pystray.Icon("logo", ioIconImange, menu=pystray.Menu(
        pystray.MenuItem("Open", OpenWindow, default=True)
    ))
    iconIo.run()

def CloseButtonEnter(event):
    close_button.config(image=close_buttonImgHoved)

def CloseButtonLeave(event):
    close_button.config(image=close_buttonImg)

def MinimizeWindow(event):
    save_window_settings()
    window.iconify()

def MinimizeButtonEnter(event):
    minimize_button.config(image=minimize_buttonImgHoved)

def MinimizeButtonLeave(event):
    minimize_button.config(image=minimize_buttonImg)

def MaximizeWindow(event):
    if window.state() == 'zoomed':
        window.state('normal')
        maximize_button.config(text="□")
    else:
        window.state('zoomed')
        maximize_button.config(text="❐")
    save_window_settings()

def MaximizeButtonEnter(event):
    if window.state() == 'zoomed':
        maximize_button.config(text="❐")
    else:
        maximize_button.config(text="□")

def MaximizeButtonLeave(event):
    if window.state() == 'zoomed':
        maximize_button.config(text="❐")
    else:
        maximize_button.config(text="□")

def get_pos(event):
    xwin = window.winfo_x()
    ywin = window.winfo_y()
    startx = event.x_root
    starty = event.y_root

    ywin = ywin - starty
    xwin = xwin - startx

    def move_window(event):
        window.geometry(f"+{event.x_root + xwin}+{event.y_root + ywin}")
    
    title_bar.bind('<B1-Motion>', move_window)

def create_back_button(parent):
    """Create a modern back button that returns to home page"""
    # Create a container frame for the back button
    back_container = Frame(parent, bg=COLORS['bg_darker'], width=100, height=35)
    back_container.place(x=20, y=20)
    back_container.pack_propagate(False)
    
    # Create the back button with arrow and text
    back_btn = Label(back_container, text="← HOME", font=("Helvetica", 11, "bold"),
                    bg=COLORS['bg_darker'], fg=COLORS['text'],
                    padx=15, pady=8, cursor="hand2")
    back_btn.pack(expand=True, fill=BOTH)
    
    # Enhanced hover effect
    def on_enter(e):
        back_btn.config(bg=COLORS['accent'], fg=COLORS['bg_darker'])
        back_container.config(bg=COLORS['accent'])
    
    def on_leave(e):
        back_btn.config(bg=COLORS['bg_darker'], fg=COLORS['text'])
        back_container.config(bg=COLORS['bg_darker'])
    
    back_btn.bind('<Enter>', on_enter)
    back_btn.bind('<Leave>', on_leave)
    back_btn.bind('<Button-1>', lambda e: HomeFrame())
    
    return back_container

# Window state management
def save_window_settings():
    try:
        if window.state() != 'withdrawn':  # Only save if window is visible
            settings = {
                "window_state": window.state(),
                "window_position": {
                    "x": window.winfo_x(),
                    "y": window.winfo_y()
                },
                "window_size": {
                    "width": window.winfo_width(),
                    "height": window.winfo_height()
                }
            }
            with open('config.json', 'w') as f:
                json.dump(settings, f, indent=4)
    except Exception:
        pass  # Fail silently if we can't save settings

def load_window_settings():
    try:
        with open('config.json', 'r') as f:
            settings = json.load(f)
            # Validate settings
            if not all(key in settings for key in ['window_state', 'window_position', 'window_size']):
                raise ValueError("Invalid settings format")
            return settings
    except Exception:
        return {
            "window_state": "normal",
            "window_position": {"x": 30, "y": 30},
            "window_size": {"width": 1200, "height": 850}
        }

# Load saved settings
settings = load_window_settings()

window = Tk()
window.title("BitLink End-Point")
window.minsize(1200, 850)
window.overrideredirect(True)
window.configure(bg=COLORS['bg_dark'])

# Set initial position and size
window.geometry(f"{settings['window_size']['width']}x{settings['window_size']['height']}+{settings['window_position']['x']}+{settings['window_position']['y']}")

# Restore window state after geometry is set
if settings['window_state'] == 'zoomed':
    window.state('zoomed')
    
# Save settings on window state changes
def CloseWindow(event):
    save_window_settings()
    window.withdraw()
    icon.run()

def MinimizeWindow(event):
    save_window_settings()
    window.iconify()

def MaximizeWindow(event):
    if window.state() == 'zoomed':
        window.state('normal')
        maximize_button.config(text="□")
    else:
        window.state('zoomed')
        maximize_button.config(text="❐")
    save_window_settings()

# Save settings periodically
def auto_save_settings():
    save_window_settings()
    window.after(30000, auto_save_settings)  # Save every 30 seconds

# Start auto-save
window.after(30000, auto_save_settings)

# Create main container with gradient effect
winFrame = Frame(window, width=1200, height=850, bg=COLORS['bg_dark'])
winFrame.pack(expand=True, fill=BOTH)
winFrame.pack_propagate(0)

# Create title bar
title_bar = Frame(window, bg=COLORS['bg_darker'], height=30)
title_bar.pack(fill=X)

# Create close button
close_button = Label(title_bar, text="×", font=("Helvetica", 13, "bold"),
                    bg=COLORS['bg_darker'], fg=COLORS['text'],
                    width=4, cursor="hand2")
close_button.pack(side=RIGHT, padx=0, pady=2)
close_button.bind('<Button-1>', CloseWindow)
create_hover_effect(close_button, COLORS['bg_darker'], COLORS['accent'])

# Create maximize button
maximize_button = Label(title_bar, text="□", font=("Helvetica", 13, "bold"),
                       bg=COLORS['bg_darker'], fg=COLORS['text'],
                       width=4, cursor="hand2")
maximize_button.pack(side=RIGHT, padx=0, pady=2)
maximize_button.bind('<Button-1>', MaximizeWindow)
create_hover_effect(maximize_button, COLORS['bg_darker'], COLORS['accent'])

# Create minimize button
minimize_button = Label(title_bar, text="−", font=("Helvetica", 13, "bold"),
                       bg=COLORS['bg_darker'], fg=COLORS['text'],
                       width=4, cursor="hand2")
minimize_button.pack(side=RIGHT, padx=0, pady=2)
minimize_button.bind('<Button-1>', MinimizeWindow)
create_hover_effect(minimize_button, COLORS['bg_darker'], COLORS['accent'])

# Add BitLink title to title bar
title_label = Label(title_bar, text="BitLink End-Point", font=("Helvetica", 10), 
                   bg=COLORS['bg_darker'], fg=COLORS['text'])
title_label.pack(side=LEFT, padx=10, pady=2)

# Make window draggable from title bar
title_bar.bind('<Button-1>', get_pos)

def HomeFrame():
    global winFrame
    winFrame = winFrame
    
    # Clear existing content
    for widget in winFrame.winfo_children():
        widget.destroy()
    
    main_container = Frame(winFrame, bg=COLORS['bg_dark'])
    main_container.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Enhanced header with gradient effect
    header = Frame(main_container, bg=COLORS['bg_darker'], height=120)
    header.pack(fill=X, pady=(0, 20))
    
    logo_container = Frame(header, bg=COLORS['bg_darker'])
    logo_container.pack(side=LEFT, padx=20, pady=10)
    
    global logoLabelImg
    logoLabelImg = PhotoImage(file='res\\Logo\\logo.png')
    logoLabel = Label(logo_container, image=logoLabelImg, bg=COLORS['bg_darker'])
    logoLabel.pack(side=LEFT, padx=(0, 15))
    
    title_container = Frame(logo_container, bg=COLORS['bg_darker'])
    title_container.pack(side=LEFT)
    
    Label(title_container, text="BitLink", font=("Helvetica", 28, "bold"), 
          bg=COLORS['bg_darker'], fg=COLORS['accent']).pack(anchor=W)
    Label(title_container, text="Antivirus Pro", font=("Helvetica", 16), 
          bg=COLORS['bg_darker'], fg=COLORS['text']).pack(anchor=W)
    
    # Enhanced status card
    status_card = create_card(main_container, None)
    
    status_header = Frame(status_card, bg=COLORS['card_bg'])
    status_header.pack(fill=X, padx=15, pady=(15, 5))
    
    Label(status_header, text="SYSTEM STATUS", font=("Helvetica", 12, "bold"), 
          bg=COLORS['card_bg'], fg=COLORS['text_secondary']).pack(side=LEFT)
    
    status_indicator = Frame(status_card, bg=COLORS['card_bg'])
    status_indicator.pack(fill=X, padx=15, pady=(0, 15))
    
    status_dot = Label(status_indicator, text="●", font=("Helvetica", 16), 
                      bg=COLORS['card_bg'], fg=COLORS['success'])
    status_dot.pack(side=LEFT, padx=(0, 10))
    
    status_label = Label(status_indicator, text="Protected", 
                        font=("Helvetica", 16, "bold"),
                        bg=COLORS['card_bg'], fg=COLORS['success'])
    status_label.pack(side=LEFT)
    
    def pulse_animation():
        """Enhanced pulse animation with smooth transition"""
        def animate_pulse(alpha=1.0, decreasing=True):
            try:
                # Calculate color based on alpha
                color = f'#{int(alpha * 255):02x}0000'  # Red color with varying alpha
                status_dot.configure(fg=color)
                
                # Update alpha value
                if decreasing:
                    alpha -= 0.1
                    if alpha <= 0:
                        alpha = 0
                        decreasing = False
                else:
                    alpha += 0.1
                    if alpha >= 1:
                        alpha = 1
                        decreasing = True
                
                # Continue animation
                if not window.winfo_exists():
                    return
                window.after(50, lambda: animate_pulse(alpha, decreasing))
            except Exception:
                pass  # Silently handle any animation errors
        
        animate_pulse()
    
    pulse_animation()
    
    # Quick actions section with modern cards
    quick_actions = create_card(main_container, "QUICK ACTIONS")
    
    actions_container = Frame(quick_actions, bg=COLORS['card_bg'])
    actions_container.pack(fill=X, padx=15, pady=(0, 15))
    
    # Create modern buttons for all functions
    def create_modern_button(text, y_pos, command=None):
        btn = Label(main_container, text=text, font=("Helvetica", 12, "bold"),
                   bg=COLORS['bg_lighter'], fg=COLORS['text'],
                   padx=25, pady=12, cursor="hand2", width=20)
        btn.place(x=160, y=y_pos)
        create_hover_effect(btn, COLORS['bg_lighter'], COLORS['accent'])
        if command:
            btn.bind('<Button-1>', command)
        return btn

    smart_scan_btn = create_modern_button("SMART SCAN", 340)
    smart_scan_btn.place(x=160, y=340)

    deep_scan_btn = create_modern_button("DEEP SCAN", 340)
    deep_scan_btn.place(x=830, y=340)

    help_support_btn = create_modern_button("HELP & SUPPORT", 400)
    help_support_btn.place(x=180, y=400)

    driver_update_btn = create_modern_button("DRIVER UPDATE", 400)
    driver_update_btn.place(x=810, y=400)

    # Statistics card
    stats_card = create_card(main_container, "SYSTEM HEALTH")
    
    stats_container = Frame(stats_card, bg=COLORS['card_bg'])
    stats_container.pack(fill=X, padx=15, pady=(0, 15))
    
    # Add some sample statistics
    def create_stat(parent, label, value):
        frame = Frame(parent, bg=COLORS['card_bg'])
        frame.pack(side=LEFT, padx=15)
        
        Label(frame, text=label, font=("Helvetica", 10),
              bg=COLORS['card_bg'], fg=COLORS['text_secondary']).pack(anchor=W)
        Label(frame, text=value, font=("Helvetica", 14, "bold"),
              bg=COLORS['card_bg'], fg=COLORS['text']).pack(anchor=W)
    
    create_stat(stats_container, "CPU Usage", "32%")
    create_stat(stats_container, "Memory Usage", "4.2 GB")
    create_stat(stats_container, "Threats Blocked", "147")
    
    # Footer with branding
    footer = Frame(main_container, bg=COLORS['bg_darker'], height=40)
    footer.pack(side=BOTTOM, fill=X)
    
    Label(footer, text="BitLink Antivirus Pro 2024",
          font=("Helvetica", 9), bg=COLORS['bg_darker'],
          fg=COLORS['text_secondary']).pack(side=LEFT, padx=20)

    #--------------------Logo Frame End ----------------#

    #--------------------Home Button --------------------#

    global homeButtonImg

    homeButtonImg = PhotoImage(file="res\\Home Frame\\Current\\Home.png")


    homeButton = Label(main_container,image=homeButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    homeButton.place(x=155,y=570)


    #--------------------Home Button End------------------#

    #--------------------Scan Button ---------------------#

    scanButtonImg = PhotoImage(file="res\\Scan Frame\\Non-Hoved\\Scan.png")
    hovScanButtonImg = PhotoImage(file="res\\Scan Frame\\Hoved\\Scan.png")
    def ScanButtonEnterFrame(event):
        scanButton.config(image=hovScanButtonImg)

    def ScanButtonLeaveFrame(event):
        scanButton.config(image=scanButtonImg)
    
    def ScanButtonCall(event):
        ScanFrame()


    scanButton = Label(main_container,image=scanButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    scanButton.place(x=335,y=570)

    scanButton.bind('<Enter>',ScanButtonEnterFrame)
    scanButton.bind('<Leave>',ScanButtonLeaveFrame)
    scanButton.bind('<Button-1>',ScanButtonCall)

    # #--------------------Scan Button End------------------#

    # #--------------------System Button -------------------#

    systemButtonImg = PhotoImage(file="res\\System Frame\\Non-Hoved\\System.png")
    hovsystemButtonImg = PhotoImage(file="res\\System Frame\\Hoved\\System.png")

    def SystemButtonEnterFrame(event):
        systemButton.config(image=hovsystemButtonImg)

    def SystemButtonLeaveFrame(event):
        systemButton.config(image=systemButtonImg)

    def SystemButtonCall(event):
        SystemFrame()


    systemButton = Label(main_container,image=systemButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    systemButton.place(x=515,y=570)

    systemButton.bind('<Enter>',SystemButtonEnterFrame)
    systemButton.bind('<Leave>',SystemButtonLeaveFrame)
    systemButton.bind('<Button-1>',SystemButtonCall)

    # #--------------------System Button End ---------------#

    #--------------------Web Button -----------------#

    webButtonImg = PhotoImage(file="res\\Web Frame\\Non-Hoved\\Web.png")
    hovWebButtonImg = PhotoImage(file="res\\Web Frame\\Hoved\\Web.png")

    def WebButtonEnterFrame(event):
        webButton.config(image=hovWebButtonImg)

    def WebButtonLeaveFrame(event):
        webButton.config(image=webButtonImg)

    def WebButtonCall(event):
        WebFrame()


    webButton = Label(main_container,image=webButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    webButton.place(x=695,y=570)

    webButton.bind('<Enter>',WebButtonEnterFrame)
    webButton.bind('<Leave>',WebButtonLeaveFrame)
    webButton.bind('<Button-1>',WebButtonCall)

    #--------------------Web Button End -------------#

    # #--------------------Tools Button -----------------#

    toolsButtonImg = PhotoImage(file="res\\Tools Frame\\Non-Hoved\\Tools.png")
    hovToolsButtonImg = PhotoImage(file="res\\Tools Frame\\Hoved\\Tools.png")

    def ToolsButtonEnterFrame(event):
        toolsButton.config(image=hovToolsButtonImg)

    def ToolsButtonLeaveFrame(event):
        toolsButton.config(image=toolsButtonImg)

    def ToolsButtonCall(event):
        ToolsFrame()


    toolsButton = Label(main_container,image=toolsButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    toolsButton.place(x=875,y=570)

    toolsButton.bind('<Enter>',ToolsButtonEnterFrame)
    toolsButton.bind('<Leave>',ToolsButtonLeaveFrame)
    toolsButton.bind('<Button-1>',ToolsButtonCall)

    # #--------------------Tools Button End -------------#


    #--------------------Animation --- ----------------#

    global robotImg
    robotImg = PhotoImage(file='res\\Home Frame\\Animation\\robotlink.png')

    robotAnimation = Label(main_container,image=robotImg,bg=COLORS['bg_dark'])
    robotAnimation.place(x=405,y=150)

    global ani
    ani = 0
    def RobotAnimation():
        global ani

        if ani == 4:
            robotAnimation.place_configure(y=153)
            ani = 0
        
        elif ani == 2:
            robotAnimation.place_configure(y=150)


        ani += 1

        robotAnimation.after(200,RobotAnimation)

    RobotAnimation()

    # #--------------------Animation End ----------------#

    # #--------------------Sub-Frame --- ----------------#

    # #--------------------Proction-Frame --- ----------------#

    # Create modern protection button
    # protection_btn = create_modern_button("PROTECTION ON", 160)
    # protection_btn.place(x=180, y=160)  

    # Create modern firewall button
    # firewall_btn = create_modern_button("FIREWALL ON", 220)
    # firewall_btn.place(x=160, y=220)  

    # Create modern full scan button
    # full_scan_btn = create_modern_button("FULL SCAN", 280)
    # full_scan_btn.place(x=150, y=280)  

    # Remove RAM BOOST button
    # ram_boost_btn = create_modern_button("RAM BOOST", 280)
    # ram_boost_btn.place(x=840, y=280)

    #--------------------Web-Frame End ----------------#

    # #--------------------FireWall-Frame --- ----------------#

    #--------------------FullScan-Frame --- ----------------#

    #--------------------QuickScan-Frame --- ----------------#

    #--------------------RamBooster-Frame --- ----------------#

    #--------------------Smart Scan-Frame --- ----------------#

    #--------------------Deep Scan-Frame --- ----------------#

    #--------------------Help-Frame --- ----------------#

    #--------------------Driver Update-Frame --- ----------------#

    # #--------------------Sub-Frame End ----------------#


##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################

def ScanFrame():
    global winFrame
    winFrame = winFrame
    
    # Clear existing content
    for widget in winFrame.winfo_children():
        widget.destroy()
    
    # Create main container
    content_frame = Frame(winFrame, bg=COLORS['bg_dark'])
    content_frame.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Add back button
    create_back_button(content_frame)
    
    # Create scan buttons
    smart_scan_btn = Label(content_frame, text="SMART SCAN", font=("Helvetica", 14, "bold"),
                          bg=COLORS['bg_lighter'], fg=COLORS['text'],
                          padx=30, pady=15, cursor="hand2")
    smart_scan_btn.place(x=180, y=280)
    create_hover_effect(smart_scan_btn, COLORS['bg_lighter'], COLORS['accent'])
    smart_scan_btn.bind('<Button-1>', start_smart_scan)
    
    deep_scan_btn = Label(content_frame, text="DEEP SCAN", font=("Helvetica", 14, "bold"),
                         bg=COLORS['bg_lighter'], fg=COLORS['text'],
                         padx=30, pady=15, cursor="hand2")
    deep_scan_btn.place(x=180, y=380)
    create_hover_effect(deep_scan_btn, COLORS['bg_lighter'], COLORS['accent'])
    deep_scan_btn.bind('<Button-1>', start_deep_scan)

    #--------------------Logo Frame End ----------------#

    #--------------------Smart_Scan --------------------#

    global smartScanButton_1
    global smartScanButton_1_Hoved

    smartScanButton_1 = PhotoImage(file='res\\Scan Frame\\Non-Hoved\\smart Scan.png').subsample(2,2)
    smartScanButton_1_Hoved = PhotoImage(file='res\\Scan Frame\\Hoved\\smart Scan.png').subsample(2,2)

    def smartScanButton_1_Enter(e):
        smartScanButton_1place.config(image=smartScanButton_1_Hoved)
    
    def smartScanButton_1_Leave(e):
        smartScanButton_1place.config(image=smartScanButton_1)

    smartScanButton_1place = Label(content_frame,image=smartScanButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    smartScanButton_1place.place(x=510,y=170)

    smartScanButton_1place.bind('<Enter>',smartScanButton_1_Enter)
    smartScanButton_1place.bind('<Leave>',smartScanButton_1_Leave)

    #--------------------Smart_Scan End ----------------#

    #--------------------Full_Scan --------------------#

    global fullScanButton_1
    global fullScanButton_1_Hoved

    fullScanButton_1 = PhotoImage(file='res\\Scan Frame\\Non-Hoved\\Full Scan.png').subsample(2,2)
    fullScanButton_1_Hoved = PhotoImage(file='res\\Scan Frame\\Hoved\\Full Scan.png').subsample(2,2)

    def fullScanButton_1_Enter(e):
        fullScanButton_1place.config(image=fullScanButton_1_Hoved)
    
    def fullScanButton_1_Leave(e):
        fullScanButton_1place.config(image=fullScanButton_1)


    fullScanButton_1place = Label(content_frame,image=fullScanButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    fullScanButton_1place.place(x=510,y=240)

    fullScanButton_1place.bind('<Enter>',fullScanButton_1_Enter)
    fullScanButton_1place.bind('<Leave>',fullScanButton_1_Leave)

    #--------------------Full_Scan End ----------------#

    #--------------------Deep_Scan --------------------#

    global deepScanButton_1
    global deepScanButton_1_Hoved

    deepScanButton_1 = PhotoImage(file='res\\Scan Frame\\Non-Hoved\\Deep Scan.png').subsample(2,2)
    deepScanButton_1_Hoved = PhotoImage(file='res\\Scan Frame\\Hoved\\Deep Scan.png').subsample(2,2)

    def deepScanButton_1_Enter(e):
        deepScanButton_1place.config(image=deepScanButton_1_Hoved)
    
    def deepScanButton_1_Leave(e):
        deepScanButton_1place.config(image=deepScanButton_1)

    def start_deep_scan(e):
        """Start a full system scan"""
        # Create scan window
        scan_window = Toplevel(window)
        scan_window.title("BitLink Deep Scan")
        scan_window.geometry("800x600")
        scan_window.configure(bg=COLORS['bg_dark'])
        
        # Progress frame
        progress_frame = Frame(scan_window, bg=COLORS['bg_dark'], height=200)
        progress_frame.pack(fill=X, padx=20, pady=20)
        
        # Status labels
        status_label = Label(progress_frame, text="Scanning system...", font=("Helvetica", 14, "bold"),
                            bg=COLORS['bg_dark'], fg=COLORS['text'])
        status_label.pack(pady=10)
        
        files_label = Label(progress_frame, text="Files scanned: 0", font=("Helvetica", 12),
                           bg=COLORS['bg_dark'], fg=COLORS['text'])
        files_label.pack(pady=5)
        
        threats_label = Label(progress_frame, text="Threats found: 0", font=("Helvetica", 12),
                             bg=COLORS['bg_dark'], fg=COLORS['text'])
        threats_label.pack(pady=5)
        
        # Results frame
        results_frame = Frame(scan_window, bg=COLORS['bg_dark'])
        results_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Create text widget for results
        results_text = Text(results_frame, font=("Helvetica", 10), bg=COLORS['bg_lighter'],
                           fg=COLORS['text'], wrap=WORD)
        results_text.pack(fill=BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=VERTICAL, command=results_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        results_text.configure(yscrollcommand=scrollbar.set)
        
        # Button frame
        button_frame = Frame(scan_window, bg=COLORS['bg_dark'])
        button_frame.pack(fill=X, padx=20, pady=10)
        
        # Stop button
        stop_button = Label(button_frame, text="Stop Scan", font=("Helvetica", 12, "bold"),
                           bg=COLORS['bg_lighter'], fg=COLORS['text'],
                           padx=20, pady=8, cursor="hand2")
        stop_button.pack(side=RIGHT, padx=5)
        create_hover_effect(stop_button, COLORS['bg_lighter'], COLORS['accent'])
        
        def update_scan_status(data):
            """Update scan window with current status"""
            if data['type'] == 'progress':
                files_label.config(text=f"Files scanned: {data['files_scanned']}")
                threats_label.config(text=f"Threats found: {data['threats_found']}")
            
            elif data['type'] in ['threat', 'duplicate']:
                results_text.insert(END, f"\n{'='*50}\n")
                if data['type'] == 'threat':
                    results_text.insert(END, f"POTENTIAL THREAT FOUND:\n{data['path']}\n")
                    results_text.insert(END, f"Reason: {data['reason']}\n")
                else:
                    results_text.insert(END, "DUPLICATE FILES FOUND:\n")
                    for path in data['paths']:
                        results_text.insert(END, f"{path}\n")
                results_text.see(END)
            
            elif data['type'] == 'complete':
                status_label.config(text="Scan Complete!")
                stop_button.config(text="Close")
            
            elif data['type'] == 'error':
                results_text.insert(END, f"\nERROR: {data['message']}\n")
                results_text.see(END)
        
        def stop_scan(event=None):
            """Stop the scan and close window"""
            if scanner.scan_running:
                scanner.stop_scan()
            else:
                scan_window.destroy()
        
        stop_button.bind('<Button-1>', stop_scan)
        
        # Start the scan
        drives = [d for d in range(65, 91) if os.path.exists(chr(d) + ':')]
        scan_paths = [chr(d) + ':\\' for d in drives]
        scanner.start_scan(scan_paths, update_scan_status)

    deepScanButton_1place = Label(content_frame,image=deepScanButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    deepScanButton_1place.place(x=510,y=310)

    deepScanButton_1place.bind('<Enter>',deepScanButton_1_Enter)
    deepScanButton_1place.bind('<Leave>',deepScanButton_1_Leave)
    deepScanButton_1place.bind('<Button-1>', start_deep_scan)

    #--------------------Deep_Scan End ----------------#

    #--------------------Custom_Scan --------------------#

    global CustomScanButton_1
    global CustomScanButton_1_Hoved

    CustomScanButton_1 = PhotoImage(file='res\\Scan Frame\\Non-Hoved\\Custom Scan.png').subsample(2,2)
    CustomScanButton_1_Hoved = PhotoImage(file='res\\Scan Frame\\Hoved\\Custom Scan.png').subsample(2,2)

    def CustomScanButton_1_Enter(e):
        CustomScanButton_1place.config(image=CustomScanButton_1_Hoved)
    
    def CustomScanButton_1_Leave(e):
        CustomScanButton_1place.config(image=CustomScanButton_1)

    CustomScanButton_1place = Label(content_frame,image=CustomScanButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    CustomScanButton_1place.place(x=530,y=380)

    CustomScanButton_1place.bind('<Enter>',CustomScanButton_1_Enter)
    CustomScanButton_1place.bind('<Leave>',CustomScanButton_1_Leave)

    #--------------------Custom_Scan End ----------------#

    #--------------------Main Logo ----------------------#

    global scanFrameMainLogo
    global scanFrameMainLogoHoved
    scanFrameMainLogo = PhotoImage(file='res\\Scan Frame\\main logo.png')
    scanFrameMainLogoHoved = PhotoImage(file='res\\Scan Frame\\main logo hoved.png')

    def scanFrameMainLogoEnter(event):
        scanFrameMainLogoPlace.config(image=scanFrameMainLogoHoved)
    
    def scanFrameMainLogoLeave(event):
        scanFrameMainLogoPlace.config(image=scanFrameMainLogo)

    
    scanFrameMainLogoPlace = Label(content_frame,image=scanFrameMainLogo,bg=COLORS['bg_dark'], cursor="hand2")
    scanFrameMainLogoPlace.place(x=772,y=100)

    scanFrameMainLogoPlace.bind('<Enter>',scanFrameMainLogoEnter)
    scanFrameMainLogoPlace.bind('<Leave>',scanFrameMainLogoLeave)

    #--------------------Main Logo End-------------------#

    #--------------------Home Button --------------------#

    homeButtonImg = PhotoImage(file="res\\Home Frame\\Non-Hoved\\Home.png")
    hovHomeButtonImg = PhotoImage(file="res\\Home Frame\\Hoved\\Home.png")

    def HomeButtonEnterFrame(event):
        homeButton.config(image=hovHomeButtonImg)

    def HomeButtonLeaveFrame(event):
        homeButton.config(image=homeButtonImg)
    
    def HomeButtonCall(event):
        HomeFrame()

    homeButton = Label(content_frame,image=homeButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    homeButton.place(x=155,y=570)

    homeButton.bind('<Enter>',HomeButtonEnterFrame)
    homeButton.bind('<Leave>',HomeButtonLeaveFrame)
    homeButton.bind('<Button-1>',HomeButtonCall)


    #--------------------Home Button End------------------#

    #--------------------Scan Button ---------------------#

    scanButtonImg = PhotoImage(file="res\\Scan Frame\\Current\\Scan.png")


    scanButton = Label(content_frame,image=scanButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    scanButton.place(x=335,y=570)

    # #--------------------Scan Button End------------------#

    # #--------------------System Button -------------------#

    systemButtonImg = PhotoImage(file="res\\System Frame\\Non-Hoved\\System.png")
    hovsystemButtonImg = PhotoImage(file="res\\System Frame\\Hoved\\System.png")

    def SystemButtonEnterFrame(event):
        systemButton.config(image=hovsystemButtonImg)

    def SystemButtonLeaveFrame(event):
        systemButton.config(image=systemButtonImg)

    def SystemButtonCall(event):
        SystemFrame()


    systemButton = Label(content_frame,image=systemButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    systemButton.place(x=515,y=570)

    systemButton.bind('<Enter>',SystemButtonEnterFrame)
    systemButton.bind('<Leave>',SystemButtonLeaveFrame)
    systemButton.bind('<Button-1>',SystemButtonCall)

    # #--------------------System Button End ---------------#

    #--------------------Web Button -----------------#

    webButtonImg = PhotoImage(file="res\\Web Frame\\Non-Hoved\\Web.png")
    hovWebButtonImg = PhotoImage(file="res\\Web Frame\\Hoved\\Web.png")

    def WebButtonEnterFrame(event):
        webButton.config(image=hovWebButtonImg)

    def WebButtonLeaveFrame(event):
        webButton.config(image=webButtonImg)

    def WebButtonCall(event):
        WebFrame()


    webButton = Label(content_frame,image=webButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    webButton.place(x=695,y=570)

    webButton.bind('<Enter>',WebButtonEnterFrame)
    webButton.bind('<Leave>',WebButtonLeaveFrame)
    webButton.bind('<Button-1>',WebButtonCall)

    #--------------------Web Button End -------------#

    # #--------------------Tools Button -----------------#

    toolsButtonImg = PhotoImage(file="res\\Tools Frame\\Non-Hoved\\Tools.png")
    hovToolsButtonImg = PhotoImage(file="res\\Tools Frame\\Hoved\\Tools.png")

    def ToolsButtonEnterFrame(event):
        toolsButton.config(image=hovToolsButtonImg)

    def ToolsButtonLeaveFrame(event):
        toolsButton.config(image=toolsButtonImg)

    def ToolsButtonCall(event):
        ToolsFrame()


    toolsButton = Label(content_frame,image=toolsButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    toolsButton.place(x=875,y=570)

    toolsButton.bind('<Enter>',ToolsButtonEnterFrame)
    toolsButton.bind('<Leave>',ToolsButtonLeaveFrame)
    toolsButton.bind('<Button-1>',ToolsButtonCall)

    # #--------------------Tools Button End -------------#

    create_back_button(content_frame)

scanner = SystemScanner()

def start_deep_scan(event=None):
    """Start a full system scan"""
    # Create scan window
    scan_window = Toplevel(window)
    scan_window.title("BitLink Deep Scan")
    scan_window.geometry("800x600")
    scan_window.configure(bg=COLORS['bg_dark'])
    
    # Progress frame
    progress_frame = Frame(scan_window, bg=COLORS['bg_dark'], height=200)
    progress_frame.pack(fill=X, padx=20, pady=20)
    
    # Status labels
    status_label = Label(progress_frame, text="Scanning system...", font=("Helvetica", 14, "bold"),
                        bg=COLORS['bg_dark'], fg=COLORS['text'])
    status_label.pack(pady=10)
    
    files_label = Label(progress_frame, text="Files scanned: 0", font=("Helvetica", 12),
                       bg=COLORS['bg_dark'], fg=COLORS['text'])
    files_label.pack(pady=5)
    
    threats_label = Label(progress_frame, text="Threats found: 0", font=("Helvetica", 12),
                         bg=COLORS['bg_dark'], fg=COLORS['text'])
    threats_label.pack(pady=5)
    
    # Results frame
    results_frame = Frame(scan_window, bg=COLORS['bg_dark'])
    results_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
    
    # Create text widget for results
    results_text = Text(results_frame, font=("Helvetica", 10), bg=COLORS['bg_lighter'],
                       fg=COLORS['text'], wrap=WORD)
    results_text.pack(fill=BOTH, expand=True)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(results_frame, orient=VERTICAL, command=results_text.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    results_text.configure(yscrollcommand=scrollbar.set)
    
    # Button frame
    button_frame = Frame(scan_window, bg=COLORS['bg_dark'])
    button_frame.pack(fill=X, padx=20, pady=10)
    
    # Stop button
    stop_button = Label(button_frame, text="Stop Scan", font=("Helvetica", 12, "bold"),
                       bg=COLORS['bg_lighter'], fg=COLORS['text'],
                       padx=20, pady=8, cursor="hand2")
    stop_button.pack(side=RIGHT, padx=5)
    create_hover_effect(stop_button, COLORS['bg_lighter'], COLORS['accent'])
    
    def update_scan_status(data):
        """Update scan window with current status"""
        if data['type'] == 'progress':
            files_label.config(text=f"Files scanned: {data['files_scanned']}")
            threats_label.config(text=f"Threats found: {data['threats_found']}")
        
        elif data['type'] in ['threat', 'duplicate']:
            results_text.insert(END, f"\n{'='*50}\n")
            if data['type'] == 'threat':
                results_text.insert(END, f"POTENTIAL THREAT FOUND:\n{data['path']}\n")
                results_text.insert(END, f"Reason: {data['reason']}\n")
            else:
                results_text.insert(END, "DUPLICATE FILES FOUND:\n")
                for path in data['paths']:
                    results_text.insert(END, f"{path}\n")
            results_text.see(END)
        
        elif data['type'] == 'complete':
            status_label.config(text="Scan Complete!")
            stop_button.config(text="Close")
        
        elif data['type'] == 'error':
            results_text.insert(END, f"\nERROR: {data['message']}\n")
            results_text.see(END)
    
    def stop_scan(event=None):
        """Stop the scan and close window"""
        if scanner.scan_running:
            scanner.stop_scan()
        else:
            scan_window.destroy()
    
    stop_button.bind('<Button-1>', stop_scan)
    
    # Start the scan
    drives = [d for d in range(65, 91) if os.path.exists(chr(d) + ':')]
    scan_paths = [chr(d) + ':\\' for d in drives]
    scanner.start_scan(scan_paths, update_scan_status)

def start_smart_scan(event=None):
    """Start a smart scan of critical system areas"""
    # Create scan window
    scan_window = Toplevel(window)
    scan_window.title("BitLink Smart Scan")
    scan_window.geometry("800x600")
    scan_window.configure(bg=COLORS['bg_dark'])
    
    # Progress frame
    progress_frame = Frame(scan_window, bg=COLORS['bg_dark'], height=200)
    progress_frame.pack(fill=X, padx=20, pady=20)
    
    # Status labels
    status_label = Label(progress_frame, text="Smart Scan in Progress...", font=("Helvetica", 14, "bold"),
                        bg=COLORS['bg_dark'], fg=COLORS['text'])
    status_label.pack(pady=10)
    
    files_label = Label(progress_frame, text="Files scanned: 0", font=("Helvetica", 12),
                       bg=COLORS['bg_dark'], fg=COLORS['text'])
    files_label.pack(pady=5)
    
    threats_label = Label(progress_frame, text="Threats found: 0", font=("Helvetica", 12),
                         bg=COLORS['bg_dark'], fg=COLORS['text'])
    threats_label.pack(pady=5)
    
    # Results frame
    results_frame = Frame(scan_window, bg=COLORS['bg_dark'])
    results_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
    
    # Create text widget for results
    results_text = Text(results_frame, font=("Helvetica", 10), bg=COLORS['bg_lighter'],
                       fg=COLORS['text'], wrap=WORD)
    results_text.pack(fill=BOTH, expand=True)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(results_frame, orient=VERTICAL, command=results_text.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    results_text.configure(yscrollcommand=scrollbar.set)
    
    # Button frame
    button_frame = Frame(scan_window, bg=COLORS['bg_dark'])
    button_frame.pack(fill=X, padx=20, pady=10)
    
    # Stop button
    stop_button = Label(button_frame, text="Stop Scan", font=("Helvetica", 12, "bold"),
                       bg=COLORS['bg_lighter'], fg=COLORS['text'],
                       padx=20, pady=8, cursor="hand2")
    stop_button.pack(side=RIGHT, padx=5)
    create_hover_effect(stop_button, COLORS['bg_lighter'], COLORS['accent'])
    
    def update_scan_status(data):
        """Update scan window with current status"""
        if data['type'] == 'progress':
            files_label.config(text=f"Files scanned: {data['files_scanned']}")
            threats_label.config(text=f"Threats found: {data['threats_found']}")
        
        elif data['type'] in ['threat', 'duplicate']:
            results_text.insert(END, f"\n{'='*50}\n")
            if data['type'] == 'threat':
                results_text.insert(END, f"POTENTIAL THREAT FOUND:\n{data['path']}\n")
                results_text.insert(END, f"Reason: {data['reason']}\n")
            else:
                results_text.insert(END, "DUPLICATE FILES FOUND:\n")
                for path in data['paths']:
                    results_text.insert(END, f"{path}\n")
            results_text.see(END)
        
        elif data['type'] == 'complete':
            status_label.config(text="Smart Scan Complete!")
            stop_button.config(text="Close")
        
        elif data['type'] == 'error':
            results_text.insert(END, f"\nERROR: {data['message']}\n")
            results_text.see(END)
    
    def stop_scan(event=None):
        """Stop the scan and close window"""
        if scanner.scan_running:
            scanner.stop_scan()
        else:
            scan_window.destroy()
    
    stop_button.bind('<Button-1>', stop_scan)
    
    # Start the scan
    scanner.smart_scan(update_scan_status)

def SystemFrame():
    global winFrame
    winFrame = winFrame
    
    # Clear existing content
    for widget in winFrame.winfo_children():
        widget.destroy()
    
    # Create main container with modern layout
    main_container = Frame(winFrame, bg=COLORS['bg_dark'])
    main_container.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Header section with gradient effect
    header = Frame(main_container, bg=COLORS['bg_darker'], height=120)
    header.pack(fill=X, pady=(0, 20))
    
    # Logo and title container
    logo_container = Frame(header, bg=COLORS['bg_darker'])
    logo_container.pack(side=LEFT, padx=20, pady=10)
    
    global logoLabelImg
    logoLabelImg = PhotoImage(file='res\\Logo\\logo.png')
    logoLabel = Label(logo_container, image=logoLabelImg, bg=COLORS['bg_darker'])
    logoLabel.pack(side=LEFT, padx=(0, 15))
    
    # Title with modern typography
    title_container = Frame(logo_container, bg=COLORS['bg_darker'])
    title_container.pack(side=LEFT)
    
    Label(title_container, text="BitLink", font=("Helvetica", 28, "bold"), 
          bg=COLORS['bg_darker'], fg=COLORS['accent']).pack(anchor=W)
    Label(title_container, text="Antivirus Pro", font=("Helvetica", 16), 
          bg=COLORS['bg_darker'], fg=COLORS['text']).pack(anchor=W)
    
    # Status section with animation
    status_frame = Frame(main_container, bg=COLORS['bg_lighter'])
    status_frame.pack(fill=X, padx=50, pady=(0, 30))
    
    # Status header
    status_header = Frame(status_frame, bg=COLORS['bg_lighter'])
    status_header.pack(fill=X, padx=20, pady=(15, 5))
    
    Label(status_header, text="SYSTEM STATUS", font=("Helvetica", 12), 
          bg=COLORS['bg_lighter'], fg=COLORS['text']).pack(side=LEFT)
    
    # Status indicator with pulse animation
    status_indicator = Frame(status_frame, bg=COLORS['bg_lighter'])
    status_indicator.pack(fill=X, padx=20, pady=(0, 15))
    
    status_dot = Label(status_indicator, text="●", font=("Helvetica", 16), 
                      bg=COLORS['bg_lighter'], fg=COLORS['success'])
    status_dot.pack(side=LEFT, padx=(0, 10))
    
    Label(status_indicator, text="Protected", font=("Helvetica", 16, "bold"), 
          bg=COLORS['bg_lighter'], fg=COLORS['success']).pack(side=LEFT)
    
    # Add pulse animation to status dot
    def pulse_animation():
        current_color = status_dot.cget("fg")
        next_color = COLORS['bg_lighter'] if current_color == COLORS['success'] else COLORS['success']
        status_dot.configure(fg=next_color)
        window.after(1000, pulse_animation)
    
    pulse_animation()
    
    # Content area with card-like sections
    content_frame = Frame(main_container, bg=COLORS['bg_dark'])
    content_frame.pack(fill=BOTH, expand=True, padx=50, pady=(0, 30))
    
    # Quick actions section
    quick_actions = Frame(content_frame, bg=COLORS['bg_lighter'])
    quick_actions.pack(fill=X, pady=(0, 20))
    
    Label(quick_actions, text="QUICK ACTIONS", font=("Helvetica", 12), 
          bg=COLORS['bg_lighter'], fg=COLORS['text']).pack(anchor=W, padx=20, pady=10)
    
    # Navigation buttons with modern styling
    button_frame = Frame(main_container, bg=COLORS['bg_dark'])
    button_frame.pack(fill=X, padx=50, pady=(0, 30))
    
    # Footer
    footer_frame = Frame(main_container, bg=COLORS['bg_darker'])
    footer_frame.pack(fill=X, side=BOTTOM)
    
    global footerImg
    footerImg = PhotoImage(file='res\\footer.png')
    footerLabel = Label(footer_frame, image=footerImg, bg=COLORS['bg_darker'])
    footerLabel.pack(pady=10)

    #--------------------Logo Frame End ----------------#

    #--------------------Protection --------------------#

    global protectionButton_1
    global protectionButton_1_Hoved

    protectionButton_1 = PhotoImage(file='res\\System Frame\\Non-Hoved\\protection.png').subsample(2,2)
    protectionButton_1_Hoved = PhotoImage(file='res\\System Frame\\Hoved\\protection.png').subsample(2,2)

    def protectionButton_1_Enter(e):
        protectionButton_1place.config(image=protectionButton_1_Hoved)
    
    def protectionButton_1_Leave(e):
        protectionButton_1place.config(image=protectionButton_1)

    protectionButton_1place = Label(content_frame,image=protectionButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    protectionButton_1place.place(x=530,y=100)

    protectionButton_1place.bind('<Enter>',protectionButton_1_Enter)
    protectionButton_1place.bind('<Leave>',protectionButton_1_Leave)

    #--------------------Protection End ----------------#   

    #--------------------Firewall --------------------#

    global firewallButton_1
    global firewallButton_1_Hoved

    firewallButton_1 = PhotoImage(file='res\\System Frame\\Non-Hoved\\firewall.png').subsample(2,2)
    firewallButton_1_Hoved = PhotoImage(file='res\\System Frame\\Hoved\\firewall.png').subsample(2,2)

    def firewallButton_1_Enter(e):
        firewallButton_1place.config(image=firewallButton_1_Hoved)
    
    def firewallButton_1_Leave(e):
        firewallButton_1place.config(image=firewallButton_1)

    firewallButton_1place = Label(content_frame,image=firewallButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    firewallButton_1place.place(x=510,y=170)

    firewallButton_1place.bind('<Enter>',firewallButton_1_Enter)
    firewallButton_1place.bind('<Leave>',firewallButton_1_Leave)

    #--------------------Firewall End ----------------#  

    #--------------------System Health --------------------#

    global systemHealthButton_1
    global systemHealthButton_1_Hoved

    systemHealthButton_1 = PhotoImage(file='res\\System Frame\\Non-Hoved\\system health.png').subsample(2,2)
    systemHealthButton_1_Hoved = PhotoImage(file='res\\System Frame\\Hoved\\system health.png').subsample(2,2)

    def systemHealthButton_1_Enter(e):
        systemHealthButton_1place.config(image=systemHealthButton_1_Hoved)
    
    def systemHealthButton_1_Leave(e):
        systemHealthButton_1place.config(image=systemHealthButton_1)

    systemHealthButton_1place = Label(content_frame,image=systemHealthButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    systemHealthButton_1place.place(x=510,y=240)

    systemHealthButton_1place.bind('<Enter>',systemHealthButton_1_Enter)
    systemHealthButton_1place.bind('<Leave>',systemHealthButton_1_Leave)

    #--------------------System Health End ----------------#  

    #--------------------System Report --------------------#

    global systemReportButton_1
    global systemReportButton_1_Hoved

    systemReportButton_1 = PhotoImage(file='res\\System Frame\\Non-Hoved\\system report.png').subsample(2,2)
    systemReportButton_1_Hoved = PhotoImage(file='res\\System Frame\\Hoved\\system report.png').subsample(2,2)

    def systemReportButton_1_Enter(e):
        systemReportButton_1place.config(image=systemReportButton_1_Hoved)
    
    def systemReportButton_1_Leave(e):
        systemReportButton_1place.config(image=systemReportButton_1)

    systemReportButton_1place = Label(content_frame,image=systemReportButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    systemReportButton_1place.place(x=530,y=310)

    systemReportButton_1place.bind('<Enter>',systemReportButton_1_Enter)
    systemReportButton_1place.bind('<Leave>',systemReportButton_1_Leave)

    #--------------------System Report End ----------------#  


    #--------------------Main Logo ----------------------#

    global systemFrameMainLogo
    global systemFrameMainLogoHoved
    systemFrameMainLogo = PhotoImage(file='res\\System Frame\\main frame logo.png')
    systemFrameMainLogoHoved = PhotoImage(file='res\\System Frame\\main frame logo hoved.png')

    def systemFrameMainLogoEnter(event):
        systemFrameMainLogoPlace.config(image=systemFrameMainLogoHoved)
    
    def systemFrameMainLogoLeave(event):
        systemFrameMainLogoPlace.config(image=systemFrameMainLogo)

    
    systemFrameMainLogoPlace = Label(content_frame,image=systemFrameMainLogo,bg=COLORS['bg_dark'])
    systemFrameMainLogoPlace.place(x=772,y=100)

    systemFrameMainLogoPlace.bind('<Enter>',systemFrameMainLogoEnter)
    systemFrameMainLogoPlace.bind('<Leave>',systemFrameMainLogoLeave)


    #--------------------Main Logo End-------------------#

    #--------------------Home Button --------------------#

    homeButtonImg = PhotoImage(file="res\\Home Frame\\Non-Hoved\\Home.png")
    hovHomeButtonImg = PhotoImage(file="res\\Home Frame\\Hoved\\Home.png")

    def HomeButtonEnterFrame(event):
        homeButton.config(image=hovHomeButtonImg)

    def HomeButtonLeaveFrame(event):
        homeButton.config(image=homeButtonImg)
    
    def HomeButtonCall(event):
        HomeFrame()

    homeButton = Label(content_frame,image=homeButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    homeButton.place(x=155,y=570)

    homeButton.bind('<Enter>',HomeButtonEnterFrame)
    homeButton.bind('<Leave>',HomeButtonLeaveFrame)
    homeButton.bind('<Button-1>',HomeButtonCall)


    #--------------------Home Button End------------------#

    #--------------------Scan Button ---------------------#

    scanButtonImg = PhotoImage(file="res\\Scan Frame\\Non-Hoved\\Scan.png")
    hovScanButtonImg = PhotoImage(file="res\\Scan Frame\\Hoved\\Scan.png")
    def ScanButtonEnterFrame(event):
        scanButton.config(image=hovScanButtonImg)

    def ScanButtonLeaveFrame(event):
        scanButton.config(image=scanButtonImg)
    
    def ScanButtonCall(event):
        ScanFrame()


    scanButton = Label(content_frame,image=scanButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    scanButton.place(x=335,y=570)

    scanButton.bind('<Enter>',ScanButtonEnterFrame)
    scanButton.bind('<Leave>',ScanButtonLeaveFrame)
    scanButton.bind('<Button-1>',ScanButtonCall)

    # #--------------------Scan Button End------------------#

    # #--------------------System Button -------------------#

    systemButtonImg = PhotoImage(file="res\\System Frame\\Non-Hoved\\System.png")
    hovsystemButtonImg = PhotoImage(file="res\\System Frame\\Hoved\\System.png")

    def SystemButtonEnterFrame(event):
        systemButton.config(image=hovsystemButtonImg)

    def SystemButtonLeaveFrame(event):
        systemButton.config(image=systemButtonImg)

    def SystemButtonCall(event):
        SystemFrame()


    systemButton = Label(content_frame,image=systemButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    systemButton.place(x=515,y=570)

    systemButton.bind('<Enter>',SystemButtonEnterFrame)
    systemButton.bind('<Leave>',SystemButtonLeaveFrame)
    systemButton.bind('<Button-1>',SystemButtonCall)

    # #--------------------System Button End ---------------#

    #--------------------Web Button -----------------#

    webButtonImg = PhotoImage(file="res\\Web Frame\\Non-Hoved\\Web.png")
    hovWebButtonImg = PhotoImage(file="res\\Web Frame\\Hoved\\Web.png")

    def WebButtonEnterFrame(event):
        webButton.config(image=hovWebButtonImg)

    def WebButtonLeaveFrame(event):
        webButton.config(image=webButtonImg)

    def WebButtonCall(event):
        WebFrame()


    webButton = Label(content_frame,image=webButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    webButton.place(x=695,y=570)

    webButton.bind('<Enter>',WebButtonEnterFrame)
    webButton.bind('<Leave>',WebButtonLeaveFrame)
    webButton.bind('<Button-1>',WebButtonCall)

    #--------------------Web Button End -------------#

    # #--------------------Tools Button -----------------#

    toolsButtonImg = PhotoImage(file="res\\Tools Frame\\Non-Hoved\\Tools.png")
    hovToolsButtonImg = PhotoImage(file="res\\Tools Frame\\Hoved\\Tools.png")

    def ToolsButtonEnterFrame(event):
        toolsButton.config(image=hovToolsButtonImg)

    def ToolsButtonLeaveFrame(event):
        toolsButton.config(image=toolsButtonImg)

    def ToolsButtonCall(event):
        ToolsFrame()


    toolsButton = Label(content_frame,image=toolsButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    toolsButton.place(x=875,y=570)

    toolsButton.bind('<Enter>',ToolsButtonEnterFrame)
    toolsButton.bind('<Leave>',ToolsButtonLeaveFrame)
    toolsButton.bind('<Button-1>',ToolsButtonCall)

    # #--------------------Tools Button End -------------#

    create_back_button(content_frame)

##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################

def WebFrame():
    global winFrame
    winFrame = winFrame
    
    # Clear existing content
    for widget in winFrame.winfo_children():
        widget.destroy()
    
    # Create main container with modern layout
    main_container = Frame(winFrame, bg=COLORS['bg_dark'])
    main_container.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Header section with gradient effect
    header = Frame(main_container, bg=COLORS['bg_darker'], height=120)
    header.pack(fill=X, pady=(0, 20))
    
    # Logo and title container
    logo_container = Frame(header, bg=COLORS['bg_darker'])
    logo_container.pack(side=LEFT, padx=20, pady=10)
    
    global logoLabelImg
    logoLabelImg = PhotoImage(file='res\\Logo\\logo.png')
    logoLabel = Label(logo_container, image=logoLabelImg, bg=COLORS['bg_darker'])
    logoLabel.pack(side=LEFT, padx=(0, 15))
    
    # Title with modern typography
    title_container = Frame(logo_container, bg=COLORS['bg_darker'])
    title_container.pack(side=LEFT)
    
    Label(title_container, text="BitLink", font=("Helvetica", 28, "bold"), 
          bg=COLORS['bg_darker'], fg=COLORS['accent']).pack(anchor=W)
    Label(title_container, text="Antivirus Pro", font=("Helvetica", 16), 
          bg=COLORS['bg_darker'], fg=COLORS['text']).pack(anchor=W)
    
    # Status section with animation
    status_frame = Frame(main_container, bg=COLORS['bg_lighter'])
    status_frame.pack(fill=X, padx=50, pady=(0, 30))
    
    # Status header
    status_header = Frame(status_frame, bg=COLORS['bg_lighter'])
    status_header.pack(fill=X, padx=20, pady=(15, 5))
    
    Label(status_header, text="SYSTEM STATUS", font=("Helvetica", 12), 
          bg=COLORS['bg_lighter'], fg=COLORS['text']).pack(side=LEFT)
    
    # Status indicator with pulse animation
    status_indicator = Frame(status_frame, bg=COLORS['bg_lighter'])
    status_indicator.pack(fill=X, padx=20, pady=(0, 15))
    
    status_dot = Label(status_indicator, text="●", font=("Helvetica", 16), 
                      bg=COLORS['bg_lighter'], fg=COLORS['success'])
    status_dot.pack(side=LEFT, padx=(0, 10))
    
    Label(status_indicator, text="Protected", font=("Helvetica", 16, "bold"), 
          bg=COLORS['bg_lighter'], fg=COLORS['success']).pack(side=LEFT)
    
    # Add pulse animation to status dot
    def pulse_animation():
        current_color = status_dot.cget("fg")
        next_color = COLORS['bg_lighter'] if current_color == COLORS['success'] else COLORS['success']
        status_dot.configure(fg=next_color)
        window.after(1000, pulse_animation)
    
    pulse_animation()
    
    # Content area with card-like sections
    content_frame = Frame(main_container, bg=COLORS['bg_dark'])
    content_frame.pack(fill=BOTH, expand=True, padx=50, pady=(0, 30))
    
    # Quick actions section
    quick_actions = Frame(content_frame, bg=COLORS['bg_lighter'])
    quick_actions.pack(fill=X, pady=(0, 20))
    
    Label(quick_actions, text="QUICK ACTIONS", font=("Helvetica", 12), 
          bg=COLORS['bg_lighter'], fg=COLORS['text']).pack(anchor=W, padx=20, pady=10)
    
    # Navigation buttons with modern styling
    button_frame = Frame(main_container, bg=COLORS['bg_dark'])
    button_frame.pack(fill=X, padx=50, pady=(0, 30))
    
    # Footer
    footer_frame = Frame(main_container, bg=COLORS['bg_darker'])
    footer_frame.pack(fill=X, side=BOTTOM)
    
    global footerImg
    footerImg = PhotoImage(file='res\\footer.png')
    footerLabel = Label(footer_frame, image=footerImg, bg=COLORS['bg_darker'])
    footerLabel.pack(pady=10)

    #--------------------Logo Frame End ----------------#

    #--------------------web shield --------------------#

    global webShieldButton_1
    global webShieldButton_1_Hoved

    webShieldButton_1 = PhotoImage(file='res\\Web Frame\\Non-Hoved\\web shield.png').subsample(2,2)
    webShieldButton_1_Hoved = PhotoImage(file='res\\Web Frame\\Hoved\\web shield.png').subsample(2,2)

    def webShieldButton_1_Enter(e):
        webShieldButton_1place.config(image=webShieldButton_1_Hoved)
    
    def webShieldButton_1_Leave(e):
        webShieldButton_1place.config(image=webShieldButton_1)

    webShieldButton_1place = Label(content_frame,image=webShieldButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    webShieldButton_1place.place(x=530,y=100)

    webShieldButton_1place.bind('<Enter>',webShieldButton_1_Enter)
    webShieldButton_1place.bind('<Leave>',webShieldButton_1_Leave)

    #--------------------web shield End ----------------# 

    #--------------------Child Safty --------------------#

    global childSaftyButton_1
    global childSaftyButton_1_Hoved

    childSaftyButton_1 = PhotoImage(file='res\\Web Frame\\Non-Hoved\\chield safty.png').subsample(2,2)
    childSaftyButton_1_Hoved = PhotoImage(file='res\\Web Frame\\Hoved\\child safty.png').subsample(2,2)

    def childSaftyButton_1_Enter(e):
        childSaftyButton_1place.config(image=childSaftyButton_1_Hoved)
    
    def childSaftyButton_1_Leave(e):
        childSaftyButton_1place.config(image=childSaftyButton_1)

    childSaftyButton_1place = Label(content_frame,image=childSaftyButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    childSaftyButton_1place.place(x=510,y=170)

    childSaftyButton_1place.bind('<Enter>',childSaftyButton_1_Enter)
    childSaftyButton_1place.bind('<Leave>',childSaftyButton_1_Leave)

    #--------------------Child Safty End ----------------#

    #--------------------Content Filter --------------------#

    global contentFilterButton_1
    global contentFilterButton_1_Hoved

    contentFilterButton_1 = PhotoImage(file='res\\Web Frame\\Non-Hoved\\content filter.png').subsample(2,2)
    contentFilterButton_1_Hoved = PhotoImage(file='res\\Web Frame\\Hoved\\content filter.png').subsample(2,2)

    def contentFilterButton_1_Enter(e):
        contentFilterButton_1place.config(image=contentFilterButton_1_Hoved)
    
    def contentFilterButton_1_Leave(e):
        contentFilterButton_1place.config(image=contentFilterButton_1)

    contentFilterButton_1place = Label(content_frame,image=contentFilterButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    contentFilterButton_1place.place(x=510,y=240)

    contentFilterButton_1place.bind('<Enter>',contentFilterButton_1_Enter)
    contentFilterButton_1place.bind('<Leave>',contentFilterButton_1_Leave)

    #--------------------Content Filter End ----------------#

    #--------------------Web Report --------------------#

    global webReportButton_1
    global webReportButton_1_Hoved

    webReportButton_1 = PhotoImage(file='res\\Web Frame\\Non-Hoved\\web report.png').subsample(2,2)
    webReportButton_1_Hoved = PhotoImage(file='res\\Web Frame\\Hoved\\web report.png').subsample(2,2)

    def webReportButton_1_Enter(e):
        webReportButton_1place.config(image=webReportButton_1_Hoved)
    
    def webReportButton_1_Leave(e):
        webReportButton_1place.config(image=webReportButton_1)

    webReportButton_1place = Label(content_frame,image=webReportButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    webReportButton_1place.place(x=530,y=310)

    webReportButton_1place.bind('<Enter>',webReportButton_1_Enter)
    webReportButton_1place.bind('<Leave>',webReportButton_1_Leave)

    #--------------------Web Report End ----------------# 

    #--------------------Main Logo ----------------------#

    global webFrameMainLogo
    global webFrameMainLogoHoved
    webFrameMainLogo = PhotoImage(file='res\\Web Frame\\main frame logo.png')
    webFrameMainLogoHoved = PhotoImage(file='res\\Web Frame\\main frame logo hoved.png')

    def webFrameMainLogoEnter(event):
        webFrameMainLogoPlace.config(image=webFrameMainLogoHoved)
    
    def webFrameMainLogoLeave(event):
        webFrameMainLogoPlace.config(image=webFrameMainLogo)

    
    webFrameMainLogoPlace = Label(content_frame,image=webFrameMainLogo,bg=COLORS['bg_dark'])
    webFrameMainLogoPlace.place(x=772,y=100)

    webFrameMainLogoPlace.bind('<Enter>',webFrameMainLogoEnter)
    webFrameMainLogoPlace.bind('<Leave>',webFrameMainLogoLeave)


    #--------------------Main Logo End-------------------#

    #--------------------Home Button --------------------#

    homeButtonImg = PhotoImage(file="res\\Home Frame\\Non-Hoved\\Home.png")
    hovHomeButtonImg = PhotoImage(file="res\\Home Frame\\Hoved\\Home.png")

    def HomeButtonEnterFrame(event):
        homeButton.config(image=hovHomeButtonImg)

    def HomeButtonLeaveFrame(event):
        homeButton.config(image=homeButtonImg)
    
    def HomeButtonCall(event):
        HomeFrame()

    homeButton = Label(content_frame,image=homeButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    homeButton.place(x=155,y=570)

    homeButton.bind('<Enter>',HomeButtonEnterFrame)
    homeButton.bind('<Leave>',HomeButtonLeaveFrame)
    homeButton.bind('<Button-1>',HomeButtonCall)


    #--------------------Home Button End------------------#

    #--------------------Scan Button ---------------------#

    scanButtonImg = PhotoImage(file="res\\Scan Frame\\Non-Hoved\\Scan.png")
    hovScanButtonImg = PhotoImage(file="res\\Scan Frame\\Hoved\\Scan.png")
    def ScanButtonEnterFrame(event):
        scanButton.config(image=hovScanButtonImg)

    def ScanButtonLeaveFrame(event):
        scanButton.config(image=scanButtonImg)
    
    def ScanButtonCall(event):
        ScanFrame()


    scanButton = Label(content_frame,image=scanButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    scanButton.place(x=335,y=570)

    scanButton.bind('<Enter>',ScanButtonEnterFrame)
    scanButton.bind('<Leave>',ScanButtonLeaveFrame)
    scanButton.bind('<Button-1>',ScanButtonCall)

    # #--------------------Scan Button End------------------#

    # #--------------------System Button -------------------#

    systemButtonImg = PhotoImage(file="res\\System Frame\\Non-Hoved\\System.png")
    hovsystemButtonImg = PhotoImage(file="res\\System Frame\\Hoved\\System.png")

    def SystemButtonEnterFrame(event):
        systemButton.config(image=hovsystemButtonImg)

    def SystemButtonLeaveFrame(event):
        systemButton.config(image=systemButtonImg)

    def SystemButtonCall(event):
        SystemFrame()


    systemButton = Label(content_frame,image=systemButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    systemButton.place(x=515,y=570)

    systemButton.bind('<Enter>',SystemButtonEnterFrame)
    systemButton.bind('<Leave>',SystemButtonLeaveFrame)
    systemButton.bind('<Button-1>',SystemButtonCall)

    # #--------------------System Button End ---------------#

    #--------------------Web Button -----------------#

    webButtonImg = PhotoImage(file="res\\Web Frame\\Non-Hoved\\Web.png")
    hovWebButtonImg = PhotoImage(file="res\\Web Frame\\Hoved\\Web.png")

    def WebButtonEnterFrame(event):
        webButton.config(image=hovWebButtonImg)

    def WebButtonLeaveFrame(event):
        webButton.config(image=webButtonImg)

    def WebButtonCall(event):
        WebFrame()


    webButton = Label(content_frame,image=webButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    webButton.place(x=695,y=570)

    webButton.bind('<Enter>',WebButtonEnterFrame)
    webButton.bind('<Leave>',WebButtonLeaveFrame)
    webButton.bind('<Button-1>',WebButtonCall)

    #--------------------Web Button End -------------#

    # #--------------------Tools Button -----------------#

    toolsButtonImg = PhotoImage(file="res\\Tools Frame\\Non-Hoved\\Tools.png")
    hovToolsButtonImg = PhotoImage(file="res\\Tools Frame\\Hoved\\Tools.png")

    def ToolsButtonEnterFrame(event):
        toolsButton.config(image=hovToolsButtonImg)

    def ToolsButtonLeaveFrame(event):
        toolsButton.config(image=toolsButtonImg)

    def ToolsButtonCall(event):
        ToolsFrame()


    toolsButton = Label(content_frame,image=toolsButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    toolsButton.place(x=875,y=570)

    toolsButton.bind('<Enter>',ToolsButtonEnterFrame)
    toolsButton.bind('<Leave>',ToolsButtonLeaveFrame)
    toolsButton.bind('<Button-1>',ToolsButtonCall)

    # #--------------------Tools Button End -------------#

    create_back_button(content_frame)

##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################

def ToolsFrame():
    global winFrame
    winFrame = winFrame
    
    # Clear existing content
    for widget in winFrame.winfo_children():
        widget.destroy()
    
    # Create main container with modern layout
    main_container = Frame(winFrame, bg=COLORS['bg_dark'])
    main_container.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Header section with gradient effect
    header = Frame(main_container, bg=COLORS['bg_darker'], height=120)
    header.pack(fill=X, pady=(0, 20))
    
    # Logo and title container
    logo_container = Frame(header, bg=COLORS['bg_darker'])
    logo_container.pack(side=LEFT, padx=20, pady=10)
    
    global logoLabelImg
    logoLabelImg = PhotoImage(file='res\\Logo\\logo.png')
    logoLabel = Label(logo_container, image=logoLabelImg, bg=COLORS['bg_darker'])
    logoLabel.pack(side=LEFT, padx=(0, 15))
    
    # Title with modern typography
    title_container = Frame(logo_container, bg=COLORS['bg_darker'])
    title_container.pack(side=LEFT)
    
    Label(title_container, text="BitLink", font=("Helvetica", 28, "bold"), 
          bg=COLORS['bg_darker'], fg=COLORS['accent']).pack(anchor=W)
    Label(title_container, text="Antivirus Pro", font=("Helvetica", 16), 
          bg=COLORS['bg_darker'], fg=COLORS['text']).pack(anchor=W)
    
    # Status section with animation
    status_frame = Frame(main_container, bg=COLORS['bg_lighter'])
    status_frame.pack(fill=X, padx=50, pady=(0, 30))
    
    # Status header
    status_header = Frame(status_frame, bg=COLORS['bg_lighter'])
    status_header.pack(fill=X, padx=20, pady=(15, 5))
    
    Label(status_header, text="SYSTEM STATUS", font=("Helvetica", 12), 
          bg=COLORS['bg_lighter'], fg=COLORS['text']).pack(side=LEFT)
    
    # Status indicator with pulse animation
    status_indicator = Frame(status_frame, bg=COLORS['bg_lighter'])
    status_indicator.pack(fill=X, padx=20, pady=(0, 15))
    
    status_dot = Label(status_indicator, text="●", font=("Helvetica", 16), 
                      bg=COLORS['bg_lighter'], fg=COLORS['success'])
    status_dot.pack(side=LEFT, padx=(0, 10))
    
    Label(status_indicator, text="Protected", font=("Helvetica", 16, "bold"), 
          bg=COLORS['bg_lighter'], fg=COLORS['success']).pack(side=LEFT)
    
    # Add pulse animation to status dot
    def pulse_animation():
        current_color = status_dot.cget("fg")
        next_color = COLORS['bg_lighter'] if current_color == COLORS['success'] else COLORS['success']
        status_dot.configure(fg=next_color)
        window.after(1000, pulse_animation)
    
    pulse_animation()
    
    # Content area with card-like sections
    content_frame = Frame(main_container, bg=COLORS['bg_dark'])
    content_frame.pack(fill=BOTH, expand=True, padx=50, pady=(0, 30))
    
    # Quick actions section
    quick_actions = Frame(content_frame, bg=COLORS['bg_lighter'])
    quick_actions.pack(fill=X, pady=(0, 20))
    
    Label(quick_actions, text="QUICK ACTIONS", font=("Helvetica", 12), 
          bg=COLORS['bg_lighter'], fg=COLORS['text']).pack(anchor=W, padx=20, pady=10)
    
    # Navigation buttons with modern styling
    button_frame = Frame(main_container, bg=COLORS['bg_dark'])
    button_frame.pack(fill=X, padx=50, pady=(0, 30))
    
    # Footer
    footer_frame = Frame(main_container, bg=COLORS['bg_darker'])
    footer_frame.pack(fill=X, side=BOTTOM)
    
    global footerImg
    footerImg = PhotoImage(file='res\\footer.png')
    footerLabel = Label(footer_frame, image=footerImg, bg=COLORS['bg_darker'])
    footerLabel.pack(pady=10)

    #--------------------Logo Frame End ----------------#

    #--------------------Driver Update --------------------#

    global driverUpdateButton_1
    global driverUpdateButton_1_Hoved

    driverUpdateButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\driver update.png').subsample(2,2)
    driverUpdateButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\driver update.png').subsample(2,2)

    def driverUpdateButton_1_Enter(e):
        driverUpdateButton_1place.config(image=driverUpdateButton_1_Hoved)
    
    def driverUpdateButton_1_Leave(e):
        driverUpdateButton_1place.config(image=driverUpdateButton_1)

    driverUpdateButton_1place = Label(content_frame,image=driverUpdateButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    driverUpdateButton_1place.place(x=510,y=160)

    driverUpdateButton_1place.bind('<Enter>',driverUpdateButton_1_Enter)
    driverUpdateButton_1place.bind('<Leave>',driverUpdateButton_1_Leave)

    #--------------------Driver Update End ----------------# 

    #--------------------Proxy --------------------#

    global proxyButton_1
    global proxyButton_1_Hoved

    proxyButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\proxy.png').subsample(2,2)
    proxyButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\proxy.png').subsample(2,2)

    def proxyButton_1_Enter(e):
        proxyButton_1place.config(image=proxyButton_1_Hoved)
    
    def proxyButton_1_Leave(e):
        proxyButton_1place.config(image=proxyButton_1)

    proxyButton_1place = Label(content_frame,image=proxyButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    proxyButton_1place.place(x=510,y=220)

    proxyButton_1place.bind('<Enter>',proxyButton_1_Enter)
    proxyButton_1place.bind('<Leave>',proxyButton_1_Leave)

    #--------------------Proxy End ----------------#

    #--------------------Cache Cleaner --------------------#

    global cacheCleanerButton_1
    global cacheCleanerButton_1_Hoved

    cacheCleanerButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\cache cleaner.png').subsample(2,2)
    cacheCleanerButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\cache cleaner.png').subsample(2,2)

    def cacheCleanerButton_1_Enter(e):
        cacheCleanerButton_1place.config(image=cacheCleanerButton_1_Hoved)
    
    def cacheCleanerButton_1_Leave(e):
        cacheCleanerButton_1place.config(image=cacheCleanerButton_1)

    cacheCleanerButton_1place = Label(content_frame,image=cacheCleanerButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    cacheCleanerButton_1place.place(x=510,y=280)

    cacheCleanerButton_1place.bind('<Enter>',cacheCleanerButton_1_Enter)
    cacheCleanerButton_1place.bind('<Leave>',cacheCleanerButton_1_Leave)

    #--------------------Cache Cleaner End ----------------#

    #--------------------Web Blocker --------------------#

    global webBlockerButton_1
    global webBlockerButton_1_Hoved

    webBlockerButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\web blocker.png').subsample(2,2)
    webBlockerButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\web blocker.png').subsample(2,2)

    def webBlockerButton_1_Enter(e):
        webBlockerButton_1place.config(image=webBlockerButton_1_Hoved)
    
    def webBlockerButton_1_Leave(e):
        webBlockerButton_1place.config(image=webBlockerButton_1)

    webBlockerButton_1place = Label(content_frame,image=webBlockerButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    webBlockerButton_1place.place(x=530,y=340)

    webBlockerButton_1place.bind('<Enter>',webBlockerButton_1_Enter)
    webBlockerButton_1place.bind('<Leave>',webBlockerButton_1_Leave)

    #--------------------Web Blocker End ----------------#

    #--------------------History Clean --------------------#

    global historyCleanButton_1
    global historyCleanButton_1_Hoved

    historyCleanButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\history clean.png').subsample(2,2)
    historyCleanButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\history clean.png').subsample(2,2)

    def historyCleanButton_1_Enter(e):
        historyCleanButton_1place.config(image=historyCleanButton_1_Hoved)
    
    def historyCleanButton_1_Leave(e):
        historyCleanButton_1place.config(image=historyCleanButton_1)

    historyCleanButton_1place = Label(content_frame,image=historyCleanButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    historyCleanButton_1place.place(x=300,y=100)

    historyCleanButton_1place.bind('<Enter>',historyCleanButton_1_Enter)
    historyCleanButton_1place.bind('<Leave>',historyCleanButton_1_Leave)

    #--------------------History Clean End ----------------#

    #--------------------File Recovery --------------------#

    global fileRecoveryButton_1
    global fileRecoveryButton_1_Hoved

    fileRecoveryButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\file recovery.png').subsample(2,2)
    fileRecoveryButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\file recovery.png').subsample(2,2)

    def fileRecoveryButton_1_Enter(e):
        fileRecoveryButton_1place.config(image=fileRecoveryButton_1_Hoved)
    
    def fileRecoveryButton_1_Leave(e):
        fileRecoveryButton_1place.config(image=fileRecoveryButton_1)

    fileRecoveryButton_1place = Label(content_frame,image=fileRecoveryButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    fileRecoveryButton_1place.place(x=280,y=160)

    fileRecoveryButton_1place.bind('<Enter>',fileRecoveryButton_1_Enter)
    fileRecoveryButton_1place.bind('<Leave>',fileRecoveryButton_1_Leave)

    #--------------------File Recovery End ----------------#

    #--------------------Web Checker --------------------#

    global webCheckerButton_1
    global webCheckerButton_1_Hoved

    webCheckerButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\web checker.png').subsample(2,2)
    webCheckerButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\web checker.png').subsample(2,2)

    def webCheckerButton_1_Enter(e):
        webCheckerButton_1place.config(image=webCheckerButton_1_Hoved)
    
    def webCheckerButton_1_Leave(e):
        webCheckerButton_1place.config(image=webCheckerButton_1)

    webCheckerButton_1place = Label(content_frame,image=webCheckerButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    webCheckerButton_1place.place(x=280,y=220)

    webCheckerButton_1place.bind('<Enter>',webCheckerButton_1_Enter)
    webCheckerButton_1place.bind('<Leave>',webCheckerButton_1_Leave)

    #--------------------Web Checker End ----------------#

    #--------------------Help --------------------#

    global helpButton_1
    global helpButton_1_Hoved

    helpButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\help.png').subsample(2,2)
    helpButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\help.png').subsample(2,2)

    def helpButton_1_Enter(e):
        helpButton_1place.config(image=helpButton_1_Hoved)
    
    def helpButton_1_Leave(e):
        helpButton_1place.config(image=helpButton_1)

    helpButton_1place = Label(content_frame,image=helpButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    helpButton_1place.place(x=280,y=280)

    helpButton_1place.bind('<Enter>',helpButton_1_Enter)
    helpButton_1place.bind('<Leave>',helpButton_1_Leave)

    #--------------------Help End ----------------#

    #--------------------About --------------------#

    global aboutButton_1
    global aboutButton_1_Hoved

    aboutButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\about.png').subsample(2,2)
    aboutButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\about.png').subsample(2,2)

    def aboutButton_1_Enter(e):
        aboutButton_1place.config(image=aboutButton_1_Hoved)
    
    def aboutButton_1_Leave(e):
        aboutButton_1place.config(image=aboutButton_1)

    aboutButton_1place = Label(content_frame,image=aboutButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    aboutButton_1place.place(x=300,y=340)

    aboutButton_1place.bind('<Enter>',aboutButton_1_Enter)
    aboutButton_1place.bind('<Leave>',aboutButton_1_Leave)

    #--------------------About End ----------------#

    #--------------------File Vault --------------------#

    global fileVaultButton_1
    global fileVaultButton_1_Hoved

    fileVaultButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\file vault.png').subsample(2,2)
    fileVaultButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\file vault.png').subsample(2,2)

    def fileVaultButton_1_Enter(e):
        fileVaultButton_1place.config(image=fileVaultButton_1_Hoved)
    
    def fileVaultButton_1_Leave(e):
        fileVaultButton_1place.config(image=fileVaultButton_1)

    fileVaultButton_1place = Label(content_frame,image=fileVaultButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    fileVaultButton_1place.place(x=80,y=100)

    fileVaultButton_1place.bind('<Enter>',fileVaultButton_1_Enter)
    fileVaultButton_1place.bind('<Leave>',fileVaultButton_1_Leave)

    #--------------------File Vault End ----------------# 

    #--------------------Auto Silent --------------------#

    global autoSilentButton_1
    global autoSilentButton_1_Hoved

    autoSilentButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\auto silent.png').subsample(2,2)
    autoSilentButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\auto silent.png').subsample(2,2)

    def autoSilentButton_1_Enter(e):
        autoSilentButton_1place.config(image=autoSilentButton_1_Hoved)
    
    def autoSilentButton_1_Leave(e):
        autoSilentButton_1place.config(image=autoSilentButton_1)

    autoSilentButton_1place = Label(content_frame,image=autoSilentButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    autoSilentButton_1place.place(x=60,y=160)

    autoSilentButton_1place.bind('<Enter>',autoSilentButton_1_Enter)
    autoSilentButton_1place.bind('<Leave>',autoSilentButton_1_Leave)

    #--------------------Auto Silent End ----------------#

    #--------------------Game Booster --------------------#

    global gameBoosterButton_1
    global gameBoosterButton_1_Hoved

    gameBoosterButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\game booster.png').subsample(2,2)
    gameBoosterButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\game booster.png').subsample(2,2)

    def gameBoosterButton_1_Enter(e):
        gameBoosterButton_1place.config(image=gameBoosterButton_1_Hoved)
    
    def gameBoosterButton_1_Leave(e):
        gameBoosterButton_1place.config(image=gameBoosterButton_1)

    gameBoosterButton_1place = Label(content_frame,image=gameBoosterButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    gameBoosterButton_1place.place(x=60,y=220)

    gameBoosterButton_1place.bind('<Enter>',gameBoosterButton_1_Enter)
    gameBoosterButton_1place.bind('<Leave>',gameBoosterButton_1_Leave)

    #--------------------Game Booster End ----------------#

    #--------------------PC Tuner --------------------#

    global PC_TunnerButton_1
    global PC_TunnerButton_1_Hoved

    PC_TunnerButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\pc tuner.png').subsample(2,2)
    PC_TunnerButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\pc tuner.png').subsample(2,2)

    def PC_TunnerButton_1_Enter(e):
        PC_TunnerButton_1place.config(image=PC_TunnerButton_1_Hoved)
    
    def PC_TunnerButton_1_Leave(e):
        PC_TunnerButton_1place.config(image=PC_TunnerButton_1)

    PC_TunnerButton_1place = Label(content_frame,image=PC_TunnerButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    PC_TunnerButton_1place.place(x=60,y=280)

    PC_TunnerButton_1place.bind('<Enter>',PC_TunnerButton_1_Enter)
    PC_TunnerButton_1place.bind('<Leave>',PC_TunnerButton_1_Leave)

    #--------------------PC Tuner End ----------------#

    #--------------------Parental Mode --------------------#

    global parentalModeButton_1
    global parentalModeButton_1_Hoved

    parentalModeButton_1 = PhotoImage(file='res\\Tools Frame\\Non-Hoved\\parental mode.png').subsample(2,2)
    parentalModeButton_1_Hoved = PhotoImage(file='res\\Tools Frame\\Hoved\\parental mode.png').subsample(2,2)

    def parentalModeButton_1_Enter(e):
        parentalModeButton_1place.config(image=parentalModeButton_1_Hoved)
    
    def parentalModeButton_1_Leave(e):
        parentalModeButton_1place.config(image=parentalModeButton_1)

    parentalModeButton_1place = Label(content_frame,image=parentalModeButton_1,bg=COLORS['bg_dark'], cursor="hand2")
    parentalModeButton_1place.place(x=80,y=340)

    parentalModeButton_1place.bind('<Enter>',parentalModeButton_1_Enter)
    parentalModeButton_1place.bind('<Leave>',parentalModeButton_1_Leave)

    #--------------------Parental Mode End ----------------#

    #--------------------Main Logo ----------------------#

    global toolsFrameMainLogo
    global toolsFrameMainLogoHoved
    toolsFrameMainLogo = PhotoImage(file='res\\Tools Frame\\main frame logo.png')
    toolsFrameMainLogoHoved = PhotoImage(file='res\\Tools Frame\\main frame logo hoved.png')

    def toolsFrameMainLogoEnter(event):
        toolsFrameMainLogoPlace.config(image=toolsFrameMainLogoHoved)
    
    def toolsFrameMainLogoLeave(event):
        toolsFrameMainLogoPlace.config(image=toolsFrameMainLogo)

    
    toolsFrameMainLogoPlace = Label(content_frame,image=toolsFrameMainLogo,bg=COLORS['bg_dark'])
    toolsFrameMainLogoPlace.place(x=772,y=100)

    toolsFrameMainLogoPlace.bind('<Enter>',toolsFrameMainLogoEnter)
    toolsFrameMainLogoPlace.bind('<Leave>',toolsFrameMainLogoLeave)


    #--------------------Main Logo End---------------------#

    #--------------------Home Button --------------------#
    
    homeButtonImg = PhotoImage(file="res\\Home Frame\\Non-Hoved\\Home.png")
    hovHomeButtonImg = PhotoImage(file="res\\Home Frame\\Hoved\\Home.png")

    def HomeButtonEnterFrame(event):
        homeButton.config(image=hovHomeButtonImg)

    def HomeButtonLeaveFrame(event):
        homeButton.config(image=homeButtonImg)
    
    def HomeButtonCall(event):
        HomeFrame()

    homeButton = Label(content_frame,image=homeButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    homeButton.place(x=155,y=570)

    homeButton.bind('<Enter>',HomeButtonEnterFrame)
    homeButton.bind('<Leave>',HomeButtonLeaveFrame)
    homeButton.bind('<Button-1>',HomeButtonCall)

    #--------------------Home Button End------------------#

    #--------------------Scan Button ---------------------#

    scanButtonImg = PhotoImage(file="res\\Scan Frame\\Non-Hoved\\Scan.png")
    hovScanButtonImg = PhotoImage(file="res\\Scan Frame\\Hoved\\Scan.png")
    def ScanButtonEnterFrame(event):
        scanButton.config(image=hovScanButtonImg)

    def ScanButtonLeaveFrame(event):
        scanButton.config(image=scanButtonImg)
    
    def ScanButtonCall(event):
        ScanFrame()


    scanButton = Label(content_frame,image=scanButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    scanButton.place(x=335,y=570)

    scanButton.bind('<Enter>',ScanButtonEnterFrame)
    scanButton.bind('<Leave>',ScanButtonLeaveFrame)
    scanButton.bind('<Button-1>',ScanButtonCall)

    # #--------------------Scan Button End------------------#

    # #--------------------System Button -------------------#

    systemButtonImg = PhotoImage(file="res\\System Frame\\Non-Hoved\\System.png")
    hovsystemButtonImg = PhotoImage(file="res\\System Frame\\Hoved\\System.png")

    def SystemButtonEnterFrame(event):
        systemButton.config(image=hovsystemButtonImg)

    def SystemButtonLeaveFrame(event):
        systemButton.config(image=systemButtonImg)

    def SystemButtonCall(event):
        SystemFrame()


    systemButton = Label(content_frame,image=systemButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    systemButton.place(x=515,y=570)

    systemButton.bind('<Enter>',SystemButtonEnterFrame)
    systemButton.bind('<Leave>',SystemButtonLeaveFrame)
    systemButton.bind('<Button-1>',SystemButtonCall)

    # #--------------------System Button End ---------------#

    #--------------------Web Button -----------------#

    webButtonImg = PhotoImage(file="res\\Web Frame\\Non-Hoved\\Web.png")
    hovWebButtonImg = PhotoImage(file="res\\Web Frame\\Hoved\\Web.png")

    def WebButtonEnterFrame(event):
        webButton.config(image=hovWebButtonImg)

    def WebButtonLeaveFrame(event):
        webButton.config(image=webButtonImg)

    def WebButtonCall(event):
        WebFrame()


    webButton = Label(content_frame,image=webButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    webButton.place(x=695,y=570)

    webButton.bind('<Enter>',WebButtonEnterFrame)
    webButton.bind('<Leave>',WebButtonLeaveFrame)
    webButton.bind('<Button-1>',WebButtonCall)

    #--------------------Web Button End -------------#

    # #--------------------Tools Button -----------------#

    global toolsButtonImg
    toolsButtonImg = PhotoImage(file="res\\Tools Frame\\Current\\Tools.png")


    toolsButton = Label(content_frame,image=toolsButtonImg,bg=COLORS['bg_dark'],cursor="hand2")
    toolsButton.place(x=875,y=570)

    # #--------------------Tools Button End -------------#

    create_back_button(content_frame)

def ProxyFrame():
        #--------------------Global Var --------------------#  
    global winFrame
    

    #--------------------Global Var End -----------------# 

    winFrame.destroy()



    #--------------------Main Frame ---------------------# 

    winFrame = winFrame

    #--------------------Main Frame End ------------------# 

    #--------------------Footer Frame --------------------#

    global footerImg
    footerImg = PhotoImage(file='res\\footer.png')

    footerLabel = Label(winFrame,image=footerImg,bg=COLORS['bg_dark'])
    footerLabel.place(x=310,y=773)

    #--------------------Footer Frame End ----------------#

    #--------------------Logo Frame start --------------#

    global logoLabelImg
    logoLabelImg = PhotoImage(file='res\\Logo\\logo.png')
    logoLabel = Label(winFrame,image=logoLabelImg,bg=COLORS['bg_dark'])
    logoLabel.place(x=10,y=0)

    global nameLabelImg
    nameLabelImg = PhotoImage(file='res\\Logo\\b logo.png').subsample(2,2)
    nameLabel = Label(winFrame,image=nameLabelImg,bg=COLORS['bg_dark'])
    nameLabel.place(x=90,y=20)
    #--------------------Logo Frame End ----------------#

    #--------------------Back Logo --------------#

    global backbtnlogo
    global backbtnlogoHov

    backbtnlogo = PhotoImage(file='res\\Common Element\\Non-Hoved\\back btn.png').subsample(6,6)
    backbtnlogoLabel = Label(winFrame,image=backbtnlogo,bg=COLORS['bg_dark'],cursor="hand2")
    backbtnlogoLabel.place(x=90,y=120)

    #--------------------Back Logo End --------------#


#--------------------Navigation Functions--------------------#
def navigate_to_home():
    clear_frame()
    HomeFrame()

def navigate_to_scan():
    clear_frame()
    ScanFrame()

def navigate_to_system():
    clear_frame()
    SystemFrame()

def navigate_to_web():
    clear_frame()
    WebFrame()

def navigate_to_tools():
    clear_frame()
    ToolsFrame()

def navigate_to_proxy():
    clear_frame()
    ProxyFrame()

HomeFrame()

window.after(100, lambda: window.deiconify())
window.after(200, lambda: window.attributes('-topmost', True))
window.after(300, lambda: window.attributes('-topmost', False))
window.overrideredirect(True)
window.mainloop()