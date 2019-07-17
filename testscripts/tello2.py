# coding=utf-8
import socket
import time
import threading
import cv2
from threading import Thread
from decorators import accepts


def float_maybe_list(str_float, sep=','):
    """ Convert a string to float. If the string contains commas, return a list of floats."""
    str_float_split = str_float.split(sep)
    if len(str_float_split) == 1:
        ret = float(str_float_split[0])
    else:
        ret = [float(x) for x in str_float_split]
    return ret


def state_str_to_dict(state_str):
    """ Decodes state string into a dictionary. """

    def item_str_to_pair(s):
        s_split = s.split(':')
        if len(s_split) > 1:
            return (s_split[0], float_maybe_list(s_split[1]))
        else:
            return (None, None)

    if len(state_str) > 0:
        return dict(item_str_to_pair(x) for x in state_str.split(';'))
    else:
        return None


def state_format(state, pairs):
    return '; '.join([':'.join([fmt, str(state[key])]) for fmt, key in pairs])


class Tello:
    """Python wrapper to interact with the Ryze Tello drone using the official Tello api.
    Tello API documentation:
    https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf
    """

    # "Static" variable that increments each time a tello object is created so they each get a different port number
    port = 9020

    # Timeout for sockets
    RESPONSE_TIMEOUT = 7  # in seconds

    # Send and receive commands, client socket
    COMMAND_UDP_IP = None
    COMMAND_UDP_PORT = 8889
    TIME_BTW_COMMANDS = 0.5  # in seconds
    TIME_BTW_RC_CONTROL_COMMANDS = 0.5  # in seconds
    time_last_command = time.clock()

    LOCAL_PORT = None
    
    # Video stream, server socket
    VIDEO_UDP_IP = '0.0.0.0'
    VIDEO_UDP_PORT = 11111

    # VideoCapture object
    background_frame_reader = None

    # flags to keep track of what additional background services are running
    is_stream_on = False
    is_keep_alive_continuous = False

    socket = None
    state_str = None
    state = None

    def __init__(self, IP):
        self.COMMAND_UDP_IP = IP
        self.LOCAL_PORT = Tello.port
        Tello.port = Tello.port + 1
        self.is_running = True
        self.__init__socket()
        self.is_stream_on = False

    def __init__socket(self):
        """ Initializes socket for giving commands and receiving responses """
        # To send commands
        self.local_address = ('', self.LOCAL_PORT)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.RESPONSE_TIMEOUT)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.local_address)  # For UDP response (receiving data)

        # Variable to recieve responses
        self.response = None

        # Run udp receiver for command responses in background
        self.receive_thread = threading.Thread(target=self.receive, args=())
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def receive(self):
        """Listens for responses from Tello. Must be run as a background thread."""
        print "command_response_receiver: starting"
        timeout_count = 0
        while self.is_running:
            try: 
                #print '1' +  self.COMMAND_UDP_IP +  str(self.response)
                self.response, client_address = self.socket.recvfrom(1024)  # buffer size is 1024 bytes
                print("Received message: " + self.response.decode(encoding='utf-8'))
                timeout_count = 0
            except socket.timeout:
                timeout_count += 1
                #print "command_response_receiver: timeout count: ", timeout_count
                if timeout_count > 60:
                    print "command_response_receiver: too many timeouts"
                    self.is_running = False

        self.socket.close()
        print "command_response_receiver: terminating"


    def print_state(self, raw=False):
        if not self.state:
            print "No state received"
        else:
            if raw:
                print self.state_str
            else:
                print state_format(self.state, [('Battery', 'bat')])
                print 'Attitude:'
                print '\t', state_format(self.state, [('Roll', 'roll'),
                                                      ('Pitch', 'pitch'),
                                                      ('Yaw', 'yaw')])
                print 'Height:', self.state['h']
                print 'Acceleration: '
                print '\t', state_format(self.state,
                                         [('X', 'agx'), ('Z', 'agy'),
                                          ('Z', 'agz')])
                if self.state['mid'] < 0:
                    print 'No mission pad detected'
                else:
                    print state_format(self.state, [('Mission pad', 'mid')])
                    print '\t', state_format(
                        self.state, [('X', 'x'), ('Y', 'y'), ('Z', 'z')])
                    print '\t', 'Yaw:', self.state['mpry'][2]

    @accepts(command=str)
    def send_command_with_return(self, command):
        """Send command to Tello and wait for its response.
        Return:
            bool: True for successful, False for unsuccessful
        """
        # Commands very consecutive makes the drone not respond to them. So wait at least self.TIME_BTW_COMMANDS seconds
        diff = time.clock() - self.time_last_command
        if diff < self.TIME_BTW_COMMANDS:
            time.sleep(self.TIME_BTW_COMMANDS - diff)

        print(str(self.COMMAND_UDP_IP) + ' Send command: ' + command)
        timestamp = time.clock()

        #give error if socket is not setup yet
        if self.socket:
            try:
                self.socket.sendto(command.encode('utf-8'), (self.COMMAND_UDP_IP, self.COMMAND_UDP_PORT))
            except socket.error as e:
                print(e)
                self.is_running = False

            while self.response is None:
                lag_time = time.clock() - timestamp
                if lag_time > self.RESPONSE_TIMEOUT:
                    print 'Timeout ', lag_time, ' exceed on command ', command
                    return False
            
            #print 'Response: ', str(self.response), '(delay: ', time.clock() - timestamp, ')'
            
            try:
                response = self.response.decode('utf-8')
            except Exception as e:
                print(e)

            self.response = None

            self.time_last_command = time.clock()
        else:
            print('Command socket not setup')
            return False

        return response

    @accepts(command=str)
    def send_command_without_return(self, command):
        """Send command to Tello without expecting a response. Use this method when you want to send a command
        continuously
            - go x y z speed: Tello fly to x y z in speed (cm/s)
                x: 20-500
                y: 20-500
                z: 20-500
                speed: 10-100
            - curve x1 y1 z1 x2 y2 z2 speed: Tello fly a curve defined by the current and two given coordinates with
                speed (cm/s). If the arc radius is not within the range of 0.5-10 meters, it responses false.
                x/y/z can’t be between -20 – 20 at the same time .
                x1, x2: 20-500
                y1, y2: 20-500
                z1, z2: 20-500
                speed: 10-60
            - rc a b c d: Send RC control via four channels.
                a: left/right (-100~100)
                b: forward/backward (-100~100)
                c: up/down (-100~100)
                d: yaw (-100~100)
        """
        # Commands very consecutive makes the drone not respond to them. So wait at least self.TIME_BTW_COMMANDS seconds

        print('Send command (no expect response): ' + command)
        self.socket.sendto(command.encode('utf-8'), (self.COMMAND_UDP_IP, self.COMMAND_UDP_PORT))

    @accepts(command=str)
    def send_control_command(self, command):
        """Send control command to Tello and wait for its response. Possible control commands:
            - command: entry SDK mode
            - takeoff: Tello auto takeoff
            - land: Tello auto land
            - streamon: Set video stream on
            - streamoff: Set video stream off
            - emergency: Stop all motors immediately
            - up x: Tello fly up with distance x cm. x: 20-500
            - down x: Tello fly down with distance x cm. x: 20-500
            - left x: Tello fly left with distance x cm. x: 20-500
            - right x: Tello fly right with distance x cm. x: 20-500
            - forward x: Tello fly forward with distance x cm. x: 20-500
            - back x: Tello fly back with distance x cm. x: 20-500
            - cw x: Tello rotate x degree clockwise x: 1-3600
            - ccw x: Tello rotate x degree counter- clockwise. x: 1-3600
            - flip x: Tello fly flip x
                l (left)
                r (right)
                f (forward)
                b (back)
            - speed x: set speed to x cm/s. x: 10-100
            - wifi ssid pass: Set Wi-Fi with SSID password

        Return:
            bool: True for successful, False for unsuccessful
        """

        response = self.send_command_with_return(command)

        if response == 'OK' or response == 'ok':
            return True
        else:
            return self.return_error_on_send_command(command, response)

    @accepts(command=str)
    def send_read_command(self, command):
        """Send set command to Tello and wait for its response. Possible set commands:
            - speed?: get current speed (cm/s): x: 1-100
            - battery?: get current battery percentage: x: 0-100
            - time?: get current fly time (s): time
            - height?: get height (cm): x: 0-3000
            - temp?: get temperature (°C): x: 0-90
            - attitude?: get IMU attitude data: pitch roll yaw
            - baro?: get barometer value (m): x
            - tof?: get distance value from TOF (cm): x: 30-1000
            - wifi?: get Wi-Fi SNR: snr

        Return:
            bool: True for successful, False for unsuccessful
        """
        response = self.send_command_with_return(command) 
        try:
            response = str(response)
        except TypeError as e:
            print(e)
            pass

        if ('error' not in response) and ('ERROR' not in response) and (
                'False' not in response):
            if response.isdigit():
                return int(response)
            else:
                return response
        else:
            return self.return_error_on_send_command(command, response)

    @staticmethod
    def return_error_on_send_command(command, response):
        """Returns False and print an informative result code to show unsuccessful response"""
        print('Command ' + command + ' was unsuccessful. Message: ' + str(response))
        return False

    def mission_pads_on(self):
        """Turn on mission pad detection
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("mon")

    def mission_pads_off(self):
        """Turn off mission pad detection
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("moff")

    def get_udp_video_address(self):
        return 'udp://@' + self.VIDEO_UDP_IP + ':' + str(self.VIDEO_UDP_PORT) + '?overrun_nonfatal=1&fifo_size=5000'

    def get_frame_reader(self):
        """Get the BackgroundFrameReader object from the camera drone. Then, you just need to call
        backgroundFrameReader.frame to get the actual frame received by the drone.
        Returns:
            BackgroundFrameReader
        """
        if self.background_frame_reader is None:
            self.background_frame_reader = BackgroundFrameReader(self, self.get_udp_video_address()).start()
        return self.background_frame_reader

    def get_frame(self):
        print 'a'
        if self.is_stream_on:
            print (self.background_frame_reader.frame is None)
            return self.background_frame_reader.frame
        else:
            return None

    def stream_on(self):
        """Set video stream on. If the response is 'Unknown command' means you have to update the Tello firmware. That
        can be done through the Tello app.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        result = self.send_control_command("streamon")
        if result is True:
            self.is_stream_on = True
            self.get_frame_reader()
        return result

    def stream_off(self):
        """Set video stream off
        Returns:
            bool: True for successful, False for unsuccessful
        """
        result = self.send_control_command("streamoff")
        if result is True:
            if self.is_stream_on:
                print 'Stopping streaming'
                self.background_frame_reader.stop()
            self.is_stream_on = False
        return result

    def keep_alive(self, continuous=True):
        """ Sends the command 'command' without waiting for a response. This is just to avoid the Tello to shut down due to inactivity
        Optional arguments:
        - continous If True (default), run a separate thread that sends this command regularly.
        """
        if continuous and not self.is_keep_alive_continuous:
            self.keep_alive_thread = threading.Thread(target=self.keep_alive_background, args=())
            self.keep_alive_thread.start()
            self.is_keep_alive_continuous = True
        else:
            return self.send_control_command('command')

    def keep_alive_background(self):
        print "keep_alive_background: starting"
        count = -1
        while self.is_running:
            time.sleep(1)
            count = count + 1
            if count == 10:
                self.keep_alive(continuous=False)
                count = 0
        print "keep_alive_background: terminating"

    def connect_wait(self):
        """Enter SDK mode
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("command")

    def connect(self):
        """Enter SDK mode
        Does not check if successful
        """
        return self.send_command_without_return("command")

    def takeoff_wait(self):
        """Tello auto takeoff
        Returns:
            bool: True for successful, False for unsuccessful
            False: Unsuccessful
        """
        return self.send_control_command("takeoff")

    def takeoff(self):
        """Tello auto takeoff
        Does not check if successful
        """
        return self.send_command_without_return("takeoff")

    def land_wait(self):
        """Tello auto land
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("land")

    def land(self):
        """Tello auto land
        Does not check if successful
        """
        return self.send_command_without_return("land")

    def emergency_wait(self):
        """Stop all motors immediately
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("emergency")

    def emergency(self):
        """Stop all motors immediately
        Does not check if successful
        """
        return self.send_command_without_return("emergency")

    @accepts(direction=str, x=int)
    def move_wait(self, direction, x):
        """Tello fly up, down, left, right, forward or back with distance x cm.
        Arguments:
            direction: up, down, left, right, forward or back
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command(direction + ' ' + str(x))

    @accepts(direction=str, x=int)
    def move(self, direction, x):
        """Tello fly up, down, left, right, forward or back with distance x cm.
        Arguments:
            direction: up, down, left, right, forward or back
            x: 20-500

        Does not check if successful
        """
        return self.send_command_without_return(direction + ' ' + str(x))

    @accepts(direction=str, x=int)
    def rotate_wait(self, direction, x):
        """Tello rotate x degree clockwise or counter clockwise.
        Arguments:
            x: 1-360

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command(direction + " " + str(x))

    @accepts(direction=str, x=int)
    def rotate(self, direction, x):
        """Tello rotate x degree clockwise or counter clockwise.
        Arguments:
            x: 1-360

        Does not check if successful
        """
        return self.send_command_without_return(direction + " " + str(x))

    @accepts(direction=str)
    def flip_wait(self, direction):
        """Tello fly flip.
        Arguments:
            direction: l (left), r (right), f (forward) or b (back)

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("flip " + direction)

    @accepts(direction=str)
    def flip(self, direction):
        """Tello fly flip.
        Arguments:
            direction: l (left), r (right), f (forward) or b (back)

        Does not check if successful
        """
        return self.send_command_without_return("flip " + direction)

    @accepts(x=int, y=int, z=int, speed=int)
    def go_xyz_speed(self, x, y, z, speed):
        """Tello fly to x y z in speed (cm/s)
        Arguments:
            x: 20-500
            y: 20-500
            z: 20-500
            speed: 10-100
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_command_without_return('go %s %s %s %s' % (x, y, z, speed))

    @accepts(x1=int, y1=int, z1=int, x2=int, y2=int, z2=int, speed=int)
    def curve(self, x1, y1, z1, x2, y2, z2, speed):
        """Tello fly a curve defined by the current and two given coordinates with speed (cm/s).
            - If the arc radius is not within the range of 0.5-10 meters, it responses false.
            - x/y/z can’t be between -20 – 20 at the same time.
        Arguments:
            x1: 20-500
            x2: 20-500
            y1: 20-500
            y2: 20-500
            z1: 20-500
            z2: 20-500
            speed: 10-60
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_command_without_return('curve %s %s %s %s %s %s %s' % (x1, y1, z1, x2, y2, z2, speed))

    @accepts(x=int)
    def set_speed_wait(self, x):
        """Set speed to x cm/s.
        Arguments:
            x: 10-100

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command("speed " + str(x))

    last_rc_control_sent = 0

    @accepts(x=int)
    def set_speed(self, x):
        """Set speed to x cm/s.
        Arguments:
            x: 10-100

        Does not check if successful
        """
        return self.send_command_without_return("speed " + str(x))

    last_rc_control_sent = 0

    @accepts(
        left_right_velocity=int,
        forward_backward_velocity=int,
        up_down_velocity=int,
        yaw_velocity=int)
    def send_rc_control(self, left_right_velocity, forward_backward_velocity,
                        up_down_velocity, yaw_velocity):
        """Send RC control via four channels. Command is sent every self.TIME_BTW_RC_CONTROL_COMMANDS seconds.
        Arguments:
            left_right_velocity: -100~100 (left/right)
            forward_backward_velocity: -100~100 (forward/backward)
            up_down_velocity: -100~100 (up/down)
            yaw_velocity: -100~100 (yaw)
        Returns:
            bool: True for successful, False for unsuccessful
        """
        if int(time.time() * 1000) - self.last_rc_control_sent < self.TIME_BTW_RC_CONTROL_COMMANDS:
            pass
        else:
            self.last_rc_control_sent = int(time.time() * 1000)
            return self.send_command_without_return(
                'rc %s %s %s %s' % (left_right_velocity,
                                    forward_backward_velocity,
                                    up_down_velocity, yaw_velocity))

    def stop(self):
        """Stops drone in a hover.

        Does not check if successful
        """
        return self.send_command_without_return("stop")
        

    def set_wifi_with_ssid_password(self):
        """Set Wi-Fi with SSID password.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.send_control_command('wifi ssid pass')

    def get_speed(self):
        """Get current speed (cm/s)
        Returns:
            False: Unsuccessful
            int: 1-100
        """
        return self.send_read_command('speed?')

    def get_battery(self):
        """Get current battery percentage
        Returns:
            False: Unsuccessful
            int: -100
        """
        if self.state:
            print '1 Send command ' + self.COMMAND_UDP_IP + ' battery?'
            
            return self.state['bat']
        else:
            print 2
            return self.send_read_command('battery?')

    def get_flight_time(self):
        """Get current fly time (s)
        Returns:
            False: Unsuccessful
            int: Seconds elapsed during flight.
        """
        return self.send_read_command('time?')

    def get_height(self):
        """Get height (cm)
        Returns:
            False: Unsuccessful
            int: 0-3000
        """
        if self.state:
            return self.state['h']
        else:
            return int(self.send_read_command('height?')[:-4])

    def get_temperature(self):
        """Get temperature (°C)
        Returns:
            False: Unsuccessful
            int: 0-90
        """
        return self.send_read_command('temp?')

    def get_attitude(self):
        """Get IMU attitude data
        Returns:
            False: Unsuccessful
            int: pitch roll yaw
        """
        return self.send_read_command('attitude?')

    def get_barometer(self):
        """Get barometer value (m)
        Returns:
            False: Unsuccessful
            int: 0-100
        """
        if self.state:
            return self.state['baro']
        else:
            return self.send_read_command('baro?')

    def get_distance_tof(self):
        """Get distance value from TOF (cm)
        Returns:
            False: Unsuccessful
            int: 30-1000
        """
        if self.state:
            print '1 ' + str(self.COMMAND_UDP_IP)
            return self.state['tof']
        else:
            print '2 ' + str(self.COMMAND_UDP_IP)
            return int(self.send_read_command('tof?')[:-4])

    def get_wifi(self):
        """Get Wi-Fi SNR
        Returns:
            False: Unsuccessful
            str: snr
        """
        return self.send_read_command('wifi?')

    def end(self):
        """Call this method when you want to end the tello object"""
        time.sleep(3)
        self.print_state()
        if self.get_height() > 1:
            self.land()
        time.sleep(1)
        self.is_running = False
        if self.is_stream_on:
            self.stream_off()


class BackgroundFrameReader:
    """
    This class read frames from a VideoCapture in background. Then, just call backgroundFrameReader.frame to get the actual one.
    """

    RESPONSE_TIMEOUT=10
    
    def __init__(self, tello, address):
        self.cap = cv2.VideoCapture(address)
        while not self.cap.isOpened():
            self.cap.open(address)
            time.sleep(1)

        #print self.cap.isOpened() -> False

        self.grabbed, self.frame = self.cap.read()
        
	#print self.frame is None -> True

        self.is_running = True
        self.is_running_update_frame = False

    def start(self):
        print 'H'
        self.frame_thread = Thread(target=self.update_frame, args=()).start()
        print 'update_frame: waiting to start'
        starttime=time.clock()
        while not self.is_running_update_frame:
            lag_time = time.clock() - starttime
            if lag_time > self.RESPONSE_TIMEOUT:
                print 'Timeout ', lag_time, ' waiting for update_frame to start. Not starting'
                self.is_running = False
                return self
        return self

    def update_frame(self):
        print "update_frame: starting"
        self.is_running_update_frame = True
        while self.is_running:
            #    if not self.grabbed or not self.cap.isOpened():
            #        self.stop()
            #    else:
            #print "Frame grab"
            (self.grabbed, self.frame) = self.cap.read()
        self.is_running_update_frame = False
        print "update_frame: terminating"

    def stop(self):
        #if self.cap.isOpened():
        #    self.cap.release()
        self.is_running = False
