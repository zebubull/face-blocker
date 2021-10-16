import traceback
import time
import numpy as np
import cv2 as cv
import utils
from utils import state

CAM_HZ = 30.0
CAM_FRAMETIME = 1.0 / CAM_HZ

def without_cam():
    try:
        start = time.perf_counter()
        utils.log_start('Performing program setup...')
        cam = utils.open_camera(0)
        face_cascade = utils.read_cascade('res/haarcascade_frontalface_default.xml')
        utils.log_success("Program setup complete...")

        while True:
            # retval is false if nothing was read
            ret, frame = cam.read()

            if not ret:
                utils.fatalerr('Couldn\'t read frame from camera.')

            frame = utils.draw_faces(frame, face_cascade)

            if state.show_window:
                state.window_open = True
                cv.imshow('Face Blocker 2', frame)

            cv.waitKey(1)

            sleep = time.perf_counter() - start
            if sleep > 0:
                time.sleep(sleep)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        utils.fatalerr(f'fatal error\n{traceback.format_exc()}', 1)
    
    utils.fatalerr('Terminating...', 0)

def with_cam():

    import pyvirtualcam as pvc
    from pyvirtualcam import PixelFormat
    try:
        utils.log_start('Performing program setup...')
        cam = utils.open_camera(0)
        pref_width = 1280
        pref_height = 720
        pref_fps_in = 30
        cam.set(cv.CAP_PROP_FRAME_WIDTH, pref_width)
        cam.set(cv.CAP_PROP_FRAME_HEIGHT, pref_height)
        cam.set(cv.CAP_PROP_FPS, pref_fps_in)

        # Query final capture device values (may be different from preferred settings).
        width = int(cam.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(cam.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps_in = cam.get(cv.CAP_PROP_FPS)
        face_cascade = utils.read_cascade('res/haarcascade_frontalface_default.xml')

        utils.vlog('Starting virtual camera')
        # 5 is the enum value for fps but the enum just doesn't work so you have to use the number 5 instead don't as me why

        block = True
        with pvc.Camera(width=width, height=height, fps=fps_in, fmt=PixelFormat.RGB) as vcam:
            utils.vlog('Started virtual camera')
            utils.log_success("Program setup complete...")
            while True:
                # retval is false if nothing was read
                ret, frame = cam.read()

                if not ret:
                    utils.fatalerr('Couldn\'t read frame from camera.')

                if block:
                    frame = utils.draw_faces(frame, face_cascade)

                if state.show_window:
                    state.window_open = True
                    cv.imshow('Face Blocker 2', frame)

                if cv.waitKey(1) == ord('b'):
                    block = not block
                vcam.send(np.array(cv.cvtColor(frame, cv.COLOR_BGR2RGB)))
                vcam.sleep_until_next_frame()


    except KeyboardInterrupt:
        pass

    except Exception as e:
        utils.fatalerr(f'fatal error\n{traceback.format_exc()}', 1)
    
    utils.fatalerr('Terminating...', 0)

def main():
    if state.use_cam:
        with_cam()
    else:
        without_cam()

if __name__ == '__main__':
    main()