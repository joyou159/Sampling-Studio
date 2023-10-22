
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
        self.current_signal = None
        self.preparing_signal = None
        self.init_ui()

    def init_ui(self):
        # Load the UI Page
        self.ui = uic.loadUi('mainwindow.ui', self)

        self.addComponent.clicked.connect(self.add_component)
        self.ui.GenerateButton.clicked.connect(self.generate_mixer)
        self.ui.signalsList.itemSelectionChanged.connect(
            self.handle_selected_signal)

    def add_component(self):

        frequency = float(self.ui.freqSpinBox.text())
        amplitude = float(self.ui.ampSpinBox.text())
        phase = float(self.ui.phaseSpinBox.text())

        component = Components(frequency, amplitude, phase)

        if self.preparing_signal is None:
            signal = Signal(f"Signal {len(self.signals)}")
            self.signals.append(signal)
            self.preparing_signal = signal
            if len(self.signals) == 1:
                self.current_signal = self.preparing_signal

        self.preparing_signal.add_component(component)
        self.add_to_attrList(component)

    def generate_mixer(self):
        if self.preparing_signal is not None:
            self.preparing_signal.generate_signal()
            self.ui.attrList.clear()
            self.add_to_signalsList(self.preparing_signal)
            self.preparing_signal = None

    def add_to_attrList(self, component):

        text = str(component)

        custom_widget = QWidget()
        layout = QHBoxLayout()

        label = QLabel(text)
        icon_button = QPushButton()
        # Set the path to your icon file
        icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.svg"))
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
        icon_button = QPushButton()
        # Set the path to your icon file
        icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.svg"))
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
            icon_button = QPushButton()
            # Set the path to your icon file
            icon_button.setIcon(QIcon("Icons/delete-svgrepo-com.svg"))
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
        if self.current_signal:
            self.add_to_componList()

    def delete_from_componList(self, component):
        self.current_signal.delete_component_after_preparing(component)
        print(self.current_signal.components)
        if self.current_signal.components == []:
            self.delete_from_signalsList(self.current_signal)

        else:
            self.update_componList()

    def update_componList(self):
        self.ui.componList.clear()
        for component in self.current_signal.components:
            self.add_to_componList()


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
