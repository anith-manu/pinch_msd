import pyo
import numpy as np
import time

class AudioServer:
    def __init__(self):
        self.server = pyo.Server(duplex=0)
        self.server.verbosity = 0
        self.server.setOutputDevice(8)
        self.server.boot().start()
    
    def close(self):
        # kill the audio
        self.server.stop()
        self.server.shutdown()
    
    def stop(self):
        self.server.stop()

    def start(self):
        self.server.start()


class AudioFbk:
    def __init__(self, server):
        self.server = server.server
        self.gains = {}

    def add_gain(self, name, elt, gain=0.0):
        """Register a decibel gain for a given
        element. Sets the elements mul
        property based on inputs from a slider
        (specified in dB)"""
        self.gains[name] = (gain, elt)

    def up(self):
        """Reflection detected"""
        pass

    def down(self):
        "Reflection lost"
        pass

    def set_rate(self, rate, x, y):
        """
        Update the tracked state.

        rate: scaled velocity
        x: velocity (0-1)
        y: range (0-1)
        """
        pass

    def set_raw(self, raw):
        """Copy in the [32,16,4] radar
        sensor state. Few feedbacks
        use this information."""
        pass



# class WindFbk(AudioFbk):
#     """Noise generator with moving
#     resonant filter"""

#     def __init__(self, server):
#         super().__init__(server)

#         self.noise = pyo.Noise()
#         self.freq = pyo.SigTo(300.0)
#         self.q = pyo.SigTo(0.0)
#         self.lp_freq = pyo.SigTo(1000.0)
#         self.lp_filter = pyo.Biquad(self.noise, freq=self.lp_freq)
#         self.filter = pyo.Resonx(self.lp_filter, freq=self.freq, q=self.q)

#         self.main_gain = pyo.SigTo(0.0, time=0.1)
#         self.delay = pyo.Delay(
#             self.filter * self.main_gain * 2.0, feedback=0.2, delay=0.0
#         )
#         self.compressor = pyo.Compress(self.delay)
#         self.out = self.compressor
#         self.out.out()

#     def set_rate(self, y):
#         y_f = float(y)
#         self.lp_freq.setValue((y_f) * 5000.0)
#         self.main_gain.setValue(y_f)
#         # self.freq.setValue(1000.0 * float(np.exp((y - 0.5) * 3.0)))
#         self.q.setValue( (y_f))



class WindFbk(AudioFbk):
    """Noise generator with moving
    resonant filter"""

    def __init__(self, server):
        super().__init__(server)


        self.noise = pyo.Noise()
        self.freq = pyo.SigTo(300.0)
        self.q = pyo.SigTo(0.0)
        self.lp_freq = pyo.SigTo(1000.0)
        self.lp_filter = pyo.Biquad(self.noise, freq=self.lp_freq)
        self.filter = pyo.Resonx(self.lp_filter, freq=self.freq, q=self.q)

        self.main_gain = pyo.SigTo(0.0, time=0.1)
        self.delay = pyo.Delay(
            self.filter * self.main_gain , feedback=0.2, delay=0.0
        )
        self.compressor = pyo.Compress(self.delay)
        self.out = self.compressor
        self.out.out()

    def set_rate(self, y):
        y_f = float(y)
        self.lp_freq.setValue((y_f) * 5000.0)
        self.main_gain.setValue(y_f)
        # self.freq.setValue(1000.0 * float(np.exp((y - 0.5) * 3.0)))
        # self.q.setValue( (y_f))


class Thunk(AudioFbk):
    """Noise generator with moving
    resonant filter"""

    def __init__(self, server):
        super().__init__(server)
        self.mul = 0
        self.ping = pyo.SfPlayer("sounds/thunk002.wav", loop=False, speed=1.0, mul=self.mul).out()
        # self.size = pyo.SigTo(0.5)
        # self.mul = 0
        # self.reverb = pyo.Delay(
        #     pyo.Freeverb(self.ping, size=self.size, bal=1.0, damp=0.75), delay=0.1, mul = self.mul
        # )
        # self.compressor = pyo.Compress(self.reverb * 2 + self.ping)
        # self.compressor.out()


    def play(self, y):
        # self.size.setValue(float(np.tanh(y) * 2))
        # self.ping.mul = y
        self.ping = pyo.SfPlayer("sounds/thunk002.wav", loop=False, speed=1, mul=y).out()

            

        

    






