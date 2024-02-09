#  ---------=========|  Credits: Miles Bierie  |  Developed: Monday, April 3, 2023 -- Friday, February 2, 2024  |=========---------  #


from tkinter import colorchooser as ch
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog
from PIL import Image, ImageTk
from math import ceil, floor
from tkinter import TclError
from pygame import mixer
from pygame import error
from tkinter import ttk
import tkinter as tk
import threading
import mutagen
import timeit
import uuid
import json
import copy
import time
import sys
import os


class Operator(tk.Frame):
    copied = None
    modifier_count = 0
    
    WIDTH = 250
    HEIGHT = 297
        
    def __init__(self, parent, name, _uuid):
        Operator.modifier_count += 1
         
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
        
        self.nameLabel = tk.Label(self.titleFrame, text=self.name, bg='lightblue', font=('Consolas', 9))
        self.nameLabel.pack(anchor=tk.W, side=tk.LEFT)
        # To stop us from focusing on two instances of the operator class at the same time
        self.nameLabel.bind('<Double-Button-1>', lambda e: self.__rename_dialog__())
        
        # Only visible when renaming
        self.nameEntry = tk.Entry(self.titleFrame, textvariable=self.nameVar, width=30, font=('Consolas', 9))
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
        menu.add_separator()
        menu.add_command(label='Print UUID', command=lambda m = self: print(self.UUID))
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
        MAX_LENGTH = 30
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
        self.name = name
        
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
        if newColor != (None, None):
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
        self.name = name
        
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
        if color != (None, None):
            frame.config(highlightbackground=color[1])
            if frame.winfo_name() == 'c1':
                self.color_1 = color[1]
            elif frame.winfo_name() == 'c2':
                self.color_2 = color[1]


