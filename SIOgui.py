#!/usr/bin/env python3

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
from subprocess import call, Popen
from datetime import datetime
from threading import Thread

# Set window size for 1280x720 touchscreen
Window.size = (1280, 720)

# Color palette
COLORS = {
    "bg": (0.04, 0.07, 0.13, 1),         # #0b1220
    "panel": (0.07, 0.09, 0.15, 1),      # #111827
    "muted": (0.58, 0.64, 0.72, 1),      # #94a3b8
    "text": (0.90, 0.91, 0.92, 1),       # #e5e7eb
    "accent": (0.13, 0.77, 0.37, 1),     # #22c55e
    "warn": (0.96, 0.62, 0.04, 1),       # #f59e0b
    "danger": (0.94, 0.27, 0.27, 1),     # #ef4444
}


class NumericInputRow(BoxLayout):
    """Custom widget for numeric input with +/- buttons"""
    def __init__(self, label_text, default_value="5", step=1, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 70
        self.spacing = 10
        self.step = step
        
        # Label
        label = Label(
            text=label_text,
            color=COLORS["text"],
            font_size='18sp',
            size_hint_x=0.4,
            halign='left',
            valign='middle'
        )
        label.bind(size=label.setter('text_size'))
        
        # Minus button
        self.minus_btn = Button(
            text='-',
            font_size='28sp',
            size_hint_x=0.15,
            background_color=COLORS["muted"],
            background_normal=''
        )
        self.minus_btn.bind(on_press=self.decrement)
        
        # Text input
        self.text_input = TextInput(
            text=default_value,
            multiline=False,
            font_size='22sp',
            size_hint_x=0.3,
            background_color=COLORS["panel"],
            foreground_color=COLORS["text"],
            padding=[5, 8, 5, 8],
            halign='center',
            input_filter='int'
        )
        
        # Plus button
        self.plus_btn = Button(
            text='+',
            font_size='28sp',
            size_hint_x=0.15,
            background_color=COLORS["muted"],
            background_normal=''
        )
        self.plus_btn.bind(on_press=self.increment)
        
        self.add_widget(label)
        self.add_widget(self.minus_btn)
        self.add_widget(self.text_input)
        self.add_widget(self.plus_btn)
    
    def increment(self, instance):
        try:
            current = int(self.text_input.text)
            self.text_input.text = str(current + self.step)
        except ValueError:
            self.text_input.text = str(self.step)
    
    def decrement(self, instance):
        try:
            current = int(self.text_input.text)
            new_value = max(0, current - self.step)
            self.text_input.text = str(new_value)
        except ValueError:
            self.text_input.text = "0"
    
    def get_value(self):
        return self.text_input.text


class ControlPanel(BoxLayout):
    """Main control panel widget"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 25
        self.spacing = 15
        self.terminal = None  # Will be set by main app
        
        # Add background color
        with self.canvas.before:
            Color(*COLORS["panel"])
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Title
        title = Label(
            text='Run Cycle',
            color=COLORS["text"],
            font_size='28sp',
            size_hint_y=None,
            height=45,
            bold=True
        )
        
        # Subtitle
        subtitle = Label(
            text='Adjust timings, power up, then start.',
            color=COLORS["muted"],
            font_size='16sp',
            size_hint_y=None,
            height=30
        )
        
        # Spray time input
        self.spray_time = NumericInputRow('Spray time (ms)', default_value='5', step=1)
        
        # Plunge delay input
        self.plunge_delay = NumericInputRow('Plunge delay (ms)', default_value='5', step=1)
        
        # Checkbox for "do not plunge"
        checkbox_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10
        )
        self.donotplunge_check = CheckBox(
            size_hint_x=0.1,
            color=COLORS["accent"]
        )
        checkbox_label = Label(
            text='Do not plunge',
            color=COLORS["text"],
            font_size='18sp',
            size_hint_x=0.9,
            halign='left',
            valign='middle'
        )
        checkbox_label.bind(size=checkbox_label.setter('text_size'))
        checkbox_layout.add_widget(self.donotplunge_check)
        checkbox_layout.add_widget(checkbox_label)
        
        # Buttons row
        buttons_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=80,
            spacing=15
        )
        
        self.powerup_btn = Button(
            text='Ready',
            font_size='22sp',
            background_color=COLORS["accent"],
            background_normal=''
        )
        self.powerup_btn.bind(on_press=self.power_up)
        
        self.powerdown_btn = Button(
            text='Abort',
            font_size='22sp',
            background_color=COLORS["warn"],
            background_normal=''
        )
        self.powerdown_btn.bind(on_press=self.power_down)
        
        buttons_row.add_widget(self.powerup_btn)
        buttons_row.add_widget(self.powerdown_btn)
        
        # Start button
        self.start_btn = Button(
            text='Spray & Plunge',
            font_size='26sp',
            size_hint_y=None,
            height=90,
            background_color=COLORS["danger"],
            background_normal='',
            disabled=True
        )
        self.start_btn.bind(on_press=self.start_process)
        
        # Add all widgets
        self.add_widget(title)
        self.add_widget(subtitle)
        self.add_widget(self.spray_time)
        self.add_widget(self.plunge_delay)
        self.add_widget(checkbox_layout)
        self.add_widget(buttons_row)
        self.add_widget(self.start_btn)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def power_up(self, instance):
        if self.terminal:
            self.terminal.add_message('Powering up system...', 'info')
        arguments = ["python3", "SIOpowerupdown.py", "--updown", "up"]
        call(arguments)
        self.start_btn.disabled = False
        if self.terminal:
            self.terminal.add_message('System powered up', 'success')
    
    def power_down(self, instance):
        print("Power down")
        if self.terminal:
            self.terminal.add_message('Powering down system...', 'warning')
        arguments = ["python3", "SIOpowerupdown.py", "--updown", "down"]
        call(arguments)
        self.start_btn.disabled = True
        if self.terminal:
            self.terminal.add_message('System powered down', 'info')
    
    def start_process(self, instance):
        print("Starting process")
        spraytime = str(float(self.spray_time.get_value()) / 1000)
        plungedelay = str(float(self.plunge_delay.get_value()) / 1000)
        if self.terminal:
            self.terminal.add_message(f'Starting spray & plunge (spray: {spraytime}s, delay: {plungedelay}s)', 'info')
        arguments = ["python3", "SIOapplyandplunge.py", "--stime", spraytime, "--pdelay", plungedelay]
        if self.donotplunge_check.active:
            arguments.append("--donotplunge")
            if self.terminal:
                self.terminal.add_message('Plunge disabled', 'warning')
        call(arguments)
        self.start_btn.disabled = True
        if self.terminal:
            self.terminal.add_message('Process completed', 'success')


class CleaningPanel(BoxLayout):
    """Cleaning panel widget"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 25
        self.spacing = 15
        self.terminal = None  # Will be set by main app
        
        # Add background color
        with self.canvas.before:
            Color(*COLORS["panel"])
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Title
        title = Label(
            text='Cleaning',
            color=COLORS["text"],
            font_size='28sp',
            size_hint_y=None,
            height=45,
            bold=True
        )
        
        # Subtitle
        subtitle = Label(
            text='Define pulse and cycles, then run.',
            color=COLORS["muted"],
            font_size='16sp',
            size_hint_y=None,
            height=30
        )
        
        # Cleaning cycles input
        self.clean_cycles = NumericInputRow('Cleaning cycles', default_value='5', step=1)
        
        # Cleaning pulse input
        self.clean_pulse = NumericInputRow('Cleaning pulse (ms)', default_value='200', step=10)
        
        # Clean button
        self.clean_btn = Button(
            text='Clean',
            font_size='26sp',
            size_hint_y=None,
            height=90,
            background_color=COLORS["accent"],
            background_normal=''
        )
        self.clean_btn.bind(on_press=self.clean_process)
        
        # Add all widgets
        self.add_widget(title)
        self.add_widget(subtitle)
        self.add_widget(self.clean_cycles)
        self.add_widget(self.clean_pulse)
        self.add_widget(self.clean_btn)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def clean_process(self, instance):
        print("Starting clean process")
        spraytime = str(float(self.clean_pulse.get_value()) / 1000)
        cycles = self.clean_cycles.get_value()
        if self.terminal:
            self.terminal.add_message(f'Starting cleaning ({cycles} cycles, {spraytime}s pulse)', 'info')
        arguments = ["python3", "SIOclean.py", "--stime", spraytime, "--cycles", cycles]
        process = Popen(arguments)
        
        # Monitor process completion in background thread
        def wait_for_completion():
            process.wait()
            if self.terminal:
                # Schedule GUI update on main thread
                Clock.schedule_once(lambda dt: self.terminal.add_message('Cleaning process completed', 'success'), 0)
        
        Thread(target=wait_for_completion, daemon=True).start()
        
        if self.terminal:
            self.terminal.add_message('Cleaning process launched', 'success')


class TerminalBox(BoxLayout):
    """Terminal-style message display box"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 440
        self.padding = 15
        self.spacing = 10
        
        # Add background color
        with self.canvas.before:
            Color(*COLORS["bg"])
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Terminal header
        header = Label(
            text='System Messages',
            color=COLORS["accent"],
            font_size='18sp',
            size_hint_y=None,
            height=30,
            bold=True,
            halign='left',
            valign='middle'
        )
        header.bind(size=header.setter('text_size'))
        
        # Scrollable text area
        self.scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['bars', 'content'],
            bar_width=10
        )
        
        self.terminal_text = TextInput(
            text='[System ready]\n',
            readonly=True,
            font_name='RobotoMono-Regular',
            font_size='16sp',
            background_color=COLORS["bg"],
            foreground_color=COLORS["text"],
            cursor_color=(0, 0, 0, 0),  # Hide cursor
            size_hint_y=None
        )
        self.terminal_text.bind(minimum_height=self.terminal_text.setter('height'))
        
        self.scroll_view.add_widget(self.terminal_text)
        
        self.add_widget(header)
        self.add_widget(self.scroll_view)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def add_message(self, message, msg_type='info'):
        """Add a message to the terminal
        msg_type: 'info', 'success', 'warning', 'error'
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Color coding based on message type
        if msg_type == 'success':
            prefix = '[OK]'
        elif msg_type == 'warning':
            prefix = '[WARN]'
        elif msg_type == 'error':
            prefix = '[ERROR]'
        else:
            prefix = '[INFO]'
        
        formatted_msg = f'{timestamp} {prefix} {message}\n'
        self.terminal_text.text += formatted_msg
        
        # Auto-scroll to bottom - force scroll view to bottom
        self.scroll_view.scroll_y = 0
    
    def clear(self):
        """Clear all messages"""
        self.terminal_text.text = ''


class StatusIndicator(Widget):
    """Colored circle indicator"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (30, 30)
        
        with self.canvas:
            self.indicator_color = Color(*COLORS["muted"])
            self.indicator = Ellipse(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_indicator, size=self._update_indicator)
    
    def _update_indicator(self, instance, value):
        self.indicator.pos = self.pos
        self.indicator.size = self.size
    
    def set_color(self, color):
        self.indicator_color.rgba = color


class StatusBar(BoxLayout):
    """Status indicator bar for device status"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 70
        self.padding = 20
        self.spacing = 30
        
        # Add background color
        with self.canvas.before:
            Color(*COLORS["panel"])
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Status label
        status_label = Label(
            text='Status:',
            color=COLORS["text"],
            font_size='20sp',
            size_hint_x=0.15,
            bold=True,
            halign='left',
            valign='middle'
        )
        status_label.bind(size=status_label.setter('text_size'))
        
        # Cryostat interlock indicator
        cryostat_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_x=0.4)
        self.cryostat_indicator = StatusIndicator()
        cryostat_label = Label(
            text='Cryostat Interlock',
            color=COLORS["text"],
            font_size='18sp',
            halign='left',
            valign='middle'
        )
        cryostat_label.bind(size=cryostat_label.setter('text_size'))
        cryostat_layout.add_widget(self.cryostat_indicator)
        cryostat_layout.add_widget(cryostat_label)
        
        # Plunger position indicator
        plunger_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint_x=0.4)
        self.plunger_indicator = StatusIndicator()
        plunger_label = Label(
            text='Plunger Position',
            color=COLORS["text"],
            font_size='18sp',
            halign='left',
            valign='middle'
        )
        plunger_label.bind(size=plunger_label.setter('text_size'))
        plunger_layout.add_widget(self.plunger_indicator)
        plunger_layout.add_widget(plunger_label)
        
        # Add all widgets
        self.add_widget(status_label)
        self.add_widget(cryostat_layout)
        self.add_widget(plunger_layout)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def set_cryostat_status(self, active):
        """Update cryostat interlock status - True = OK (green), False = Error (red)"""
        if active:
            self.cryostat_indicator.set_color(COLORS["accent"])
        else:
            self.cryostat_indicator.set_color(COLORS["danger"])
    
    def set_plunger_status(self, position):
        """Update plunger position - 'up' = green, 'down' = warn, 'unknown' = muted"""
        if position == 'up':
            self.plunger_indicator.set_color(COLORS["accent"])
        elif position == 'down':
            self.plunger_indicator.set_color(COLORS["warn"])
        else:
            self.plunger_indicator.set_color(COLORS["muted"])


