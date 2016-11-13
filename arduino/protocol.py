import json
import datetime

import dateutil.parser
import serial

def parse_status(raw):
    status = json.loads(raw)
    status['dtm'] = dateutil.parser.parse(status['dtm'])
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

class Arduino:

    def __init__(self, tty, baudrate):
        self.io = serial.Serial(tty, baudrate)
        self._wait_till_started()

    def _wait_till_started(self):
        line = '';
        while 'program loaded' not in line:
            print(line)
            line = self.io.readline().decode('utf-8')
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

    def _send_command(self, cmd):
        print('command: %s' % cmd)
        self.io.write(cmd.encode('utf-8'))

    def _read_response(self):
        response = self.io.readline().decode('utf-8')
        print("response: %s" % response)
        return response
