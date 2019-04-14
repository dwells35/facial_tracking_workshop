#System
import time
import random
#3rd Party
import imutils
from imutils.video import VideoStream
from imutils.video import FileVideoStream
import cv2
import dlib
#Local
from Deep_Detector import Deep_Detector
from Tracker import Tracker

'''
####################
   MACHINE VISION
####################
'''

def get_detection_data(indices, net, detections):
    """
    Pick a random index from that list of indices (this way, if there are multiple people,
    the alien won't get fixated on just one person) and return that face's bounding box

    Parameters
    ----------
    indices: list of ints
        List of integer indices corresponding to faces in the detections list that meet or exceed the confidence threshold

    net: Deep_Detector detector
        The Deep_Detector object from which data about the detected faces is pulled

    detections: 4D array of ints
        4D array of faces that the net identified in the image

    Returns
    -------

    bounding_box: tuple of ints
        tuple of length 4 with corners of the bounding box of the detected face in it: (startX, startY, endX, endY)
    """

    num = random.randint(0, len(indices) - 1)
    ind_of_interest = indices[num]
    #get bounding box of detected face
    bounding_box = net.detection_box(detections, ind_of_interest)

    return bounding_box

def run_detector(net, frame, tracker, face_width_threshold):
    """
    Uses a nerual net to detect faces in an input image and starts a tracker if a vaild face is found

    Picks a face from a list of detected faces. If a face is found, a bounding box
    for the face is returned and the center of the box is given to the queue for
    animation. The bounding box is also used to create a new correlation tracker.
    
    If none are found, tracking_face is False, and the detector tries
    again on the next frame.

    Parameters
    ----------
    net: Deep_Detector detector
        The Deep_Detector object from which data about the detected faces is pulled

    frame: numpy ndarray
        image from input video stream from which to find faces

    tracker: Tracker
        A tracker object that is used to create a new correlation tracker if a valid face is found

    face_width_threshold: int
        Maximum width of a bounding box containing a face; used to help prevent false positives seen in previous testing

    Returns
    -------
    tracking_face: boolean
        Flag denoting that a face was found that met all necessary criteria and has been given to the Tracker to track
    """

    detections = net.get_detections(frame)
    indices = net.get_detection_inds(detections)
    tracking_face = False
    if len(indices) > 0:
        bounding_box = get_detection_data(indices, net, detections)
        #unpack bounding box into its components
        startX, startY, endX, endY = bounding_box
        detected_center_raw = (int((endX - startX) / 2) + startX, int((endY - startY) / 2) + startY)


        if (endX - startX) < face_width_threshold:
            tracker = start_tracker(tracker, frame, startX, startY, endX, endY)
            tracking_face = True

        if len(indices) > 0:
            cv2.rectangle(frame, (startX, startY), (endX, endY),
            (0, 0, 255), 2)
            cv2.imshow('main frame', frame)
    cv2.imshow('main frame', frame)

    return tracking_face

def run_tracker(tracker, frame):
    """
    Get center point of updated bouning box from tracker;
    put this in the queue for animation

    Parameters
    ----------
    tracker: dlib Correlation Tracker
        Tracker object that processes the image

    frame: numpy ndarray
        most recent image from camera

    """

    tracked_center_raw = tracker.update_position(frame)
    tracked_center_raw = (tracked_center_raw.x, tracked_center_raw.y)

    cv2.imshow('main frame', frame)

def start_tracker(tracker, frame, startX, startY, endX, endY):
    """Create a tracker based on the bounding box returned from the detector"""
    tracker.get_tracker().start_track(frame, 
                        dlib.rectangle( startX,
                                        startY,
                                        endX,
                                        endY))
    return tracker

def run_machine_vision():
    """
    Manage both the detector (neural net) and the tracker in a
    seperate process than the animation.

    """

    #use imutils.FileVideoStream to read video from a file for testing
    #vs = FileVideoStream('no_vis_light.mp4').start()

    #use imutils.VideoStream to read video from a webcam for testing
    vs = VideoStream(src=0).start()

    #Threaded application of PTGrey Camera-- Use PTCamera_Threaded
    #vs = PTCamera(resolution = video_dims).start()

    #Non-threaded application of PTGrey Camera
    #vs = PTCamera(resolution = video_dims)

    #Let the camera warm up and set configuration
    time.sleep(2)
    print("[INFO] loading model...")
    #create an insance of the detector
    net = Deep_Detector('deploy.prototxt.txt','res10_300x300_ssd_iter_140000.caffemodel', refresh_rate = 2, confidence = .4)

    #initialize a tracker
    print("[INFO] initializing tracker")
    tracker = Tracker(quality_threshold = 6)
    
    last_detector_update_time = time.time()
    current_time = time.time()
    tracking_face = False
    tracked_center = (0,0)
    running = True
    start_machine_vision_time = time.time()
    #count = 0
    #detector_count = 0

    #check to make sure that the identified face is of a reasonable size; For the PTGrey Camera, I found ~50 works well.
    #other cameras will require other thresholds
    face_width_threshold = 200
    no_frame_count = 0

    while running:
        current_time = time.time()
        #Reading from the camera is I/O gating.
        frame = vs.read()
        if frame.all() != None:
            no_frame_count = 0
            frame = imutils.resize(frame, width=300)

            if not tracking_face or current_time - last_detector_update_time > net.get_refresh_rate():
                last_detector_update_time = current_time
                tracking_face = run_detector(net, frame, tracker, face_width_threshold)
                #count += 1
                #detector_count += 1

            if tracking_face:
                #count += 1
                track_quality = tracker.get_track_quality(frame)
                if track_quality >= tracker.get_quality_threshold():
                    run_tracker(tracker, frame)
                else:
                    tracking_face = False 

            #Wait sixteen milliseconds before looping again. OpenCV will freeze if this number
            #is too low or the waitKey call is omitted. If waitKey is called with no params,
            #the program will wait indefinitely for the user to hit a key before it
            #runs another loop; nice for debugging. 
            #Quit the program if the user hits the "q" key on the keyboard
            if cv2.waitKey(16) == ord('q'):
                break

        else:
            no_frame_count += 1
            if no_frame_count == 50:
                print('Received too many null frames; exiting machine_vision_subprocess')
                break
        
    end_machine_vision_time = time.time()
    #fps = count / (end_machine_vision_time - start_machine_vision_time)
    #print('Machine Vision fps: ' + str(fps))
    vs.stop()
    cv2.destroyAllWindows()
    #print('Detector Count: ' + str(detector_count))

if __name__ == '__main__':
    run_machine_vision();