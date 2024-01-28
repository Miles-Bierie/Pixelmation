#  ---------=========|  Credits: Miles Bierie  |  Developed: Monday, April 3, 2023 -- Sunday, January 28, 2024  |=========---------  #


from tkinter import colorchooser as ch
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog
from PIL import Image, ImageTk
from math import ceil, floor
from tkinter import TclError
from pygame import mixer
from tkinter import ttk
import tkinter as tk
import send2trash
import threading
import mutagen
import timeit
import uuid
import json
import copy
import time
import sys
import os

if sys.platform == 'win32':
    import winsound
    
class Operator(tk.Frame):
    copied = None
    modifier_count = 0
    
    WIDTH = 250
    HEIGHT = 297
        
    def __init__(self, parent, name, _uuid):
        # Are we renaming the modifier?
        self.renaming = False
        
        # The name/title of the widget
        self.name = name
        self.nameVar = tk.StringVar(value=self.name)
        
        # ID specific to this modifier
        self.UUID = (uuid.uuid1() if _uuid == None else _uuid)
        
        
        super().__init__(master=parent)
        
        # Basic properties
        self.config(width=self.WIDTH, height=self.HEIGHT, highlightbackground='black', highlightthickness=1)
        self.pack_propagate(False)
        
        # Is this modifier active?
        self.enabled = tk.BooleanVar(value=True)
        
        self.titleFrame = tk.Frame(self, bg='lightblue', width=self.WIDTH, height=24, highlightbackground='black', highlightthickness=1)
        self.titleFrame.pack(side=tk.TOP)
        self.titleFrame.pack_propagate(False)
        self.titleFrame.bind('<Button-1>', lambda e: self.__rename__(True))
        
        self.nameLabel = tk.Label(self.titleFrame, text=self.name, bg='lightblue')
        self.nameLabel.pack(anchor=tk.W, side=tk.LEFT)
        self.nameLabel.bind('<Double-Button-1>', lambda e: self.__rename_dialog__())
        
        # Only visible when renaming
        self.nameEntry = tk.Entry(self.titleFrame, textvariable=self.nameVar, width=32)
        self.nameEntry.bind('<Return>', lambda e: self.__rename__(True))
        self.nameEntry.bind('<FocusOut>', lambda e: self.__rename__(True))
        self.nameEntry.bind('<Escape>', lambda e: self.__rename__(False))
        
        self.enableCheck = tk.Checkbutton(self.titleFrame, variable=self.enabled, command=self.__toggle_enable__, bg='lightblue')
        self.enableCheck.pack(anchor=tk.E, side=tk.RIGHT)
        
        self.mainFrame = tk.Frame(self, width=self.WIDTH, height=self.HEIGHT-24, highlightbackground='black', highlightthickness=1)
        self.mainFrame.pack(side=tk.BOTTOM, anchor=tk.S)
        self.mainFrame.pack_propagate(False)
        self.mainFrame.bind('<Button-1>', lambda e: self.__rename__(True))
        
        for widget in self.winfo_children():
            widget.bind('<Button-3>', lambda e: self.__option_dialog__())
        
    # Shows the rename entry
    def __rename_dialog__(self):
        self.renaming = True
        self.nameLabel.pack_forget()
        
        self.nameEntry.pack(anchor=tk.W, side=tk.LEFT)
        self.nameEntry.focus()
        
    def __option_dialog__(self):
        menu = tk.Menu(tearoff=False)
        menu.add_command(label='Copy Modifier', command=lambda: self.__copy__())
        menu.add_command(label='Paste Modifier')
        menu.add_separator()
        menu.add_command(label='Delete Modifier', command=lambda m = self: m.destroy())
        menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        
    def __toggle_enable__(self):
        # Command gets run before the value gets updated, so we negate the check
        if not self.enabled.get():
            self.titleFrame.config(bg='gray')
            self.nameLabel.config(bg='gray')
            self.enableCheck.config(bg='gray')
            
            self.mainFrame.pack_forget()
            self.config(height=24)
        else:
            self.titleFrame.config(bg='lightblue')
            self.nameLabel.config(bg='lightblue')
            self.enableCheck.config(bg='lightblue')
            
            self.mainFrame.pack(side=tk.BOTTOM, anchor=tk.S)
            self.config(height=self.HEIGHT)
 
    def __copy__(self):
        Operator.copied = self.UUID
        
    def __rename__(self, rename):
        MAX_LENGTH = 37
        self.focus() # And, therefore, remove focus from the entry, incase you clicked on another Operator instance
        
        if not self.renaming:
            return

        if self.nameVar.get() == '' or not rename:
            self.nameVar.set(self.name)
        
        nameStr = self.nameVar.get().strip()

        if len(nameStr) > MAX_LENGTH:
            abbr = nameStr[:MAX_LENGTH-3]
            abbr = abbr.strip() + '...'
            self.nameLabel.config(text=abbr)
        else:
            self.nameLabel.config(text=nameStr)
        
        self.nameVar.set(nameStr)
        self.name = nameStr
        
        self.nameEntry.pack_forget()
        self.nameLabel.pack(anchor=tk.W, side=tk.LEFT)
        
        self.renaming = False


class TintOperator(Operator):
    def __init__(self, parent, name="TintOperator", _uuid=None): 
        super().__init__(parent=parent, name=name, _uuid=_uuid)
        
        self.parent = parent
        
        # What is this?
        self.type = 'TintOperator'
        
        self.tintColor = '#ffffff'
        
        self.redVar = tk.StringVar(master=self, value='255')
        self.greenVar = tk.StringVar(master=self, value='255')
        self.blueVar = tk.StringVar(master=self, value='255')
        
        # Color-picker button
        self.buttonFrame = tk.Frame(self.mainFrame, highlightbackground='white', highlightthickness=2)
        self.buttonFrame.pack(side=tk.TOP, pady=10)
        self.colorButton = tk.Button(self.buttonFrame, text='Tint', command=self.pick_color, width=26)
        self.colorButton.pack()
        
        rgbFrame = tk.Frame(self.mainFrame, highlightbackground='black', highlightthickness=2)
        rgbFrame.pack(pady=(10, 0))
        
        tk.Label(rgbFrame, text='Red:').pack(side=tk.LEFT, padx=(0, 5))
        self.redEntry = tk.Entry(rgbFrame, width=3, textvariable=self.redVar, name='red')
        self.redEntry.pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Label(rgbFrame, text='Green:').pack(side=tk.LEFT, padx=(0, 5))
        self.greenEntry = tk.Entry(rgbFrame, width=3, textvariable=self.greenVar, name='green')
        self.greenEntry.pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Label(rgbFrame, text='Blue:').pack(side=tk.LEFT, padx=(0, 5))
        self.blueEntry = tk.Entry(rgbFrame, width=3, textvariable=self.blueVar, name='blue')
        self.blueEntry.pack(side=tk.LEFT, padx=(0, 8))
        
        for widget in rgbFrame.winfo_children():
            if widget.winfo_class() == 'Entry':
                self.redVar.trace_add('write', lambda e1, e2, e3: self.manual_color())
                self.greenVar.trace_add('write', lambda e1, e2, e3: self.manual_color())
                self.blueVar.trace_add('write', lambda e1, e2, e3: self.manual_color())
        
    def pick_color(self):
        newColor = ch.askcolor(parent=self.parent, initialcolor=self.tintColor)
        if newColor:
            self.colorChooserUI = True

            self.tintColor = newColor[1]
            self.buttonFrame.config(highlightbackground=self.tintColor)
            self.update_entries(newColor[0])
            
    def manual_color(self):  
        try:
            var = self.focus_get().winfo_name()
            
            if var in ('red', 'green', 'blue'):

            # Make sure we are only typing numbers
                eval(f'self.{var}Var.set("".join(i for i in self.{var}Var.get() if i.isdigit()))')
                
                color = (int(self.redVar.get()), int(self.greenVar.get()), int(self.blueVar.get()))
                self.tintColor = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
                self.buttonFrame.config(highlightbackground=self.tintColor)
            
        # The entry is empty, or we used the color chooser
        except (ValueError, AttributeError):
            pass
        
        # The value is not a valid color value
        except TclError:
            eval(f'self.{var}Var.set(255)')
            
    def update_entries(self, rgb):
        if rgb:
            self.redVar.set(rgb[0])
            self.greenVar.set(rgb[1])
            self.blueVar.set(rgb[2])
            
class MonochromeOperator(Operator):
    def __init__(self, parent, name='MonochromeOperator', _uuid=None):
        super().__init__(parent=parent, name=name, _uuid=_uuid)
        
        self.parent = parent
        
        self.type = 'MonochromeOperator'
        
        self.redVar = tk.BooleanVar(value=True)
        self.greenVar = tk.BooleanVar(value=True)
        self.blueVar = tk.BooleanVar(value=True)
        
        self.color_1 = '#ffffff'
        self.color_2 = '#000000'
        
        checkFrame = tk.Frame(self.mainFrame, height=76, width=self.WIDTH, highlightbackground='black', highlightthickness=1)
        checkFrame.pack(side=tk.TOP, pady=(10, 0))
        checkFrame.pack_propagate(False)
        
        tk.Checkbutton(checkFrame, variable=self.redVar, text="Use Red Channel").pack(anchor=tk.W)
        tk.Checkbutton(checkFrame, variable=self.greenVar, text="Use Green Channel").pack(anchor=tk.W)
        tk.Checkbutton(checkFrame, variable=self.blueVar, text="Use Blue Channel").pack(anchor=tk.W)
        
        colorFrame = tk.Frame(self.mainFrame, height=76, width=self.WIDTH, highlightbackground='black', highlightthickness=1)
        colorFrame.pack(pady=32)
        colorFrame.pack_propagate(False)
        
        self.buttonFrame_1 = tk.Frame(colorFrame, highlightbackground='white', highlightthickness=2, name='c1')
        self.buttonFrame_1.pack(side=tk.TOP, pady=(5, 2))
        self.colorButton_1 = tk.Button(self.buttonFrame_1, text='Color 1', command=lambda: self.pick_color(self.buttonFrame_1), width=26)
        self.colorButton_1.pack()
        
        self.buttonFrame_2 = tk.Frame(colorFrame, highlightbackground='black', highlightthickness=2, name='c2')
        self.buttonFrame_2.pack(side=tk.TOP, pady=2)
        self.colorButton_2 = tk.Button(self.buttonFrame_2, text='Color 2', command=lambda: self.pick_color(self.buttonFrame_2), width=26)
        self.colorButton_2.pack()
        
    def pick_color(self, frame):
        color = ch.askcolor(initialcolor=frame['highlightbackground'], parent=self.parent)
        if color:
            frame.config(highlightbackground=color[1])
            if frame.winfo_name() == 'c1':
                self.color_1 = color[1]
            elif frame.winfo_name() == 'c2':
                self.color_2 = color[1]