class Main:
    def __init__(self) -> None:
        def try_delete_guide():
            if not self.isPlaying:
                try:
                    self.canvas.delete(self.canvas.find_withtag('guide'))
                except AttributeError:
                    pass

        self.projectDir = '' # The directory of the current project
        self.extension = 'pxproj' # Project file name extension
        self.projectData = {} # Loads the project file into json format
        self.pixels = [] # Contains a list of the pixels on the screen (so they can be referanced)
        self.audioFile = None # The path to the audio file
        self.outputDirectory = tk.StringVar(value='') # The directory we render to
        self.isComplexProject = tk.BooleanVar()
        # self.autoSave = tk.BooleanVar()
        
        self.paused = False
        self.playback = 0.0
        self.audioLength = 0
        self.volume = tk.IntVar(value=50)

        self.res = tk.StringVar(value=8) # The project resolution (8 is default)
        self.currentFrame = tk.StringVar(value='1')
        self.currentFrame_mem = 1 # Remember the frame (for inserting a frame)
        self.framerateDelay = -1 # Default value (Unasigned)
        self.framerate = -1 # FPS
        self.frameStorage = None # Stores a frame when copying and pasting
        self.frameCount = 0 # How many frame are in the project
        self.cacheIndex = 0 # Where we are in the history

        self.clickCoords = {} # Where we clicked on the canvas
        self.shiftCoords = {} # Where we shifted on the canvas
        self.undoCache = [] # Stores the undo data in frame dictionaries

        self.showAlphaVar = tk.BooleanVar()
        self.showGridVar = tk.BooleanVar(value=True)
        self.gridColor = '#000000'
        self.colorPickerData = ('0,0,0', '#000000') #Stores the data from the color picker

        self.isShifting = False
        self.isPlaying = False
        self.control = False
        self.gotoOpen = False
        self.exportOpen = False
        self.modifierUIOpened = False

        self.complexProjectFileSample = {
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
                ],
            "variables": [
                    {}
                ]
            }
        
        self.simpleProjectFileSample = {
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
                ]
            }

        root.bind_all('<Control-s>', lambda e: self.save(True))
        root.bind_all('<Command-s>', lambda e: self.save(True))
        
        root.bind_all('<KeyRelease-Shift_L>', lambda e: self.set_isShifting_false())
        root.bind_all('<KeyRelease-Shift_R>', lambda e: self.set_isShifting_false())
        
        root.bind('<Control-z>', lambda e: self.undo())
        root.bind('<Command-z>', lambda e: self.undo())
        root.bind('<Control-y>', lambda e: self.redo())
        root.bind('<Command-y>', lambda e: self.redo())
        root.bind('<Control-Shift-Z>', lambda e: self.redo()) # 'Z' is capital because you are holding down shift
        root.bind('<Command-Shift-Z>', lambda e: self.redo())
        
        root.bind('<l>', lambda e: self.load_frame())
        root.bind('<*>', lambda e: self.root_nodrag())
        root.bind('<Shift-Leave>', lambda e: try_delete_guide())

        self.load()
        
    def root_drag(self) -> None:
        if mixer.music.get_busy:
            root.bind('<Motion>', lambda e: self.root_nodrag())
            mixer.music.set_pos(self.playback)
        
    def root_nodrag(self) -> None:
        if mixer.music.get_busy:
            if self.audioFile != None:
                mixer.music.set_pos(self.playback)
            self.currentFrame.set(max(int(self.currentFrame.get()) - 2, 1))
            root.unbind("<Motion>")

    def undo(self) -> None:
        if self.cacheIndex == 0:
            return

        self.cacheIndex -= 1
        cache: dict = self.undoCache[self.cacheIndex]
        frame: list = cache[frameIndex := str(list(cache.keys())[0])]

        if (goto := (frameIndex[frameIndex.find('_') + 1:])) != self.currentFrame.get():
            self.currentFrame.set(str(goto))
            # if f'frame_' + self.currentFrame.get() not in self.jsonFrames[0].keys():
            #     self.currentFrame.set(str(goto-1))
            #     self.insert_frame()

        self.jsonFrames[0][frameIndex] = frame[0]
            
        self.projectData['frames'] = self.jsonFrames
        self.load_frame()
        
    def redo(self) -> None:
        if self.cacheIndex == len(self.undoCache):
            return

        cache: dict = self.undoCache[self.cacheIndex]
        frame: list = cache[frameIndex := str(list(cache.keys())[0])]
        
        if (goto := (frameIndex[frameIndex.find('_') + 1:])) != self.currentFrame.get():
            self.currentFrame.set(str(goto))
            self.load_frame()
            
        self.jsonFrames[0][frameIndex] = frame[1]

        self.projectData['frames'] = self.jsonFrames
        self.load_frame()
        
        self.cacheIndex += 1
        
    def load(self) -> None:
        def openDir(): # Opens the project directory
            os.chdir(self.projectDir[:self.projectDir.rfind('/')])
            
            if sys.platform == 'win32':
                os.system(f'Explorer .')
            else:
                os.system('open .')
        
        # Start the pygame mixer for audio playback
        mixer.pre_init(buffer=4096, channels=1, frequency=48000)
        mixer.init()
        self.change_volume()
        
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
        # self.fileMenu.add_separator()
        # self.fileMenu.add_checkbutton(label="Auto-Save", variable=self.autoSave, state=tk.DISABLED)

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
        self.frameTop.pack(anchor=tk.N, padx=8)
        
        # Make the column sizes the same
        for i in range(3):
            self.frameTop.grid_columnconfigure(i, weight=1, uniform='topFrame')

        # Add middle/canvas frame
        self.frameMiddle = tk.Frame(root, width=870, height=870, highlightthickness=3, highlightbackground="white")
        self.frameMiddle.pack(anchor=tk.S, pady=(10, 0))
        self.frameMiddle.pack_propagate(False)

        # Add bottom frame
        self.frameBottom = tk.Frame(root, width=1080, height=40)
        self.frameBottom.pack(side=tk.BOTTOM, pady=(0, 3))
        self.frameBottom.pack_propagate(False)

        # Top frame widgets
       
        #Add the color picker
        self.colorPickerFrame = tk.Frame(self.frameTop, highlightthickness=2, highlightbackground='black')
        self.colorPickerFrame.grid(row=0, column=0, sticky=tk.NW, pady=(10, 0))
        self.colorPickerButton = tk.Button(self.colorPickerFrame, text="Color Picker", command=self.ask_color, font=('Calibri', 14))
        self.colorPickerButton.pack()

        # Add the tools:

        # Key binds
        root.bind('q', lambda e: self.tool_select(1))
        root.bind('w', lambda e: self.tool_select(2))
        root.bind('e', lambda e: self.tool_select(3))
        root.bind('r', lambda e: self.tool_select(4))
        root.bind('t', lambda e: self.tool_select(5))
        root.bind('c', lambda e: print(self.undoCache))

        root.bind('<Return>', lambda e: root.focus())
        root.bind('<Escape>', lambda e: self.esc())
        
        root.bind('<p>', lambda e: (mixer.music.stop() if mixer.music.get_busy() else mixer.music.play()))
        root.bind('<Control-n>', lambda e: self.new_file_dialog())
        root.bind('<Control-o>', lambda e: self.open_file(True))
        root.bind('<Control-q>', lambda e: self.quit())

        WIDTH = (6 if sys.platform == 'win32' else 2)

        # Frame
        self.toolsFrame = tk.LabelFrame(self.frameTop, text="Tools", height=60, width=380, fg='black')
        self.toolsFrame.grid(row=0, column=1, sticky=tk.N)
        self.toolsFrame.propagate(False)

        # Pen
        self.penFrame = tk.Frame(self.toolsFrame, height=2, width=WIDTH, highlightthickness=2, highlightbackground='red')
        self.penFrame.pack(side=tk.LEFT, padx=4)

        tk.Button(self.penFrame, text="Pen", relief=tk.RAISED, height=2, width=WIDTH, command=lambda: self.tool_select(1)).pack()

        # Eraser
        self.eraserFrame = tk.Frame(self.toolsFrame, height=2, width=WIDTH, highlightthickness=2, highlightbackground='white')
        self.eraserFrame.pack(side=tk.LEFT, padx=4)

        tk.Button(self.eraserFrame, text="Eraser", relief=tk.RAISED, height=2, width=WIDTH, command=lambda: self.tool_select(2)).pack()

        # Remove tool
        self.removeFrame = tk.Frame(self.toolsFrame, height=2, width=WIDTH, highlightthickness=2, highlightbackground='white')
        self.removeFrame.pack(side=tk.LEFT, padx=4)
       
        tk.Button(self.removeFrame, text="Remove", relief=tk.RAISED, height=2, width=WIDTH, command=lambda: self.tool_select(3)).pack()

        # Repalce tool
        self.replaceFrame = tk.Frame(self.toolsFrame, height=2, width=WIDTH, highlightthickness=2, highlightbackground='white')
        self.replaceFrame.pack(side=tk.LEFT, padx=4)
       
        tk.Button(self.replaceFrame, text="Replace", relief=tk.RAISED, height=2, width=WIDTH, command=lambda: self.tool_select(4)).pack()
        
        # Fill tool
        self.fillFrame = tk.Frame(self.toolsFrame, height=2, width=WIDTH, highlightthickness=2, highlightbackground='white')
        self.fillFrame.pack(side=tk.LEFT, padx=4)
       
        tk.Button(self.fillFrame, text="Fill", relief=tk.RAISED, height=2, width=WIDTH, command=lambda: self.tool_select(5)).pack()

        # Add frame display
        frameDisplayFrame = tk.Frame(self.frameTop, width=200, height=20)
        frameDisplayFrame.grid(row=0, column=2, sticky=tk.NE)
        self.decreaseFrameButton = tk.Button(frameDisplayFrame, text="-", command=self.decrease_frame, state='disabled', font=('Courier New', 9))
        self.decreaseFrameButton.pack(side=tk.LEFT, padx=((200 if sys.platform == 'win32' else 100), 0), pady=(10, 0))
        self.frameDisplayButton = tk.Menubutton(frameDisplayFrame, textvariable=self.currentFrame, width=6, disabledforeground='black', relief=tk.RIDGE)
        self.frameDisplayButton.pack(pady=(10, 0), side=tk.LEFT)
        self.increaseFrameButton = tk.Button(frameDisplayFrame, text="+", command=self.increase_frame, font=('Courier New', 9), state='disabled')
        self.increaseFrameButton.pack(side=tk.LEFT, pady=(10, 0))

        # Volume
        volumeStyle = ttk.Style()
        volumeStyle.theme_use("default")

        self.volumeSlider = ttk.Scale(root, length=164, from_=0, to=100, variable=self.volume, style='blue.Horizontal.TScale', command=lambda e: self.change_volume())
        self.volumeSlider.place(relx=.8, rely=.964)

        # Add play button
        self.playButton = tk.Button(self.frameBottom, text="<No Project>", state='disabled', height=2, width=32, command=lambda: self.play_init(False))
        self.playButton.place(relx=.5, rely=.5, anchor='center')
        
        root.bind('<KeyPress-Control_L>', lambda e: self.play_button_mode(True))
        root.bind('<KeyRelease-Control_L>', lambda e: self.play_button_mode(False))

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

    def get_click_coords(self, event: tk.Event) -> None:
        self.clickCoords = event

    def return_data_set_true(self) -> None:
        self.returnData = True

    def ask_color(self) -> None:
        color = ch.askcolor(initialcolor=self.colorPickerData[1])
        if color == (None, None):
            return

        self.colorPickerData = color
        if self.colorPickerData:
            self.colorPickerFrame.config(highlightbackground=self.colorPickerData[1]) # Set the border of the button to the chosen color

    def pick_color(self, event: tk.Event) -> None:
        self.selectedPixel = self.canvas.find_closest(event.x, event.y)
        self.colorPickerData = ['None'] # Add a placeholder item
        self.colorPickerData.append(self.canvas.itemcget(self.selectedPixel, option='fill') if self.canvas.itemcget(self.selectedPixel, option='fill') != 'white' else '#ffffff')
        self.colorPickerFrame.config(highlightbackground = self.colorPickerData[1])

    def tool_select(self, tool: int) -> None:
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
                self.replaceFrame.config(highlightbackground='red')
            elif tool == 5:
                self.fillFrame.config(highlightbackground='red')

    def update_title(self) -> None:
        root.title("Pixel-Art Animator-" + self.projectDir)

    def update_grid(self, triggered: bool) -> None:
        if self.showGridVar.get():
            for pixel in self.pixels:
                self.canvas.itemconfig(str(pixel), outline=self.gridColor)
        else:
            for pixel in self.pixels:
                self.canvas.itemconfig(str(pixel), outline='')

        if triggered:
            root.title("Pixel-Art Animator-" + self.projectDir + '*')

    def set_grid_color(self, menu: bool) -> None:
        if menu:
            color = ch.askcolor()[1]
            if color == (None, None):
                return
            
            self.gridColor = color
            root.title("Pixel-Art Animator-" + self.projectDir + '*')

        if self.showGridVar.get() or not menu:
            for pixel in self.pixels:
                    self.canvas.itemconfig(str(pixel), outline=self.gridColor)

    def new_project_name_filter(self, res: tk.StringVar) -> None:
        try:
            res.set(''.join([i for i in res.get() if i.isdigit()]))
            if int(res.get()) <= 64 and int(res.get()) > 0:
                pass
            else:
                res.set(64)
        except:
            pass
        
    def new_project_framerate_filter(self, framerate: tk.StringVar) -> None:
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

    def on_unlock(self) -> None:
        self.fileMenu.entryconfig('Rename', state=tk.ACTIVE)
        self.fileMenu.entryconfig('Save', state=tk.ACTIVE)
        self.fileMenu.entryconfig('Save As', state=tk.ACTIVE)
        self.fileMenu.entryconfig('Export', state=tk.ACTIVE)

        self.fileMenu.entryconfig(f"Open Directory in {'Explorer' if sys.platform == 'win32' else 'Finder'}", state=tk.ACTIVE)

        try:
            self.fileMenu.entryconfig('Load Audio', state=tk.ACTIVE)
        except tk.TclError:
            self.fileMenu.entryconfig('Unload Audio', state=tk.ACTIVE)

        self.editMenu.entryconfig('Clear', state=tk.ACTIVE)
        self.editMenu.entryconfig('Fill', state=tk.ACTIVE)
        self.editMenu.entryconfig('Set Framerate', state=tk.ACTIVE)
        self.editMenu.entryconfig('Modifier UI', state=(tk.ACTIVE if self.isComplexProject.get() else tk.DISABLED))
       
        self.displayMenu.entryconfig('Show Grid', state=tk.ACTIVE)
        self.displayMenu.entryconfig('Grid Color', state=tk.ACTIVE)
        self.displayMenu.entryconfig('Show Alpha', state=tk.ACTIVE)

        self.increaseFrameButton['state'] = "normal"
        self.frameDisplayButton['state'] = "normal"
        self.decreaseFrameButton['state'] = 'normal'

        self.playButton.config(state='normal', text="Play")
        
        root.bind('<Control-e>', lambda e: self.export_display())

        root.bind('<KeyPress-Shift_L>', lambda e: self.frame_skip(True))
        root.bind('<KeyPress-Shift_R>', lambda e: self.frame_skip(True))
        root.bind('<KeyRelease-Shift_L>', lambda e: self.frame_skip(False))
        root.bind('<KeyRelease-Shift_R>', lambda e: self.frame_skip(False))

        root.bind('<Right>', lambda e: self.increase_frame())
        root.bind('<space>', lambda e: self.play_space())
        root.bind('<Left>', lambda e: self.decrease_frame())
        
        # For goto
        for i in range(1, 10):
            root.bind(f'<KeyPress-{i}>', lambda e, num = i: self.goto(str(num)))

        self.frameMiddle.config(highlightthickness=3, highlightbackground="darkblue")

    def new_file_dialog(self) -> None:
        def quit():
            self.isComplexProject.set(complexValue)
            self.newFileTL.destroy()

        newRes = tk.StringVar(value=self.res.get())
        newFramerate = tk.StringVar(value='10')         
        complexValue = self.isComplexProject.get()
        # We store this so that if the value is changed but a new file is not created,
        # the "isComplexProject" variable will be set back to the correct value.
        
        #Add the toplevel window
        self.newFileTL = tk.Toplevel(width=128, height=320)
        self.newFileTL.attributes("-topmost", True)
        self.newFileTL.protocol('WM_DELETE_WINDOW', quit)
        self.newFileTL.resizable(False, False)
        self.newFileTL.title("New File")
        self.newFileTL.focus()
        self.newFileTL.bind('<Escape>', lambda e: quit)
        self.newFileTL.bind('<Return>', lambda e: self.create_new_file(newRes))
       
        #Add the main frame
        newFileFrame = tk.Frame(self.newFileTL, height=156, width=256)
        newFileFrame.pack()
        newFileFrame.pack_propagate(False)
        
        newFramerateEntry = tk.Entry(newFileFrame, textvariable=newFramerate, width=3, font=('Courier New', 15))
        newFramerateEntry.pack(side=tk.BOTTOM)
        tk.Label(newFileFrame, text="Framerate:", font=('Courier New', 12)).pack(side=tk.BOTTOM)

        tk.Button(newFileFrame, text="Create Project", command=lambda: self.create_new_file(newRes, newFramerate), font=('Calibri', 12)).pack(side=tk.TOP)
        newFileSetResolutionEntry = tk.Entry(newFileFrame, textvariable=newRes, width=3, font=('Courier New', 15))
        newFileSetResolutionEntry.pack(side=tk.BOTTOM)
        tk.Label(newFileFrame, text="Project Resolution:", font=('Courier New', 12)).pack(side=tk.BOTTOM, pady=(0, 8))
        
        tk.Checkbutton(self.newFileTL, text='Complex Project', variable=self.isComplexProject, font=('Courier New', 12)).pack(side=tk.BOTTOM, pady=8)

        newRes.trace_add('write', lambda e1, event2, event3: self.new_project_name_filter(newRes))
        newFramerate.trace_add('write', lambda e1, event2, event3: self.new_project_framerate_filter(newFramerate))
       
    def create_new_file(self, res: tk.StringVar, framerate: tk.StringVar) -> None:
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
                    
            self.delay(framerate.get())

            # Create the data files for the project
            if self.isComplexProject.get():
                self.complexProjectFileSample['data']['resolution'] = self.res.get() # Write the file resolution
                self.complexProjectFileSample['data']['gridcolor'] = self.gridColor
                self.complexProjectFileSample['data']['showgrid'] = int(self.showGridVar.get())
                self.complexProjectFileSample['data']['framerate'] = self.framerate
                self.complexProjectFileSample['data']['output'] = self.outputDirectory.get()

                self.jsonSampleDump = json.dumps((self.complexProjectFileSample), indent=4, separators=(',', ':')) # Read the project data as json text
                
            else:
                self.simpleProjectFileSample['data']['resolution'] = self.res.get() # Write the file resolution
                self.simpleProjectFileSample['data']['gridcolor'] = self.gridColor
                self.simpleProjectFileSample['data']['showgrid'] = int(self.showGridVar.get())
                self.simpleProjectFileSample['data']['framerate'] = self.framerate
                self.simpleProjectFileSample['data']['output'] = self.outputDirectory.get()

                self.jsonSampleDump = json.dumps((self.simpleProjectFileSample), indent=4, separators=(',', ':')) # Read the project data as json text

            #Write the file resolution to the file
            self.settingsFile = open(self.projectDir, 'w')
            self.settingsFile.write(self.jsonSampleDump)
            self.settingsFile.close()
            
            self.projectData = self.complexProjectFileSample
            self.jsonFrames = self.projectData['frames']
            
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
            
    def set_framerate(self) -> None:
        framerate = simpledialog.askinteger(title="Set Framerate", prompt="Set framerate (1 - 60):", minvalue=1, maxvalue=60)
        if framerate != None:
            self.delay(framerate)
            root.title("Pixel-Art Animator-" + self.projectDir + "*")

    def open_file(self, dialog: bool) -> None:
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
                                
                                mixer.music.queue(self.audioFile)
                                mixer.music.load(self.audioFile)
                                
                                audio = mutagen.File(self.audioFile)
                                self.audioLength = audio.info.length
                                self.audioLength = int((self.audioLength % 60) * 1000)
                                
                                try:
                                    self.fileMenu.entryconfig("Load Audio", label="Unload Audio")
                                except TclError:
                                    pass
                        else:
                            try:
                                self.fileMenu.entryconfig("Unload Audio", label="Load Audio")
                            except TclError:
                                pass
                    
                self.projectDir = self.fileOpen
                
                self.currentFrame.set(1) # Reset the current frame
                self.playback = 0
                self.isPlaying = False

                self.res.set(self.projectData['data']['resolution']) # Load resolution
                self.showGridVar.set(self.projectData['data']['showgrid']) # Load grid state
                self.gridColor = self.projectData['data']['gridcolor'] # Load grid color
                self.framerate = self.projectData['data']['framerate'] # Load framerate
                self.outputDirectory.set(self.projectData['data']['output'])
                
                if 'modifiers' in self.projectData.keys():
                    self.isComplexProject.set(True)
                else:
                    self.isComplexProject.set(False)

                self.delay(self.framerate) # Set the framerate to the saved framerate

            except IndentationError:
                mb.showerror(title="Project", message=f"Failed to load {self.fileOpen}; Unknown Error!")
                return
            
            self.add_canvas(True)
            self.modifierUIOpened = False
            
            if self.showAlphaVar.get():
                self.load_frame()
            
            self.exportOpen = False
            root.focus_force()
            
    def load_audio(self) -> None:
        if self.audioFile == None: # So unload audio button doesn't open the file dialog
            audioPath = fd.askopenfilename(
                title="Open audio file",
                filetypes=(("mp3", '*.mp3'),("wav", '*.wav'))
            )

            if len(audioPath) > 1:
                root.title("Pixel-Art Animator-" + self.projectDir + '*')
                self.fileMenu.entryconfig("Load Audio", label="Unload Audio")
                self.audioFile = audioPath
                mixer.music.unload()
                self.paused = False
                try:
                    mixer.music.load(self.audioFile)

                    audio = mutagen.File(self.audioFile)
                    self.audioLength = audio.info.length
                    self.audioLength = int((self.audioLength % 60) * 1000)
                except error: # pygame error
                    mb.showerror(title='Audio', message='Failed to load audio!')
            else:
                try:
                    self.fileMenu.entryconfig("Unload Audio", label="Load Audio")
                except TclError:
                    pass

                self.audioFile = None
                mixer.music.unload()
                
        else:
            try:
                self.fileMenu.entryconfig('Unload Audio', label='Load Audio')
            except error:
                pass
            root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
            self.audioFile = None

    def save(self, all: bool) -> None:
        if not self.showAlphaVar.get(): # If show alpha is not toggled
            if '*' == root.title()[-1]:
                with open(self.projectDir, 'r+') as self.fileOpen:
                    #self.projectData = json.load(self.fileOpen)
                    self.projectData['data']['resolution'] = self.res.get()
                    self.projectData['data']['gridcolor'] = self.gridColor
                    self.projectData['data']['showgrid'] = int(self.showGridVar.get())
                    self.projectData['data']['audio'] = self.audioFile
                    self.projectData['data']['framerate'] = self.framerate
                    self.projectData['data']['output'] = self.outputDirectory.get()

                    if all:
                        self.save_frame()
                        self.cacheIndex = 0
                        self.undoCache.clear()
                        self.frameMiddle.config(highlightthickness=3, highlightbackground="darkblue")
                   
                    self.jsonSampleDump = json.dumps(self.projectData, indent=4, separators=(',', ':')) # Read the project data as json text
                    self.fileOpen.seek(0)
                    self.fileOpen.truncate(0)
                    self.fileOpen.write(self.jsonSampleDump)
                    
                    if all:
                        # Load new file data
                        self.projectData = json.loads(self.jsonSampleDump)
                        self.jsonFrames = self.projectData['frames']
                        
                    root.title(root.title()[0:-1]) # Remove the star in the project title
                    
    def save_frame(self) -> None:
        colorFrameDict = {}
        frameCache = {'frame_' + self.currentFrame.get(): ['', '']} # Store the data before and after saving
        frameCache['frame_' + self.currentFrame.get()][0] = self.jsonFrames[0]['frame_' + self.currentFrame.get()]

        for pixel in self.pixels:
            pixelColor = self.canvas.itemcget(pixel, option='fill') # Get the colors of each pixel
            if pixelColor == 'white':
                continue

            if self.isComplexProject.get():
                colorFrameDict[str(pixel)] = ["", ""]
                colorFrameDict[str(pixel)][0] = pixelColor
                colorFrameDict[str(pixel)][1] = pixelColor
            else:
                colorFrameDict[str(pixel)] = pixelColor

        frameCache['frame_' + self.currentFrame.get()][1] = colorFrameDict

        if frameCache['frame_' + self.currentFrame.get()][0] != frameCache['frame_' + self.currentFrame.get()][1]: # If the frame was changed
            self.cacheIndex += 1

            if self.cacheIndex-1 < len(self.undoCache): # Reset later history if there is any
                self.undoCache = self.undoCache[:self.cacheIndex]
                self.undoCache[self.cacheIndex-1] = frameCache # Add the changes to the undo cache
            else:
                self.undoCache.append(frameCache) # Add the changes to the undo cache
        
        self.jsonFrames[0][f'frame_{self.currentFrame.get()}'] = colorFrameDict
        self.projectData['frames'] = self.jsonFrames

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
            self.load_frame()
            self.save_frame()

    def rename_dialog(self) -> None:
        self.renameVar = tk.StringVar()
        self.renameVar.set(os.path.splitext(os.path.split(self.projectDir)[1])[0])

        # Create the rename window
        renameTL = tk.Toplevel(width=480, height=80)
        renameTL.resizable(False, False)
        renameTL.title("Rename Project")
        renameTL.attributes('-topmost', True)
        
        renameTL.bind('<Return>', lambda e: self.rename(renameTL))
        renameTL.bind('<Escape>', lambda e: renameTL.destroy())

        # Add the rename entry and button:
        rename = tk.Entry(renameTL, width=26, textvariable=self.renameVar, font=('Courier New', 14))
        rename.pack(padx=4)
        rename.focus()
        
        tk.Button(renameTL, width=24, height=2, text="Rename", command=lambda: self.rename(renameTL)).pack()

    def rename(self, renameTL: tk.Toplevel) -> None:
        self.canRename = True # Keeps track of if the new name is valid
        for i in self.renameVar.get():
            if i in r'\/:*?"<>|' or len(self.renameVar.get()) == 0:
                self.canRename = False

        if self.canRename: # If the new name is valid
            os.chdir(os.path.split(self.projectDir)[0])
            os.rename(self.projectDir, self.renameVar.get() + '.' + self.extension)
            self.projectDir = os.path.split(self.projectDir)[0] + '/' + self.renameVar.get() + '.' + self.extension # Set the project directory to the new name
            renameTL.destroy()

            self.update_title()
            self.save(False)

    def add_canvas(self, readPixels: bool) -> None:
        self.returnData = False

        # Update the title
        self.update_title()

        # Delete any previous canvases
        [canvas.destroy() for canvas in self.frameMiddle.winfo_children()]
        self.pixels.clear()

        self.canvas = tk.Canvas(self.frameMiddle, height=866, width=866)
        self.canvas.pack()
        self.canvas.bind('<Shift-Motion>', self.draw_line_guide)
        

        # Create pixels
        self.toY = int(self.res.get())
        self.posX = 2
        self.posY = 2

        loading = tk.Label(root, text='Loading...', font=('Default', 100))
        loading.place(x=root.winfo_width()/4, y=root.winfo_height()/2 - 64) # Display the loading screen
        root.update()

        self.fileOpen = open(self.projectDir, 'r')
        if readPixels:
            self.projectData = json.load(self.fileOpen)
            
        if self.showAlphaVar.get(): # If show alpha is selected, disable it before drawing to the canvas
            self.display_alpha(False)
                
        pixelate = (self.canvas.winfo_width()-5)/int(self.res.get())

        for pix in range(int(self.res.get())**2):                                                                                                       # Save coords for use with the fill tool
            pixel = self.canvas.create_rectangle(self.posX, self.posY, self.posX + pixelate, self.posY + pixelate, fill='white', tags=f'^"x_0":{self.posX},"y_0":{self.posY},"x_1":{self.posX + pixelate},"y_1":{self.posY + pixelate}&'.replace('^', '{').replace('&', '}'))

            self.canvas.tag_bind(pixel, "<ButtonPress-1>", lambda e: self.on_press(e))
            self.canvas.tag_bind(pixel, "<B1-Motion>", lambda e: self.on_press(e))
            self.canvas.tag_bind(pixel, "<ButtonRelease-1>", lambda e: self.on_release())

            self.pixels.append(pixel)

            # Set the pixel color
            if readPixels:
                self.jsonFrames = self.projectData['frames']
                try:
                    self.savedPixelColors = self.jsonFrames[0][f'frame_'+self.currentFrame.get()]
                    self.canvas.itemconfig(pixel, fill=self.savedPixelColors[str(pixel)][1 if self.isComplexProject.get() else 0:])

                except KeyError: # If the pixel is not present within the json file
                    self.canvas.itemconfig(pixel, fill='white') # Fill pixels with white (0 alpha)

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

    def on_press(self, event: dict) -> None:
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
                    self.canvas.itemconfig(self.selectedPixel, fill=self.colorPickerData[1])

            elif self.eraserFrame['highlightbackground'] == 'red': # If the eraser mode is selected...
                self.canvas.itemconfig(self.selectedPixel, fill='white')

            elif self.removeFrame['highlightbackground'] == 'red': # If the remove mode is selected...
                self.canvas_remove_color()

            elif self.replaceFrame['highlightbackground'] == 'red': # If the replace mode is selected...
                if not self.canvas.itemcget(self.selectedPixel, option='fill') == self.colorPickerData[1]: # If the pixel color is already the pen color
                    self.canvas_replace_color()

            elif self.fillFrame['highlightbackground'] == 'red': # If the fill mode is selected...
                if not self.canvas.itemcget(self.selectedPixel, option='fill') == self.colorPickerData[1]: # If the pixel color is already the pen color
                    selectedPixel = self.canvas.find_closest(self.clickCoords.x, self.clickCoords.y)
                    selectedColor = self.canvas.itemcget(selectedPixel, option='fill')
                    offset = self.canvas.winfo_width() / int(self.res.get())
                    
                    # Calculate the coords of the center of the pixel (gets rid of chance that not all tiles will be filled)
                    tags = json.loads(self.canvas.itemcget(selectedPixel, 'tags')[:-8])
                    pos_x = tags['x_0'] + ((tags['x_1'] - tags['x_0']) / 2)
                    pos_y = tags['y_0'] + ((tags['y_1'] - tags['y_0']) / 2)

                    self.canvas_fill_recursive((pos_x, pos_y), offset, selectedColor)
        except:
            pass # I don't want it to yell at me
        
    def set_shift_coords(self, event: tk.Event) -> None:
        self.shiftCoords['x'] = event.x
        self.shiftCoords['y'] = event.y
        
    def draw_line_guide(self, event: tk.Event) -> None: # Guess
        if not self.penFrame.cget('highlightbackground') == 'red' or self.isPlaying:
            return

        if not self.isShifting:
            self.set_shift_coords(event)
            self.isShifting = True

        if self.canvas.find_withtag('guide') != ():
            self.canvas.delete(self.canvas.find_withtag('guide')[0])

        line = self.canvas.create_line(self.shiftCoords['x'], self.shiftCoords['y'], event.x, event.y, tags='guide', width=8, activefill=self.colorPickerData[1], capstyle=tk.ROUND)
        self.canvas.tag_bind(line, '<Leave>', lambda e: self.canvas.delete(line))
        self.canvas.tag_bind(line, '<Shift-Leave>', lambda e: self.canvas.delete(line))
        self.canvas.tag_bind(line, '<Button-1>', lambda e: self.draw_line(line))
            
    def draw_line(self, line: int) -> None:
        root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
        for pixel in self.pixels:
            coords = self.canvas.coords(str(pixel))
            overlap = self.canvas.find_overlapping(coords[0], coords[1], coords[2], coords[3])
            for selected in overlap:
                if self.canvas.itemcget(str(selected), 'tags')[0] == 'g': # 'g' is in 'guide'
                    self.canvas.itemconfig(str(pixel), fill=self.colorPickerData[1])
                    break
        
        self.canvas.delete(line)
        self.save_frame()
        
    def set_isShifting_false(self) -> None:
        self.isShifting = False
        
    def on_release(self) -> None:
        if self.isPlaying or self.showAlphaVar.get():
            return
        
        self.save_frame()

    def canvas_clear(self) -> None:
        for pixel in self.pixels:
            self.canvas.itemconfig(pixel, fill='white')
        
        root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
        self.frameMiddle.config(highlightbackground="red")
        self.save_frame()

    def canvas_fill(self) -> None:
        fillColor = ch.askcolor()
        if fillColor != (None, None): # If we selected a color (didn't hit cancel)
            for pixel in self.pixels:
                self.canvas.itemconfig(pixel, fill=fillColor[1])

            root.title("Pixel-Art Animator-" + self.projectDir + '*')
            self.frameMiddle.config(highlightbackground="red")
            self.save_frame()

    def canvas_remove_color(self) -> None:
        selectedPixel = self.canvas.find_closest(self.clickCoords.x, self.clickCoords.y)
        selectedColor = self.canvas.itemcget(selectedPixel, option='fill')
        for pixel in self.pixels:
            if self.canvas.itemcget(pixel, option='fill') == selectedColor:
                self.canvas.itemconfig(pixel, fill='white')
                
    def canvas_replace_color(self) -> None:
        selectedPixel = self.canvas.find_closest(self.clickCoords.x, self.clickCoords.y)
        selectedColor = self.canvas.itemcget(selectedPixel, option='fill')
        for pixel in self.pixels:
            if self.canvas.itemcget(pixel, option='fill') == selectedColor:
                self.canvas.itemconfig(pixel, fill=self.colorPickerData[1])
        
    def canvas_fill_recursive(self, pos: tuple | list, offset: float, color: str) -> None:
        selectedPixel = self.canvas.find_closest(pos[0], pos[1])

        if self.canvas.itemcget(selectedPixel, 'fill') == color:
            self.canvas.itemconfig(selectedPixel, fill=self.colorPickerData[1])

            self.canvas_fill_recursive((pos[0] + offset, pos[1]), offset, color)
            self.canvas_fill_recursive((pos[0] - offset, pos[1]), offset, color)
            self.canvas_fill_recursive((pos[0], pos[1] + offset), offset, color)
            self.canvas_fill_recursive((pos[0], pos[1] - offset), offset, color)

    def insert_frame(self) -> None: # Inserts a frame after the current frame
        self.currentFrame_mem = int(self.currentFrame.get())
        self.frameCount += 1

        root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title

        # Get the number of frames
        self.jsonFrames = self.projectData['frames']
        self.jsonFrames[0][f'frame_{int(len(self.jsonFrames[0])) + 1}'] = {}      

        for loop in range(int(len(self.jsonFrames[0])) - self.currentFrame_mem):
            # Get the data from the previous frame and copy it to the current frame
            self.jsonFrames[0][f'frame_{int(len(self.jsonFrames[0])) - loop}'] = self.jsonFrames[0][f'frame_{int(len(self.jsonFrames[0])) - loop - 1}']
           
        self.currentFrame.set(self.currentFrame_mem + 1)
        self.save_frame()

    def delete_frame(self) -> None:
        root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
        self.frameMiddle.config(highlightthickness=3, highlightbackground="darkblue")
        newData = copy.deepcopy(self.jsonFrames) # Create a copy of the frame list (as to not change the original durring iteration)
        
        if self.frameCount != 1:
            self.frameCount -= 1
        
        # Reset the undo cache (may change later)
        self.cacheIndex = 0
        self.undoCache = {}
            
        frameIterate = int(self.currentFrame.get())
        
        for frame in range(int(self.currentFrame.get()), len(self.jsonFrames[0]) + 1):
            if frameIterate != len(self.jsonFrames[0]): # If the frame is not the last frame, copy the data from the next frame
                newData[0][f'frame_{frameIterate}'] = self.jsonFrames[0][f'frame_{frameIterate + 1}']
                frameIterate += 1
            else: # Remove the last frame
                for loop, frame in enumerate(self.jsonFrames[0]):
                    if loop + 1 == len(self.jsonFrames[0]):
                        del newData[0][frame]

        if int(self.currentFrame.get()) == len(self.jsonFrames[0]) and self.currentFrame.get() != "0": # If you are on the previous last frame, move back one frame
            self.currentFrame.set(int(self.currentFrame.get()) - 1)
        try:
            self.jsonFrames[0] = newData[0]
            self.load_frame()
        except KeyError:
            self.currentFrame.set(1)
            self.canvas_clear()
        self.save_frame()

    def increase_frame(self) -> None:
        if self.frameCount == 1:
            return
            
        if int(self.currentFrame.get()) != int(len(self.jsonFrames[0])):
            self.currentFrame.set(str(int(self.currentFrame.get()) + 1))

        else: # Go to beginning
            self.currentFrame.set(1)
            if self.audioFile != None:
                if mixer.music.get_busy():
                    mixer.music.set_pos(0.001)
                else:
                    if self.isPlaying:
                        mixer.music.play()
            
        self.load_frame()
       
    def decrease_frame(self) -> None:
        if self.frameCount == 1:
            return
            
        self.currentFrame.set(str(int(self.currentFrame.get()) - 1))

        if int(self.currentFrame.get()) < 1:
            self.currentFrame.set(int(len(self.jsonFrames[0])))

        if self.audioFile != None:
            self.get_playback_pos()

        self.load_frame()

    def frame_skip(self, mode: bool) -> None: # Displays the '→←' text or the '+-' text, depending on current functionality
        if mode == True:
            self.increaseFrameButton.config(text="→", command=self.to_last)
            self.decreaseFrameButton.config(text="←", command=self.to_first)

            root.bind('<Right>', lambda e: self.to_last())
            root.bind('<Left>', lambda e: self.to_first())
        else:
            self.increaseFrameButton.config(text="+", command=self.increase_frame)
            self.decreaseFrameButton.config(text="-", command=self.decrease_frame)

            root.bind('<Right>', lambda e: self.increase_frame())
            root.bind('<Left>', lambda e: self.decrease_frame())

    def to_first(self) -> None: # Go to first frame
        self.currentFrame.set(1)
        self.load_frame()

    def to_last(self) -> None: # Go to last frame
        self.currentFrame.set(self.frameCount)
        self.load_frame()

    def load_frame(self, loadFile: bool = False) -> None: # Display the frame
        if loadFile:
            with open(self.projectDir, 'r') as self.fileOpen:
                self.projectData = json.load(self.fileOpen)
                self.jsonFrames = self.projectData['frames']

        if len(self.jsonFrames[0][f'frame_' + self.currentFrame.get()]) == 0: # If the frame is empty
            for pixel in range(int(self.res.get())**2):
                self.canvas.itemconfig(self.pixels[pixel], fill='white') # Fill pixels with white (0 alpha)
            return

        self.savedPixelColors = self.jsonFrames[0][f'frame_' + self.currentFrame.get()]

        # Code here is spread out to maximize speed
        if self.showAlphaVar.get(): # If show alpha is selected
            for pixel in range(int(self.res.get())**2):
                self.canvas.itemconfig(self.pixels[pixel], fill=('black' if self.savedPixelColors.get(str(self.pixels[pixel])) else 'white'))
        else:
            if self.isComplexProject.get():
                for pixel in range(int(self.res.get())**2):
                    if self.savedPixelColors.get(str(self.pixels[pixel])):
                        self.canvas.itemconfig(self.pixels[pixel], fill=self.savedPixelColors[str(self.pixels[pixel])][1])
                    else:
                        self.canvas.itemconfig(self.pixels[pixel], fill='white')
            else:
                for pixel in range(int(self.res.get())**2):
                    if self.savedPixelColors.get(str(self.pixels[pixel])):
                        self.canvas.itemconfig(self.pixels[pixel], fill=self.savedPixelColors[str(self.pixels[pixel])])
                    else:
                        self.canvas.itemconfig(self.pixels[pixel], fill='white')

        if self.audioFile != None:
            self.get_playback_pos()

    def load_from(self, frame: int) -> None:
        for pixel in range(int(self.res.get())**2):
            try:
                self.savedPixelColors = self.jsonFrames[0][f'frame_{frame}']

                if self.canvas.itemcget(self.pixels[pixel], option='fill') != self.savedPixelColors[str(self.pixels[pixel])][1 if self.isComplexProject.get() else 0:]:
                    root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
                self.canvas.itemconfig(self.pixels[pixel], fill=self.savedPixelColors[str(self.pixels[pixel])][1 if self.isComplexProject.get() else 0:])
            except:
                self.canvas.itemconfig(self.pixels[pixel], fill='white')

        self.save_frame(True)

    def display_alpha(self, triggered: bool) -> None:
        if triggered and self.showAlphaVar.get(): #If this was triggered by pressing the show alpha button
            if '*' == root.title()[-1]:
                self.save_frame() # Save the current image

        if self.showAlphaVar.get():
            for pixel in self.pixels:
                    self.frameDisplayButton.config(state=tk.DISABLED)
                    self.canvas.itemconfig(pixel, fill=['black' if self.canvas.itemcget(pixel, option='fill') == 'white' else 'white']) # Show the alpha
        else: # Reload the colors from the file
            self.frameDisplayButton.config(state=tk.NORMAL)
            self.load_frame()

    def goto(self, start: str) -> None:
        text = tk.StringVar(value=start)
        
        def remove(goto):
            gotoTL.destroy()
            self.gotoOpen = False
            if goto:
                if int(text.get()) > self.frameCount:
                    self.currentFrame.set(self.frameCount)
                else:
                    self.currentFrame.set(int(text.get()))
                self.load_frame()
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
            return

        self.gotoOpen = True
        gotoTL = tk.Toplevel()
        gotoTL.title("Goto...")
        gotoTL.geometry('240x64')
        gotoTL.resizable(False, False)
        gotoTL.focus()
        
        tk.Label(gotoTL, width=1000, height=10, textvariable=text, font=('Calibri', 16), justify=tk.LEFT).pack()
        
        gotoTL.bind('<FocusOut>', lambda e: remove(False))
        gotoTL.bind('<Escape>', lambda e: remove(False))
        gotoTL.bind('<Return>', lambda e: remove(True))
        
        for i in range(10):
            gotoTL.bind(f'<KeyPress-{i}>', lambda e, num = i: display(num))
            
        gotoTL.bind('<BackSpace>', lambda e: display(None))

    def quit(self) -> None:
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
            
    def var_filter(self, var: tk.StringVar, min: int, max: int) -> None:
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
        
    def trash(self, directory: str) -> None:
        os.chdir(directory)
        sucess = True
        if len(os.listdir()) > 0:
            try:
                for i in os.listdir():
                    os.remove(i)
            except IndentationError:
                sucess = False
        else:
            sucess = None
        
        self.trashResponce(sucess)
    
    def trashResponce(self, sucess: bool) -> None:
        if sucess == None:
            mb.showinfo(title="Trash", message="No files found!")
        elif sucess:
            mb.showinfo(title="Trash", message="Files deleted successfully!")
        else:
            mb.showerror(title="Trash", message="Failed to delete one or more files!")
            
        self.clearFolderButton.config(state='normal', text="Clear Folder")
        self.exportTL.focus()

    def export_display(self) -> None:
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
        
    def export(self, fileName: str, extension: str, alpha: bool, isSequance: bool, *args, **kwargs) -> None:
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
                root.bell()
                
        def cancelDialog(button = None):
            if button != None:
                button.config(state=tk.DISABLED)
            self.rendering = not mb.askyesno(title="Cancel Render", message="Are you sure you want to cancel the current render?")
            if (self.rendering or self.rendering == None) and button != None:
                button.config(state=tk.NORMAL)
                
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
            
            infoLabel = tk.Label(renderFrameMiddle, text=f"Rendering frame 1 of {floor(frameCount / args[2] + 1)}")
            infoLabel.pack(anchor=tk.W)
            
            progressBar = ttk.Progressbar(renderFrameMiddle, length=420, maximum=frameCount, style="blue.Horizontal.TProgressbar")
            progressBar.pack(pady=(4, 6))
            
            cancelButton = ttk.Button(renderFrameBottom, text="Cancel", width=64)
            cancelButton.config(command=lambda b = cancelButton: cancelDialog(b))
            cancelButton.pack()

            renderTL.update()
            
            frame = 0 # The frame we are rendering
            position = 0

            for i in range(args[0], args[1] + 1):
                if self.rendering:
                    position += 1
                    subStr = '0' * len(str(args[1]))

                    subStr = subStr[: (len(str(args[1])) - len(str(args[0]))) - (len(str(i))-len(str(args[0])))]
                    subStr += str(i)
                    
                    if position % args[2] == 0:
                        img = Image.new(size=(int(self.res.get()), int(self.res.get())), mode=('RGBA' if alpha and usingAlpha else 'RGB'))
                        pixels = self.jsonFrames[0][f"frame_{i}"]
                        px = 0
                        frame += 1

                        for y in range(0,img.size[1]):
                            for x in range(0,img.size[0]):
                                px += 1
                                try:
                                    color = pixels[str(px)][1 if self.isComplexProject.get() else 0:]
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
                        
                        infoLabel.config(text=f"Rendering frame {min(frame + 1, floor(frameCount / args[2] + 1))} of {floor(frameCount / args[2] + 1)}")
                        
                        progressBar.config(value=position)
                        renderTL.update()
                else: # If we cancel the render
                    break
                
            renderTL.attributes('-topmost', True)
            renderTL.protocol('WM_DELETE_WINDOW', lambda e = 1: e) # Do nothing
            cancelButton['command'] = ""

            if self.rendering:
                progressBar.config(style='green.Horizontal.TProgressbar')
                infoLabel.config(text="Finished Rendering!")
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
        
    def hex_to_rgb(self, color: str) -> list:
        color = color[1:]
        return list(int(color[i:i+2], 16) for i in (0, 2, 4))

    def open_output_dir(self) -> None:
        output = fd.askdirectory()
        if len(output) > 1:
            self.outputDirectory.set(output)
            root.title("Pixel-Art Animator-" + self.projectDir + '*')
        self.exportTL.focus()

    def get_playback_pos(self) -> None:
        self.playback = max(self.framerateDelay * float(self.currentFrame.get()) - self.framerateDelay, 0.0000001)  # Get the audio position
        if self.audioFile != None:
            if not mixer.music.get_busy():
                mixer.music.play()
                mixer.music.set_pos(self.playback)
                mixer.music.pause()
    
    def change_volume(self) -> None:
        mixer.music.set_volume(self.volume.get() / 100)

    def play_space(self) -> None:
        if self.control:
            self.play_init(True)
        else:
            self.play_init(False)

    def esc(self) -> None: # Stop the playback by pressing escape
        root.focus()
        if self.isPlaying:
            self.play_init(True)

    def play_init(self, stopMode: bool) -> None:
        loop = False
        if stopMode and not self.isPlaying:
            pass
        elif not self.isPlaying:
            loop = True
        if not self.isPlaying:
            self.currentFrame_mem = int(self.currentFrame.get())

        self.play(stopMode, self.currentFrame_mem, loop)

    def play(self, stopMode: bool, save: int, isLoop: bool) -> None:
        def end():
            self.playButton.config(text="Play")
            root.unbind('<Configure>')

            if stopMode:
                self.currentFrame.set(self.currentFrame_mem)

                self.load_frame()
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
            
            correction = (0.000006787699999999 if sys.platform == 'win32' else 0.000005014499999999)

        while self.isPlaying:
            time1 = timeit.default_timer()
            self.increase_frame()
            root.update()
            if not isLoop:
                if int(self.currentFrame.get()) == self.currentFrame_mem:
                    end()
                    return
            if self.isPlaying:
                time.sleep(max((self.framerateDelay - correction * int(self.res.get())) - (timeit.default_timer() - time1), 0))
        end()

    def play_button_mode(self, isControl: bool) -> None:
        self.control = isControl
        if isControl:
            self.playButton.config(command=lambda: self.play_init(True))
        else:
            self.playButton.config(command=lambda: self.play_init(False))

    def delay(self, delay: int) -> None:
        self.framerate = delay
        self.framerateDelay = max(0.00001, 1 / float(delay))
        root.title("Pixel-Art Animator-" + self.projectDir + '*')
        
    def modifier_ui(self) -> None:
        def draw_frame():
            # Draw the current frame to the preview canvas
            for pixel in range(int(self.res.get())**2):
                if self.jsonFrames[0].get(f'frame_' + self.currentFrame.get()):
                    self.savedPixelColors = self.jsonFrames[0][f'frame_' + self.currentFrame.get()]
                    try:
                        self.previewCanvas.itemconfig(self.pixels[pixel], fill=self.savedPixelColors[str(self.pixels[pixel])][1])
                    except KeyError:
                        self.previewCanvas.itemconfig(self.pixels[pixel], fill='white')
                else:
                    self.savedPixelColors = 'white'
                    self.previewCanvas.itemconfig(self.pixels[pixel], fill='white')
                    
        def draw_grid(showGrid):
            for i in range(int(self.res.get())**2):
                if showGrid:
                    self.previewCanvas.itemconfig(str(i+1), outline=self.gridColor)
                else:
                    self.previewCanvas.itemconfig(str(i+1), outline='')
                    
        # TEMP FUNCTION
        def get():
            for oper in self.operatorFrame.winfo_children():
                if hasattr(oper, 'UUID'):
                    print(oper.name + ' :: ' + str(oper.UUID))
        # TEMP FUNCTION
        
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
            
            self.modifierTL.bind('<u>', lambda e: get())
            
            previewVar = tk.BooleanVar(master=self.modifierTL, value=True)
            gridVar = tk.BooleanVar(master=self.modifierTL, value=False)
            
            root.update()
            
            # Main frames:
            
            # Holds the canvas that holds the frame that holds the operators
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
            operatorCanvas.bind('<Button-1>', lambda e: self.modifierTL.focus())
            
            self.previewFrame = tk.Frame(self.modifierTL, width=560, height=560, highlightbackground='green', highlightthickness=2)
            self.previewFrame.pack(side=tk.TOP, anchor=tk.NW)
            
            self.variableFrame = tk.Frame(self.modifierTL, width=568, height=340, bg='black', highlightbackground='darkblue', highlightthickness=2)
            self.variableFrame.pack(side=tk.BOTTOM, anchor=tk.SW)
            self.variableFrame.pack_propagate(False)
            self.variableFrame.bind('<Button-1>', lambda e: self.modifierTL.focus())
            
            self.previewCanvas = tk.Canvas(self.previewFrame, width=560, height=560, bg='lightblue')
            self.previewCanvas.pack()
            self.previewCanvas.pack_propagate(False)
            self.previewCanvas.bind('<Button-1>', lambda e: self.modifierTL.focus())
            
            root.update()
            
            # Add pixels to preview canvas
            if not self.modifierUIOpened:
                menu = tk.Menu(self.modifierTL, tearoff=False)
                menu.add_checkbutton(label="Preview", variable=previewVar)
                menu.add_checkbutton(label="Grid", variable=gridVar, command=lambda: draw_grid(gridVar.get()))
                
                toY = int(self.res.get())
                posX = 2
                posY = 2

                loading = tk.Label(self.previewCanvas, text='Loading...', font=('Default', 84), bg='lightblue')
                loading.pack(anchor=tk.CENTER, pady=(self.previewCanvas.winfo_height()/2 - 84, 0)) # Display the loading screen
                root.update()

                for i in range(int(self.res.get())**2):
                    pixelate = (self.previewCanvas.winfo_width()-5)/int(self.res.get())
                    self.previewCanvas.create_rectangle(posX, posY, posX + pixelate, posY + pixelate, fill='white')
                    self.previewCanvas.tag_bind(str(i + 1), '<Button-3>', lambda e: menu.tk_popup(e.x_root, e.y_root))

                    posX += pixelate
                    toY -= 1

                    if toY == 0:
                        toY = int(self.res.get())
                        posY += pixelate
                        posX = 2

                loading.destroy()
                
            draw_frame()
                
            # Modifier frame setup
            addButton = tk.Menubutton(self.operatorFrame, text='➕', font=('Calibri', 16), highlightbackground='black', highlightthickness=1)
            addButton.pack(side=tk.TOP, anchor=tk.NW, pady=(0, 1), padx=1)

            addButton.menu = tk.Menu(addButton, tearoff=False)
            addButton['menu'] = addButton.menu
            addButton.menu.add_command(label='Tint Operator', command=lambda: self.add_modifier(0))
            addButton.menu.add_command(label='Monochrome Operator', command=lambda: self.add_modifier(1))

            tk.Frame(self.operatorFrame, width=Operator.WIDTH+PADDING, height=2, highlightbackground='darkblue', highlightthickness=2).pack(side=tk.TOP)
            
            # Variable frame setup:
            variableLinkFrame = tk.Frame(self.variableFrame, width=self.variableFrame.winfo_width()*(1/3)-3, height=self.variableFrame.winfo_height())
            variableLinkFrame.pack(side=tk.LEFT, anchor=tk.W)
            variableLinkFrame.pack_propagate(False)
            
            variableListFrame = tk.Frame(self.variableFrame, width=self.variableFrame.winfo_width()*(2/3)-3, height=self.variableFrame.winfo_height())
            variableListFrame.pack(side=tk.RIGHT, anchor=tk.E)
            
            root.update()
            
            variableListWindow = tk.PanedWindow(variableListFrame, width=variableListFrame.winfo_width(), height=variableListFrame.winfo_height())
            variableListWindow.pack()
            
            variableTypeFrame = tk.Frame(variableListWindow, width=variableListFrame.winfo_width()/4, height=variableListFrame.winfo_height())
            variableNameFrame = tk.Frame(variableListWindow, width=variableListFrame.winfo_width()/2, height=variableListFrame.winfo_height())
            variableValueFrame = tk.Frame(variableListWindow, width=variableListFrame.winfo_width()/4, height=variableListFrame.winfo_height())
            variableTypeFrame.propagate(False)
            variableNameFrame.propagate(False)
            variableTypeFrame.propagate(False)
            
            variableListWindow.add(variableTypeFrame)
            variableListWindow.add(variableNameFrame)
            variableListWindow.add(variableValueFrame)
            
            root.update()
            
            variableListWindow.paneconfig(variableTypeFrame, minsize=10)
            variableListWindow.paneconfig(variableNameFrame, minsize=10)
            variableListWindow.paneconfig(variableValueFrame, minsize=10)
            
            tk.Label(variableTypeFrame, width=variableTypeFrame.winfo_width(), text="Type:", font=('Calibri', 17), underline=True).pack(side=tk.TOP)
            tk.Label(variableNameFrame, width=variableNameFrame.winfo_width(), text="Name:", font=('Calibri', 17), underline=True).pack(side=tk.TOP)
            tk.Label(variableValueFrame, width=variableValueFrame.winfo_width(), text="Value:", font=('Calibri', 17), underline=True).pack(side=tk.TOP)
            
            tk.Label(variableLinkFrame, width=variableLinkFrame.winfo_width(), text="Linker:", font=('Calibri', 17), underline=True).pack(side=tk.TOP)
            
            # Add var type menus
            for i in range(12):
                button = ttk.Menubutton(variableTypeFrame, width=variableTypeFrame.winfo_width(), name=str(i))
                button.pack(side=tk.TOP)
                button.menu = tk.Menu(button, tearoff=False)
                button.variable = tk.StringVar(value='none')
                button['menu'] = button.menu
                button.config(textvariable=button.variable)
                
                button.menu.add_radiobutton(label='none', variable=button.variable, command=lambda _id=button.winfo_name(), var=button.variable: self.set_row(var, _id, variableNameFrame, variableValueFrame))
                button.menu.add_radiobutton(label='int', variable=button.variable, command=lambda  _id=button.winfo_name(), var=button.variable: self.set_row(var, _id, variableNameFrame, variableValueFrame))
                button.menu.add_radiobutton(label='float', variable=button.variable, command=lambda  _id=button.winfo_name(), var=button.variable: self.set_row(var, _id, variableNameFrame, variableValueFrame))
                button.menu.add_radiobutton(label='string', variable=button.variable, command=lambda  _id=button.winfo_name(), var=button.variable: self.set_row(var, _id, variableNameFrame, variableValueFrame))

            # Add entries
            for iterate, frame in enumerate(('variableNameFrame', 'variableValueFrame')):
                cf:tk.Frame = vars()[frame]
                for i in range(12):
                    tk.Entry(cf, width=cf.winfo_width(), font=('Calibri', 13), name=str(iterate) + '_' + str(i), state=tk.DISABLED).pack(side=tk.TOP)
            
            self.modifierUIOpened = True
            
    def set_row(self, var: tk.StringVar, _id: str, *args: tk.Frame) -> None:
        for frame in (args[0], args[1]):
            for entry in frame.winfo_children():
                if entry.winfo_name()[entry.winfo_name().find('_') + 1:] == str(_id):
                    entry.config(state=tk.DISABLED if var.get() == 'none' else tk.NORMAL)
                
    def add_modifier(self, modifier: int) -> None:
        match modifier:
            case 0:
                TintOperator(self.operatorFrame).pack(anchor=tk.NW)
            case 1:
                MonochromeOperator(self.operatorFrame).pack(anchor=tk.NW)
            case 2:
                ... # TODO: ReplaceOperator(self.operatorFrame).pack(anchor=tk.NW)
            case 3:
                ... # TODO: FillOperator(self.operatorFrame).pack(anchor=tk.NW)
            case 4:
                ... # TODO: NoiseOperator(self.operatorFrame).pack(anchor=tk.NW)



#-----====Main Program Start====-----#
sys.setrecursionlimit(64**2) # So the fill tool works

root = tk.Tk()
root.title("Pixel-Art Animatitor")
root.geometry('1000x1000')
root.resizable(False, False)

m_cls = Main()
root.protocol("WM_DELETE_WINDOW", m_cls.quit) # Open the quit dialogue when closing

root.mainloop()