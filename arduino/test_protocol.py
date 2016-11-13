import protocol as p
import datetime

def test_status():
    raw = '''{"dtm":"1970-01-01T00:00:04", "day":4, "temperature":17.50, "desired":14.00, "heating":"off", "debounce":56, "debounce_max":120, "manual_time_left":0}'''

    expected = {
        u'dtm': datetime.datetime(1970,1,1,0,0,4),
        u'day': 4,
        u'temperature': 17.50,
        u'desired': 14.00,
        u'heating': 'off',
        u'debounce': 56,
        u'debounce_max': 120,
        u'manual_time_left': 0
        }

    actual = p.parse_status(raw)

    assert expected == actual


def test_encode_time():
    raw = '19:43'

    expected = 197
    actual = p.encode_time(raw)
    assert expected == actual

def test_encode_time_midnight():
    raw = '00:00'

    expected = 0
    actual = p.encode_time(raw)
    assert expected == actual

def test_encode_time_skip():
    raw = ''

    expected=255
    actual = p.encode_time(raw)
    assert expected == actual
