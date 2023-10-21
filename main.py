
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QColorDialog, QListWidgetItem, QMessageBox, QDialogButtonBox
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
from  Components import Components

 
class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        #Signals objects
        self.signals =[]
        self.init_ui()
    def init_ui(self):
        # Load the UI Page
        self.ui = uic.loadUi('mainwindow.ui', self)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
