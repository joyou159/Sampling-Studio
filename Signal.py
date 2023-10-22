from  Components import Components
import numpy as np

class Signal:
    def __init__(self, name):
        self.name = name
        self.components = []
        self.data =[]
        
        self.snr = None
        self.sample_rate = None
        
    def add_component(self,component):
        self.components.append(component)
        
    def delete_component_after_preparing(self, component):
        if component in self.components:
            self.components.remove(component)
        self.generate_samples()
        
    def delete_component_during_preparing(self, component):
        if component in self.components:
            self.components.remove(component)
            
    
        
    def generate_signal(self):
        self.generate_samples()



    def generate_samples(self):
        time = np.linspace(0, 1, 1000)

        # Initialize self.samples as an empty array with the same shape
        self.data = np.zeros(time.shape)

        # Generate the signal samples for each component and add them
        for component in self.components:
            self.data += component.amplitude * np.sin(2 * np.pi * component.frequency * time + component.phase)

        


        
    


