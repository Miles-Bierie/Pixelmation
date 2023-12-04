import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import colorchooser as ch
import os
import json
import copy
import time
from pygame import mixer
import timeit
import mutagen
from PIL import Image, ImageTk
from math import ceil

class VolumeSlider(tk.Canvas):
    def __init__(self, master=None, *, command=None, to=100,from_=0,**kwargs):
        super().__init__(master, **kwargs)
        self.min_value = from_
        self.max_value = to
        self.value = 0
        self.master = master
        self.slider_width = 20
        self.command_flag = 0
        self.buffer_value = 0
        self.command = command
        self.height = 20  
        self.configure(height=self.height)
        self.set_real_value()   
        self.set_resolution()
        self.slider = self.create_rectangle(self.value, 0, self.value + self.slider_width, self.height, fill='gray', tags='slider')
        self.left_side = self.create_rectangle(0, 0, self.value,self.height, fill='green', tags='left_side')        
        self.right_side = self.create_rectangle(self.value + self.slider_width, 0, self.winfo_width(), self.height, fill='black', tags='right_side')
        self.buffer = self.create_rectangle(self.value + self.slider_width, 2,self.value + self.slider_width + self.buffer_value , self.height-2, fill='blue', tags='buffer')
        self.bind('<Configure>', self.set_resolution)
        self.bind('<Button-1>', self.on_event)
        self.bind('<B1-Motion>', self.on_event)

    def set_real_value(self):
        relation = self.value / (self.winfo_width()-self.slider_width)
        self.real_value = self.min_value + relation * (self.max_value-self.min_value) 

    def set_resolution(self, event = None):
        self.value = (self.real_value / (self.max_value-self.min_value)) * (self.winfo_width()-self.slider_width)
        self.value= max(0, min(self.winfo_width()-self.slider_width, self.value))
        self.set_coords()

    def set_slider(self):
        self.set_coords()
        self.set_real_value()   

    def set_coords(self):
        self.coords('slider', self.value, 0, self.value + self.slider_width, self.height)
        self.coords('left_side', 0,0,self.value,self.height)
        self.coords('right_side', self.value + self.slider_width,0,self.winfo_width(),self.height)
        self.coords('buffer', self.value + self.slider_width, 2,self.value + self.slider_width + self.buffer_value , self.height-2)

    def on_event(self, event):
        self.value = max(0, min(self.winfo_width()-self.slider_width, event.x))
        self.set_slider()
        if self.command and self.command_flag == 0:
            self.command_flag = 1
            self.after(200, self.execute_command)

    def execute_command(self):
        self.command()
        self.set_real_value()
        self.command_flag = 0

    def get(self):
        relation = self.value / (self.winfo_width()-self.slider_width)
        return relation * (self.max_value-self.min_value)

    def set(self, value = False, buffer = 0):
        if buffer:
            self.buffer_value = buffer
            relation = buffer / (self.max_value-self.min_value)
            buffer = relation * (self.winfo_width()-self.slider_width)
            self.buffer_value= max(0, min(self.winfo_width()-self.slider_width, self.value))
        if value:
            relation = value / (self.max_value-self.min_value)
            self.value = relation * (self.winfo_width()-self.slider_width)
            self.value= max(0, min(self.winfo_width()-self.slider_width, self.value))
        if value or buffer:
            self.set_slider()

    def config(self, **kwargs):
        self.set_real_value()   
        for key, value in kwargs.items():
            if key == 'from_':
                self.min_value = value
            elif key == 'to':
                self.max_value = value
            elif key == 'value':
                self.real_value = value
        self.value = (self.real_value / (self.max_value-self.min_value)) * (self.winfo_width()-self.slider_width)
        self.value= max(0, min(self.winfo_width()-self.slider_width, self.value))
        self.set_coords()


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

        self.VOLUME = 0.8 # Default volume
        self.FRAMERATES = (1, 3, 8, 10, 12, 15, 20, 24, 30, 60)

        self.res = tk.StringVar() # The project resolution
        self.res.set(8)
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
                    "frame_1": {
                    }
                }
            ]
        }

        root.bind('<Control-s>', lambda event: self.save(True))
        root.bind('<Command-s>', lambda event: self.save(True))
        root.bind('<Control-z>', lambda event: self.undo())
        root.bind('<Command-z>', lambda event: self.undo())

        self.load()
        
    def undo(self):
        self.load_frame(True)
        root.title(''.join([i for i in root.title() if i != '*'])) # Remove the star in the project title

    def load(self):
        def openDir(): # Opens the project directory
            os.chdir(self.projectDir[:self.projectDir.rfind('/')])
            os.system(f'Explorer .')
        
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
        self.fileMenu.add_command(label="Open Directory in Explorer", command=openDir, state=tk.DISABLED)
        self.fileMenu.add_command(label="Load Audio", command=self.open_audio, state=tk.DISABLED)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Quit", command=self.quit)

        # Setup edit cascade
        self.editMenu = tk.Menu(self.menubar, tearoff=0)
        self.editMenu.add_command(label="Clear", command=self.canvas_clear, state=tk.DISABLED)
        self.editMenu.add_command(label="Fill", command=self.canvas_fill, state=tk.DISABLED)
        self.editMenu.add_separator()
        
        # Setup display cascasde
        self.displayMenu = tk.Menu(self.menubar, tearoff=0)
        self.displayMenu.add_checkbutton(label="Show Grid", variable=self.showGridVar, command=lambda: self.update_grid(True), state=tk.DISABLED)
        self.displayMenu.add_command(label="Grid Color", command=lambda: self.set_grid_color(True), state=tk.DISABLED)
        self.displayMenu.add_checkbutton(label="Show Alpha", variable=self.showAlphaVar, command=lambda: self.display_alpha(True))

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
        self.frameMiddle = tk.Frame(root, width=1080, height=10)
        self.frameMiddle.pack(anchor=tk.CENTER)

        # Add bottom frame
        self.frameBottom = tk.Frame(root, width=1080, height=10)
        self.frameBottom.pack(side=tk.BOTTOM)
        self.frameBottom.pack_propagate()

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

        # Frame
        self.toolsFrame = tk.LabelFrame(self.frameTop, text="Tools", height=60, width=266, bg='white')
        self.toolsFrame.pack(anchor=tk.NW, side=tk.LEFT, padx=(175, 0))
        self.toolsFrame.pack_propagate(False)

        # Pen
        self.penFrame = tk.Frame(self.toolsFrame, height=14, width=6, highlightthickness=2, highlightbackground='red')
        self.penFrame.pack(side=tk.LEFT, padx=5)

        self.penButton = tk.Button(self.penFrame, text="Pen", relief=tk.RAISED, height=14, width=6, command=lambda: self.tool_select(1))
        self.penButton.pack()

        # Eraser
        self.eraserFrame = tk.Frame(self.toolsFrame, height=14, width=6, highlightthickness=2, highlightbackground='white')
        self.eraserFrame.pack(side=tk.LEFT, padx=5)

        self.eraserButton = tk.Button(self.eraserFrame, text="Eraser", relief=tk.RAISED, height=14, width=6, command=lambda: self.tool_select(2))
        self.eraserButton.pack()

        # Remove tool
        self.removeFrame = tk.Frame(self.toolsFrame, height=14, width=6, highlightthickness=2, highlightbackground='white')
        self.removeFrame.pack(side=tk.LEFT, padx=5)
       
        self.removeButton = tk.Button(self.removeFrame, text="Remove", relief=tk.RAISED, height=14, width=6, command=lambda: self.tool_select(3))
        self.removeButton.pack()

        # Repalce tool
        self.replaceFrame = tk.Frame(self.toolsFrame, height=14, width=6, highlightthickness=2, highlightbackground='white')
        self.replaceFrame.pack(side=tk.LEFT, padx=5)
       
        self.replaceButton = tk.Button(self.replaceFrame, text="Replace", relief=tk.RAISED, height=14, width=6, command=lambda: self.tool_select(4))
        self.replaceButton.pack()

        # Add frame display
        self.decreaseFrameButton = tk.Button(self.frameTop, text="-", command=self.decrease_frame, state='disabled', font=('Courier New', 9))
        self.decreaseFrameButton.pack(side=tk.LEFT, padx=(234, 0), pady=(10, 0))
        self.frameDisplayButton = tk.Menubutton(self.frameTop, textvariable=self.currentFrame, width=6, disabledforeground='black', relief=tk.RIDGE)
        self.frameDisplayButton.pack(pady=(10, 0), side=tk.LEFT)
        self.increaseFrameButton = tk.Button(self.frameTop, text="+", command=self.increase_frame, font=('Courier New', 9), state='disabled')
        self.increaseFrameButton.pack(side=tk.LEFT, pady=(10, 0))

        # Add delay input
        #self.frameDelay = tk.Entry(self.frameBottom, width=4, textvariable=self.frameDelayVar, font=('Calibri', 16)).pack(side=tk.LEFT, padx=(300,0))
        self.volumeSlider = VolumeSlider(self.frameBottom, width=200, from_= 0, to=1, command=lambda: self.change_volume())
        self.volumeSlider.config(value=self.VOLUME)
        self.volumeSlider.pack(side=tk.RIGHT, anchor=tk.SE, pady=10)

        # Add play button
        self.playButton = tk.Button(self.frameBottom, text="Play", height=2, width=32, command=lambda: self.play_init(False))
        self.playButton.pack(side=tk.BOTTOM, padx=(320, 100), anchor=tk.CENTER)
        root.bind_all('<KeyPress-Control_L>', lambda event: self.play_button_mode(True))
        root.bind_all('<KeyRelease-Control_L>', lambda event: self.play_button_mode(False))

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
        self.colorPickerData = ch.askcolor()
        self.colorPickerFrame.config(highlightbackground=self.colorPickerData[1]) # Set the border of the button to the chosen color

    def pick_color(self, event):
        self.selectedPixel = self.canvas.find_closest(event.x, event.y)
        self.colorPickerData = ['None'] # Add a placeholder item
        self.colorPickerData.append(self.canvas.itemcget(self.selectedPixel, option='fill') if self.canvas.itemcget(self.selectedPixel, option='fill') != 'white' else '#ffffff')
        self.colorPickerFrame.config(highlightbackground = self.colorPickerData[1])

    def tool_select(self, tool):
        for frame in self.toolsFrame.winfo_children():
                frame.config(highlightbackground='white')

        if tool == 1:
            self.penFrame.config(highlightbackground='red')
        if tool == 2:
            self.eraserFrame.config(highlightbackground='red')
        if tool == 3:
            self.removeFrame.config(highlightbackground='red')
        if tool == 4:
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
            mem = 64
            res.set(''.join([i for i in self.newFileSetResolutionEntry.get() if i.isdigit()]))
            if int(res.get()) <= 64:
                mem = res.get()
            else:
                res.set(mem)
        except:
            pass

        if len(self.res.get()) > 0 and int(self.res.get()) > 64:
            self.res.set(64)
        if len(self.res.get()) > 0 and int(self.res.get()) == 0:
            self.res.set(1)

    def unlock_buttons(self):
        self.fileMenu.entryconfig('Rename', state=tk.ACTIVE)
        self.fileMenu.entryconfig('Save', state=tk.ACTIVE)
        self.fileMenu.entryconfig('Save As', state=tk.ACTIVE)
        self.fileMenu.entryconfig('Export', state=tk.ACTIVE)

        self.fileMenu.entryconfig('Open Directory in Explorer', state=tk.ACTIVE)
        self.fileMenu.entryconfig('Load Audio', state=tk.ACTIVE)

        self.editMenu.entryconfig('Clear', state=tk.ACTIVE)
        self.editMenu.entryconfig('Fill', state=tk.ACTIVE)
       
        self.displayMenu.entryconfig('Show Grid', state=tk.ACTIVE)
        self.displayMenu.entryconfig('Grid Color', state=tk.ACTIVE)

        self.increaseFrameButton['state'] = "normal"
        self.frameDisplayButton['state'] = "normal"
        self.decreaseFrameButton['state'] = 'normal'
        
        root.bind('<Control-e>', lambda event: self.export_display())

        root.bind('<KeyPress-Shift_L>', lambda event: self.frame_skip(True))
        root.bind('<KeyPress-Shift_R>', lambda event: self.frame_skip(True))
        root.bind('<KeyRelease-Shift_L>', lambda event: self.frame_skip(False))
        root.bind('<KeyRelease-Shift_R>', lambda event: self.frame_skip(False))
        
        #root.bind('<KeyRelease-Left>', lambda event: self.load_frame(False))
        #root.bind('<KeyRelease-Right>', lambda event: self.load_frame(False))
        root.bind('<l>', lambda event: self.set_frame())

        root.bind('<Right>', lambda event: self.increase_frame())
        root.bind('<space>', lambda event: self.play_space())
        root.bind('<Left>', lambda event: self.decrease_frame())
        
        # For goto
        for i in range(1, 10):
            root.bind(f'<KeyPress-{i}>', lambda e, num = i: self.goto(str(num)))
        
    def set_frame(self):
        self.currentFrame.set(3200)
        self.load_frame(False)

    def new_file_dialog(self):
        newRes = tk.StringVar(value=self.res.get())
        
        #Add the toplevel window
        self.newFileTL = tk.Toplevel(width=128, height=200)
        self.newFileTL.attributes("-topmost", True)
        self.newFileTL.resizable(False, False)
        self.newFileTL.title("New File")
        self.newFileTL.focus()
        self.newFileTL.bind('<Escape>', lambda event: self.newFileTL.destroy())
       
        #Add the main frame
        self.newFileFrame = tk.Frame(self.newFileTL, height=128, width=256)
        self.newFileFrame.pack()
        self.newFileFrame.pack_propagate(False)

        self.newFileOpenDirectoyButton = tk.Button(self.newFileFrame, text="Open Directory", command=lambda: self.create_new_file(newRes), font=('Calibri', 12)).pack(side=tk.TOP)
        self.newFileSetResolutionEntry = tk.Entry(self.newFileFrame, textvariable=newRes, width=3, font=('Courier New', 15))
        self.newFileSetResolutionEntry.pack(side=tk.BOTTOM)
        tk.Label(self.newFileFrame, text="Project Resolution:", font=('Courier New', 12)).pack(side=tk.BOTTOM, pady=4)

        newRes.trace('w', lambda event1, event2, event3: self.new_project_name_filter(newRes))
        
    def add_framerates(self):
        self.framerateMenu.delete('0', tk.LAST)
        var = tk.BooleanVar(value=True)
        for i in self.FRAMERATES:
                if self.framerate == i:
                    self.framerateMenu.add_radiobutton(label=str(i), variable=var, command=lambda delay = i: self.delay(delay))
                else:
                    self.framerateMenu.add_radiobutton(label=str(i), command=lambda delay = i: self.delay(delay))
                root.update()
                var.set(True)
                root.update()
                if self.framerate == i:
                    var.set(True)
                    root.update()
       
    def create_new_file(self, res):
        self.res.set(res.get()) # Set project resolution to the new resolution
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
            self.projectFileSample['data']['framerate'] = 10
            self.projectFileSample['data']['output'] = self.outputDirectory.get()

            self.jsonSampleDump = json.dumps(self.projectFileSample, indent=4, separators=(',', ':')) # Read the project data as json text

            #Write the file resolution to the file
            self.settingsFile = open(self.projectDir, 'w')
            self.settingsFile.write(self.jsonSampleDump)
            self.settingsFile.close()
            
            self.jsonReadFile = self.projectFileSample
            self.jsonFrames = self.jsonReadFile['frames']
            
            if self.framerate == -1: # Add the framerate menu cascade, before self.framerateNum is assigned
                        self.editMenu.add_cascade(label="Set Framerate", menu=self.framerateMenu)
            
            self.add_framerates()
            try:
                self.newFileTL.destroy()
            except:
                pass

            self.add_canvas(False)
        else:
            try:
                self.newFileTL.attributes("-topmost", True)
            except AttributeError: # If this function was called using Save As
                pass

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

        if len(self.fileOpen) > 0 or not dialog:
            try:
                self.currentFrame.set(1) # Reset the current frame
                self.audioFile = None
                self.playback = 0
                self.isPlaying = False

                self.projectDir = self.fileOpen
                self.file = open(f'{self.projectDir}', 'r')
                self.projectData = json.load(self.file)
                self.file.close()
                
                if self.framerate == -1: # Add the framerate menu cascade, before self.framerateNum is assigned
                        self.editMenu.add_cascade(label="Set Framerate", menu=self.framerateMenu)

                self.res.set(self.projectData['data']['resolution']) # Load resolution
                self.showGridVar.set(self.projectData['data']['showgrid']) # Load grid state
                self.gridColor = self.projectData['data']['gridcolor'] # Load grid color
                self.audioFile = self.projectData['data']['audio'] # Load audio
                self.framerate = self.projectData['data']['framerate'] # Load framerate
                self.outputDirectory.set(self.projectData['data']['output'])

                self.delay(self.framerate) # Set the framerate to the saved framerate               

                # Add framerate menu
                self.add_framerates()

                if self.audioFile != None:
                    mixer.music.queue(self.audioFile)
                    mixer.music.load(self.audioFile)

                    audio = mutagen.File(self.audioFile)
                    self.audioLength = audio.info.length
                    self.audioLength = int((self.audioLength % 60) * 1000)

                self.file.close()
            except Exception as e:
                print(e)
                return False
            self.add_canvas(True)
            
    def open_audio(self):
        audioPath = fd.askopenfilename(
            title="Open audio file",
            filetypes=(("mp3", '*.mp3'),("wav", '*.wav'))
        )
        
        if len(audioPath) > 1:
            self.audioFile = audioPath
            mixer.music.unload()
            self.paused = False
            mixer.music.load(self.audioFile)

            audio = mutagen.File(self.audioFile)
            self.audioLength = audio.info.length
            self.audioLength = int((self.audioLength % 60) * 1000)
            #print(self.audioLength)
            
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
                    
                    root.title(''.join([i for i in root.title() if i != '*'])) # Remove the star in the project title

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

        self.canvas = tk.Canvas(self.frameMiddle, height=1026-160, width=1026-160)
        self.canvas.pack(pady=(20, 0))

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
                        self.canvas.itemconfig(self.pixel, fill=self.savedPixelColor[str(self.pixel)])

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
        self.unlock_buttons()
        
        loading.destroy() # Remove the loading text

    def on_press(self, event: dict):
        self.get_click_coords(event)

        if self.showAlphaVar.get(): # Stop the user from drawing in show alpha mode
            return False
       
        self.cursor_X = event.x
        self.cursor_Y = event.y
        self.selectedPixel = self.canvas.find_closest(event.x, event.y)
       
        try:
            root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
            if self.penFrame['highlightbackground'] == 'red': # If pen mode is selected...
                if self.canvas.itemcget(self.selectedPixel, option='fill') == self.colorPickerData[1]: # If the pixel color is already the pen color
                    pass
                else:
                    root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
                    self.canvas.itemconfig(self.selectedPixel, fill=self.colorPickerData[1])

            elif self.eraserFrame['highlightbackground'] == 'red': # If the eraser mode is selected...
                self.canvas.itemconfig(self.selectedPixel, fill='white')

            elif self.removeFrame['highlightbackground'] == 'red': # If the remove mode is selected...
                self.canvas_remove_color()

            elif self.replaceFrame['highlightbackground'] == 'red': # If the replace mode is selected...
                if self.canvas.itemcget(self.selectedPixel, option='fill') == self.colorPickerData[1]: # If the pixel color is already the pen color
                    pass
                else:
                    self.canvas_replace_color()
        except:
            pass # I don't want it to yell at me

    def canvas_clear(self) -> None:
        root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
        for pixel in self.pixels:
            self.canvas.itemconfig(pixel, fill='white')

    def canvas_fill(self) -> None:
        self.fillColor = ch.askcolor()
        for pixel in self.pixels:
            self.canvas.itemconfig(pixel, fill=self.fillColor[1])


    def canvas_remove_color(self) -> None:
        self.selectedPixel = self.canvas.find_closest(self.clickCoords.x, self.clickCoords.y)
        self.selectedColor = self.canvas.itemcget(self.selectedPixel, option='fill')
        for pixel in self.pixels:
            if self.canvas.itemcget(pixel, option='fill') == self.selectedColor:
                self.canvas.itemconfig(pixel, fill='white')

        self.colorPickerData[1] = self.colorPickerData[1] # I don't now why this is needed, but the pen color needs to be re-assigned

    def canvas_replace_color(self) -> None:
        self.selectedPixel = self.canvas.find_closest(self.clickCoords.x, self.clickCoords.y)
        self.selectedColor = self.canvas.itemcget(self.selectedPixel, option='fill')
        for pixel in self.pixels:
            if self.canvas.itemcget(pixel, option='fill') == self.selectedColor:
                self.canvas.itemconfig(pixel, fill=self.colorPickerData[1])

        self.colorPickerData[1] = self.colorPickerData[1] # Needed for some reason idk

    def save_frame(self) -> None:
        root.title(''.join([i for i in root.title() if i != '*'])) # Remove the star in the project title

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
                    self.color_Frame_Dict[pixel] = self.pixelColor
                    self.jsonFrames[0][f'frame_{self.currentFrame.get()}'] = self.color_Frame_Dict

            self.jsonSampleDump = json.dumps(self.jsonReadFile, indent=4, separators=(',', ':'))

            self.fileOpen.write(self.jsonSampleDump)
            
            # Load new file data
            self.jsonReadFile = json.loads(self.jsonSampleDump)
            self.jsonFrames = self.jsonReadFile['frames']

    def insert_frame(self) -> None: # Inserts a frame after the current frame
        self.currentFrame_mem = int(self.currentFrame.get())

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
        if int(self.currentFrame.get()) != int(len(self.jsonFrames[0])):
            self.currentFrame.set(str(int(self.currentFrame.get()) + 1))
            if mixer.music.get_busy():
                    pass
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
                    self.canvas.itemconfig(self.pixels[pixel], fill=self.savedPixelColor[str(self.pixels[pixel])])

            except KeyError: # If the pixel is not present within the json file
                if self.showAlphaVar.get():
                    self.canvas.itemconfig(self.pixels[pixel], fill='black') # Fill pixels with white (0 alpha)
                else:
                    self.canvas.itemconfig(self.pixels[pixel], fill='white') # Fill pixels with white (0 alpha)

        if self.audioFile != None:
            self.get_playback_pos()

    def load_from(self, frame: int) -> None:
        for pixel in range(int(self.res.get())**2):
            with open(self.projectDir, 'r') as self.fileOpen:
                self.jsonReadFile = json.load(self.fileOpen)
                try:
                    self.json_readFrames = self.jsonReadFile['frames']
                    self.savedPixelColor = self.json_readFrames[0][f'frame_{frame}']

                    if self.canvas.itemcget(self.pixels[pixel], option='fill') != self.savedPixelColor[str(self.pixels[pixel])]: # If the pixel color is already the pen color
                        root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title

                    self.canvas.itemconfig(self.pixels[pixel], fill=self.savedPixelColor[str(self.pixels[pixel])])
                except:
                    self.canvas.itemconfig(self.pixels[pixel], fill='white')
                    
        self.save_frame()

    def display_alpha(self, triggered):
        if triggered and self.showAlphaVar.get(): #If this was triggered by pressing the show alpha button
            if '*' == root.title()[-1]:
                self.save_frame() # Save the current image

        for pixel in self.pixels:
            if self.showAlphaVar.get():
                self.canvas.itemconfig(pixel, fill=['black' if self.canvas.itemcget(pixel, option='fill') == 'white' else 'white']) # Show the alpha
            else: # Reload the colors from the file
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
            self.quitMode = mb.askyesnocancel(title="File Not Saved", message="Do you want to save your project?")

            if self.quitMode: # Save and quit
                self.save(True)
                root.destroy()
            if self.quitMode == False: # Quit without saving
                root.destroy()
            if self.quitMode == None: # Do nothing
                return None
        else:
            root.destroy()

    def export_display(self):
        def close():
            self.exportOpen = False
            self.exportTL.destroy()

        if self.exportOpen:
            self.exportTL.focus()
            return None

        self.exportOpen = True
        
        # Add the toplevel
        self.exportTL = tk.Toplevel(width=400, height=500)
        self.exportTL.resizable(False, False)
        self.exportTL.title("Export Animation")
        self.exportTL.protocol("WM_DELETE_WINDOW", close)
        self.exportTL.focus()

        # Create the notebook
        self.tabs = ttk.Notebook(self.exportTL)
        self.tabs.pack()

        # Create the frames
        self.sequenceFrame = tk.Frame(self.exportTL, width=400, height=500)
        self.singleFrame = tk.Frame(self.exportTL, width=400, height=500)

        self.exportFrameTop = tk.Frame(self.sequenceFrame, width=400, height=100, highlightbackground='black', highlightthickness=2)
        self.exportFrameTop.pack(side=tk.TOP)
        self.exportFrameTop.pack_propagate(False)
        self.exportFrameMiddle = tk.Frame(self.sequenceFrame, width=400, height=50)
        self.exportFrameMiddle.pack(side=tk.LEFT,pady=(0, 64))
        self.exportFrameBottom1 = tk.Frame(self.sequenceFrame, width=400, height=500)
        self.exportFrameBottom1.pack(side=tk.BOTTOM)
        self.exportFrameBottom2 = tk.Frame(self.sequenceFrame, width=400)
        self.exportFrameBottom2.pack(side=tk.BOTTOM)

        # Add the tabs
        self.tabs.add(self.sequenceFrame, text="Image sequence")
        self.tabs.add(self.singleFrame, text="Single Image")

        # Create the menus
        self.exportTypeStr = tk.StringVar(value='.png') # Set the default output extenion

        outputDirectoryEntry = tk.Entry(self.exportFrameTop, textvariable=self.outputDirectory, width=32, font=('Calibri', 14))
        outputDirectoryEntry.pack(side=tk.LEFT,anchor=tk.NW, padx=(5, 0))
        tk.Label(self.exportFrameTop, text="Output Directory:", font=('Calibri', 14)).pack(side=tk.TOP, anchor=tk.NW, padx=5, before=outputDirectoryEntry)

        tk.Button(self.exportFrameTop, text="open", font=('Calibri', 10), command=self.open_output_dir).pack(side=tk.LEFT,anchor=tk.NW)
        tk.OptionMenu(self.exportFrameMiddle, self.exportTypeStr, ".png", ".tga", ".tiff").pack(side=tk.LEFT, anchor=tk.NW)
        
        # Alpha checkbox
        useAlphaVar = tk.BooleanVar()
        tk.Checkbutton(self.exportFrameBottom2, variable=useAlphaVar, text="Use Alpha").pack()

        # Create the export button
        tk.Button(self.exportFrameBottom2, text="Export", command=lambda: self.export(useAlphaVar.get())).pack(side=tk.BOTTOM)

        # Get the frame count
        tk.Label(self.exportFrameBottom1, width=40, text=f"Total frame count: {self.frameCount}").pack(side=tk.BOTTOM) # Display the total frame count
        
    def export(self, alpha):
        fileName = f"{self.outputDirectory.get()}/Render"
        img = Image.new(size=(int(self.res.get()), int(self.res.get())), mode=('RGBA' if alpha else 'RGB'), color='blue')
        px = 0 # The current pixel being referanced
        for y in range(0,img.size[1]):
            for x in range(0,img.size[0]):
                px += 1
                color = self.canvas.itemcget(str(px), "fill")
                if color != 'white':
                    rgb = self.hex_to_rgb(color)
                    rgb.append(255)
                    rgb = tuple(rgb)
                    img.putpixel((x, y), rgb)
                else:
                    if alpha:
                        img.putpixel((x, y), (0, 0, 0, 0))
                    else:
                        img.putpixel((x, y), (255, 255, 255, 255))
                
        img = img.resize(size=(int(self.res.get()) * ceil(1024 / int(self.res.get())), int(self.res.get()) * ceil(1024 / int(self.res.get()))), resample=4)
        img.save(fileName + self.exportTypeStr.get(), self.exportTypeStr.get()[1:])
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
        mixer.music.set_volume(self.volumeSlider.get())

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
            self.fileOpen.close()
            if stopMode:
                self.currentFrame.set(self.currentFrame_mem)

                self.load_frame(False)
                self.isPlaying = False

                if self.audioFile != None:
                    mixer.music.rewind() # Restart the song
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

        self.fileOpen = open(self.projectDir, 'r') # Open the file

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
                    return None
            try:
                if self.isPlaying:
                    time2 = timeit.default_timer()
                    time_total = time2 - time1
                    time_total = self.framerateDelay - time_total
                    time.sleep(max(time_total, 0))
            except:
                return None
        end()

    def play_button_mode(self, isControl):
        self.control = isControl
        if isControl:
            self.playButton.config(command=lambda: self.play_init(True))
        else:
            self.playButton.config(command=lambda: self.play_init(False))

    def delay(self, delay):
        self.framerate = delay
        self.framerateDelay = 1 / float(delay)



#-----====Main Program Start====-----#
root = tk.Tk()
root.title("Pixel-Art Animatitor")
root.geometry('990x1000')
root.resizable(False, False)

m_cls = Main()
root.protocol("WM_DELETE_WINDOW", m_cls.quit) # Open the quit dialogue when closing

root.mainloop()