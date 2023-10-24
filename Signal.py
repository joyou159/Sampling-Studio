from Components import Components
import numpy as np


class Signal:
    def __init__(self, name):
        self.name = name
        self.components = [] 
        self.data = [] 
        self.time = np.linspace(0, 1, 1000)   

        self.snr = None
        self.sample_rate = None
        self.maxFreq = None
        self.sampling_mode = None # either 0 or 1  (0 --> actual || 1 --> normalized )

    def add_component(self, component):
        self.components.append(component)
    
    def change_sampling_mode(self,mode_num):
        self.sampling_mode = mode_num

    def change_sample_rate(self, new_sample_rate):
        self.sample_rate = new_sample_rate

    def delete_component_after_preparing(self, component):
        if component in self.components:
            self.components.remove(component)
        # re-generating the data  
        self.generate_samples() 

    def delete_component_during_preparing(self, component):
        if component in self.components:
            self.components.remove(component)

    def generate_signal(self):
        self.generate_samples()
        self.sample_rate = self.maxFreq
        self.sampling_mode = 0 # by default 
    
    def generate_samples(self):
        
        # Initialize self.samples as an empty array with the same shape
        self.data = np.zeros(self.time.shape)

        # Generate the signal samples for each component and add them
        for component in self.components:
            self.data += component.amplitude * \
                np.sin(2 * np.pi * component.frequency * self.time + component.phase)
        
        self.maxFreq = max([component.frequency for component in self.components])
        
