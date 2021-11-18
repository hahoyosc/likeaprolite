import cv2
from threading import Thread


class VideoStreamWidget(object):
    def __init__(self, link, camname, path, src=0):
        self.record = True
        self.capture = cv2.VideoCapture(link)

        # Resize calculations.
        ratio = 70
        # Get frames dimensions.
        self.width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        # Calculate the ratio of the width from percentage.
        reduction = ((100 - ratio) / 100) * self.width
        ratio = reduction / float(self.width)
        # Construct the dimensions.
        self.dimensions = (int(reduction), int(self.height * ratio))

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        self.camname = camname
        self.link = link
        self.path = path

        # self.fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.writer = cv2.VideoWriter(
            filename=path,
            fourcc=self.fourcc,
            fps=25.0,
            frameSize=(int(self.width), int(self.height))
        )

    # Get the camera capture.
    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
            # time.sleep(0.0001)

    # Show the actual frame on the application.
    def show_frame(self):
        while self.record:
            # Return the resized frame.
            frame = cv2.resize(self.frame, self.dimensions, interpolation=cv2.INTER_LANCZOS4)

            # Write the video.
            if self.status:
                self.save_frame()

                # Encode to show in the web server.
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()

            # Concat frame one by one and show result.
            # yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(frame) + b'\r\n')
            yield (b"--frame\r\nContent-Type: video/jpeg2000\r\n\r\n" + frame + b"\r\n")
            # time.sleep(0.0001)
        else:
            self.writer.release()
            # self.capture.release()

    # Record the frame on the output video.
    def save_frame(self):
        self.writer.write(self.frame)
