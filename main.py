
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFileDialog, QMessageBox, QColorDialog, QListWidgetItem, QMessageBox, QDialogButtonBox, QPushButton
import wfdb
import numpy as np
import sys
from pyqtgraph.Qt import QtCore
from PyQt6 import QtWidgets, uic
import pyqtgraph as pg
import csv
from fpdf import FPDF
from pyqtgraph.exporters import ImageExporter
import os
import random
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence, QIcon


from Signal import Signal
from Components import Components


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Signals objects

        self.signals = [] 
        # self.time = [] why they might be global, while they can be local for the browse method, as said by the Eng.
        # self.data = []
        self.current_signal = None
        self.preparing_signal = None
        self.sliders_init = None # handling_sliders (either set or update)

        self.init_ui()

    def init_ui(self):
        # Load the UI Page
        self.ui = uic.loadUi('mainwindow.ui', self)
        self.ui.graph1.setLimits(xMin = -0.1, xMax =1.1)
        self.ui.graph2.setLimits(xMin = -0.1, xMax =1.1)
        self.ui.graph3.setLimits(xMin = -0.1, xMax =1.1)

        self.addComponent.clicked.connect(self.add_component)
        self.ui.GenerateButton.clicked.connect(self.generate_mixer)
        self.ui.signalsList.itemSelectionChanged.connect(
            self.handle_selected_signal)
        self.ui.uploadButton.clicked.connect(self.browse)
        self.ui.startLabel.setText("")
        self.ui.endLabel.setText("")
        self.ui.sampleSlider.valueChanged.connect(self.handle_sliders)
        self.ui.actualRadio.toggled.connect(self.radioToggled)
        self.ui.normalRadio.toggled.connect(self.radioToggled)

        # there is a function called update_sliders() that can be used with Noise slider as well 
        

    def browse(self):
        file_filter = "Raw Data (*.csv)"
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Open Signal File', './', filter=file_filter)
        
        if file_path:
            self.open_file(file_path)
    

    def open_file(self, path: str):
        time = []
        data = []
        # Extract the file extension (last 3 characters) from the path
        filetype = path[-3:]

        # Check if the file type is CSV, text (txt), or Excel (xls)
        if filetype in ["csv", "txt", "xls"]:
            # Open the data file for reading ('r' mode)
            with open(path, 'r') as data_file:
                # Create a CSV reader object with comma as the delimiter
                data_reader = csv.reader(data_file, delimiter=',')

                # Iterate through each row (line) in the data file
                for row in data_reader:
                    # Extract the time value from the first column (index 0)
                    time_value = float(row[0])

                    # Extract the amplitude value from the second column (index 1)
                    amplitude_value = float(row[1])

                    # Append the time and amplitude values to respective lists
                    time.append(time_value)
                    data.append(amplitude_value)
                    
        numbering = len(self.signals) - 1 
        signal = Signal(f"signal {numbering}") 
        signal.time = time
        signal.data = data
        self.current_signal = signal
        # self.set_sliders ()
        self.plot_mixed_signals(signal)


    def sample_and_reconstruct(self,signal):
        # signal.sample_rate = 20 # for the sake of testing. 
        self.ui.graph2.clear()
        signal

        # Sample the continuous signal
        sampled_time = np.array([signal.time[i] for i in range(0,len(signal.time),int(len(signal.time)/signal.sample_rate))]) # depends on the signal samples 
        sampled_data = np.array([signal.data[i] for i in range(0,len(signal.data),int(len(signal.data)/signal.sample_rate))])

        # marking the samples at graph1 plot
        scatter_plot = pg.ScatterPlotItem(x=sampled_time, y=sampled_data, pen='r', symbol='x', size=10)
        self.ui.graph1.addItem(scatter_plot)

        # reconstruct the signal using sinc interpolation 
        sampling_interval = 1 / signal.sample_rate
        interpolated_data = np.zeros_like(signal.time)
        for i in range(len(sampled_data)):
            interpolated_data += sampled_data[i] * np.sinc((signal.time - sampled_time[i])/sampling_interval)
        

        # plotting the interpolated signal in graph2
        self.ui.graph2.setLabel('left', "Amplitude")
        self.ui.graph2.setLabel('bottom', "Time")
        self.ui.graph2.plot(signal.time,interpolated_data)
        self.ui.graph2.setLimits(yMin = min(interpolated_data)-1, yMax =max(interpolated_data)+1)


    def plot_mixed_signals(self, signal):
        if signal:
            self.ui.graph1.clear()

            # Create a plot item
            self.ui.graph1.setLabel('left', "Amplitude")
            self.ui.graph1.setLabel('bottom', "Time")

            # Initialize the time axis (assuming all signals have the same time axis)
            x_data = signal.time
            
            y_data = signal.data

        # Plot the mixed waveform
            self.ui.graph1.plot(x_data, y_data, name=signal.name)
            self.ui.graph1.setLimits(yMin = min(y_data)-1, yMax =max(y_data)+1)
            
            # handling plot in graph2
            self.sample_and_reconstruct(signal) 
    


    def add_component(self):
        frequency = int(self.ui.freqSpinBox.text())
        amplitude = int(self.ui.ampSpinBox.text())
        phase = int(self.ui.phaseSpinBox.text())

        component = Components(frequency, amplitude, phase)

        if self.preparing_signal is None:
            name = f"Signal {len(self.signals)}"
            signal = Signal(name)
            self.signals.append(signal)
            self.preparing_signal = signal
            # what is the meaning of this ??
            # if len(self.signals) == 1:
            #     self.current_signal = self.preparing_signal

        self.preparing_signal.add_component(component)
        self.add_to_attrList(component)
        # self.plot_signal(self.preparing_signal)


    def generate_mixer(self):
        if self.preparing_signal is not None:
            self.preparing_signal.generate_signal()
            self.ui.attrList.clear()
            self.add_to_signalsList(self.preparing_signal)
            self.preparing_signal = None

        # Select the last row in signalsList
        last_row = len(self.signals) - 1
        if last_row >= 0:
            self.ui.signalsList.setCurrentRow(last_row)
        self.ui.actualRadio.setChecked(True)
        self.set_sliders()
        self.current_signal = self.signals[-1]
        self.plot_mixed_signals(self.current_signal)

        

    def add_to_attrList(self, component):

        text = str(component)

        custom_widget = QWidget()
        layout = QHBoxLayout()

        label = QLabel(text)
        label.setStyleSheet("color:white")

        icon_button = QPushButton()
        # Set the path to your icon file
        icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.svg"))
        icon_button.setStyleSheet("background-color:transparent")
        icon_button.clicked.connect(
            lambda: self.delete_from_attrList(component))

        layout.addWidget(icon_button)
        layout.addWidget(label)
        custom_widget.setLayout(layout)

        # Create a QListWidgetItem and set the custom widget as the display widget
        item = QListWidgetItem()
        item.setSizeHint(custom_widget.sizeHint())
        self.ui.attrList.addItem(item)
        self.ui.attrList.setItemWidget(item, custom_widget)

        # Reset the values
        self.ui.freqSpinBox.setValue(0)
        self.ui.ampSpinBox.setValue(0)
        self.ui.phaseSpinBox.setValue(0)


    def delete_from_attrList(self, component):
        self.preparing_signal.delete_component_during_preparing(component)
        self.update_attrList()


    def update_attrList(self):
        self.ui.attrList.clear()
        for component in self.preparing_signal.components:
            self.add_to_attrList(component)

    def add_to_signalsList(self, signal):

        text = signal.name

        custom_widget = QWidget()
        layout = QHBoxLayout()

        label = QLabel(text)
        label.setStyleSheet("color:white")
        icon_button = QPushButton()
        # Set the path to your icon file
        icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.svg"))
        icon_button.setStyleSheet("background-color:transparent")
        icon_button.clicked.connect(
            lambda: self.delete_from_signalsList(signal))

        layout.addWidget(icon_button)
        layout.addWidget(label)
        custom_widget.setLayout(layout)

        # Create a QListWidgetItem and set the custom widget as the display widget
        item = QListWidgetItem()
        item.setSizeHint(custom_widget.sizeHint())
        self.ui.signalsList.addItem(item)
        self.ui.signalsList.setItemWidget(item, custom_widget)


    def delete_from_signalsList(self, signal):
        for sig in self.signals:
            if signal == sig:
                if self.current_signal == signal:
                    self.current_signal = None
                    self.ui.componList.clear()
                self.signals.remove(signal)
        self.update_signalsList()


    def update_signalsList(self):
        current_item = self.ui.signalsList.currentRow()
        self.ui.signalsList.clear()
        for signal in self.signals:
            self.add_to_signalsList(signal)
        self.ui.signalsList.setCurrentRow(current_item)


    def add_to_componList(self):
        self.ui.componList.clear()
        for component in self.current_signal.components:
            text = str(component)
            custom_widget = QWidget()
            layout = QHBoxLayout()

            label = QLabel(text)
            label.setStyleSheet("color:white")
            icon_button = QPushButton()
            # Set the path to your icon file
            icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.svg"))
            icon_button.setStyleSheet("background-color:transparent")
            icon_button.clicked.connect(
                lambda: self.delete_from_componList(component))

            layout.addWidget(icon_button)
            layout.addWidget(label)
            custom_widget.setLayout(layout)

            # Create a QListWidgetItem and set the custom widget as the display widget
            item = QListWidgetItem()
            item.setSizeHint(custom_widget.sizeHint())
            self.ui.componList.addItem(item)
            self.ui.componList.setItemWidget(item, custom_widget)

    def get_selected_signal(self):
        selected_item = self.ui.signalsList.currentItem()

        if selected_item:
            # Get the custom widget associated with the selected item
            custom_widget = self.ui.signalsList.itemWidget(selected_item)

            # Assuming the label is the first child of the custom widget
            label = custom_widget.findChild(QLabel)

            if label:
                signal_name = label.text()
                # Find the signal object with the matching name
                for signal in self.signals:
                    if signal.name == signal_name:
                        return signal  # Return the selected signal

    def handle_selected_signal(self):
        selected_signal = self.get_selected_signal()
        self.current_signal = selected_signal
        self.set_sliders()
        self.ui.graph1.clear()
        self.plot_mixed_signals(self.current_signal)
        if self.current_signal:
            self.add_to_componList()

    def delete_from_componList(self, component):
        self.current_signal.delete_component_after_preparing(component)
        self.handle_selected_signal()
        print(self.current_signal.components)
        if self.current_signal.components == []:
            self.delete_from_signalsList(self.current_signal)

        else:
            self.update_componList()

    def update_componList(self):
        self.ui.componList.clear()
        for component in self.current_signal.components:
            self.add_to_componList()

    def handle_sliders(self):
        if self.sliders_init: # the first call is always a set up 
            self.sliders_init = False # suppress the calling 
        else: # any further calling will be adjusting 
            self.update_sliders()

    def update_sliders(self):
        self.current_signal.change_sample_rate(int(self.ui.sampleSlider.value()))
        self.plot_mixed_signals(self.current_signal)
        

    def set_sliders(self):
        self.sliders_init = True
        if self.current_signal == None:
            return 
        elif self.current_signal.sampling_mode == 0:
            self.ui.actualRadio.setChecked(True)
            self.ui.sampleSlider.setMinimum(1)
            self.ui.sampleSlider.setMaximum(int(self.current_signal.maxFreq * 4)) 
            self.ui.startLabel.setText("1")
            self.ui.endLabel.setText(str(int(self.current_signal.maxFreq * 4)))
            self.sampleSlider.setSingleStep(1)
            self.sampleSlider.setValue(int(self.current_signal.sample_rate)) # handle_sliders is called() due to the connection, and i want to suppress this calling 
        else:
            self.ui.normalRadio.setChecked(True)
            self.ui.sampleSlider.setMinimum(self.current_signal.maxFreq)
            self.ui.sampleSlider.setMaximum(int(self.current_signal.maxFreq * 4)) 
            self.ui.startLabel.setText("1 x Max freq")
            self.ui.endLabel.setText(f"4 x Max freq")
            self.sampleSlider.setSingleStep(int(self.current_signal.maxFreq))
            self.sampleSlider.setValue(int(self.current_signal.sample_rate))

    def radioToggled(self):
        if self.ui.actualRadio.isChecked():
            self.current_signal.change_sampling_mode(0)
            self.set_sliders()
        else:
            self.current_signal.change_sampling_mode(1)
            self.set_sliders()
        

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
