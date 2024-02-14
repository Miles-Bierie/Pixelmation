# Pixelmation
### A python 3.12 Tkinter application for creating pixel-art animations!

<br>

## About
&nbsp;&nbsp;&nbsp; This program is more of a passion project than an actual animation software. Like, you would be better off using pretty much anything else. But, if you do want to use it, then here you go. This application's UI runs entirely using Tkinter, and therefore is not very good when it comes to playback speed on projects with a large resolution, *especially* on a Windows device. This program is mostly ment for more small scale applications, such as sprite animations.  

## Key features:
+ An alpha channel
+ Audio playback
+ Volume slider
+ Toggleable grid
+ Customizable grid color
+ Ability to copy/paste frames
+ Cool text that says "Loading..." when it is loading a file

### Please Note:
#### This project is <u>*still in development*</u>, and will be updated regularly probably I think with new features.

<br>

## Shortcuts

| Keybinds | Description |
| :-------: | --------------------- |
| Ctrl+Q    | Quit                  |
| Ctrl+N    | New Project           |
| Ctrl+O    | Open Project          |
| Ctrl+E    | Export                |
| Ctrl+S    | Save                  |
| Ctrl+Z    | Undo stroke           |
| Ctrl+Y    | Redo stroke           |
| Button 3  | Pick color            |
| P         | Play/stop audio       |
| Q         | Pen tool              |
| W         | Eraser Tool           |
| E         | Remove tool           |
| R         | Replace Tool          |
| T         | Fill Tool             |
| M         | Modifier UI (Complex) |
| Spacebar  | Play/pause            |
| Ctrl+Spacebar (while stopped) | Play through to current frame  |
| Ctrl+Spacebar (while playing) or Esc | Return to initial frame |

<br>

## Creating a New File
Clicking File -> New or using the Ctrl+N keybind will prompt you with a very simple popup dialog. This will ask you to input a project resolution from 1 to 64, a framerate from 1 to 60, and if the project is simple or complex (use simple for now; a complex project just uses more memory at the moment). Then, press "Create Project" or enter, and specify a path and file name for the project. After a path is selected, the .pxproj file will be created at that location.

## Opening an Existing File
Clicking File -> Open or using the Ctrl+O keybind will prompt you to open a .pxproj file. If the file is not formatted correctly for any reason, an error should instruct you on what the file is missing.

## Adding Audio to a Project
If you ever want to add audio to a project, go to File -> Load Audio, and select an audio file.  

Audio types currently supported:
+ Mp3
+ WAV

You may unload audio by pressing the button again.

## Renaming a Project
If you want to rename a project from within the animation program, go to File -> Rename, type in a new name, and press "Rename" or enter to rename. You can still rename the file manually if you wish to do so.

## Adding / Removing / Loading Frames
The display for the current frame is also a button that lets you do a few different frame-related things, such as adding and and removing frames, as well as copying other frames to the current frame. When you add a frame, it will be a copy of the previous frame. When you delete a frame, all other frames will automatically be shifted down to account for the missing frame. When creating, pasting, or loading a frame from the previous or next frame, that frame will be saved automatically.

## Alpha channel
The button to enable/disable the alpha channel can be found under the edit menu. When alpha is displayed, the frame will be saved automatically. The alpha channel supports either fully opaque or fully transparent, so external processing will be needed for a partial value. When displaying the alpha values, white is opaque and black is transparent. While display alpha is enabled, you will not be able to edit the current frame.

## Tools
+ **Pen:** &nbsp; Does what you would expect; draws in the color selected by the color picker
    + Hold down shift to draw a strait line
+ **Eraser:** &nbsp; Also does what you would expect; Erases the pixel. Erased pixels have an alpha of 0
+ **Remove:** &nbsp; Erases all pixels that have the selected pixels color
+ **Replace:** &nbsp; Replaces all pixels that have the selected pixels color with the current pen color
+ **Fill:** &nbsp; Same as replace, except it will treat any color other then the selected tiles' color as a barrier

When you edit the frame, the canvas's border will turn red, indicating that there are unsaved changes. When you save, the border will revert back to dark blue.

