import json
import datetime
import traceback
import dateutil.parser
import serial
import select

def parse_status(raw):
    if raw == "*timeout*":
        status = { 'status': 'timeout', 'temperature': 0, 'heater': 'off' }
    else:
        status = json.loads(raw)
        status['dtm'] = dateutil.parser.parse(status['dtm'])
        status['status'] = 'ok'
    return status

def parse_schedule(raw):
    schedule = json.loads(raw)
    return schedule

def encode_time(tm):
    byte = 0
    if tm:
        (h, m) = [int(x) for x in tm.split(':')]
        byte = 10*h + m // 6
    else:
        byte = 255
    return '{:03d}'.format(byte)



class ArduinoError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Arduino:

    def __init__(self, tty, baudrate):
        self.tty = tty
        self.baudrate = baudrate
        self._io = None

    @property
    def io(self):
        if getattr(self, '_io') is None:
            self._io = serial.Serial(self.tty, self.baudrate)
        return self._io

    def reset_io(self):
        if getattr(self, '_io'):
            try:
                self._io.close()
            except Exception as err:
                print("could not close _io in Arduino: {}".format(err))
                traceback.print_exc()
        self._io = None

    def _wait_till_started(self):
        line = '';
        while 'program loaded' not in line:
            print(line)
            line = self._io.readline().decode('utf-8')
        print('arduino ready')

    def get_status(self):
        self._send_command('S')
        self.status = parse_status(self._read_response())
        return self.status

    def get_schedule(self):
        self._send_command('L')
        self.schedule = parse_schedule(self._read_response())
        return self.schedule

    def set_schedule(self, day, times):
        cmd = 'P' + str(day)
        for t in times:
            cmd = cmd + encode_time(t)
        self._send_command(cmd)

    def set_time(self):
        epoch = int(datetime.datetime.now().timestamp())
        self._send_command('T' + str(epoch))

    def activate_heating(self):
        self._send_command('M')

    def _send_command(self, cmd):
        print('command: %s' % cmd)
        for attempt in range(3):
            print('attempt: %s' % attempt)
            try:
                self.io.write(cmd.encode('utf-8'))
            except Exception as err:
                print("Warning: {}".format(err))
                traceback.print_exc()
                self.reset_io()
            else:
                break
        else:
            raise ArduinoError("Cannot connect to arduino for writing.")

    def _read_response(self):
        for attempt in range(3):
            print('read attempt: %s' % attempt)
            rfds, wfds, efds = select.select([self.io], [], [], 2)
            if self.io in rfds:
                response = self.io.readline().decode('utf-8')
                print("response: %s" % response)
                return response
        else:
            raise ArduinoError("Cannot read response from arduino.")
