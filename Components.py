import numpy as np

class Components:
    def __init__(self, frequency, amplitude, phase):
        self._frequency = frequency
        self._amplitude = amplitude
        self._phase = phase
    
    def __str__(self):
        return f"signal: {self.frequency} Hz, {self.amplitude} V, {self.phase} degrees"

    @property
    def frequency(self):
        return self._frequency

    @property
    def amplitude(self):
        return self._amplitude

    @property
    def phase(self):
        return self._phase

    # def generate_samples(self, time, sample_rate):
    #     amplitude = self.amplitude
    #     frequency = self.frequency
    #     phase = self.phase

    #     samples = amplitude * np.sin(2 * np.pi * frequency * time + phase)

    #     return samples
    