+ ### Undo:
    - Undoing will only effect the canvas, and won't take into account other setting changes.
    - You may change the cache size by going to Edit -> Set Undo Limit (max is 1024)
    - If you delete a frame that has been cached/edited, it will clear the cache

## Playback
-You can play or pause the animation by pressing the play/pause button. Crazy, right? Pressing the spacebar will do the same.  
-<u>Control-clicking</u> the play button or <u>pressing the escape key</u> while the animation is playing will stop and go back to the frame you started playing on. You can also use <u>control-spacebar</u>.  
-<u>Control-clicking</u> the button or using <u>control-spacebar</u> while the animation is *not* playing will play the animation through one, stopping on the frame you started on. For example, if you do this on frame 16, it will play to the end, go to the beginning, and play until stopping on frame 16.

## Frame Navigation  
-You can use the + and - buttons surrounding the frame display button to go to the next or previous frame. You can also use the forward and back arrows to do this.  
-Holding shift while doing this will allow you to jump to the first or last frame.  
-In order to go to a specific frame, you can start typing the frame number you want on your number row, and press enter when you finish to jump to that frame, or escape to cancel. <u>This does not currently work with the numpad.</u>

## Exporting
Open the export dialog by going to File -> Export, or by using Ctrl+E keybind. To render out an image sequence, you will first need to input a valid output path. You can type this in or open it through a dialog using the "open" button to the right of the output path entry. **The open directory button is for opening the output path in the file explorer.**  

The "Clear Folder" button sends all contents of the output directory to the trash.

**File name:**  
&nbsp;&nbsp;&nbsp; The file name is the name that the rendered images will be, followed by a number if you are rendering an image sequence rather than a single image. The extension is determined by the dropdown menu next to the file name entry box. Defaults to a png file.

**Alpha:**  
&nbsp;&nbsp;&nbsp; Selecting the "Use Alpha" checkbox will render the image with an alpha channel (duh). When not rendering with transparency, 0 alpha will be rendered out as white. Note that jpeg images <u>do not</u> support an alpha channel.

**Frame Settings:**  
From/To: *(you will probably never need these)*  
&nbsp;&nbsp;&nbsp; If you want to render out a specific section of your animation, change these values to specify the range of frames to render.

Step: *(you will probably never need this)*  
&nbsp;&nbsp;&nbsp; How many frames to move forward after an image in a sequence is rendered. For example, to render out every other frame, set this value to 2. Default of 1 will render every frame in the specified range. Max is 10.

Resolution:  
&nbsp;&nbsp;&nbsp; The image resolution of the files being rendered. Checking "Local" will make the resolutions multiples of the project resolution, instead of multiples of 2. Max is 4096.

**Rendering:**  
*Render Image* Button:  
&nbsp;&nbsp;&nbsp; Renders the current frame being displayed on the canvas.

*Render Sequence* Button:  
&nbsp;&nbsp;&nbsp; Renders out the image sequence to the specified output directory.

<br>

## Extra Info:
### Simple project file structure:  
    {
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
                    1: "#ffffff",
                    2: "#ffffff",
                    <ect...>
                }
                "frame_2": {...}
            }
        ]
    }

### Complex project file structure:  
    {
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
                    1: ["#ffffff", #ffffff],
                    2: ["#ffffff", #ffffff],
                    <ect...>
                }
                "frame_2": {...}
            }
        ],
        "modifiers": [
            {}
        ],
        "variables": [
            {}
        ]
    }

## Notes:

+ Framerate:
    + The playback performance is around twice as fast if the grid is not enabled
    + This program is faster on a mac than on Windows.

+ Development:
    + This program was developed almost entirely on a Windows computer. Therefore, some features might not work on other platforms. I will try to make this program as cross-compatible as I can, but no promises.

    + I am currently making a modifier system that will allow you to do color correction and stuff. This feature will take a long time to implament, and probably won't be very useful, but... I want to, so yeah.
        - This can be accessed by creating a file and checking the 'Complex Project' checkbox, then going to Display -> Modifier UI (Not in main release!)
        - Currently doesn't do anything