class ShakeItOffApp(App):
    def build(self):
        # Set window background color
        Window.clearcolor = COLORS["bg"]
        
        # Main layout with proper constraints
        main_layout = BoxLayout(
            orientation='vertical', 
            padding=20, 
            spacing=15
        )
        
        # Header - fixed height
        header_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=90,
            spacing=5
        )
        
        header = Label(
            text='Shake-it-off',
            color=COLORS["accent"],
            font_size='38sp',
            size_hint_y=None,
            height=50,
            bold=True
        )
        
        subheader = Label(
            text='Ergonomic control for spray, plunge, and cleaning cycles',
            color=COLORS["muted"],
            font_size='16sp',
            size_hint_y=None,
            height=30
        )
        
        header_layout.add_widget(header)
        header_layout.add_widget(subheader)
        
        # Content layout (two panels side by side) - proportional
        content_layout = BoxLayout(
            orientation='horizontal', 
            spacing=20,
            size_hint_y=0.35
        )
        
        # Control panel
        self.control_panel = ControlPanel(size_hint_x=0.6, size_hint_y=1)
        
        # Cleaning panel
        self.cleaning_panel = CleaningPanel(size_hint_x=0.4, size_hint_y=1)
        
        # Add panels to content layout
        content_layout.add_widget(self.control_panel)
        content_layout.add_widget(self.cleaning_panel)
        
        # Terminal message box - proportional
        self.terminal = TerminalBox(size_hint_y=0.45)
        
        # Status bar at bottom - fixed height
        self.status_bar = StatusBar(size_hint_y=None, height=70)
        
        # Add to main layout in order
        main_layout.add_widget(header_layout)
        main_layout.add_widget(content_layout)
        main_layout.add_widget(self.terminal)
        main_layout.add_widget(self.status_bar)
        
        # Link terminal to panels for message logging
        self.control_panel.terminal = self.terminal
        self.cleaning_panel.terminal = self.terminal
        
        # Initial messages
        self.terminal.add_message('System initialized', 'success')
        self.terminal.add_message('Ready for operations', 'info')
        
        return main_layout


if __name__ == '__main__':
    ShakeItOffApp().run()
