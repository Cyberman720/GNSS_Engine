"""
This is a basic python script that takes in a sine wave, and converts it to bits
I will be implementing the three major types of shift keying to do this.
the object of this file is to be a function collection for a driver to use.
"""
import numpy as np
import csv
import os
import math
from scipy.signal import periodogram
import matplotlib.pyplot as plt
from matplotlib import rcParams

def show_wave(to_show):
    """helper function to show the wave when I want to"""
    plt.plot(to_show)
    plt.show()



def ascii_binary_translator(translate_me):
    """
    this is a helper function that takes in either binary or Text and outputs the inverse.
    """
    bits = 8
    if translate_me.isnumeric():
        working_string = str(translate_me)
        grouped = [(working_string[i:i+bits]) for i in range(0, len(working_string), bits)]
        binary_string = " ".join(str(x) for x in grouped)
        translated = ''.join([chr(int(binary, 2)) for binary in binary_string.split(' ')])
    else:
        binary = ' '.join([f'{ord(char):08b}' for char in translate_me])
        translated = ("{}".format(binary)).replace(" ", "")
    return translated


def save_wave(wave, file_name):
    """ saves the wave as a basic CSV of measured points."""
    file_checker = True
    while file_checker:
        duplicate_catcher = 0
        file_location = "Waves/{}.csv".format(file_name)
        if os.path.isfile(file_location) == True:
            file_name = "{}({})".format(file_name, duplicate_catcher)
        else:
            np.savetxt(file_location, wave, delimiter=',')
            break
        duplicate_catcher += 1


def load_wave(file):
    """load an existing wave"""
    file_location = "Waves/{}.csv".format(file)
    with open(file_location, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    empty = []
    for i in data:
        empty.append(i[0])
    arr = np.array(empty, dtype=np.float32)
    return arr


def stringify(to_encode):
    """simple helper that turns list of binary values into string to send other places"""
    binary_string = ""
    for i in to_encode:
        binary_string = "{}{}".format(binary_string, i)
    return binary_string


def correlationCoefficient(X, Y, n):
    """
        I couldn't find a better way of calculating a pearson R value for correlating the two lists of signals.
        takes in list X and compares it against list Y, it works though the length of the list n to do a full comparison
    """
    sum_X = 0
    sum_Y = 0
    sum_XY = 0
    squareSum_X = 0
    squareSum_Y = 0

    i = 0
    while i < n:
        # sum of elements of array X.
        sum_X = sum_X + X[i]
        # sum of elements of array Y.
        sum_Y = sum_Y + Y[i]
        # sum of X[i] * Y[i].
        sum_XY = sum_XY + X[i] * Y[i]
        # sum of square of array elements.
        squareSum_X = squareSum_X + X[i] * X[i]
        squareSum_Y = squareSum_Y + Y[i] * Y[i]
        i += 1
    # use formula for calculating correlation
    # coefficient.
    corr = (float)(n * sum_XY - sum_X * sum_Y) / (float)(math.sqrt((n * squareSum_X -
                                                                    sum_X * sum_X) * (n * squareSum_Y - sum_Y * sum_Y)))
    return corr

def plot_frequency_spectrum(signal_receved, reference_wave, sample_rate):
    """This is a helper function that can be used to graph out our frequency stuff."""
    # periodogram gives us a power spectrum at discrete frequency bins
    f_s, P_s = periodogram(signal_receved, 1 / sample_rate, scaling='spectrum')
    f_c, P_c = periodogram(reference_wave, 1 / sample_rate, scaling='spectrum')
    rcParams.update({'font.size': 12})
    ax = plt.figure(figsize=(15, 8))
    plt.title("GPS Spreading")
    plt.xlabel("Frequency [GHz]")
    plt.ylabel(r"Relative Power [$\frac{V^2}{Hz}$]")
    ax.axes[0].grid(color='grey', alpha=0.2, linestyle='dashed', linewidth=0.5)

    # chart signal and carrier
    plt.semilogy(f_s, P_s, '#e31d1d', alpha=0.9, label="Spread GPS signal")
    plt.semilogy(f_c, P_c, '#709afa', label="Plain sine wave")
    plt.legend(loc=1)

    # show 30 MHz on either side of the center frequency
    ax.axes[0].set_xlim([(1.57542e9 - 30e6), (1.57542e9 + 30e6)])
    ax.axes[0].set_ylim([1e-32, 1])
    plt.show()

