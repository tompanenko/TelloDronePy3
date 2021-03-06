# coding=utf-8
import socket
import time
import threading
import cv2
from threading import Thread
#from decorator import accepts


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
        print("STATE STRING " + str(state_str))
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
    port = 9010
    states = {}
    raw_states = {}

    # Timeout for sockets
    RESPONSE_TIMEOUT = 7  # in seconds

    # Send and receive commands, client socket
    COMMAND_UDP_IP = '192.168.10.1'
    COMMAND_UDP_PORT = 8889
    TIME_BTW_COMMANDS = 0.5  # in seconds
    TIME_BTW_RC_CONTROL_COMMANDS = 0.5  # in seconds
    time_last_command = time.time()

    # Port to receive information from multiple drones
    LOCAL_PORT = None

    # Receive state, server socket
    STATE_UDP_IP = '0.0.0.0'
    STATE_UDP_PORT = 8890
    last_received_state = time.time()

    # Video stream, server socket
    VIDEO_UDP_IP = '0.0.0.0'
    VIDEO_UDP_PORT = 11111

    # VideoCapture object
    background_frame_reader = None

    # flags to keep track of what additional background services are running
    is_stream_on = False
    is_keep_alive_continuous = False

    command_socket = None
    state_socket = None
    socket = None
    state_str = None
    state = None

    '''
    def __init__(self):
        self.is_running = True
        self.__init__command_socket()
        self.__init__state_socket()
        self.is_stream_on = False
    
    def __init__(self, IP):
        self.is_running = True
        self.COMMAND_UDP_IP = IP
        # self.VIDEO_UDP_IP = IP
        self.LOCAL_PORT = Tello.port
        Tello.port = Tello.port + 1
        self.__init__socket()
        self.is_stream_on = False
    '''
    def __init__(self, IP='192.168.10.1', getState=True):
        self.is_running = True
        if IP == '192.168.10.1' or getState:
            print( 'here')
            self.COMMAND_UDP_IP = IP
            self.__init__command_socket()
            Tello.states[IP] = None
            Tello.raw_states[IP] = None
            if len(Tello.states) == 1:
                self.__init__state_socket()
            self.current_state = 0
        else:
            print( 'no here')
            self.COMMAND_UDP_IP = IP
            # self.VIDEO_UDP_IP = IP
            self.LOCAL_PORT = Tello.port
            Tello.port += 1
            self.__init__socket()
        self.is_stream_on = False
    
    def __init__command_socket(self):
        """ Initializes socket for giving commands and receiving responses """
        # To send commands
        self.command_address = (self.COMMAND_UDP_IP, self.COMMAND_UDP_PORT)
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.command_socket.settimeout(self.RESPONSE_TIMEOUT)
        self.command_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.command_socket.bind(('', self.COMMAND_UDP_PORT))  # For UDP response (receiving data)

        # Variable to recieve responses
        self.response = None

        # Run udp receiver for command responses in background
        self.command_thread = threading.Thread(target=self.command_response_receiver, args=())
        self.command_thread.daemon = True
        self.command_thread.start()

    def __init__state_socket(self):
        """ Initializes socket for receiving state """
        # To receive state
        self.state_address = (self.STATE_UDP_IP, self.STATE_UDP_PORT)
        self.state_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.state_socket.settimeout(self.RESPONSE_TIMEOUT)
        self.state_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.state_socket.bind(self.state_address)

        # Run udp receiver for state in background
        state_thread = threading.Thread(target=self.state_receiver, args=())
        state_thread.daemon = True
        state_thread.start()

    def command_response_receiver(self):
        """Listens for responses from Tello. Must be run as a background thread."""
        print( "command_response_receiver: starting")
        timeout_count = 0
        while self.is_running:
            try:
                self.response, _ = self.command_socket.recvfrom(1024)  # buffer size is 1024 bytes
                timeout_count = 0
            except socket.timeout:
                timeout_count += 1
                print( "command_response_receiver: timeout count: ", timeout_count)
                if timeout_count > 60:
                    print( "command_response_receiver: too many timeouts")
                    #self.is_running = False

        self.command_socket.close()
        print( "command_response_receiver: terminating")

    def state_receiver(self):
        """Listens for state from Tello. Must be run as a background thread."""
        timeout_count = 0
        self.state_counter = 0
        print( "state_receiver: starting")
        while self.is_running:
            try:
                self.state_str, address_port = self.state_socket.recvfrom(200)
                drone_address = address_port[0]
                # The following command echoes back the state to the drone. Not sure it is necessary.
                # sent = self.state_socket.sendto(self.state_str, client_address)
                self.state = state_str_to_dict(self.state_str)
                self.state['address'] = drone_address
                Tello.raw_states[drone_address] = self.state_str
                Tello.states[drone_address] = self.state
                self.state_counter += 1
                timeout_count = 0
            except socket.timeout:
                timeout_count += 1
                print( "state_receiver: timeout count: ", timeout_count)
                if timeout_count > 10:  # CHANGE BACK TO 60 WHEN FINISHED
                    print( "command_response_receiver: too many timeouts")
                    self.is_running = False

        # except Exception as e:
        # print((e))
        self.state_socket.close()
        print( "state_receiver: terminating")

    def print_state(self, raw=False):
        if self.COMMAND_UDP_IP not in Tello.states:
            print( "No state received")
        else:
            if raw:
                print( Tello.raw_states[self.COMMAND_UDP_IP])
            #else:
            #    print Tello.states[self.COMMAND_UDP_IP]
            
            else:
                print( state_format(Tello.states[self.COMMAND_UDP_IP], [('Address', 'address')]))
                print( state_format(Tello.states[self.COMMAND_UDP_IP], [('Battery', 'bat')]))
                print( 'Attitude:')
                print( '\t', state_format(Tello.states[self.COMMAND_UDP_IP], [('Roll', 'roll'),
                                                      ('Pitch', 'pitch'),
                                                      ('Yaw', 'yaw')]))
                print( 'Height:', Tello.states[self.COMMAND_UDP_IP]['h'])
                print( 'Acceleration: ')
                print( '\t', state_format(Tello.states[self.COMMAND_UDP_IP],)
                                         [('X', 'agx'), ('Z', 'agy'),
                                          ('Z', 'agz')])
                if Tello.states[self.COMMAND_UDP_IP]['mid'] < 0:
                    print( 'No mission pad detected')
                else:
                    print( state_format(Tello.states[self.COMMAND_UDP_IP], [('Mission pad', 'mid')]))
                    print( '\t', state_format(),
                        Tello.states[self.COMMAND_UDP_IP], [('X', 'x'), ('Y', 'y'), ('Z', 'z')])
                    print( '\t', 'Yaw:', Tello.states[self.COMMAND_UDP_IP]['mpry'][2])
               
    
    def get_state(self, raw=False):
        if self.COMMAND_UDP_IP not in Tello.states:
            print( 'No state received for ', self.COMMAND_UDP_IP)
            return False
        else:
            if raw:
                return Tello.raw_states[self.COMMAND_UDP]
            else:
                return Tello.states[self.COMMAND_UDP]
        '''
        if not self.state:
            print 'No state received'
            return False
        else:
            if raw:
                return self.state_str
            else:
                return self.state
        '''
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
        print( "command_response_receiver: starting")
        timeout_count = 0
        while self.is_running:
            try:
                self.response, _ = self.socket.recvfrom(1024)  # buffer size is 1024 bytes
                print("Received message: " + self.response.decode(encoding='utf-8'))
                timeout_count = 0
            except socket.timeout:
                timeout_count += 1
                print( "command_response_receiver: timeout count: ", timeout_count)
                if timeout_count > 60:
                    print( "command_response_receiver: too many timeouts")
                    self.is_running = False

        self.socket.close()
        print( "command_response_receiver: terminating")
    
    def start_tracking(self):
        '''Start tracking thread'''
        self.stop_track = False
        tracking_thread = threading.Thread(target=self.track, args=())
        tracking_thread.daemon = True
        tracking_thread.start()
        
    
    def stop_tracking(self):
        '''End tracking thread'''
        self.stop_track = True

    def track(self):
        '''Track the Tello's position in x, y, z - axes
        Must be run as a background thread
        '''
        self.x = 0
        self.y = 0
        self.z = 0
        self.x_cm = 0
        self.y_cm = 0
        self.z_cm = 0
        init_time = time.time()
        prev_time = init_time
        while self.is_running and not self.stop_track:
            state_time =  self.wait_for_update()
            velx = float(self.get_vgx())
            vely = float(self.get_vgy())
            velz = float(self.get_vgz())
            dt = state_time - prev_time
            prev_time = state_time
            self.x = self.x + velx*dt
            self.y = self.y + vely*dt
            self.z = self.z + velz*dt
            if self.x != 0:
                self.x_cm =  10.0 * self.x + 11.7 * (self.x/abs(self.x))
            else:
                self.x_cm = 0
            if self.y != 0:
                self.y_cm = -10.3 * self.y + 10.5 * (-1 * self.y/abs(self.y))
            else:
                self.y_cm = 0
            if self.z != 0:
                self.z_cm = -13.5 * self.z + 13.8 * (-1 * self.z/abs(self.z))
            else:
                self.z_cm = 0

    
    def get_pos(self, cm=True):
        if cm:
            return self.x_cm, self.y_cm, self.z_cm
        else:
            return self.x, self.y, self.z
    
    #@accepts(command=str)
    def send_command_with_return(self, command):
        """Send command to Tello and wait for its response.
        Return:
            bool: True for successful, False for unsuccessful
        """
        # Commands very consecutive makes the drone not respond to them. So wait at least self.TIME_BTW_COMMANDS seconds
        diff = time.time() - self.time_last_command
        if diff < self.TIME_BTW_COMMANDS:
            time.sleep(self.TIME_BTW_COMMANDS - diff)

        print('Send command: ' + command)
        timestamp = time.time()

        # give error if socket is not setup yet
        if self.socket or self.command_socket:
            try:
                if self.socket:
                    self.socket.sendto(command.encode('utf-8'), (self.COMMAND_UDP_IP, self.COMMAND_UDP_PORT))
                elif self.command_socket:
                    self.command_socket.sendto(command.encode('utf-8'), self.command_address)
            except socket.error as e:
                print(e)
                self.is_running = False

            while self.response is None:
                lag_time = time.time() - timestamp
                if lag_time > self.RESPONSE_TIMEOUT:
                    print( 'Timeout ', lag_time, ' exceed on command ', command)
                    return False

            print( 'Response: ', str(self.response), '(delay: ', time.time() - timestamp, ')')

            try:
                response = self.response.decode('utf-8')
            except Exception as e:
                print(e)

            self.response = None

            self.time_last_command = time.time()
        else:
            print('Command socket not setup')
            return False

        return response

    #@accepts(command=str)
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
                x/y/z can???t be between -20 ??? 20 at the same time .
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

        if self.socket:
            self.socket.sendto(command.encode('utf-8'), (self.COMMAND_UDP_IP, self.COMMAND_UDP_PORT))
        elif self.command_socket:
            self.command_socket.sendto(command.encode('utf-8'), self.command_address)

    #@accepts(command=str)
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

    #@accepts(command=str)
    def send_read_command(self, command):
        """Send set command to Tello and wait for its response. Possible set commands:
            - speed?: get current speed (cm/s): x: 1-100
            - battery?: get current battery percentage: x: 0-100
            - time?: get current fly time (s): time
            - height?: get height (cm): x: 0-3000
            - temp?: get temperature (??C): x: 0-90
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

    def _udp_video_address(self):
        return 'udp://@' + self.VIDEO_UDP_IP + ':' + str(self.VIDEO_UDP_PORT) # + '?overrun_nonfatal=1&fifo_size=5000'

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
        if self.is_stream_on:
            # print self.background_frame_reader.frame is None -> True
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
                print( 'Stopping streaming')
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
        print( "keep_alive_background: starting")
        count = -1
        while self.is_running:
            time.sleep(1)
            count = count + 1
            if count == 10:
                self.keep_alive(continuous=False)
                count = 0
        print( "keep_alive_background: terminating")

    def connect(self, wait=True):
        """Enter SDK mode
        Returns:
            bool: True for successful, False for unsuccessful
        """
        if wait:
            return self.send_control_command("command")
        else:
            return self.send_command_without_return("command")

    def takeoff(self, wait=True):
        """Tello auto takeoff
        Returns:
            bool: True for successful, False for unsuccessful
            False: Unsuccessful
        """
        if wait:
            return self.send_control_command("takeoff")
        else:
            return self.send_command_without_return("takeoff")

    def land(self, wait=True):
        """Tello auto land
        Returns:
            bool: True for successful, False for unsuccessful
        """
        if wait:
            return self.send_control_command("land")
        else:
            return self.send_command_without_return("land")

    def emergency(self, wait=True):
        """Stop all motors immediately
        Returns:
            bool: True for successful, False for unsuccessful
        """
        if wait:
            return self.send_control_command("emergency")
        else:
            return self.send_command_without_return("emergency")

    #@accepts(direction=str, x=int, wait=bool)
    def move(self, direction, x, wait=True):
        """Tello fly up, down, left, right, forward or back with distance x cm.
        Arguments:
            direction: up, down, left, right, forward or back
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        if wait:
            return self.send_control_command(direction + ' ' + str(x))
        else:
            return self.send_command_without_return(direction + ' ' + str(x))

    #@accepts(x=int, wait=bool)
    def move_up(self, x, wait=True):
        """Tello fly up with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("up", x, wait)

    #@accepts(x=int, wait=bool)
    def move_down(self, x, wait=True):
        """Tello fly down with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("down", x, wait)

    #@accepts(x=int, wait=bool)
    def move_forward(self, x, wait=True):
        """Tello fly forward with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("forward", x, wait)

    #@accepts(x=int, wait=bool)
    def move_back(self, x, wait=True):
        """Tello fly back with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("back", x, wait)

    #@accepts(x=int, wait=bool)
    def move_left(self, x, wait=True):
        """Tello fly forward with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("left", x, wait)

    #@accepts(x=int, wait=bool)
    def move_right(self, x, wait=True):
        """Tello fly back with distance x cm.
        Arguments:
            x: 20-500

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.move("right", x, wait)

    #@accepts(direction=str, x=int, wait=bool)
    def rotate(self, direction, x, wait=True):
        """Tello rotate x degree clockwise or counter clockwise.
        Arguments:
            x: 1-360

        Returns:
            bool: True for successful, False for unsuccessful
        """
        if wait:
            return self.send_control_command(direction + ' ' + str(x))
        else:
            return self.send_command_without_return(direction + ' ' + str(x))

    #@accepts(x=int, wait=bool)
    def rotate_cw(self, x, wait=True):
        """Tello rotate x degree clockwise.
        Arguments:
            x: 1-360

        Returns:
            bool: True for successful, False for unsuccessful
        """
        return self.rotate("cw ", x, wait)

    #@accepts(x=int, wait=bool)
    def rotate_ccw(self, x, wait=True):
        """Tello rotate x degree counterclockwise.
        Arguments:
            x: 1-360

        Returns:
            bool: True for successful, False for unsuccessful
        """

        return self.rotate("ccw ", x, wait)

    #@accepts(direction=str, wait=bool)
    def flip(self, direction, wait=True):
        """Tello fly flip.
        Arguments:
            direction: l (left), r (right), f (forward) or b (back)

        Returns:
            bool: True for successful, False for unsuccessful
        """
        if wait:
            return self.send_control_command("flip " + direction)
        else:
            return self.send_command_without_return("flip " + direction)

    def flip_left(self, wait=True):
        """Tello fly flip left.
        """
        return self.flip("l", wait)

    def flip_right(self, wait=True):
        """Tello fly flip right.
        """
        return self.flip("r", wait)

    def flip_forward(self, wait=True):
        """Tello fly flip forward.
        """
        return self.flip("f", wait)

    def flip_back(self, wait=True):
        """Tello fly flip back.
        """
        return self.flip("b", wait)

    #@accepts(x=int, y=int, z=int, speed=int)
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

    #@accepts(x1=int, y1=int, z1=int, x2=int, y2=int, z2=int, speed=int)
    def curve(self, x1, y1, z1, x2, y2, z2, speed):
        """Tello fly a curve defined by the current and two given coordinates with speed (cm/s).
            - If the arc radius is not within the range of 0.5-10 meters, it responses false.
            - x/y/z can???t be between -20 ??? 20 at the same time.
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

    #@accepts(x=int, wait=bool)
    def set_speed(self, x, wait=True):
        """Set speed to x cm/s.
        Arguments:
            x: 10-100

        Returns:
            bool: True for successful, False for unsuccessful
        """
        if wait:
            return self.send_control_command("speed " + str(x))
        else:
            return self.send_command_without_return("speed " + str(x))

    last_rc_control_sent = 0

    #@accepts(
        # left_right_velocity=int,
        # forward_backward_velocity=int,
        # up_down_velocity=int,
        # yaw_velocity=int)
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

    def stop(self, wait=True):
        """Stops drone in a hover.

        Returns:
            bool: True for successful, False for unsuccessful
        """
        if wait:
            return self.send_control_command("stop")
        else:
            return self.send_command_without_return("stop")

    #@accepts(ssid=str, password=str, wait=bool)
    def set_wifi_with_ssid_password(self, ssid, password, wait=True):
        """Set Wi-Fi with SSID password.
        Returns:
            bool: True for successful, False for unsuccessful
        """
        if wait:
            return self.send_control_command('ap ' + ssid + ' ' + password)
        else:
            return self.send_command_without_return('ap ' + ssid + ' ' + password)

    def get_speed(self):
        """Get current speed (cm/s)
        Returns:
            False: Unsuccessful
            int: 1-100
        """
        return self.send_read_command('speed?')

    def get_vgx(self):
        """Get current speed (cm/s)
        Returns:
            False: Unsuccessful
            int: 1-100
        """
        if self.COMMAND_UDP_IP in Tello.states:
            return Tello.states[self.COMMAND_UDP_IP]['vgx']
        else:
            return False

    def get_vgy(self):
        """Get current speed (cm/s)
        Returns:
            False: Unsuccessful
            int: 1-100
        """
        if self.state:
            return self.state['vgy']
        else:
            return False

    def get_vgz(self):
        """Get current speed (cm/s)
        Returns:
            False: Unsuccessful
            int: 1-100
        """
        if self.state:
            return self.state['vgz']
        else:
            return False

    def get_battery(self):
        """Get current battery percentage
        Returns:
            False: Unsuccessful
            int: -100
        """
        if self.state:
            return self.state['bat']
        else:
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
            return self.send_read_command('height?')

    def get_temperature(self):
        """Get temperature (??C)
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
            return self.state['tof']
        else:
            return self.send_read_command('tof?')

    def get_wifi(self):
        """Get Wi-Fi SNR
        Returns:
            False: Unsuccessful
            str: snr
        """
        return self.send_read_command('wifi?')

    def wait_for_update(self):
        while self.current_state == self.state_counter:
            pass
        timestamp = time.time()
        self.current_state = self.state_counter
        return timestamp
    
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

    RESPONSE_TIMEOUT = 10

    def __init__(self, tello, address):
        self.cap = cv2.VideoCapture(address)
        print( '')
        if not self.cap.isOpened():
            self.cap.open(address)
        if self.cap.isOpened():
            print( 'OPEN')

        # print self.cap.isOpened() -> False

        self.grabbed, self.frame = self.cap.read()

        # print self.frame is None -> True

        self.is_running = True
        self.is_running_update_frame = False

    def start(self):
        self.frame_thread = Thread(target=self.update_frame, args=()).start()
        print( 'update_frame: waiting to start')
        starttime = time.time()
        while not self.is_running_update_frame:
            lag_time = time.time() - starttime
            if lag_time > self.RESPONSE_TIMEOUT:
                print( 'Timeout ', lag_time, ' waiting for update_frame to start. Not starting')
                self.is_running = False
                return self
        return self

    def update_frame(self):
        print( "update_frame: starting")
        self.is_running_update_frame = True
        while self.is_running:
            #    if not self.grabbed or not self.cap.isOpened():
            #        self.stop()
            #    else:
            # print( "Frame grab")
            (self.grabbed, self.frame) = self.cap.read()
        self.is_running_update_frame = False
        print( "update_frame: terminating")

    def stop(self):
        # if self.cap.isOpened():
        #    self.cap.release()
        self.is_running = False

