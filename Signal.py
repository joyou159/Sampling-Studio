from  Components import Components

class Signal:
    def __init__(self, name):
        self.name = name
        self.components = []
        self.samples =[]
        
        self.snr = None
        self.sample_rate = None
        
        
    def add_component(self,component):
        self.components.append(component)
    



