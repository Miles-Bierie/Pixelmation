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
from math import trunc
#import numba as nb

class CustomScale(tk.Canvas):
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
        print(self.real_value)
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
        self.pixels = [] # Contains a list of the pixels on the screen (so they can be referanced)
        self.audioFile = None
        
        self.paused = False
        self.playback = 0.0
        self.playOffset = 0

        self.res = tk.StringVar() # The project resolution
        self.res.set(8)
        self.currentFrame = tk.StringVar()
        self.currentFrame.set('1')
        self.currentFrame_mem = 1
        self.frameDelayVar = tk.StringVar()
        self.frameDelayVar.set(0.05)

        self.clickCoords = {}

        self.showAlphaVar = tk.BooleanVar()
        self.showGridVar = tk.BooleanVar()
        self.gridColor = '#000000'
        self.colorPickerData = ('0,0,0', '#000000') #Stores the data from the color picker

        self.showUpdatesVar = tk.BooleanVar()
        self.showGridVar.set(True)
        self.isPlaying = False
        self.control = False


        self.projectFileSample = {
            "data": {
            "resolution": 16,
            "gridcolor": "#000000",
            "audio": None
            },
            "frames": [
                {
                    "frame_1": {
                    }
                }
            ]
        }

        root.bind('<Control-s>', lambda event: self.save())
        root.bind('<Command-s>', lambda event: self.save())
        root.bind('<Control-z>', lambda event: self.loadFrame())
        root.bind('<Command-z>', lambda event: self.loadFrame())

        self.load()

    def load(self):
        def openDir(): # Opens the project directory
            os.chdir(self.projectDir[0:self.projectDir.rfind('/')])
            os.system(f'Explorer .')
            
        mixer.init()
        mixer.set_num_channels(1)
        

        # Add the menubar:
        self.menubar = tk.Menu(root) # Main menubar
        root.config(menu=self.menubar)

        # Setup file cascade
        self.fileMenu = tk.Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label="New", command=self.newFileDialogue)
        self.fileMenu.add_command(label="Open", command=self.openFile)
        self.fileMenu.add_command(label="Rename", command=self.renameDialogue, state=tk.DISABLED)
        self.fileMenu.add_command(label="Save", command=self.save, state=tk.DISABLED)
        self.fileMenu.add_command(label="Save As", command=self.saveAs, state=tk.DISABLED)
        self.fileMenu.add_command(label="Export", command=self.exportDisplay, state=tk.DISABLED)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Open Directory in Explorer", command=openDir, state=tk.DISABLED)
        self.fileMenu.add_command(label="Load Audio", command=self.openAudio, state=tk.DISABLED)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Quit", command=self.quit)

        # Setup edit cascade
        self.editMenu = tk.Menu(self.menubar, tearoff=0)
        self.editMenu.add_command(label="Clear", command=self.canvasClear, state=tk.DISABLED)
        self.editMenu.add_command(label="Fill", command=self.canvasFill, state=tk.DISABLED)
        #self.editMenu.add_separator()
        #self.editMenu.add_command(label="Set Undo-Limit", command=self.undoLimit)

        # Setup display cascasde
        self.displayMenu = tk.Menu(self.menubar, tearoff=0)
        self.displayMenu.add_checkbutton(label="Show Grid", variable=self.showGridVar, command=lambda: self.updateGrid(True), state=tk.DISABLED)
        self.displayMenu.add_command(label="Grid Color", command=lambda: self.setGridColor(True), state=tk.DISABLED)
        self.displayMenu.add_checkbutton(label="Show Alpha", variable=self.showAlphaVar, command=lambda: self.displayAlpha(True))
        self.displayMenu.add_checkbutton(label="Show Updates", variable=self.showUpdatesVar)

        # Add the file cascades
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        self.menubar.add_cascade(label="Edit", menu=self.editMenu)
        self.menubar.add_cascade(label="Display", menu=self.displayMenu)

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
        self.colorPickerButton = tk.Button(self.colorPickerFrame, text="Color Picker", command=self.askColor, font=('Calibri', 14))
        self.colorPickerButton.pack()

        # Add the tools:

        # Key binds
        root.bind('q', lambda event: self.toolSelect(1))
        root.bind('w', lambda event: self.toolSelect(2))
        root.bind('e', lambda event: self.toolSelect(3))
        root.bind('r', lambda event: self.toolSelect(4))

        root.bind('<Return>', lambda event: root.focus())
        root.bind('<Escape>', lambda event: self.esc())

        # Frame
        self.toolsFrame = tk.LabelFrame(self.frameTop, text="Tools", height=60, width=266, bg='white')
        self.toolsFrame.pack(anchor=tk.NW, side=tk.LEFT, padx=(175, 0))
        self.toolsFrame.pack_propagate(False)

        # Pen
        self.penFrame = tk.Frame(self.toolsFrame, height=14, width=6, highlightthickness=2, highlightbackground='red')
        self.penFrame.pack(side=tk.LEFT, padx=5)

        self.penButton = tk.Button(self.penFrame, text="Pen", relief=tk.RAISED, height=14, width=6, command=lambda: self.toolSelect(1))
        self.penButton.pack()

        # Eraser
        self.eraserFrame = tk.Frame(self.toolsFrame, height=14, width=6, highlightthickness=2, highlightbackground='white')
        self.eraserFrame.pack(side=tk.LEFT, padx=5)

        self.eraserButton = tk.Button(self.eraserFrame, text="Eraser", relief=tk.RAISED, height=14, width=6, command=lambda: self.toolSelect(2))
        self.eraserButton.pack()

        # Remove tool
        self.removeFrame = tk.Frame(self.toolsFrame, height=14, width=6, highlightthickness=2, highlightbackground='white')
        self.removeFrame.pack(side=tk.LEFT, padx=5)
       
        self.removeButton = tk.Button(self.removeFrame, text="Remove", relief=tk.RAISED, height=14, width=6, command=lambda: self.toolSelect(3))
        self.removeButton.pack()

        # Repalce tool
        self.replaceFrame = tk.Frame(self.toolsFrame, height=14, width=6, highlightthickness=2, highlightbackground='white')
        self.replaceFrame.pack(side=tk.LEFT, padx=5)
       
        self.replaceButton = tk.Button(self.replaceFrame, text="Replace", relief=tk.RAISED, height=14, width=6, command=lambda: self.toolSelect(4))
        self.replaceButton.pack()

        # Add frame display
        self.decreaseFrameButton = tk.Button(self.frameTop, text="-", command=self.decreaseFrame, state='disabled', font=('Courier New', 9))
        self.decreaseFrameButton.pack(side=tk.LEFT, padx=(234, 0), pady=(10, 0))
        self.frameDisplayButton = tk.Menubutton(self.frameTop, textvariable=self.currentFrame, width=6, disabledforeground='black', relief=tk.RIDGE)
        self.frameDisplayButton.pack(pady=(10, 0), side=tk.LEFT)
        self.increaseFrameButton = tk.Button(self.frameTop, text="+", command=self.increaseFrame, font=('Courier New', 9), state='disabled')
        self.increaseFrameButton.pack(side=tk.LEFT, pady=(10, 0))

        # Add delay input
        self.frameDelay = tk.Entry(self.frameBottom, width=4, textvariable=self.frameDelayVar, font=('Calibri', 16)).pack(side=tk.LEFT, padx=(300,0))
        self.volumeSlider = CustomScale(self.frameBottom, width=200, from_= 0, to=1, command=lambda: self.changeVolume())
        self.volumeSlider.config(value=0.8)
        self.volumeSlider.pack(side=tk.RIGHT, anchor=tk.SE)

        # Add play button
        self.playButton = tk.Button(self.frameBottom, text="Play", height=2, width=32, command=lambda: self.play_init(False))
        self.playButton.pack(side=tk.BOTTOM, padx=(0, 100), anchor=tk.CENTER)
        root.bind_all('<KeyPress-Control_L>', lambda event: self.playButtonMode(True))
        root.bind_all('<KeyRelease-Control_L>', lambda event: self.playButtonMode(False))
        

        # Add the frame button dropdown
        self.frameDisplayButton.menu = tk.Menu(self.frameDisplayButton, tearoff=0)
        self.frameDisplayButton['menu'] = self.frameDisplayButton.menu
        self.frameDisplayButton['state'] = 'disabled'

        self.frameDisplayButton.menu.add_command(label="Insert Frame", command=self.insertFrame)
        self.frameDisplayButton.menu.add_command(label="Delete Frame", command=self.deleteFrame)
        self.frameDisplayButton.menu.add_command(label="Load from Previous", command=lambda: self.loadFrom(str(int(self.currentFrame.get()) - 1)))
        self.frameDisplayButton.menu.add_command(label="Load from Next", command=lambda: self.loadFrom(str(int(self.currentFrame.get()) + 1)))

    def getClickCoords(self, event):
        self.clickCoords = event

    def returnDataSetTrue(self):
        self.returnData = True

    def askColor(self):
        self.colorPickerData = ch.askcolor()
        self.colorPickerFrame.config(highlightbackground=self.colorPickerData[1]) # Set the border of the button to the chosen color

    def pickColor(self, event):
        self.selectedPixel = self.canvas.find_closest(event.x, event.y)
        self.colorPickerData = ['None'] # Add a placeholder item
        self.colorPickerData.append(self.canvas.itemcget(self.selectedPixel, option='fill') if self.canvas.itemcget(self.selectedPixel, option='fill') != 'white' else '#ffffff')
        self.colorPickerFrame.config(highlightbackground = self.colorPickerData[1])

    def toolSelect(self, tool):
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

    def updateTitle(self):
        root.title("Pixel-Art Animator-" + self.projectDir)

    def updateGrid(self, triggered):
        if self.showGridVar.get():
            for pixel in self.pixels:
                self.canvas.itemconfig(str(pixel), outline=self.gridColor)

                if self.showUpdatesVar.get(): root.update_idletasks()
        else:
            for pixel in self.pixels:
                self.canvas.itemconfig(str(pixel), outline='')

                if self.showUpdatesVar.get(): root.update_idletasks()
       
        if triggered:
            root.title("Pixel-Art Animator-" + self.projectDir + '*')

    def setGridColor(self, menu):
        if menu:
            self.gridColor = ch.askcolor()[1]
            root.title("Pixel-Art Animator-" + self.projectDir + '*')

        if self.showGridVar.get() or not menu:
            for pixel in self.pixels:
                    self.canvas.itemconfig(str(pixel), outline=self.gridColor)

                    if self.showUpdatesVar.get(): root.update_idletasks()

    def newProjectNameFilter(self):
        try:
            self.res.set(''.join([i for i in self.newFileSetResolutionEntry.get() if i.isdigit()]))
        except:
            pass

        if len(self.res.get()) > 0 and int(self.res.get()) > 64:
            self.res.set(64)
        if len(self.res.get()) > 0 and int(self.res.get()) == 0:
            self.res.set(1)

    def unlockButtons(self):
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

        root.bind("<KeyPress-Shift_L>", lambda event: self.frameSkip(True))
        root.bind("<KeyPress-Shift_R>", lambda event: self.frameSkip(True))
        root.bind("<KeyRelease-Shift_L>", lambda event: self.frameSkip(False))
        root.bind("<KeyRelease-Shift_R>", lambda event: self.frameSkip(False))

        root.bind('<Right>', lambda event: self.increaseFrame())
        root.bind('<space>', lambda event: self.playSpace())
        root.bind('<Left>', lambda event: self.decreaseFrame())

        root.bind('<Up>', lambda event: self.delay(.05))
        root.bind('<Down>', lambda event: self.delay(-.05))

    def newFileDialogue(self):
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

        self.newFileOpenDirectoyButton = tk.Button(self.newFileFrame, text="Open Directory", command=self.createNewFile, font=('Calibri', 12)).pack(side=tk.TOP)
        self.newFileSetResolutionEntry = tk.Entry(self.newFileFrame, textvariable=self.res, width=3, font=('Courier New', 15))
        self.newFileSetResolutionEntry.pack(side=tk.BOTTOM)
        tk.Label(self.newFileFrame, text="Project Resolution:", font=('Courier New', 12)).pack(side=tk.BOTTOM, pady=4)

        self.res.trace('w', lambda event1, event2, event3: self.newProjectNameFilter())
       
    def createNewFile(self):
        self.newFileTL.attributes("-topmost", False)
        self.newDir = fd.asksaveasfilename(
            title="Choose Directory",
            defaultextension=("pixel project", f'*.{self.extension}'),
            filetypes=(("pixel project", f'*.{self.extension}'),("pixel project", f'*.{self.extension}'))
            )

        if len(self.newDir) > 0:
            self.projectDir = self.newDir
            self.currentFrame.set(1) # Reset the current frame

            # Create the data files for the project
            self.projectFileSample['data']['resolution'] = self.res.get() # Write the file resolution
            self.projectFileSample['data']['gridcolor'] = self.gridColor
            self.projectFileSample['data']['showgrid'] = int(self.showGridVar.get())

            self.jsonSampleDump = json.dumps(self.projectFileSample, indent=4, separators=(',', ':')) # Read the project data as json text

            #Write the file resolution to the file
            self.settingsFile = open(self.projectDir, 'w')
            self.settingsFile.write(self.jsonSampleDump)
            self.settingsFile.close()

            try:
                self.newFileTL.destroy()
            except:
                pass

            self.addCanvas(False)
        else:
            try:
                self.newFileTL.attributes("-topmost", True)
            except AttributeError: # If this function was called using Save As
                pass

    def openFile(self):
        if '*' in root.title():
            self.saveMode = mb.askyesno(title="Unsaved Changes", message="Would you like to save the current project?")
            if self.saveMode:
                self.save()

        self.fileOpen = fd.askopenfilename(
            title="Open Project File",
            filetypes=(("pixel project", f'*.{self.extension}'),("pixel project", f'*.{self.extension}')))
        if len(self.fileOpen) > 0:
            try:
                self.currentFrame.set(1) # Reset the current frame

                self.projectDir = self.fileOpen
                self.file = open(f'{self.projectDir}', 'r')
                self.projectData = json.load(self.file)

                self.res.set(self.projectData['data']['resolution']) # Load resolution
                self.showGridVar.set(self.projectData['data']['showgrid']) # Load grid state
                self.gridColor = self.projectData['data']['gridcolor'] # Load grid color
                self.audioFile = self.projectData['data']['audio'] # Load grid color
                
                if self.audioFile != None:
                    mixer.music.queue(self.audioFile)
                    mixer.music.load(self.audioFile)

                self.file.close()
            except:
                return False
            self.addCanvas(True)
            
    def openAudio(self):
        audioPath = fd.askopenfilename(
            title="Open audio file",
            filetypes=(("mp3", '*.mp3'),("wav", '*.wav'))
        )
        
        if len(audioPath) > 1:
            self.audioFile = audioPath
            mixer.music.unload()
            self.paused = False
            mixer.music.load(self.audioFile)
            mixer.music.play()
            mixer.music.rewind()
            root.title("Pixel-Art Animator-" + self.projectDir + '*')

    def save(self) -> None:
        if not self.showAlphaVar.get(): # If show alpha is not toggled
            try:
                with open(self.projectDir, 'r+') as self.fileOpen:
                    self.json_projectFile = json.load(self.fileOpen)
                    self.json_projectFile['data']['resolution'] = self.res.get()
                    self.json_projectFile['data']['gridcolor'] = self.gridColor
                    self.json_projectFile['data']['showgrid'] = int(self.showGridVar.get())
                    self.json_projectFile['data']['audio'] = self.audioFile
                    self.jsonSampleDump = json.dumps(self.json_projectFile, indent=4, separators=(',', ':')) # Read the project data as json text
                    self.fileOpen.seek(0)
                    self.fileOpen.truncate(0)
                    self.fileOpen.write(self.jsonSampleDump)

                self.saveFrame()
            except: # In case a project is not open
                pass

    def saveAs(self) -> None:
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

    def renameDialogue(self) -> None:
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
            if i in '\/:*?"<>|' or len(self.renameVar.get()) == 0:
                self.canRename = False

        if self.canRename: # If the new name is valid
            os.chdir(os.path.split(self.projectDir)[0])
            os.rename(self.projectDir, self.renameVar.get() + '.' + self.extension)
            self.projectDir = os.path.split(self.projectDir)[0] + '/' + self.renameVar.get() + '.' + self.extension # Set the project directory to the new name
            self.renameTL.destroy()

            self.updateTitle()
            self.save()

    def addCanvas(self, readPixels):
        self.returnData = False
        # Update the title
        self.updateTitle()

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
       
        for pixel in range(int(self.res.get())**2):
            self.pixelate = (self.canvas.winfo_width()-5)/int(self.res.get())
            self.pixel = self.canvas.create_rectangle(self.posX, self.posY, self.posX + self.pixelate, self.posY + self.pixelate, fill='white')

            #self.canvas.tag_bind(f'{pixel + 2}', "<ButtonPress-1>", lambda event: self.on_press(event))
            self.canvas.tag_bind(f'{pixel + 1}', "<ButtonPress-1>", lambda event: self.on_press(event))
            self.canvas.tag_bind(f'{pixel + 1}', "<B1-Motion>", lambda event: self.on_press(event))

            self.pixels.append(self.pixel)

                # Set the pixel color
            with open(self.projectDir, 'r') as self.fileOpen:
                if readPixels:
                    self.json_readFile = json.load(self.fileOpen)

                    self.json_Frames = self.json_readFile['frames']
                    try:
                        self.savedPixelColor = self.json_Frames[0][f'frame_'+self.currentFrame.get()]

                        if self.showAlphaVar.get(): # If show alpha is selected
                            self.displayAlpha(False)
                        else:
                            self.canvas.itemconfig(self.pixel, fill=self.savedPixelColor[str(self.pixel)])

                    except KeyError: # If the pixel is not present within the json file
                        self.canvas.itemconfig(self.pixel, fill='white') # Fill pixels with white (0 alpha)

            self.posX += self.pixelate
            self.toY -= 1

            if self.toY == 0:
                self.toY = int(self.res.get())
                self.posY += self.pixelate
                self.posX = 2

                if self.showUpdatesVar.get(): root.update_idletasks()

        # Add the popup color picker
        self.canvas.bind('<Button-3>', self.pickColor)

        self.setGridColor(False)
        self.updateGrid(False)
        self.unlockButtons()
        
        loading.destroy() # Remove the loading text

    def on_press(self, event: dict):
        self.getClickCoords(event)

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
                self.canvasRemoveColor()

            elif self.replaceFrame['highlightbackground'] == 'red': # If the replace mode is selected...
                if self.canvas.itemcget(self.selectedPixel, option='fill') == self.colorPickerData[1]: # If the pixel color is already the pen color
                    pass
                else:
                    self.canvasReplaceColor()
        except:
            pass # I don't want it to yell at me

    def canvasClear(self) -> None:
        root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title
        for pixel in self.pixels:
            self.canvas.itemconfig(pixel, fill='white')

            if self.showUpdatesVar.get(): root.update_idletasks()
    def canvasFill(self) -> None:
        self.fillColor = ch.askcolor()
        for pixel in self.pixels:
            self.canvas.itemconfig(pixel, fill=self.fillColor[1])

            if self.showUpdatesVar.get(): root.update_idletasks()

    def canvasRemoveColor(self) -> None:
        self.selectedPixel = self.canvas.find_closest(self.clickCoords.x, self.clickCoords.y)
        self.selectedColor = self.canvas.itemcget(self.selectedPixel, option='fill')
        for pixel in self.pixels:
            if self.canvas.itemcget(pixel, option='fill') == self.selectedColor:
                self.canvas.itemconfig(pixel, fill='white')

        self.colorPickerData[1] = self.colorPickerData[1] # I don't now why this is needed, but the pen color needs to be re-assigned

    def canvasReplaceColor(self) -> None:
        self.selectedPixel = self.canvas.find_closest(self.clickCoords.x, self.clickCoords.y)
        self.selectedColor = self.canvas.itemcget(self.selectedPixel, option='fill')
        for pixel in self.pixels:
            if self.canvas.itemcget(pixel, option='fill') == self.selectedColor:
                self.canvas.itemconfig(pixel, fill=self.colorPickerData[1])

        self.colorPickerData[1] = self.colorPickerData[1] # Needed for some reason idk

    def undoLimit(self) -> None: # Unused
        self.undoFrame = tk.Toplevel(height=10, width=20)
        self.undoEntry = tk.Entry(self.undoFrame, textvariable=self.undoLimitVar)

    def saveFrame(self) -> None:
        root.title(''.join([i for i in root.title() if i != '*'])) # Remove the star in the project title

        with open(self.projectDir, 'r+') as self.fileOpen:
            self.jsonFile = json.load(self.fileOpen)

            # Clear the project file
            self.fileOpen.seek(0)
            self.fileOpen.truncate(0)

            self.json_Frames = self.jsonFile['frames']

            if not f'frame_{self.currentFrame.get()}' in self.json_Frames[0]: # If the current frame is not stored in the project file, append it
                self.json_Frames[0][f'frame_{self.currentFrame.get()}'] = {}
           
            self.json_Frames[0][f'frame_{self.currentFrame.get()}'] = {}

            self.color_Frame_Dict = {}
            for pixel in self.pixels:
                self.pixelColor = self.canvas.itemcget(pixel, option='fill') # Get the colors of each pixel

                if self.pixelColor != 'white': # If the frame is not transparent
                    self.color_Frame_Dict[pixel] = self.pixelColor
                    self.json_Frames[0][f'frame_{self.currentFrame.get()}'] = self.color_Frame_Dict

            self.jsonSampleDump = json.dumps(self.jsonFile, indent=4, separators=(',', ':'))

            self.fileOpen.write(self.jsonSampleDump)

    def insertFrame(self) -> None: # Inserts a frame after the current frame
        self.currentFrame_mem = int(self.currentFrame.get())

        # Create a new frame at the end of the sequance
        with open(self.projectDir, 'r+') as self.fileOpen:
            self.jsonFile = json.load(self.fileOpen)

            # Get the number of frames
            self.json_Frames = self.jsonFile['frames']
            self.json_Frames[0][f'frame_{int(len(self.json_Frames[0])) + 1}'] = {}      

            for loop in range(int(len(self.json_Frames[0])) - self.currentFrame_mem):
                # Get the data from the previous frame and copy it to the current frame
                self.json_Frames[0][f'frame_{int(len(self.json_Frames[0])) - loop}'] = self.json_Frames[0][f'frame_{int(len(self.json_Frames[0])) - loop - 1}']
           
            self.currentFrame.set(self.currentFrame_mem + 1)

        self.fileOpen = open(self.projectDir, 'r+')
        self.fileOpen.seek(0)
        self.fileOpen.truncate(0)
        self.jsonSampleDump = json.dumps(self.jsonFile, indent=4, separators=(',', ':'))
        self.fileOpen.write(self.jsonSampleDump)
        self.fileOpen.close()

    def deleteFrame(self) -> None:
        with open(self.projectDir, 'r+') as self.fileOpen:
            self.jsonFile = json.load(self.fileOpen)
            self.json_Frames = self.jsonFile['frames'][0]
            self.newData = copy.deepcopy(self.json_Frames) # Create a copy of the frame list (as to not change the original durring iteration)
            
            i = int(self.currentFrame.get())
            for frame in range(int(self.currentFrame.get()), len(self.json_Frames) + 1):
                if i != len(self.json_Frames): # If the frame is not the last frame, copy the data from the next frame
                    self.newData[f'frame_{i}'] = self.json_Frames[f'frame_{i + 1}']
                    i += 1
                else: # Remove the last frame
                    for loop, frame in enumerate(self.json_Frames):
                        if loop + 1 == len(self.json_Frames):
                            self.newData.pop(frame)

            self.jsonFile['frames'][0] = self.newData # Set the frames to the new data
            
            self.jsonDump = json.dumps(self.jsonFile, indent=4, separators=(',', ':'))
            self.fileOpen.seek(0)
            self.fileOpen.truncate(0)
            self.fileOpen.writelines(self.jsonDump)

        if int(self.currentFrame.get()) - 1 == len(self.json_Frames) - 1 and self.currentFrame.get() != "0": # If you are on the previous last frame, move back one frame
            self.currentFrame.set(int(self.currentFrame.get()) - 1)
        else:
            pass
        try:
            self.loadFrame()  
        except KeyError:
            self.currentFrame.set(1)
            self.canvasClear()
            self.saveFrame()

    def increaseFrame(self) -> None:
        # Get frame count
        if not self.isPlaying: # If we do not already have the file open; for performance so we don't have to open and close the file for every frame
            with open(self.projectDir, 'r') as self.fileOpen:
                self.jsonFile = json.load(self.fileOpen)
                self.json_Frames = self.jsonFile['frames']

        if int(self.currentFrame.get()) != int(len(self.json_Frames[0])):
            self.currentFrame.set(str(int(self.currentFrame.get()) + 1))
        else:
            self.currentFrame.set(1)
            if self.audioFile != None:
                mixer.music.set_pos(0.001)
            
        self.loadFrame()
       
    def decreaseFrame(self) -> None:
        # Get frame count
        with open(self.projectDir, 'r') as self.fileOpen:
            self.jsonFile = json.load(self.fileOpen)
            self.json_Frames = self.jsonFile['frames']

        self.currentFrame.set(str(int(self.currentFrame.get()) - 1))

        if int(self.currentFrame.get()) < 1:
            self.currentFrame.set(int(len(self.json_Frames[0])))

        if self.audioFile != None:
            self.getPlaybackPos()

        self.loadFrame()

    def frameSkip(self, mode: bool) -> None: # Displays the '→←' text or the '+-' text, depending on current functionality
        if mode == True:
            self.increaseFrameButton.config(text="→", command=self.toLast)
            self.decreaseFrameButton.config(text="←", command=self.toFirst)

            root.bind('<Right>', lambda event: self.toLast())
            root.bind('<Left>', lambda event: self.toFirst())
        else:
            self.increaseFrameButton.config(text="+", command=self.increaseFrame)
            self.decreaseFrameButton.config(text="-", command=self.decreaseFrame)

            root.bind('<Right>', lambda event: self.increaseFrame())
            root.bind('<Left>', lambda event: self.decreaseFrame())

    def toFirst(self): # Go to first frame
        self.currentFrame.set(1)
        self.loadFrame()

    def toLast(self): # Go to last frame
        with open(self.projectDir, 'r') as self.fileOpen:
            self.jsonFile = json.load(self.fileOpen)
            self.json_Frames = self.jsonFile['frames']

        self.currentFrame.set(int(len(self.json_Frames[0])))
        self.loadFrame()

    def loadFrame(self) -> None: # Display the frame
        if not self.isPlaying:
            with open(self.projectDir, 'r') as self.fileOpen:
                self.json_readFile = json.load(self.fileOpen)
                self.json_Frames = self.json_readFile['frames']

        if len(self.json_Frames[0][f'frame_' + self.currentFrame.get()]) == 0: # If the frame is empty
            for pixel in range(int(self.res.get())**2):
                self.canvas.itemconfig(self.pixels[pixel], fill='white') # Fill pixels with white (0 alpha)
            return None

        for pixel in range(int(self.res.get())**2):
            try:
                if self.json_Frames[0].get(f'frame_' + self.currentFrame.get()):
                    self.savedPixelColor = self.json_Frames[0][f'frame_' + self.currentFrame.get()]

                if self.showAlphaVar.get(): # If show alpha is selected
                    self.displayAlpha(False)
                else:
                    self.canvas.itemconfig(self.pixels[pixel], fill=self.savedPixelColor[str(self.pixels[pixel])])

            except KeyError: # If the pixel is not present within the json file
                self.canvas.itemconfig(self.pixels[pixel], fill='white') # Fill pixels with white (0 alpha)

        if self.audioFile  != None:
            self.getPlaybackPos()

    def loadFrom(self, frame: int) -> None:
        for pixel in range(int(self.res.get())**2):
            with open(self.projectDir, 'r') as self.fileOpen:
                self.json_readFile = json.load(self.fileOpen)
                try:
                    self.json_readFrames = self.json_readFile['frames']
                    self.savedPixelColor = self.json_readFrames[0][f'frame_{frame}']

                    if self.canvas.itemcget(self.pixels[pixel], option='fill') != self.savedPixelColor[str(self.pixels[pixel])]: # If the pixel color is already the pen color
                        root.title("Pixel-Art Animator-" + self.projectDir + "*") # Add a star at the end of the title

                    self.canvas.itemconfig(self.pixels[pixel], fill=self.savedPixelColor[str(self.pixels[pixel])])
                except:
                    self.canvas.itemconfig(self.pixels[pixel], fill='white')

    def displayAlpha(self, triggered):
        if triggered and self.showAlphaVar.get(): #If this was triggered by pressing the show alpha button
            self.saveFrame() # Save the current image

        for pixel in self.pixels:
            if self.showAlphaVar.get():
                self.canvas.itemconfig(pixel, fill=['#000000' if self.canvas.itemcget(pixel, option='fill') == 'white' else 'white']) # Show the alpha
            else: # Reload the colors from the file
                with open(self.projectDir, 'r') as self.fileOpen:
                    self.json_readFile = json.load(self.fileOpen)
                    self.json_Frames = self.json_readFile['frames']
                    self.savedPixelColor = self.json_Frames[0][f'frame_'+self.currentFrame.get()]
                    try:
                        self.canvas.itemconfig(pixel, fill=self.savedPixelColor[str(pixel)])
                    except:
                        self.canvas.itemconfig(pixel, fill='white')

    def quit(self):
        if '*' in root.title(): # If the file is not saved...
            self.quitMode = mb.askyesnocancel(title="File Not Saved", message="Do you want to save your project?")

            if self.quitMode: # Save and quit
                self.save()
                root.destroy()
            if self.quitMode == False: # Quit without saving
                root.destroy()
            if self.quitMode == None: # Do nothing
                return None
        else:
            root.destroy()

    def exportDisplay(self):
        # Add the toplevel
        self.exportTL = tk.Toplevel(width=400, height=500)
        self.exportTL.resizable(False, False)
        self.exportTL.title("Export Animation")
        self.exportTL.attributes("-topmost", True)

        # Create the notebook
        self.tabs = ttk.Notebook(self.exportTL)
        self.tabs.pack()

        # Create the frames
        self.sequanceFrame = tk.Frame(self.exportTL, width=400, height=500)
        self.singleFrame = tk.Frame(self.exportTL, width=400, height=500)

        self.exportFrameTop = tk.Frame(self.sequanceFrame, width=400, height=100)
        self.exportFrameTop.pack(side=tk.TOP)
        self.exportFrameTop.pack_propagate(False)
        self.exportFrameMiddle = tk.Frame(self.sequanceFrame, width=400, height=50)
        self.exportFrameMiddle.pack(side=tk.LEFT,pady=(0, 64))
        self.exportFrameBottom1 = tk.Frame(self.sequanceFrame, width=400, height=500)
        self.exportFrameBottom1.pack(side=tk.BOTTOM)
        self.exportFrameBottom2 = tk.Frame(self.sequanceFrame, width=400)
        self.exportFrameBottom2.pack(side=tk.BOTTOM)

        # Add the tabs
        self.tabs.add(self.sequanceFrame, text="Image Sequance")
        self.tabs.add(self.singleFrame, text="Single Image")

        # Create the menus
        self.outputDirectory = tk.StringVar()
        self.exportTypeStr = tk.StringVar()
        self.exportTypeStr.set(".png") # Set the default output extenion

        self.outputDirectoryEntry = tk.Entry(self.exportFrameTop, textvariable=self.outputDirectory, width=32, font=('Calibri', 14))
        self.outputDirectoryEntry.pack(side=tk.LEFT,anchor=tk.NW, padx=(5, 0))
        tk.Label(self.exportFrameTop, text="Output Directory:", font=('Calibri', 14)).pack(side=tk.TOP, anchor=tk.NW, padx=5, before=self.outputDirectoryEntry)

        self.outputDirectoryButton = tk.Button(self.exportFrameTop, text="open", font=('Calibri', 10), command=self.openOutputDir).pack(side=tk.LEFT,anchor=tk.NW)
        self.exportType = tk.OptionMenu(self.exportFrameMiddle, self.exportTypeStr, ".png", ".jpeg", ".tiff").pack(side=tk.LEFT, anchor=tk.NW)

        # Create the export button
        tk.Button(self.exportFrameBottom1, text="Export").pack(side=tk.BOTTOM)

        # Get the frame count
        with open(self.projectDir, 'r') as self.fileOpen:
            self.json_readFile = json.load(self.fileOpen)
            self.json_Frames = self.json_readFile['frames']

        tk.Label(self.exportFrameBottom1, width=40, text=f"Total frame count: {(len(self.json_Frames[0]))}").pack() # Display the total frame count

    def openOutputDir(self):
        self.exportTL.attributes("-topmost", False)
        output = fd.askdirectory()
        if len(output) > 1:
            self.outputDirectory.set(output)
        self.exportTL.attributes("-topmost", True)
        
    def getPlaybackPos(self):
        self.playback = max(float(self.frameDelayVar.get()) * float(self.currentFrame.get()) - float(self.frameDelayVar.get()), 0.0001)  # Get the audio position
        if self.audioFile != None:
            mixer.music.play()
            mixer.music.set_pos(self.playback)
            if not self.isPlaying:
                mixer.music.pause()
    
    def changeVolume(self):
        mixer.music.set_volume(self.volumeSlider.get())

    def playSpace(self):
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
                self.loadFrame()
                self.isPlaying = False

                if self.audioFile != None:
                    mixer.music.rewind() # Restart the song
                    #mixer.music.set_pos(self.playback) # Set the location of the song
                self.paused = False
            else:
                self.paused = True
                if self.audioFile != None:
                    mixer.music.pause()
                print(self.playback)
                
            self.getPlaybackPos()
        
        def play_audio(): # Plays the audio, if there is any
            self.getPlaybackPos()

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

        while self.isPlaying:
            time1 = timeit.default_timer()
            self.increaseFrame()
            root.update()
            if not loop:
                if int(self.currentFrame.get()) == self.currentFrame_mem:
                    end()
                    return None
            try:
                time2 = timeit.default_timer()
                time_total = time2 - time1
                time_total = float(self.frameDelayVar.get()) - time_total
                time.sleep(max(time_total, 0))
            except:
                return None
        end()

    def playButtonMode(self, isControl):
        self.control = isControl
        if isControl:
            self.playButton.config(command=lambda: self.play_init(True))
        else:
            self.playButton.config(command=lambda: self.play_init(False))

    def delay(self, delay):
        if float(self.frameDelayVar.get()) > -1:
            self.frameDelayVar.set(float(self.frameDelayVar.get()) + delay if float(self.frameDelayVar.get()) + delay > 0 else 0)


#-----====Main Program Start====-----#
root = tk.Tk()
root.title("Pixel-Art Animatitor")
root.geometry('990x1000')
root.resizable(False, False)

m_cls = Main()
root.protocol("WM_DELETE_WINDOW", m_cls.quit) # Open the quit dialogue when closing

root.mainloop()