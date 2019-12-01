from collections import deque

def flip(f):
    return lambda *a: f(*reversed(a))

def kickstart(it):
    deque(it, maxlen=0)

def remap(oldValue, oldMin, oldMax, newMin, newMax):
    # Linear conversion
    if oldMin == newMin and oldMax == newMax:
        return oldValue;
    return (((oldValue - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) + newMin;

def clamp(value, clamp_min, clamp_max):
    return min(clamp_max, max(clamp_min, value))
