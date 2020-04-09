"""
Reactive Transport Gradients
A tool designed to take in arrays and calculate gradients and various other things related to trying to
use Reactive Transport Theories to quantify and navigate hydrothermal alteration systems
"""
# imports

import numpy as np
import pandas as pd
import numexpr as ne
from numpy import sqrt, arctan2
from PyQt5 import QtCore, QtWidgets, uic
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#FORM_CLASS, _ = uic.loadUiType(os.path.join(
#    os.path.dirname(__file__), 'RTGDialog.ui'))
FORM_CLASS, _ = uic.loadUiType(resource_path('RTGDialog.ui'))

class Interface(QtWidgets.QMainWindow, FORM_CLASS):
    calc_done = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(QtWidgets.QMainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.show()

        #connect interface items
        self.btn_infile.clicked.connect(lambda :self.openFileBrowser(self.led_input))
        self.btn_outfile.clicked.connect(lambda: self.saveFileBrowser(self.led_output))
        self.led_input.textChanged.connect(self.on_text_changed)
        self.led_output.textChanged.connect(self.on_text_changed)
        self.btn_run.clicked.connect(lambda: self.rtg(self.led_input.text(), self.led_output.text(),
                                                      self.chk_asc.isChecked()))
        self.calc_done.connect(self.showMsg)

    def saveFileBrowser(self, target):
        filename, filter =QtWidgets.QFileDialog.getSaveFileName(self, 'Save As', '/', "*.csv")
        target.setText(filename)

    def openFileBrowser(self, target):
        filename, filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '/', "*.csv")
        target.setText(filename)

    @QtCore.pyqtSlot(str)
    def showMsg(self, outfile):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Calculations complete")
        msg.setWindowTitle("RTG Calculations")
        msg.setDetailedText(outfile)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.buttonClicked.connect(self.reset)
        msg.exec()

    def on_text_changed(self):
        self.btn_run.setEnabled(bool(self.led_input.text()) and bool(self.led_output.text()))

    def reset(self):
        self.led_input.clear()
        self.led_output.clear()
        self.btn_run.setEnabled(False)

    # function for converting from cartesian to spherical
    def cart2sph(self,x, y, z, ceval=ne.evaluate):
        """ x, y, z :  ndarray coordinates
            ceval: backend to use:
                  - eval :  pure Numpy
                  - numexpr.evaluate:  Numexpr """
        azimuth = np.rad2deg(ceval('arctan2(x,y)')) + 180 # switched x and y to align o with north and shift to 0-360
        xy2 = ceval('x**2 + y**2')
        elevation = np.rad2deg(ceval('arctan2(z, sqrt(xy2))')) # gives inclination, with horizontal =0
        r = eval('sqrt(xy2 + z**2)')
        return azimuth, elevation, r

    def rtg(self, datafile, output, Z_Asc= False):
        # Read data into array
        # data assumptions that must be met:
        # 1) the array of points is orthogonal to x,y,z
        # 2) the array points are equidistant (this may be modified to allow for distance array to be added?)
        # 3) there is only one variable

        # assumes datafile has x,y,z and Nprog as header names. TODO If go to gui may be able to interactively set
        df = pd.read_csv(datafile, index_col=['x', 'y', 'z'], usecols=['x', 'y', 'z', 'Nprog'])

        # get unique values of the grid coords for determining shape and spacing
        z_val = df.index.get_level_values('z').unique()
        y_val = df.index.get_level_values('y').unique()
        x_val = df.index.get_level_values('x').unique()

        # work out shape of data assuming grid is orthogonal to axes
        z_size = len(z_val)
        y_size = len(y_val)
        x_size = len(x_val)

        # work out spacing in the array
        z_space = (z_val[0] - z_val[-1]) / (len(z_val) - 1)
        y_space = (y_val[0] - y_val[-1]) / (len(y_val) - 1)
        x_space = (x_val[0] - x_val[-1]) / (len(x_val) - 1)

        # sort the array. assume z is in RL therefore descending.
        sorted = df.sort_values(['z', 'y', 'x'], ascending=[Z_Asc, True, True])

        # reshape into ndarray
        Nprog_array = sorted.values.reshape(z_size, y_size, x_size)

        # perform gradient calculation
        gz, gy, gx = np.gradient(Nprog_array, z_space, y_space, x_space)
        # convert to spherical coords to represent vector
        azi, ele, r = self.cart2sph(gx, gy, gz)

        # Bring back together into dataframe
        result = pd.DataFrame({'Nprog': sorted.values.reshape(-1), 'Azi': azi.reshape(-1), 'Ele': ele.reshape(-1),
                               'r': r.reshape(-1), 'gx': gx.reshape(-1), 'gy': gy.reshape(-1), 'gz': gz.reshape(-1)},
                              sorted.index)
        # open up coords for calculation
        result = result.reset_index()
        # calculate dist to source
        result["dist"] = result["Nprog"] / result["r"]
        # and estimated source location
        result["x_sl"] = result["x"] + (result["Nprog"] / result["gx"])
        result["y_sl"] = result["y"] + (result["Nprog"] / result["gy"])
        result["z_sl"] = result["z"] + (result["Nprog"] / result["gz"])

        # write to file
        #output = r"C:\Users\Valheran\PycharmProjects\RTGradients\testoutput.csv"
        result.to_csv(output)
        self.calc_done.emit(output)   # tried to do it with signal

#code to run the window
app = QtWidgets.QApplication(sys.argv)
window = Interface()
app.exec()
