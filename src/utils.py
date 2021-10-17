import sys
import numpy as np
import cv2 as cv
from os.path import exists

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def printerr(error: str) -> None:
    '''
    Prints a log message indicating that an error occured
    '''
    print(f'{bcolors.FAIL}[ERROR] {error}{bcolors.ENDC}')
    return

class ProgramState:
    def __init__(self):
        self.camera: cv.VideoCapture = None
        self.window_open: bool = False
        self.face_cascade = None

        self.argv = sys.argv
        self.argc = len(self.argv)
        self.verbose = False
        self.show_window = True
        self.use_image = False
        self.block_image = None
        self.use_cam = False
        self.block_alpha_mask = None
        self.imwidth = 0
        self.imheight = 0

        self.__read_args()

    def __read_args(self):
        for i in range(0, self.argc):
            val = self.argv[i]
            if val == '-v' or val == '--verbose':
                self.verbose = True
            elif val == '-w' or val == '--hide-window':
                self.show_window = False
            elif val == '-i' or val == '--image':
                if not exists(self.argv[i+1]):
                    printerr(f'Could not find image at {self.argv[i+1]}. Using default rectangle.')
                else:
                    try:
                        import numpy as np
                        self.block_image = cv.imread(self.argv[i+1])
                        self.imwidth = self.block_image.shape[0]
                        self.imheight = self.block_image.shape[1]
                        self.block_image = np.array(self.block_image)
                        self.block_alpha_mask = self.block_image[:, :, 2] / 255.0
                        self.use_image = True
                    except ModuleNotFoundError:
                        printerr(f'Please install numpy to use this option. Using default rectangle.')
                    except:
                        printerr(f'Error reading image at {self.argv[i+1]}. Using default rectangle.')
            elif val =='-c' or val == '--camera':
                try:
                    import numpy as np
                    import pyvirtualcam
                    self.use_cam = True
                except ModuleNotFoundError:
                    printerr(f'Please install numpy and pyvirtualcam to use this option.')
            elif val == '-h' or val == '--help':
                self.print_help()
                exit(0)

    def print_help(self):
        print('''
Face Blocker v2.0 by pixelatedCorn
----------------------------------
                
-h, --help             Display this menu
-v, --verbose          Run the program in verbose mode
-i, --image [path]     Block out faces with an image instead of a green rectangle
-w, --hide-window      Run the program without display output to a window
-c, --camera           Outputs the program to a virtual camera with pyvirtualcam. May require installation of additional programs''')


state = ProgramState()

def fatalerr(error: str, exit_code: int)-> None:
    '''
    Prints a log message indicating that a fatal error occured and exits the program
    '''
    print(f'{bcolors.FAIL}{bcolors.BOLD}[FATAL ERROR] {error}')

    if state.camera != None:
        nvlog('Releasing camera stream')
        state.camera.release()
        nvlog('Camera stream released')

    if state.window_open:
        nvlog('Closing window')
        cv.destroyAllWindows();
        nvlog('Closed window')

    print(f'Exiting with code {exit_code}')
    print(bcolors.ENDC, end='')

    exit(exit_code)

def log_start(msg: str) -> None:
    '''
    Prints a log message that informs the user that some task has started with blue text
    '''
    print(f'{bcolors.OKBLUE}[START] {msg}{bcolors.ENDC}')

def log_success(msg: str)-> None:
    '''
    Prints a log message that informs the user that some task has been completed with green text
    '''
    print(f'{bcolors.OKGREEN}[SUCCESS] {msg} {bcolors.ENDC}')

def vlog(msg: str) -> None:
    '''
    Prints a log message only in verbose mode with cyan text
    '''
    global state
    if state.verbose:
        print(f'{bcolors.OKCYAN}[INFO] {msg}{bcolors.ENDC}')

def nvlog(msg: str) -> None:
    '''
    Prints a log message only in verbose mode with whatever text color is currently set
    '''
    global state
    if state.verbose:
        print(f'[INFO] {msg}')

def open_camera(index: int)-> cv.VideoCapture:
    vlog('Getting camera stream')
    # I have no idea what CAP_DSHOW does but it doesn't work without it
    state.camera = cv.VideoCapture(index, cv.CAP_DSHOW)
    vlog('Opened camera stream')

    if not state.camera.isOpened():
        fatalerr('couldn\'t open camera feed')

    return state.camera

def read_cascade(path: str):
    vlog('Reading face detection cascade')
    try:
        state.face_cascade = cv.CascadeClassifier(path)
    except FileNotFoundError:
        fatalerr('Face detection cascade not found', 2)
    except Exception as e:
        fatalerr('fatal error: {e}', 3)
    
    vlog('Read face detection cascade')

    return state.face_cascade

# I totally stole this from stackoverflow
def overlay_transparent(background, overlay, x, y):

    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        w = int(w)
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        h = int(h)
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype = overlay.dtype) * 255
            ],
            axis = 2,
        )

    overlay_image = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    h = int(h)
    w = int(w)
    x = int(x)
    y = int(y)

    background[y:y+h, x:x+w] = (1.0 - mask) * background[y:y+h, x:x+w] + mask * overlay_image

    return background

def block_face(frame, coords):
    global state
    (x, y, w, h) = coords
    if state.use_image:
        dx = x + (w / 2) - (state.imwidth / 2)
        dy = y + (h / 2) - (state.imheight / 2)
        try:
            frame = overlay_transparent(frame, state.block_image, dx, dy)
        except ValueError:
            printerr('Overlay image out of bounds')
    else:
        cv.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), -1)

prev_faces = []

def draw_faces(frame, cascade):
    global prev_faces
    global state
    grayscale = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(grayscale, 1.2, 5)
    i = 0
    for (x, y, w, h) in faces:
        i += 1
        if w < 80 or h < 80:
            i = 0
        block_face(frame, (x, y, w, h))
    if i == 0:
        for (x, y, w, h) in prev_faces:
            block_face(frame, (x, y, w, h))
    else:
        prev_faces = faces

    return frame
