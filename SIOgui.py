#!/usr/bin/env python3

from guizero import App, TextBox, Text, PushButton, CheckBox, Box
from subprocess import call, Popen

def startprocess():
    print("starting process")
    spraytime = str(float(stime.value)/1000)
    plungedelay = str(float(pdelay.value)/1000)
    arguments = ["python","SIOapplyandplunge.py","--stime",spraytime,"--pdelay",plungedelay]
    if donotplunge.value==1:
        arguments.append("--donotplunge")
    call(arguments)
    button_start.disable()
    
def powerup():
    print("Power up")
    arguments = ["python","SIOpowerupdown.py","--updown","up"]
    call(arguments)
    button_start.enable()
    
def powerdown():
    print("Power down")
    arguments = ["python","SIOpowerupdown.py","--updown","down"]
    call(arguments)
    button_start.disable()
    
def cleanprocess():
    print("starting clean process")
    spraytime  = str(float(cleantime.value)/1000)
    cycles = cleancycles.value
    arguments = ["python","SIOclean.py","--stime",spraytime,"--cycles",cycles]
    Popen(arguments)

palette = {
    "bg": "#0b1220",
    "panel": "#111827",
    "muted": "#94a3b8",
    "text": "#e5e7eb",
    "accent": "#22c55e",
    "warn": "#f59e0b",
    "danger": "#ef4444"
}

app = App(
    title="Shake-it-off Control",
    layout="grid",
    width=760,
    height=420,
    bg=palette["bg"]
)
app.tk.configure(padx=18, pady=18)

header = Text(app, text="Shake-it-off", grid=[0,0,2,1], size=20, color=palette["accent"], font="Segoe UI Semibold")
subhead = Text(
    app,
    text="Ergonomic control for spray, plunge, and cleaning cycles",
    grid=[0,1,2,1],
    size=10,
    color=palette["muted"],
    font="Segoe UI"
)

control_card = Box(app, layout="grid", grid=[0,2], width=440, height=260)
control_card.bg = palette["panel"]
control_card.tk.configure(padx=14, pady=14)

run_title = Text(control_card, text="Run Cycle", grid=[0,0,2,1], size=13, color=palette["text"], font="Segoe UI Semibold")
run_hint = Text(control_card, text="Adjust timings, power up, then start.", grid=[0,1,2,1], size=9, color=palette["muted"], font="Segoe UI")

stimelabel  = Text(control_card, text="Spray time (ms)", grid=[0,2], color=palette["text"], font="Segoe UI")
stime       = TextBox(control_card, grid=[1,2], text="5", width=10)
stime.text_color = palette["text"]
pdelaylabel = Text(control_card, text="Plunge delay (ms)", grid=[0,3], color=palette["text"], font="Segoe UI")
pdelay      = TextBox(control_card, grid=[1,3], text="5", width=10)
pdelay.text_color = palette["text"]
donotplunge = CheckBox(control_card, text="Do not plunge", grid=[0,4,2,1])
donotplunge.text_color = palette["text"]
donotplunge.font = "Segoe UI"

button_up   = PushButton(control_card, command=powerup, text="Ready", grid=[0,5], width=12)
button_down = PushButton(control_card, command=powerdown, text="Abort", grid=[1,5], width=12)
button_start= PushButton(control_card, command=startprocess, text="Spray & Plunge", grid=[0,6,2,1], width=24)

button_up.bg = palette["accent"]
button_up.text_color = palette["bg"]
button_down.bg = palette["warn"]
button_down.text_color = palette["bg"]
button_start.bg = palette["danger"]
button_start.text_color = palette["bg"]
button_start.disable()

clean_card = Box(app, layout="grid", grid=[1,2], width=260, height=260)
clean_card.bg = palette["panel"]
clean_card.tk.configure(padx=14, pady=14)

clean_title = Text(clean_card, text="Cleaning", grid=[0,0,2,1], size=13, color=palette["text"], font="Segoe UI Semibold")
clean_hint = Text(clean_card, text="Define pulse and cycles, then run.", grid=[0,1,2,1], size=9, color=palette["muted"], font="Segoe UI")

cleancycleslabel = Text(clean_card, text="Cleaning cycles", grid=[0,2], color=palette["text"], font="Segoe UI")
cleancycles      = TextBox(clean_card, text="5", grid=[1,2], width=10)
cleancycles.text_color = palette["text"]
cleantimelabel   = Text(clean_card, text="Cleaning pulse (ms)", grid=[0,3], color=palette["text"], font="Segoe UI")
cleantime        = TextBox(clean_card, text="200", grid=[1,3], width=10)
cleantime.text_color = palette["text"]
clean            = PushButton(clean_card, command=cleanprocess, text="Clean", grid=[0,4,2,1], width=18)

clean.bg = palette["accent"]
clean.text_color = palette["bg"]

app.display()