class Main:
    def __init__(self):
        self.projectDir = ''
        self.extension = 'pxproj' # Project file name extension
        self.jsonReadFile = {} # Loads the project file into json format
        self.pixels = [] # Contains a list of the pixels on the screen (so they can be referanced)
        self.audioFile = None
        self.outputDirectory = tk.StringVar(value='')
        
        self.paused = False
        self.playback = 0.0
        self.playOffset = 0
        self.audioLength = 0
        self.volume = tk.IntVar()
        
        self.VOLUME = 0.5 # Default volume
        self.FRAMERATES = (1, 3, 8, 10, 12, 15, 20, 24, 30, 60)

        self.res = tk.StringVar(value=8) # The project resolution (8 is default)
        self.currentFrame = tk.StringVar(value='1')
        self.currentFrame_mem = 1
        self.framerateDelay = -1 # Default value (Unasigned)
        self.framerate = -1
        self.frameStorage = None # Stores a frame when copying and pasting
        self.frameCount = 0

        self.clickCoords = {}

        self.showAlphaVar = tk.BooleanVar()
        self.showGridVar = tk.BooleanVar(value=True)
        self.gridColor = '#000000'
        self.colorPickerData = ('0,0,0', '#000000') #Stores the data from the color picker

        self.isPlaying = False
        self.control = False
        self.gotoOpen = False
        self.exportOpen = False
        self.modifierUIOpened = False

        self.projectFileSample = {
            "data": {
                "resolution": 16,
                "showgrid": 1,
                "gridcolor": "#000000",
                "audio": None,
                "output": "",
                "framerate": 10
            },
            "frames": [
                {
                    "frame_1": {}
                    }
                ],
            "modifiers": [
                {}
                ]
            }

        root.bind_all('<Control-s>', lambda event: self.save(True))
        root.bind_all('<Command-s>', lambda event: self.save(True))
        root.bind('<Control-z>', lambda event: self.undo())
        root.bind('<Command-z>', lambda event: self.undo())
        
        root.bind('<*>', lambda e: self.root_nodrag())

        self.load()
        
    def root_drag(self):
        if mixer.music.get_busy:
            root.bind('<Motion>', lambda e: self.root_nodrag())
            mixer.music.set_pos(self.playback)
        
    def root_nodrag(self):
        if mixer.music.get_busy:
            if self.audioFile != None:
                mixer.music.set_pos(self.playback)
            self.currentFrame.set(max(int(self.currentFrame.get()) - 2, 1))
            root.unbind("<Motion>")

    def undo(self):
        answer = mb.askyesno(title="Undo", message="Are you sure you want to revert to the last save?")
        if answer:
            self.load_frame(True)
            root.title(root.title()[0:-1]) # Remove the star in the project title
            self.frameMiddle.config(highlightbackground='darkblue')
        
    def load(self):
        def openDir(): # Opens the project directory
            os.chdir(self.projectDir[:self.projectDir.rfind('/')])
            
            if sys.platform == 'win32':
                os.system(f'Explorer .')
            else:
                os.system('open .')
        
        mixer.pre_init(buffer=4096)
        mixer.init()
        mixer.set_num_channels(1)
        
        # Add the menubar:
        self.menubar = tk.Menu(root) # Main menubar
        root.config(menu=self.menubar)

        # Setup file cascade
        self.fileMenu = tk.Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label="New", command=self.new_file_dialog)
        self.fileMenu.add_command(label="Open", command=lambda: self.open_file(True))
        self.fileMenu.add_command(label="Rename", command=self.rename_dialog, state=tk.DISABLED)
        self.fileMenu.add_command(label="Save", command=lambda: self.save(True), state=tk.DISABLED)
        self.fileMenu.add_command(label="Save As", command=self.save_as, state=tk.DISABLED)
        self.fileMenu.add_command(label="Export", command=self.export_display, state=tk.DISABLED)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label=f"Open Directory in {'Explorer' if sys.platform == 'win32' else 'Finder'}", command=openDir, state=tk.DISABLED)
        self.fileMenu.add_command(label="Load Audio", command=self.load_audio, state=tk.DISABLED)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Quit", command=self.quit)

        # Setup edit cascade
        self.editMenu = tk.Menu(self.menubar, tearoff=0)
        self.editMenu.add_command(label="Clear", command=self.canvas_clear, state=tk.DISABLED)
        self.editMenu.add_command(label="Fill", command=self.canvas_fill, state=tk.DISABLED)
        self.editMenu.add_separator()
        self.editMenu.add_command(label="Set Framerate", command=self.set_framerate, state=tk.DISABLED)
        self.editMenu.add_separator()
        self.editMenu.add_command(label="Modifier UI", command=self.modifier_ui, state=tk.DISABLED)
        
        # Setup display cascasde
        self.displayMenu = tk.Menu(self.menubar, tearoff=0)
        self.displayMenu.add_checkbutton(label="Show Grid", variable=self.showGridVar, command=lambda: self.update_grid(True), state=tk.DISABLED)
        self.displayMenu.add_command(label="Grid Color", command=lambda: self.set_grid_color(True), state=tk.DISABLED)
        self.displayMenu.add_checkbutton(label="Show Alpha", variable=self.showAlphaVar, command=lambda: self.display_alpha(True), state=tk.DISABLED)

        # Add the file cascades
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        self.menubar.add_cascade(label="Edit", menu=self.editMenu)
        self.menubar.add_cascade(label="Display", menu=self.displayMenu)

        self.framerateMenu = tk.Menu(self.editMenu, tearoff=0)

        # Frames:

        # Add top frame
        self.frameTop = tk.Frame(root, width=1080, height=10)
        self.frameTop.pack(anchor=tk.NW)

        # Add middle/canvas frame
        self.frameMiddle = tk.Frame(root, width=870, height=870)
        self.frameMiddle.pack(anchor=tk.CENTER, pady=(10, 0))
        self.frameMiddle.pack_propagate(False)

        # Add bottom frame
        self.frameBottom = tk.Frame(root, width=1080, height=40)
        self.frameBottom.pack(side=tk.BOTTOM, pady=(0, 3))
        self.frameBottom.pack_propagate(False)

        # Top frame widgets
       
        #Add the color picker
        self.colorPickerFrame = tk.Frame(self.frameTop, highlightthickness=2, highlightbackground='black')
        self.colorPickerFrame.pack(padx=(4, 75), side=tk.LEFT)
        self.colorPickerButton = tk.Button(self.colorPickerFrame, text="Color Picker", command=self.ask_color, font=('Calibri', 14))
        self.colorPickerButton.pack()

        # Add the tools:

        # Key binds
        root.bind('q', lambda event: self.tool_select(1))
        root.bind('w', lambda event: self.tool_select(2))
        root.bind('e', lambda event: self.tool_select(3))
        root.bind('r', lambda event: self.tool_select(4))

        root.bind('<Return>', lambda event: root.focus())
        root.bind('<Escape>', lambda event: self.esc())
        
        root.bind('<p>', lambda event: (mixer.music.stop() if mixer.music.get_busy() else mixer.music.play()))
        root.bind('<Control-n>', lambda event: self.new_file_dialog())
        root.bind('<Control-o>', lambda event: self.open_file(True))
        root.bind('<Control-q>', lambda event: self.quit())

        # Frame
        self.toolsFrame = tk.LabelFrame(self.frameTop, text="Tools", height=60, width=(266 if sys.platform == 'win32' else 420), bg='white', fg='black')
        self.toolsFrame.pack(anchor=tk.N, side=tk.LEFT, padx=((175 if sys.platform == 'win32' else 60), 0))

        # Pen
        self.penFrame = tk.Frame(self.toolsFrame, height=2, width=6, highlightthickness=2, highlightbackground='red')
        self.penFrame.pack(side=tk.LEFT, padx=5)

        tk.Button(self.penFrame, text="Pen", relief=tk.RAISED, height=2, width=6, command=lambda: self.tool_select(1)).pack()

        # Eraser
        self.eraserFrame = tk.Frame(self.toolsFrame, height=2, width=6, highlightthickness=2, highlightbackground='white')
        self.eraserFrame.pack(side=tk.LEFT, padx=5)

        tk.Button(self.eraserFrame, text="Eraser", relief=tk.RAISED, height=2, width=6, command=lambda: self.tool_select(2)).pack()

        # Remove tool
        self.removeFrame = tk.Frame(self.toolsFrame, height=2, width=6, highlightthickness=2, highlightbackground='white')
        self.removeFrame.pack(side=tk.LEFT, padx=5)
       
        tk.Button(self.removeFrame, text="Remove", relief=tk.RAISED, height=2, width=6, command=lambda: self.tool_select(3)).pack()

        # Repalce tool
        self.replaceFrame = tk.Frame(self.toolsFrame, height=2, width=6, highlightthickness=2, highlightbackground='white')
        self.replaceFrame.pack(side=tk.LEFT, padx=5)
       
        tk.Button(self.replaceFrame, text="Replace", relief=tk.RAISED, height=2, width=6, command=lambda: self.tool_select(4)).pack()

        # Add frame display
        self.decreaseFrameButton = tk.Button(self.frameTop, text="-", command=self.decrease_frame, state='disabled', font=('Courier New', 9))
        self.decreaseFrameButton.pack(side=tk.LEFT, padx=((234 if sys.platform == 'win32' else 120), 0), pady=(10, 0))
        self.frameDisplayButton = tk.Menubutton(self.frameTop, textvariable=self.currentFrame, width=6, disabledforeground='black', relief=tk.RIDGE)
        self.frameDisplayButton.pack(pady=(10, 0), side=tk.LEFT)
        self.increaseFrameButton = tk.Button(self.frameTop, text="+", command=self.increase_frame, font=('Courier New', 9), state='disabled')
        self.increaseFrameButton.pack(side=tk.LEFT, pady=(10, 0))

        # Volume
        volumeStyle = ttk.Style()
        volumeStyle.theme_use("default")

        self.volumeSlider = ttk.Scale(root, length=164, from_=0, to=100, variable=self.volume, style='blue.Horizontal.TScale', command=lambda e: self.change_volume())
        self.volumeSlider.place(relx=.8, rely=.964)
        
        self.volume.set(80) # Set the initial volume

        # Add play button
        self.playButton = tk.Button(self.frameBottom, text="<No Project>", state='disabled', height=2, width=32, command=lambda: self.play_init(False))
        self.playButton.place(relx=.5, rely=.5, anchor='center')
        
        root.bind('<KeyPress-Control_L>', lambda event: self.play_button_mode(True))
        root.bind('<KeyRelease-Control_L>', lambda event: self.play_button_mode(False))

        # Add the frame button dropdown
        self.frameDisplayButton.menu = tk.Menu(self.frameDisplayButton, tearoff=0)
        self.frameDisplayButton['menu'] = self.frameDisplayButton.menu
        self.frameDisplayButton['state'] = 'disabled'

        self.frameDisplayButton.menu.add_command(label="Insert Frame", command=self.insert_frame)
        self.frameDisplayButton.menu.add_command(label="Delete Frame", command=self.delete_frame)
        self.frameDisplayButton.menu.add_separator()
        self.frameDisplayButton.menu.add_command(label="Load from Previous", command=lambda: self.load_from(str(int(self.currentFrame.get()) - 1)))
        self.frameDisplayButton.menu.add_command(label="Load from Next", command=lambda: self.load_from(str(int(self.currentFrame.get()) + 1)))
        self.frameDisplayButton.menu.add_separator()
        self.frameDisplayButton.menu.add_command(label="Copy Frame", command=lambda: self.copy_paste('copy'))
        self.frameDisplayButton.menu.add_command(label="Paste Frame", command=lambda: self.copy_paste('paste'))

    def get_click_coords(self, event):
        self.clickCoords = event

    def return_data_set_true(self):
        self.returnData = True

    def ask_color(self):
        self.colorPickerData = ch.askcolor(initialcolor=self.colorPickerData[1])
        if self.colorPickerData:
            self.colorPickerFrame.config(highlightbackground=self.colorPickerData[1]) # Set the border of the button to the chosen color

    def pick_color(self, event):
        self.selectedPixel = self.canvas.find_closest(event.x, event.y)
        self.colorPickerData = ['None'] # Add a placeholder item
        self.colorPickerData.append(self.canvas.itemcget(self.selectedPixel, option='fill') if self.canvas.itemcget(self.selectedPixel, option='fill') != 'white' else '#ffffff')
        self.colorPickerFrame.config(highlightbackground = self.colorPickerData[1])

    def tool_select(self, tool):
        if not self.isPlaying:
            for frame in self.toolsFrame.winfo_children():
                    frame.config(highlightbackground='white')

            if tool == 1:
                self.penFrame.config(highlightbackground='red')
            elif tool == 2:
                self.eraserFrame.config(highlightbackground='red')
            elif tool == 3:
                self.removeFrame.config(highlightbackground='red')
            elif tool == 4:
                self.replaceFrame.config(highlightbackground = 'red')

    def update_title(self):
        root.title("Pixel-Art Animator-" + self.projectDir)

    def update_grid(self, triggered):
        if self.showGridVar.get():
            for pixel in self.pixels:
                self.canvas.itemconfig(str(pixel), outline=self.gridColor)
        else:
            for pixel in self.pixels:
                self.canvas.itemconfig(str(pixel), outline='')

        if triggered:
            root.title("Pixel-Art Animator-" + self.projectDir + '*')

    def set_grid_color(self, menu):
        if menu:
            self.gridColor = ch.askcolor()[1]
            root.title("Pixel-Art Animator-" + self.projectDir + '*')

        if self.showGridVar.get() or not menu:
            for pixel in self.pixels:
                    self.canvas.itemconfig(str(pixel), outline=self.gridColor)

    def new_project_name_filter(self, res):
        try:
            res.set(''.join([i for i in res.get() if i.isdigit()]))
            if int(res.get()) <= 64 and int(res.get()) > 0:
                pass
            else:
                res.set(64)
        except:
            pass
        
    def new_project_framerate_filter(self, framerate):
        try:
            framerate.set(''.join([i for i in self.newFramerateEntry.get() if i.isdigit()]))
            if int(framerate.get()) <= 60 and int(framerate.get()) > 0:
                pass
            else:
                framerate.set(60)
        except:
            pass

        if len(self.res.get()) > 0 and int(self.res.get()) > 64:
            self.res.set(64)
        if len(self.res.get()) > 0 and int(self.res.get()) == 0:
            self.res.set(1)

    def on_unlock(self):
        self.fileMenu.entryconfig('Rename', state=tk.ACTIVE)
        self.fileMenu.entryconfig('Save', state=tk.ACTIVE)
        self.fileMenu.entryconfig('Save As', state=tk.ACTIVE)
        self.fileMenu.entryconfig('Export', state=tk.ACTIVE)

        self.fileMenu.entryconfig(f'Open Directory in {'Explorer' if sys.platform == 'win32' else 'Finder'}', state=tk.ACTIVE)

        try:
            self.fileMenu.entryconfig('Load Audio', state=tk.ACTIVE)
        except tk.TclError:
            self.fileMenu.entryconfig('Unload Audio', state=tk.ACTIVE)

        self.editMenu.entryconfig('Clear', state=tk.ACTIVE)
        self.editMenu.entryconfig('Fill', state=tk.ACTIVE)
        self.editMenu.entryconfig('Set Framerate', state=tk.ACTIVE)
        self.editMenu.entryconfig('Modifier UI', state=tk.ACTIVE)
       
        self.displayMenu.entryconfig('Show Grid', state=tk.ACTIVE)
        self.displayMenu.entryconfig('Grid Color', state=tk.ACTIVE)
        self.displayMenu.entryconfig('Show Alpha', state=tk.ACTIVE)

        self.increaseFrameButton['state'] = "normal"
        self.frameDisplayButton['state'] = "normal"
        self.decreaseFrameButton['state'] = 'normal'

        self.playButton.config(state='normal', text="Play")
        
        root.bind('<Control-e>', lambda event: self.export_display())

        root.bind('<KeyPress-Shift_L>', lambda event: self.frame_skip(True))
        root.bind('<KeyPress-Shift_R>', lambda event: self.frame_skip(True))
        root.bind('<KeyRelease-Shift_L>', lambda event: self.frame_skip(False))
        root.bind('<KeyRelease-Shift_R>', lambda event: self.frame_skip(False))

        root.bind('<Right>', lambda event: self.increase_frame())
        root.bind('<space>', lambda event: self.play_space())
        root.bind('<Left>', lambda event: self.decrease_frame())
        
        # For goto
        for i in range(1, 10):
            root.bind(f'<KeyPress-{i}>', lambda e, num = i: self.goto(str(num)))
            
        self.frameMiddle.config(highlightthickness=3, highlightbackground="darkblue")

    def new_file_dialog(self):
        newRes = tk.StringVar(value=self.res.get())
        newFramerate = tk.StringVar(value='10')
        
        #Add the toplevel window
        self.newFileTL = tk.Toplevel(width=128, height=256)
        self.newFileTL.attributes("-topmost", True)
        self.newFileTL.resizable(False, False)
        self.newFileTL.title("New File")
        self.newFileTL.focus()
        self.newFileTL.bind('<Escape>', lambda event: self.newFileTL.destroy())
        self.newFileTL.bind('<Return>', lambda event: self.create_new_file(newRes))
       
        #Add the main frame
        newFileFrame = tk.Frame(self.newFileTL, height=156, width=256)
        newFileFrame.pack()
        newFileFrame.pack_propagate(False)
        
        self.newFramerateEntry = tk.Entry(newFileFrame, textvariable=newFramerate, width=3, font=('Courier New', 15))
        self.newFramerateEntry.pack(side=tk.BOTTOM)
        tk.Label(newFileFrame, text="Framerate:", font=('Courier New', 12)).pack(side=tk.BOTTOM)

        tk.Button(newFileFrame, text="Create Project", command=lambda: self.create_new_file(newRes, newFramerate), font=('Calibri', 12)).pack(side=tk.TOP)
        self.newFileSetResolutionEntry = tk.Entry(newFileFrame, textvariable=newRes, width=3, font=('Courier New', 15))
        self.newFileSetResolutionEntry.pack(side=tk.BOTTOM)
        tk.Label(newFileFrame, text="Project Resolution:", font=('Courier New', 12)).pack(side=tk.BOTTOM, pady=(0, 8))

        newRes.trace_add('write', lambda event1, event2, event3: self.new_project_name_filter(newRes))
        newFramerate.trace_add('write', lambda event1, event2, event3: self.new_project_framerate_filter(newFramerate))
       
    def create_new_file(self, res, framerate):
        if res.get() == '' or framerate.get() == '':
            mb.showerror(title="Invalid Data", message="Please fill out all forms!")
            return

        self.res.set(res.get()) # Set project resolution to the new resolution
        self.delay(int(framerate.get()))
        self.newFileTL.attributes("-topmost", False)
        self.newDir = fd.asksaveasfilename(
            title="Choose Directory",
            defaultextension=("pixel project", f'*.{self.extension}'),
            filetypes=(("pixel project", f'*.{self.extension}'),("pixel project", f'*.{self.extension}'))
            )

        if len(self.newDir) > 0:
            self.projectDir = self.newDir
            self.currentFrame.set(1) # Reset the current frame
            self.audioFile = None
            self.playback = 0
            if self.isPlaying:
                self.isPlaying= False
                if mixer.music.get_busy():
                    mixer.music.stop()

            # Create the data files for the project
            self.projectFileSample['data']['resolution'] = self.res.get() # Write the file resolution
            self.projectFileSample['data']['gridcolor'] = self.gridColor
            self.projectFileSample['data']['showgrid'] = int(self.showGridVar.get())
            self.projectFileSample['data']['framerate'] = self.framerate
            self.projectFileSample['data']['output'] = self.outputDirectory.get()

            self.jsonSampleDump = json.dumps(self.projectFileSample, indent=4, separators=(',', ':')) # Read the project data as json text

            #Write the file resolution to the file
            self.settingsFile = open(self.projectDir, 'w')
            self.settingsFile.write(self.jsonSampleDump)
            self.settingsFile.close()
            
            self.jsonReadFile = self.projectFileSample
            self.jsonFrames = self.jsonReadFile['frames']
            
            self.framerateDelay = .04
            
            try:
                self.newFileTL.destroy()
            except:
                pass

            self.add_canvas(False)
            self.modifierUIOpened = False
        else:
            try:
                self.newFileTL.attributes("-topmost", True)
            except AttributeError: # If this function was called using Save As
                pass
            
    def set_framerate(self):
        framerate = simpledialog.askinteger(title="Set Framerate", prompt="Set framerate (1 - 60):", minvalue=1, maxvalue=60)
        if framerate != None:
            self.delay(framerate)
            root.title("Pixel-Art Animator-" + self.projectDir + "*")

    def open_file(self, dialog):
        if '*' in root.title():
            self.saveMode = mb.askyesno(title="Unsaved Changes", message="Would you like to save the current project?")
            if self.saveMode:
                self.save(True)

        if dialog:
            self.fileOpen = fd.askopenfilename(
                title="Open Project File",
                filetypes=(("pixel project", f'*.{self.extension}'),("pixel project", f'*.{self.extension}')))
        else:
            self.fileOpen = self.projectDir
            
        if not self.isPlaying:
            self.play_button_mode(False)

        if len(self.fileOpen) > 0 or not dialog:
            try:
                with open(f'{self.fileOpen}', 'r') as file:
                    self.projectData = json.load(file)
                
                for i in ('resolution', 'showgrid', 'gridcolor', 'audio', 'framerate', 'output'):
                    if i not in self.projectData['data']:
                        mb.showerror(title="Project", message=f"Failed to load {self.fileOpen};\n missing {i} section!")
                    
                    if i == 'audio':
                        if (fileCheck := self.projectData['data']['audio']) != None:
                            if not os.path.isfile(fileCheck):
                                mb.showerror(title="Project", message=f"Failed to load audio; Please check that the file exists!")
                                self.audioFile = None
                            else:
                                self.audioFile = self.projectData['data']['audio'] # Load audio
                                
                                self.fileMenu.entryconfig("Load Audio", label="Unload Audio")

                                mixer.music.queue(self.audioFile)
                                mixer.music.load(self.audioFile)
                                
                                audio = mutagen.File(self.audioFile)
                                self.audioLength = audio.info.length
                                self.audioLength = int((self.audioLength % 60) * 1000)
                    
                self.projectDir = self.fileOpen
                
                self.currentFrame.set(1) # Reset the current frame
                self.playback = 0
                self.isPlaying = False

                self.res.set(self.projectData['data']['resolution']) # Load resolution
                self.showGridVar.set(self.projectData['data']['showgrid']) # Load grid state
                self.gridColor = self.projectData['data']['gridcolor'] # Load grid color
                self.framerate = self.projectData['data']['framerate'] # Load framerate
                self.outputDirectory.set(self.projectData['data']['output'])

                self.delay(self.framerate) # Set the framerate to the saved framerate               

            except IndentationError as e:
                mb.showerror(title="Project", message=f"Failed to load {self.fileOpen}; Unknown Error!")
                return
            
            self.add_canvas(True)
            self.modifierUIOpened = False
            
            if self.showAlphaVar.get():
                self.load_frame(False)
            
            self.exportOpen = False
            root.focus_force()
            
    def load_audio(self):
        if self.audioFile == None:
            audioPath = fd.askopenfilename(
                title="Open audio file",
                filetypes=(("mp3", '*.mp3'),("wav", '*.wav'))
            )

            if len(audioPath) > 1:
                self.fileMenu.entryconfig("Load Audio", label="Unload Audio")
                self.audioFile = audioPath
                mixer.music.unload()
                self.paused = False
                mixer.music.load(self.audioFile)

                audio = mutagen.File(self.audioFile)
                self.audioLength = audio.info.length
                self.audioLength = int((self.audioLength % 60) * 1000)
        else:
            self.fileMenu.entryconfig("Unload Audio", label="Load Audio")
            self.audioFile = None
            mixer.music.unload()
                
        root.title("Pixel-Art Animator-" + self.projectDir + '*')

    def save(self, all) -> None:
        if not self.showAlphaVar.get(): # If show alpha is not toggled
            try:
                if '*' == root.title()[-1]:
                    with open(self.projectDir, 'r+') as self.fileOpen:
                        self.json_projectFile = json.load(self.fileOpen)
                        self.json_projectFile['data']['resolution'] = self.res.get()
                        self.json_projectFile['data']['gridcolor'] = self.gridColor
                        self.json_projectFile['data']['showgrid'] = int(self.showGridVar.get())
                        self.json_projectFile['data']['audio'] = self.audioFile
                        self.json_projectFile['data']['framerate'] = self.framerate
                        self.json_projectFile['data']['output'] = self.outputDirectory.get()
                        self.jsonSampleDump = json.dumps(self.json_projectFile, indent=4, separators=(',', ':')) # Read the project data as json text
                        self.fileOpen.seek(0)
                        self.fileOpen.truncate(0)
                        self.fileOpen.write(self.jsonSampleDump)
                    
                    root.title(root.title()[0:-1]) # Remove the star in the project title

                    if all:
                        self.save_frame()
            except: # In case a project is not open
                pass

    def save_as(self) -> None:
        self.newDir = fd.asksaveasfilename(
            title="Choose Directory",
            defaultextension=("pixel project", f'*.{self.extension}'),
            filetypes=(("pixel project", f'*.{self.extension}'),("pixel project", f'*.{self.extension}'))
        )

        if len(self.newDir) > 1:
            with open(self.projectDir, 'r') as self.fileOpen:
                self.fileData = self.fileOpen.readlines()
           
            with open(self.newDir, 'w') as self.fileOpen:
                self.fileOpen.writelines(self.fileData)

            self.projectDir = self.newDir
            self.open_file(False)
            
    def copy_paste(self, mode:str) -> None:
        if mode == 'copy':
            self.frameStorage = f'frame_{self.currentFrame.get()}'
        elif mode == 'paste':
            self.jsonFrames[0][f'frame_{self.currentFrame.get()}'] = self.jsonFrames[0][self.frameStorage]
            self.load_frame(False)
            self.save_frame()

    def rename_dialog(self) -> None:
        self.renameVar = tk.StringVar()
        self.renameVar.set(os.path.splitext(os.path.split(self.projectDir)[1])[0])

        # Create the rename window
        self.renameTL = tk.Toplevel(width=480, height=80)
        self.renameTL.resizable(False, False)
        self.renameTL.title("Rename Project")
        self.renameTL.attributes('-topmost', True)
        self.renameTL.focus()
        
        self.renameTL.bind('<Return>', lambda event: self.rename())
        self.renameTL.bind('<Escape>', lambda event: self.renameTL.destroy())

        # Add the rename entry and button:
        self.renameEntry = tk.Entry(self.renameTL, width=26, textvariable=self.renameVar, font=('Courier New', 14)).pack(padx=4)
        self.renameButton = tk.Button(self.renameTL, width=24, height=2, text="Rename", command=self.rename).pack()

    def rename(self) -> None:
        self.canRename = True # Keeps track of if the new name is valid
        for i in self.renameVar.get():
            if i in r'\/:*?"<>|' or len(self.renameVar.get()) == 0:
                self.canRename = False

        if self.canRename: # If the new name is valid
            os.chdir(os.path.split(self.projectDir)[0])
            os.rename(self.projectDir, self.renameVar.get() + '.' + self.extension)
            self.projectDir = os.path.split(self.projectDir)[0] + '/' + self.renameVar.get() + '.' + self.extension # Set the project directory to the new name
            self.renameTL.destroy()

            self.update_title()
            self.save(False)

    def add_canvas(self, readPixels):
        self.returnData = False
        # Update the title
        self.update_title()

        # Delete any previous canvases
        [canvas.destroy() for canvas in self.frameMiddle.winfo_children()]
        self.pixels.clear()

        self.canvas = tk.Canvas(self.frameMiddle, height=866, width=866)
        self.canvas.pack()

        # Create pixels
        self.toY = int(self.res.get())
        self.posX = 2
        self.posY = 2

        loading = tk.Label(root, text='Loading...', font=('Default', 100))
        loading.place(x=root.winfo_width()/4, y=root.winfo_height()/2 - 64) # Display the loading screen
        root.update()

        self.fileOpen = open(self.projectDir, 'r')
        if readPixels:
                self.jsonReadFile = json.load(self.fileOpen)

        for pixel in range(int(self.res.get())**2):
            pixelate = (self.canvas.winfo_width()-5)/int(self.res.get())
            self.pixel = self.canvas.create_rectangle(self.posX, self.posY, self.posX + pixelate, self.posY + pixelate, fill='white')

            self.canvas.tag_bind(f'{pixel + 1}', "<ButtonPress-1>", lambda event: self.on_press(event))
            self.canvas.tag_bind(f'{pixel + 1}', "<B1-Motion>", lambda event: self.on_press(event))
            self.pixels.append(self.pixel)

            # Set the pixel color
            if readPixels:

                self.jsonFrames = self.jsonReadFile['frames']
                try:
                    self.savedPixelColor = self.jsonFrames[0][f'frame_'+self.currentFrame.get()]

                    if self.showAlphaVar.get(): # If show alpha is selected
                        self.display_alpha(False)
                    else:
                        self.canvas.itemconfig(self.pixel, fill=self.savedPixelColor[str(self.pixel)][1])

                except KeyError: # If the pixel is not present within the json file
                    self.canvas.itemconfig(self.pixel, fill='white') # Fill pixels with white (0 alpha)

            self.posX += pixelate
            self.toY -= 1

            if self.toY == 0:
                self.toY = int(self.res.get())
                self.posY += pixelate
                self.posX = 2

        # Get number of frames
        self.frameCount = len(self.jsonFrames[0].values())
        
        self.fileOpen.close()
        
        # Add the popup color picker
        self.canvas.bind('<Button-3>', self.pick_color)

        self.set_grid_color(False)
        self.update_grid(False)
        self.on_unlock()
        
        loading.destroy() # Remove the loading text

    def on_press(self, event: dict):
        if self.isPlaying:
            return

        self.get_click_coords(event)

        if self.showAlphaVar.get(): # Stop the user from drawing in show alpha mode
            return
       
        self.cursor_X = event.x
        self.cursor_Y = event.y
        self.selectedPixel = self.canvas.find_closest(event.x, event.y)
       
        try:
            root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
            self.frameMiddle.config(highlightbackground="red")
            
            if self.penFrame['highlightbackground'] == 'red': # If pen mode is selected...
                if not self.canvas.itemcget(self.selectedPixel, option='fill') == self.colorPickerData[1]: # If the pixel color is already the pen color
                    root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
                    self.canvas.itemconfig(self.selectedPixel, fill=self.colorPickerData[1])

            elif self.eraserFrame['highlightbackground'] == 'red': # If the eraser mode is selected...
                self.canvas.itemconfig(self.selectedPixel, fill='white')

            elif self.removeFrame['highlightbackground'] == 'red': # If the remove mode is selected...
                self.canvas_remove_color()

            elif self.replaceFrame['highlightbackground'] == 'red': # If the replace mode is selected...
                if not self.canvas.itemcget(self.selectedPixel, option='fill') == self.colorPickerData[1]: # If the pixel color is already the pen color
                    self.canvas_replace_color()
        except:
            pass # I don't want it to yell at me

    def canvas_clear(self) -> None:
        root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
        for pixel in self.pixels:
            self.canvas.itemconfig(pixel, fill='white')
            
        root.title("Pixel-Art Animator-" + self.projectDir + '*')
        self.frameMiddle.config(highlightbackground="red")

    def canvas_fill(self) -> None:
        fillColor = ch.askcolor()
        if fillColor != (None, None): # If we selected a color (didn't hit cancel)
            for pixel in self.pixels:
                self.canvas.itemconfig(pixel, fill=fillColor[1])

            root.title("Pixel-Art Animator-" + self.projectDir + '*')
            self.frameMiddle.config(highlightbackground="red")

    def canvas_remove_color(self) -> None:
        selectedPixel = self.canvas.find_closest(self.clickCoords.x, self.clickCoords.y)
        selectedColor = self.canvas.itemcget(selectedPixel, option='fill')
        for pixel in self.pixels:
            if self.canvas.itemcget(pixel, option='fill') == selectedColor:
                self.canvas.itemconfig(pixel, fill='white')

        self.colorPickerData[1] = self.colorPickerData[1] # I don't now why this is needed, but the pen color needs to be re-assigned

    def canvas_replace_color(self) -> None:
        selectedPixel = self.canvas.find_closest(self.clickCoords.x, self.clickCoords.y)
        selectedColor = self.canvas.itemcget(selectedPixel, option='fill')
        for pixel in self.pixels:
            if self.canvas.itemcget(pixel, option='fill') == selectedColor:
                self.canvas.itemconfig(pixel, fill=self.colorPickerData[1])

        self.colorPickerData[1] = self.colorPickerData[1] # Needed for some reason idk

    def save_frame(self) -> None:
        root.title(root.title()[0:-1]) # Remove the star in the project title
        self.frameMiddle.config(highlightbackground="darkblue")

        with open(self.projectDir, 'r+') as self.fileOpen:
            self.jsonReadFile = json.load(self.fileOpen)

            # Clear the project file
            self.fileOpen.seek(0)
            self.fileOpen.truncate(0)

            self.jsonFrames = self.jsonReadFile['frames']

            if not f'frame_{self.currentFrame.get()}' in self.jsonFrames[0]: # If the current frame is not stored in the project file, append it
                self.jsonFrames[0][f'frame_{self.currentFrame.get()}'] = {}
           
            self.jsonFrames[0][f'frame_{self.currentFrame.get()}'] = {}

            self.color_Frame_Dict = {}
            for pixel in self.pixels:
                self.pixelColor = self.canvas.itemcget(pixel, option='fill') # Get the colors of each pixel

                if self.pixelColor != 'white': # If the frame is not transparent
                    self.color_Frame_Dict[pixel] = ["", ""]
                    self.color_Frame_Dict[pixel][0] = self.pixelColor
                    self.color_Frame_Dict[pixel][1] = self.pixelColor
                    self.jsonFrames[0][f'frame_{self.currentFrame.get()}'] = self.color_Frame_Dict

            self.jsonSampleDump = json.dumps(self.jsonReadFile, indent=4, separators=(',', ':'))

            self.fileOpen.write(self.jsonSampleDump)
            
            # Load new file data
            self.jsonReadFile = json.loads(self.jsonSampleDump)
            self.jsonFrames = self.jsonReadFile['frames']

    def insert_frame(self) -> None: # Inserts a frame after the current frame
        if self.frameMiddle['highlightbackground'] == "red" and self.frameCount > 1:
            answer = mb.askyesnocancel(title="Unsaved Changes", message="Would you like to save the current frame?")
            if answer:
                self.save_frame()
            elif answer == None:
                return
            self.frameMiddle.config(highlightbackground="darkblue")
            
        self.currentFrame_mem = int(self.currentFrame.get())
        self.frameCount += 1

        # Create a new frame at the end of the sequence
        with open(self.projectDir, 'r+') as self.fileOpen:
            self.jsonReadFile = json.load(self.fileOpen)

            # Get the number of frames
            self.jsonFrames = self.jsonReadFile['frames']
            self.jsonFrames[0][f'frame_{int(len(self.jsonFrames[0])) + 1}'] = {}      

            for loop in range(int(len(self.jsonFrames[0])) - self.currentFrame_mem):
                # Get the data from the previous frame and copy it to the current frame
                self.jsonFrames[0][f'frame_{int(len(self.jsonFrames[0])) - loop}'] = self.jsonFrames[0][f'frame_{int(len(self.jsonFrames[0])) - loop - 1}']
           
            self.currentFrame.set(self.currentFrame_mem + 1)

        self.fileOpen = open(self.projectDir, 'r+')
        self.fileOpen.seek(0)
        self.fileOpen.truncate(0)
        self.jsonSampleDump = json.dumps(self.jsonReadFile, indent=4, separators=(',', ':'))
        self.fileOpen.write(self.jsonSampleDump)
        self.fileOpen.close()

    def delete_frame(self) -> None:
        with open(self.projectDir, 'r+') as self.fileOpen:
            self.jsonReadFile = json.load(self.fileOpen)
            self.jsonFrames = self.jsonReadFile['frames'][0]
            self.newData = copy.deepcopy(self.jsonFrames) # Create a copy of the frame list (as to not change the original durring iteration)
            
            if self.frameCount != 1:
                self.frameCount -= 1
                
            i = int(self.currentFrame.get())
            
            for frame in range(int(self.currentFrame.get()), len(self.jsonFrames) + 1):
                if i != len(self.jsonFrames): # If the frame is not the last frame, copy the data from the next frame
                    self.newData[f'frame_{i}'] = self.jsonFrames[f'frame_{i + 1}']
                    i += 1
                else: # Remove the last frame
                    for loop, frame in enumerate(self.jsonFrames):
                        if loop + 1 == len(self.jsonFrames):
                            self.newData.pop(frame)

            self.jsonReadFile['frames'][0] = self.newData # Set the frames to the new data
            
            self.jsonDump = json.dumps(self.jsonReadFile, indent=4, separators=(',', ':'))
            self.fileOpen.seek(0)
            self.fileOpen.truncate(0)
            self.fileOpen.writelines(self.jsonDump)

        if int(self.currentFrame.get()) - 1 == len(self.jsonFrames) - 1 and self.currentFrame.get() != "0": # If you are on the previous last frame, move back one frame
            self.currentFrame.set(int(self.currentFrame.get()) - 1)
        else:
            pass
        try:
            self.load_frame(True)  
        except KeyError:
            self.currentFrame.set(1)
            self.canvas_clear()
            self.save_frame()

    def increase_frame(self) -> None:
        # Get frame count
        if self.frameCount == 1:
            return
        
        if self.frameMiddle['highlightbackground'] == "red" and self.frameCount > 1:
            answer = mb.askyesnocancel(title="Unsaved Changes", message="Would you like to save the current frame?")
            if answer:
                self.save_frame()
            elif answer == None:
                return
            self.frameMiddle.config(highlightbackground="darkblue")
            
            root.title(root.title()[0:-1])
            
        if int(self.currentFrame.get()) != int(len(self.jsonFrames[0])):
            self.currentFrame.set(str(int(self.currentFrame.get()) + 1))
        else:
            self.currentFrame.set(1)
            if self.audioFile != None:
                if mixer.music.get_busy():
                    mixer.music.set_pos(0.001)
                else:
                    if self.isPlaying:
                        mixer.music.play()
            
        self.load_frame(False)
       
    def decrease_frame(self) -> None:
        if self.frameCount == 1:
            return
        
        if self.frameMiddle['highlightbackground'] == "red" and self.frameCount > 1:
            answer = mb.askyesnocancel(title="Unsaved Changes", message="Would you like to save the current frame?")
            if answer:
                self.save_frame()
            elif answer == None:
                return
            self.frameMiddle.config(highlightbackground="darkblue")
            
        self.currentFrame.set(str(int(self.currentFrame.get()) - 1))

        if int(self.currentFrame.get()) < 1:
            self.currentFrame.set(int(len(self.jsonFrames[0])))

        if self.audioFile != None:
            self.get_playback_pos()

        self.load_frame(False)

    def frame_skip(self, mode: bool) -> None: # Displays the '→←' text or the '+-' text, depending on current functionality
        if mode == True:
            self.increaseFrameButton.config(text="→", command=self.to_last)
            self.decreaseFrameButton.config(text="←", command=self.to_first)

            root.bind('<Right>', lambda event: self.to_last())
            root.bind('<Left>', lambda event: self.to_first())
        else:
            self.increaseFrameButton.config(text="+", command=self.increase_frame)
            self.decreaseFrameButton.config(text="-", command=self.decrease_frame)

            root.bind('<Right>', lambda event: self.increase_frame())
            root.bind('<Left>', lambda event: self.decrease_frame())

    def to_first(self): # Go to first frame
        self.currentFrame.set(1)
        self.load_frame(False)

    def to_last(self): # Go to last frame
        self.currentFrame.set(self.frameCount)
        self.load_frame(False)

    def load_frame(self, loadFile) -> None: # Display the frame
        if loadFile:
            with open(self.projectDir, 'r') as self.fileOpen:
                self.jsonReadFile = json.load(self.fileOpen)
                self.jsonFrames = self.jsonReadFile['frames']

        if len(self.jsonFrames[0][f'frame_' + self.currentFrame.get()]) == 0: # If the frame is empty
            for pixel in range(int(self.res.get())**2):
                self.canvas.itemconfig(self.pixels[pixel], fill='white') # Fill pixels with white (0 alpha)
            return None

        for pixel in range(int(self.res.get())**2):
            try:
                if self.jsonFrames[0].get(f'frame_' + self.currentFrame.get()):
                    self.savedPixelColor = self.jsonFrames[0][f'frame_' + self.currentFrame.get()]

                if self.showAlphaVar.get(): # If show alpha is selected
                    self.canvas.itemconfig(self.pixels[pixel], fill=('white' if self.savedPixelColor[str(self.pixels[pixel])] else 'black'))
                else:
                    self.canvas.itemconfig(self.pixels[pixel], fill=self.savedPixelColor[str(self.pixels[pixel])][1])

            except KeyError: # If the pixel is not present within the json file
                if self.showAlphaVar.get():
                    self.canvas.itemconfig(self.pixels[pixel], fill='black') # Fill pixels with black (0 alpha)
                else:
                    self.canvas.itemconfig(self.pixels[pixel], fill='white') # Fill pixels with white (0 alpha)

        if self.audioFile != None:
            self.get_playback_pos()

    def load_from(self, frame: int) -> None:
        with open(self.projectDir, 'r') as self.fileOpen:
            for pixel in range(int(self.res.get())**2):
                self.jsonReadFile = json.load(self.fileOpen)
                try:
                    self.json_readFrames = self.jsonReadFile['frames']
                    self.savedPixelColor = self.json_readFrames[0][f'frame_{frame}']

                    if self.canvas.itemcget(self.pixels[pixel], option='fill') != self.savedPixelColor[str(self.pixels[pixel])]: # If the pixel color is already the pen color
                        root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title

                    self.canvas.itemconfig(self.pixels[pixel], fill=self.savedPixelColor[str(self.pixels[pixel][1])])
                except:
                    self.canvas.itemconfig(self.pixels[pixel], fill='white')
                    
        self.save_frame()

    def display_alpha(self, triggered):
        if triggered and self.showAlphaVar.get(): #If this was triggered by pressing the show alpha button
            if '*' == root.title()[-1]:
                self.save_frame() # Save the current image

        for pixel in self.pixels:
            if self.showAlphaVar.get():
                self.frameDisplayButton.config(state=tk.DISABLED)
                self.canvas.itemconfig(pixel, fill=['black' if self.canvas.itemcget(pixel, option='fill') == 'white' else 'white']) # Show the alpha
            else: # Reload the colors from the file
                self.frameDisplayButton.config(state=tk.NORMAL)
                self.load_frame(False)
                break
            
    def goto(self, start):
        text = tk.StringVar(value=start)
        
        def remove(goto):
            gotoTL.destroy()
            self.gotoOpen = False
            if goto:
                if int(text.get()) > self.frameCount:
                    self.currentFrame.set(self.frameCount - 1)
                else:
                    self.currentFrame.set(int(text.get()) - 1)
                self.increase_frame()
                if mixer.music.get_busy():
                    self.get_playback_pos()
                    mixer.music.set_pos(self.playback)
            
        def display(char):
            if char != None:
                if len(text.get()) < len(str(self.frameCount)):
                    text.set(text.get() + str(char))
            else:
                if len(text.get()) > 1:
                    text.set(text.get()[:-1])
            
        if self.gotoOpen:
            return None
        
        self.gotoOpen = True
        gotoTL = tk.Toplevel()
        gotoTL.title("Goto...")
        gotoTL.geometry('240x64')
        gotoTL.resizable(False, False)
        # gotoTL.attributes('-toolwindow', True)
        gotoTL.focus()
        
        label = tk.Label(gotoTL, width=1000, height=10, textvariable=text, font=('Calibri', 16), justify=tk.LEFT).pack()
        
        gotoTL.bind('<FocusOut>', lambda e: remove(False))
        gotoTL.bind('<Escape>', lambda e: remove(False))
        gotoTL.bind('<Return>', lambda e: remove(True))
        
        for i in range(10):
            gotoTL.bind(f'<KeyPress-{i}>', lambda e, num = i: display(num))
            
        gotoTL.bind('<BackSpace>', lambda e: display(None))

    def quit(self):
        if '*' in root.title(): # If the file is not saved...
            quitMode = mb.askyesnocancel(title="File Not Saved", message="Do you want to save your project?")
            if quitMode == None: # Do nothing
                return

            if quitMode: # Save and quit
                self.save(True)
                root.destroy()
            else:
                root.destroy()
        else:
            root.destroy()
            
    def var_filter(self, var, min, max):
        try:
            var.set("".join(i for i in var.get() if i.isdigit()))
            if min != None:
                if int(var.get()) < min:
                    var.set(min)
                    
            if max != None:
                if int(var.get()) > max:
                    var.set(max)
        except ValueError:
            pass
        
    def trash(self, directory):
        os.chdir(directory)
        sucess = True
        if len(os.listdir()) > 0:
            try:
                send2trash.send2trash(os.listdir())
            except:
                sucess = False
        else:
            sucess = None
        
        self.trashResponce(sucess)
    
    def trashResponce(self, sucess):
        if sucess == None:
            mb.showinfo(title="Trash", message="No files found!")
        elif sucess:
            mb.showinfo(title="Trash", message="Files deleted successfully!")
        else:
            mb.showerror(title="Trash", message="Failed to delete one or more files!")
            
        self.clearFolderButton.config(state='normal', text="Clear Folder")
        self.exportTL.focus()

    def export_display(self):
        def open_dir():
            cdr = os.getcwd()
            os.chdir(self.outputDirectory.get())
            os.system("Explorer .")
            os.chdir(cdr)
            
        def get_resolutions(value):
            resolutions = []
            res = value
            while res <= 4096: # Generate resolutions up to 4k
                resolutions.append(res)
                res*= 2
                
            if 4096 not in resolutions:
                resolutions.append(4096)
                
            return resolutions
        
        def l_g_res(value):
                if value:
                    self.resolutions = get_resolutions(int(self.res.get()))
                else:
                    self.resolutions = get_resolutions(32)
                    
                self.resolutionBox.pack_forget()
                self.resolutionBox = tk.Spinbox(self.exportFrameMiddleBottom, width=4, textvariable=self.resVar, values=self.resolutions, state='readonly')
                self.resolutionBox.pack(side=tk.LEFT, padx=(6, 0))
                
                self.checkbutton.pack_forget()
                self.checkbutton = tk.Checkbutton(self.exportFrameMiddleBottom, text="Local", variable=localResVar, command=lambda: l_g_res(localResVar.get()))
                self.checkbutton.pack(side=tk.LEFT, padx=(10, 0))
                
        def alphaAvailable(type):
            if type in (".jpeg"):                
                self.alphaCheck.config(state='disabled')
            else:
                self.alphaCheck.config(state='normal')
                
        def askTrash(directory):
            self.clearFolderButton.config(state='disabled', text="Clearing...")
            ans = mb.askyesno(title="Trash", message="Are you sure you want to clear all items from this folder?")
            if ans:
                threading.Thread(target=self.trash, args=(self.outputDirectory.get(),)).start()
            else:
                self.clearFolderButton.config(state='normal', text="Clear Folder")
                self.exportTL.focus()
        
        if self.exportOpen:
            self.exportTL.deiconify()
            self.exportTL.focus()
            return

        self.exportOpen = True
        
        # Resolution values
        self.resolutions = get_resolutions(32) # Base resolution
            
        localResVar = tk.BooleanVar()
        
        # Add the toplevel
        self.exportTL = tk.Toplevel(width=640, height=500)
        self.exportTL.resizable(True, False)
        self.exportTL.title("Export Animation")
        self.exportTL.protocol("WM_DELETE_WINDOW", self.exportTL.withdraw)
        self.exportTL.focus()
        self.exportTL.withdraw()
        
        self.exportTL.bind('<Escape>', lambda e: self.exportTL.withdraw())

        # Create the frames
        frameWidth = (420 if sys.platform == 'win32' else 548)
        
        self.sequenceFrame = tk.Frame(self.exportTL, width=frameWidth, height=300)
        self.sequenceFrame.pack()

        self.exportFrameTop = tk.Frame(self.sequenceFrame, width=frameWidth, height=100, highlightbackground='black', highlightthickness=2)
        self.exportFrameTop.pack(side=tk.TOP)
        self.exportFrameTop.pack_propagate(False)
        
        self.exportFrameMiddleTop = tk.Frame(self.sequenceFrame, width=frameWidth, height=50, highlightbackground='black', highlightthickness=2)
        self.exportFrameMiddleTop.pack(pady=(20, 0))
        self.exportFrameMiddleTop.pack_propagate(False)
        
        self.exportFrameMiddleBottom = tk.Frame(self.sequenceFrame, width=frameWidth, height=50, highlightbackground='black', highlightthickness=2)
        self.exportFrameMiddleBottom.pack(pady=20)
        self.exportFrameMiddleBottom.pack_propagate(False)
        
        self.exportFrameBottom1 = tk.Frame(self.sequenceFrame, width=frameWidth, height=500)
        self.exportFrameBottom1.pack(side=tk.BOTTOM)
        
        self.exportFrameBottom2 = tk.Frame(self.sequenceFrame, width=frameWidth)
        self.exportFrameBottom2.pack(side=tk.BOTTOM)

        # Create the menus:
        
        # Directory panel
        exportTypeStr = tk.StringVar(value='.png') # Set the default output extenion
        exportFileNameStr = tk.StringVar(value=os.path.splitext(os.path.split(self.projectDir)[1])[0])

        outputDirectoryEntry = tk.Entry(self.exportFrameTop, textvariable=self.outputDirectory, width=36, font=('Calibri', 14))
        outputDirectoryEntry.grid(row=1, column=0, columnspan=3)
        
        root.update()
        
        self.outputDirectory.trace_add('write', lambda e1, e2, e3: root.title("Pixel-Art Animator-" + self.projectDir + '*'))
        
        tk.Label(self.exportFrameTop, text="Output Directory:", font=('Calibri', 14)).grid(row=0, column=0)
        tk.Button(self.exportFrameTop, text="open", font=('Calibri', 10), command=self.open_output_dir).grid(row=1, column=3, sticky=tk.W)
        tk.Button(self.exportFrameTop, text="Open Directory", font=('Calibri', 10), command=lambda: (open_dir()) if sys.platform == 'win32' else (os.system(f"open {self.outputDirectory.get()}"))).grid(row=2, column=0, sticky=tk.W, padx=(112, 0))
        self.clearFolderButton = tk.Button(self.exportFrameTop, text="Clear Folder", font=('Calibri', 10), command=lambda: askTrash(self.outputDirectory.get()))
        self.clearFolderButton.grid(row=2, column=2, sticky=tk.E, columnspan=2, padx=(0, 112))
        
        # Render panel:
        tk.Label(self.exportFrameMiddleTop, text="File Name: ").pack(side=tk.TOP, anchor=tk.NW)
        tk.Entry(self.exportFrameMiddleTop, textvariable=exportFileNameStr, width=30).pack(side=tk.LEFT)
        tk.OptionMenu(self.exportFrameMiddleTop, exportTypeStr, ".png", ".jpeg", ".tga", ".tiff", command=lambda ext: alphaAvailable(ext)).pack(side=tk.LEFT, anchor=tk.NW)
        
        # Alpha checkbox
        useAlphaVar = tk.BooleanVar()
        self.alphaCheck = tk.Checkbutton(self.exportFrameMiddleTop, variable=useAlphaVar, text="Use Alpha", font=("Calibri", 11), justify=tk.CENTER)
        self.alphaCheck.pack()
        
        # Duration panel:
        self.fromVar = tk.StringVar(value='1')
        self.toVar = tk.StringVar(value=self.frameCount)
        self.stepVar = tk.IntVar()
        self.resVar = tk.IntVar()
        
        self.fromVar.trace_add('write', lambda e1, e2, e3: self.var_filter(self.fromVar, 1, self.frameCount - 1))
        self.toVar.trace_add('write', lambda e1, e2, e3: self.var_filter(self.toVar, 1, self.frameCount))
        
        tk.Label(self.exportFrameMiddleBottom, text="Render Settings:").pack(side=tk.TOP, anchor=tk.NW)

        tk.Label(self.exportFrameMiddleBottom, text="From:").pack(side=tk.LEFT)
        tk.Entry(self.exportFrameMiddleBottom, width=4, textvariable=self.fromVar).pack(side=tk.LEFT, padx=4)
        
        tk.Label(self.exportFrameMiddleBottom, text="To:").pack(side=tk.LEFT, padx=(6, 0))
        tk.Entry(self.exportFrameMiddleBottom, width=4, textvariable=self.toVar).pack(side=tk.LEFT, padx=4)
        
        tk.Label(self.exportFrameMiddleBottom, text="Step:").pack(side=tk.LEFT, padx=(6, 0))
        tk.Spinbox(self.exportFrameMiddleBottom, width=4, textvariable=self.stepVar, from_=1.0, to=10.0, state='readonly').pack(side=tk.LEFT, padx=4)
        
        tk.Label(self.exportFrameMiddleBottom, text="Resolution:").pack(side=tk.LEFT, padx=(6, 0))
        self.resolutionBox = tk.Spinbox(self.exportFrameMiddleBottom, width=4, textvariable=self.resVar, values=self.resolutions, state='readonly')
        self.resolutionBox.pack(side=tk.LEFT, padx=(6, 0))
        
        self.checkbutton = tk.Checkbutton(self.exportFrameMiddleBottom, text="Local", variable=localResVar, command=lambda: l_g_res(localResVar.get()))
        self.checkbutton.pack(side=tk.LEFT, padx=(10, 0))
        
        # Create the export buttons
        ttk.Button(self.exportFrameBottom2, text="Render Sequence", width=16, command=lambda: self.export(exportFileNameStr.get(), exportTypeStr.get(), useAlphaVar.get(), True, int(self.fromVar.get()), int(self.toVar.get()), self.stepVar.get(), resolution=self.resVar.get(), usingAlpha=(True if self.alphaCheck['state'] == 'normal' else False))).pack(side=tk.LEFT, anchor=tk.W)
        ttk.Button(self.exportFrameBottom2, text="Render Image", width=16, command=lambda: self.export(exportFileNameStr.get(), exportTypeStr.get(), useAlphaVar.get(), False, resolution=self.resVar.get(), usingAlpha=(True if self.alphaCheck['state'] == 'normal' else False))).pack(side=tk.RIGHT, anchor=tk.E)
        
        self.exportTL.update_idletasks() # So we can get the resolution that one time
        
        ttk.Separator(self.exportFrameBottom1, orient='horizontal').pack(ipadx=320, pady=(8, 0)) # Seperator
        tk.Label(self.exportFrameBottom1, width=40, text=f"Total frame count: {self.frameCount}").pack(side=tk.BOTTOM) # Display the total frame count
        
        self.exportTL.after(10, lambda: self.exportTL.deiconify())
        
    def export(self, fileName, extension, alpha, isSequance, *args, **kwargs):
        try:
            os.stat(self.outputDirectory.get())
        except FileNotFoundError:
            mb.showerror(title="Path Error", message="Output directory does not exist")
            self.exportTL.focus()
            return
        
        self.rendering = True
        resolution = kwargs['resolution']
        usingAlpha = kwargs['usingAlpha']
        
        def beep(): # Don't beep if user clickes off the application
            root.update()
            
            if renderTL.focus_get() != None:
                winsound.MessageBeep()
                
        def cancelDialog():
            self.rendering = not mb.askyesno(title="Cancel Render", message="Are you sure you want to cancel the current render?")
                
        fileName = f"{self.outputDirectory.get()}/{fileName}"
                
        if isSequance:
            if (frameCount := args[1] - args[0]) <= 0: # Makes sure we have a valid frame range
                mb.showerror(title="Frame Error", message='"From" value must be less than "to" value!')
                self.exportTL.focus()
                return
            
            if (args[0]) <= 0: # Makes sure we have a valid frame range
                mb.showerror(title="Frame Error", message='"From" value must be 1 or greater!')
                self.exportTL.focus()
                return
            
            if (args[1]) > self.frameCount: # Makes sure we have a valid frame range
                mb.showerror(title="Frame Error", message='"To" value must be less than or equal to the frame count!')
                self.exportTL.focus()
                return
            
            # Create UI
            renderTL = tk.Toplevel()
            renderTL.title("Rendering...")
            renderTL.geometry("480x360")
            renderTL.resizable(False, False)
            renderTL.grab_set() # Keep the render window in focus
            renderTL.focus()
            
            renderTL.protocol('WM_DELETE_WINDOW', cancelDialog)
            
            # Progress bar styles
            progressBarStyle = ttk.Style()
            progressBarStyle.configure("red.Horizontal.TProgressbar", foreground='red', background='red')
            progressBarStyle.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
            progressBarStyle.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue')
            
            if sys.platform == 'win32':
                renderTL.bind('<FocusOut>', lambda e: beep()) # Beep if we try to click off
            
            renderFrameBottom = tk.Frame(renderTL, width=40, height=100)
            renderFrameBottom.pack(side=tk.BOTTOM, pady=(0, 4))
            
            ttk.Separator(renderTL, orient='horizontal').pack(side=tk.BOTTOM, ipadx=1000, pady=(0, 4))
            
            renderFrameMiddle = tk.Frame(renderTL, width=64, height=128)
            renderFrameMiddle.pack(side=tk.BOTTOM, pady=(4, 0))
            
            renderFrameTop = tk.Frame(renderTL, width=280, height=280, highlightbackground='black', highlightthickness=1)
            renderFrameTop.pack(side=tk.TOP)
            renderFrameTop.pack_propagate(False)
            
            # Main GUI:
            imageDisplay = tk.Canvas(renderFrameTop, bg='lightblue')
            imageDisplay.pack(expand=True)
            imageDisplay.create_text(20, 20, text="")
            
            infoLabel = tk.Label(renderFrameMiddle, text="Starting Up...")
            infoLabel.pack(anchor=tk.W)
            
            progressBar = ttk.Progressbar(renderFrameMiddle, length=420, maximum=frameCount, style="blue.Horizontal.TProgressbar")
            progressBar.pack(pady=(4, 6))
            
            cancelButton = ttk.Button(renderFrameBottom, text="Cancel", width=64, command=lambda: cancelDialog())
            cancelButton.pack()
            
            subStr = '0' * len(str(frameCount + 1))
            position = 0
            index = len(str(frameCount + 1)) - 1
            
            renderTL.update()
            
            frame = 0 # The frame we are rendering

            for i in range(args[0], args[1] + 1):
                if self.rendering:
                    position += 1
                    index = len(str(frameCount + 1)) - 1
                    subStr = subStr[:len(str(index)) - len(str(position)) - 1]
                    subStr += str(position)
                    
                    if position % args[2] == 0:
                        img = Image.new(size=(int(self.res.get()), int(self.res.get())), mode=('RGBA' if alpha and usingAlpha else 'RGB'))
                        pixels = self.jsonFrames[0][f"frame_{i}"]
                        px = 0
                        frame += 1

                        for y in range(0,img.size[1]):
                            for x in range(0,img.size[0]):
                                px += 1
                                try:
                                    color = pixels[str(px)]
                                    rgb = self.hex_to_rgb(color)
                                    rgb.append(255)
                                    img.putpixel((x, y), tuple(rgb))
                                except KeyError:
                                    if alpha and usingAlpha:
                                        img.putpixel((x, y), (0) * 4)
                                    else:
                                        img.putpixel((x, y), (255, 255, 255, 255))
                                            
                        img = img.resize(size=(int(self.res.get()) * ceil(resolution / int(self.res.get())), int(self.res.get()) * ceil(resolution / int(self.res.get()))), resample=4).resize(size=(resolution, resolution))
                        img.save(fileName + "_" + subStr + extension, extension[1:])
                        img.close()
                        
                        imageDisplay.delete('1')
                        renderedImage = ImageTk.PhotoImage(image=(Image.open(fileName + "_" + subStr + extension).resize((imageDisplay.winfo_width(), imageDisplay.winfo_height()), resample=0)))
                        imageDisplay.create_image(1, 1, anchor=tk.NW, image=renderedImage)
                        
                        infoLabel.config(text=f"Rendered frame {frame} of {floor(frameCount / args[2] + 1)}")
                        
                        progressBar.config(value=position)
                        renderTL.update()
                else: # If we cancel the render
                    break
                
            renderTL.attributes('-topmost', True)
            renderTL.protocol('WM_DELETE_WINDOW', lambda e = 1: e) # Do nothing
            cancelButton['command'] = ""

            if self.rendering:
                progressBar.config(style='green.Horizontal.TProgressbar')
                renderTL.grab_release()
                
                mb.showinfo(title="Render", message="Render complete!")
                renderTL.destroy()
                
                self.exportTL.focus()
            else:
                progressBar.config(style='red.Horizontal.TProgressbar', value=frameCount)
                renderTL.grab_release()
                
                mb.showinfo(title="Render", message="Render halted!")
                renderTL.destroy()

                self.exportTL.focus()
        else:
            img = Image.new(size=(int(self.res.get()), int(self.res.get())), mode=('RGBA' if alpha and usingAlpha else 'RGB'))
            px = 0 # The current pixel being referanced
            
            for y in range(0,img.size[1]):
                for x in range(0,img.size[0]):
                    px += 1
                    color = self.canvas.itemcget(str(px), "fill")
                    if color != 'white':
                        rgb = self.hex_to_rgb(color)
                        rgb.append(255)
                        img.putpixel((x, y), tuple(rgb))
                    else:
                        if alpha and usingAlpha:
                            img.putpixel((x, y), (0) * 4)
                        else:
                            img.putpixel((x, y), (255, 255, 255, 255))
                
            img = img.resize(size=(int(self.res.get()) * ceil(resolution / int(self.res.get())), int(self.res.get()) * ceil(resolution / int(self.res.get()))), resample=0).resize(size=(resolution, resolution))
            img.save(fileName + extension, extension[1:])
            img.close()
        
    def hex_to_rgb(self, color):
        color = color[1:]
        return list(int(color[i:i+2], 16) for i in (0, 2, 4))

    def open_output_dir(self):
        output = fd.askdirectory()
        if len(output) > 1:
            self.outputDirectory.set(output)
            root.title("Pixel-Art Animator-" + self.projectDir + '*')
        self.exportTL.focus()

    def get_playback_pos(self):
        self.playback = max(self.framerateDelay * float(self.currentFrame.get()) - self.framerateDelay, 0.0001)  # Get the audio position
        if self.audioFile != None:
            if not mixer.music.get_busy():
                mixer.music.play()
                mixer.music.set_pos(self.playback)
                mixer.music.pause()
    
    def change_volume(self):
        mixer.music.set_volume(self.volume.get() / 100)

    def play_space(self):
        if self.control:
            self.play_init(True)
        else:
            self.play_init(False)

    def esc(self): # Stop the playback by pressing escape
        root.focus()
        if self.isPlaying:
            self.play_init(True)

    def play_init(self, stopMode):
        loop = False
        if stopMode and not self.isPlaying:
            pass
        elif not self.isPlaying:
            loop = True
        if not self.isPlaying:
            self.currentFrame_mem = int(self.currentFrame.get())

        self.play(stopMode, self.currentFrame_mem, loop)

    def play(self, stopMode, save, loop):
        def end():
            self.playButton.config(text="Play")
            root.unbind('<Configure>')

            if stopMode:
                self.currentFrame.set(self.currentFrame_mem)

                self.load_frame(False)
                self.isPlaying = False

                if self.audioFile != None:  # Restart and stop the audio
                    mixer.music.rewind()
                    mixer.music.stop()
                self.paused = False
            else:
                self.paused = True
                if self.audioFile != None:
                    mixer.music.pause()

            self.get_playback_pos()

        def play_audio(): # Plays the audio, if there is any
            self.get_playback_pos()

            if self.audioFile != None:
                if self.paused:
                    mixer.music.unpause()
                else:
                    mixer.music.play(start=self.playback)

        root.bind('<Configure>', lambda e: self.root_drag())

        self.currentFrame_mem = save
        self.isPlaying = not self.isPlaying
        if self.isPlaying:
            self.playButton.config(text="Stop")
            play_audio()

            time.sleep(self.framerateDelay)

        while self.isPlaying:
            time1 = timeit.default_timer()
            self.increase_frame()
            root.update()
            if not loop:
                if int(self.currentFrame.get()) == self.currentFrame_mem:
                    end()
                    return
            try:
                if self.isPlaying:
                    time.sleep(max((self.framerateDelay - 0.000006164899999999 * int(self.res.get())) - (timeit.default_timer() - time1), 0))
            except:
                return
        end()

    def play_button_mode(self, isControl):
        self.control = isControl
        if isControl:
            self.playButton.config(command=lambda: self.play_init(True))
        else:
            self.playButton.config(command=lambda: self.play_init(False))

    def delay(self, delay):
        self.framerate = delay
        self.framerateDelay = max(0.00001, 1 / float(delay))
        root.title("Pixel-Art Animator-" + self.projectDir + '*')
        
        
    def modifier_ui(self):
        def draw_frame():
            # Draw the current frame to the preview canvas
            for pixel in range(int(self.res.get())**2):
                try:
                    if self.jsonFrames[0].get(f'frame_' + self.currentFrame.get()):
                        self.savedPixelColor = self.jsonFrames[0][f'frame_' + self.currentFrame.get()]
                        self.previewCanvas.itemconfig(self.pixels[pixel], fill=self.savedPixelColor[str(self.pixels[pixel])][1])
                    else:
                        self.savedPixelColor = 'white'
                        self.previewCanvas.itemconfig(self.pixels[pixel], fill='white')

                except KeyError: # If the pixel is not present within the json file
                    self.previewCanvas.itemconfig(self.pixels[pixel], fill='white') # Fill pixels with white (0 alpha)
        
        if self.modifierUIOpened:
            self.modifierTL.deiconify()
            draw_frame()
        else:
            # Toplevel setup
            self.modifierTL = tk.Toplevel(root, width=880, height=940)
            self.modifierTL.title("Modifier Editor")
            self.modifierTL.protocol('WM_DELETE_WINDOW', self.modifierTL.withdraw)
            self.modifierTL.propagate(False)
            self.modifierTL.resizable(False, False)
            self.modifierTL.focus()
            
            PADDING = 23
            
            # Main frames
            operatorContainer = tk.Frame(self.modifierTL, width=Operator.WIDTH+PADDING, height=940, highlightbackground='darkblue', highlightthickness=2)
            operatorContainer.pack(side=tk.RIGHT, anchor=tk.NE)
            operatorContainer.pack_propagate(False)
            
            operatorCanvas = tk.Canvas(operatorContainer, width=Operator.WIDTH+PADDING, height=940)
            operatorCanvas.pack(side=tk.LEFT)
            
            scrollbar = tk.Scrollbar(operatorContainer, command=operatorCanvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(60, 10), padx=(0, 2), before=operatorCanvas)
            
            self.operatorFrame = tk.Frame(operatorCanvas, width=Operator.WIDTH+PADDING, height=940)
            self.operatorFrame.bind('<Configure>', lambda e: operatorCanvas.configure(scrollregion=operatorCanvas.bbox('all')))
            
            operatorCanvas.create_window((0, 0), window=self.operatorFrame, anchor=tk.NW)
            operatorCanvas.configure(yscrollcommand=scrollbar.set)
            
            self.previewFrame = tk.Frame(self.modifierTL, width=560, height=560, highlightbackground='green', highlightthickness=2)
            self.previewFrame.pack(side=tk.TOP, anchor=tk.NW)
            
            self.settingsFrame = tk.Frame(self.modifierTL, width=568, height=340, highlightbackground='darkblue', highlightthickness=2)
            self.settingsFrame.pack(side=tk.BOTTOM, anchor=tk.SW)
            
            self.previewCanvas = tk.Canvas(self.previewFrame, width=560, height=560, bg='lightblue')
            self.previewCanvas.pack()
            self.previewCanvas.pack_propagate(False)
            
            root.update()
            
            # Add pixels to preview canvas
            if not self.modifierUIOpened:
                toY = int(self.res.get())
                posX = 2
                posY = 2

                loading = tk.Label(self.previewCanvas, text='Loading...', font=('Default', 84), bg='lightblue')
                loading.pack(anchor=tk.CENTER, pady=(self.previewCanvas.winfo_height()/2 - 84, 0)) # Display the loading screen
                root.update()

                for pixel in range(int(self.res.get())**2):
                    pixelate = (self.previewCanvas.winfo_width()-5)/int(self.res.get())
                    tile = self.previewCanvas.create_rectangle(posX, posY, posX + pixelate, posY + pixelate, fill='white')
                    self.pixels.append(tile)

                    posX += pixelate
                    toY -= 1

                    if toY == 0:
                        toY = int(self.res.get())
                        posY += pixelate
                        posX = 2

                loading.pack_forget()
                
            draw_frame()
                
            # Modifier setup
            addButton = tk.Menubutton(self.operatorFrame, text='➕', font=('Calibri', 16), highlightbackground='black', highlightthickness=1)
            addButton.pack(side=tk.TOP, anchor=tk.NW, pady=(0, 1), padx=1)

            addButton.menu = tk.Menu(addButton, tearoff=False)
            addButton['menu'] = addButton.menu
            addButton.menu.add_command(label='Tint Operator', command=lambda: self.add_modifier(0))
            addButton.menu.add_command(label='Monochrome Operator', command=lambda: self.add_modifier(1))

            tk.Frame(self.operatorFrame, width=Operator.WIDTH+PADDING, height=2, highlightbackground='darkblue', highlightthickness=2).pack(side=tk.TOP)
            
            self.modifierUIOpened = True
                
                
    def add_modifier(self, modifier):
        match modifier:
            case 0:
                TintOperator(self.operatorFrame).pack(anchor=tk.NW)
                
            case 1:
                MonochromeOperator(self.operatorFrame).pack(anchor=tk.NW)
                

#-----====Main Program Start====-----#
root = tk.Tk()
root.title("Pixel-Art Animatitor")
root.geometry('990x1000')
root.resizable(False, False)

m_cls = Main()
root.protocol("WM_DELETE_WINDOW", m_cls.quit) # Open the quit dialogue when closing

root.mainloop()