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


# function for converting from cartesian to spherical
def cart2sph(x, y, z, ceval=ne.evaluate):
    """ x, y, z :  ndarray coordinates
        ceval: backend to use:
              - eval :  pure Numpy
              - numexpr.evaluate:  Numexpr """
    azimuth = np.rad2deg(ceval('arctan2(x,y)')) % 360  # switched x and y to align 0 with north and % to shift to 0-360
                                            # use of % is a bit unique to python in -ve numbers, matlab should be similar
    xy2 = ceval('x**2 + y**2')
    elevation = np.rad2deg(ceval('arctan2(z, sqrt(xy2))'))  # gives inclination, with horizontal =0
    r = eval('sqrt(xy2 + z**2)')
    return azimuth, elevation, r


# Read data into array
# data assumptions that must be met:
# 1) the array of points is orthogonal to x,y,z
# 2) the array points are equidistant (this may be modified to allow for distance array to be added?)
# 3) there is only one variable
# TODO probably make this interactive either in GUI or script argument
datafile = r'C:\Users\Valheran\PycharmProjects\RTGradients\testdatahumpx.csv'

# assumes datafile has x,y,z and Nprog as header names. If go to gui may be able to interactively set
df = pd.read_csv(datafile, index_col=['x', 'y', 'z'], usecols=['x', 'y', 'z', 'Nprog'])

# sort the array. assume z is in RL therefore ascending.   TODO perhaps this needs to be a flag
Z_Asc = True # Flag for ascending or descending Z
sorted = df.sort_values(['z', 'y', 'x'], ascending=[Z_Asc, True, True])

# get unique values of the grid coords for determining shape and spacing
z_val = sorted.index.get_level_values('z').unique()
y_val = sorted.index.get_level_values('y').unique()
x_val = sorted.index.get_level_values('x').unique()

# work out shape of data assuming grid is orthogonal to axes
z_size = len(z_val)
y_size = len(y_val)
x_size = len(x_val)

# work out spacing in the array

z_space = (z_val[-1] - z_val[0]) / (len(z_val) - 1)
y_space = (y_val[-1] - y_val[0]) / (len(y_val) - 1)
x_space = (x_val[-1] - x_val[0]) / (len(x_val) - 1)


# reshape into ndarray
Nprog_array = sorted.values.reshape(z_size, y_size, x_size)

# perform gradient calculation
gz, gy, gx = np.gradient(Nprog_array, z_space, y_space, x_space)
# convert to spherical coords to represent vector
azi, ele, r = cart2sph(gx, gy, gz)

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
output = r"C:\Users\Valheran\PycharmProjects\RTGradients\testoutputgrad.csv"
result.to_csv(output)
