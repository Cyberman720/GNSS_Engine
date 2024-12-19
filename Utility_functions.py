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


"""******************************************************************************************************************"""
def decimate(list_in, factor):
    """ helper function to decimate a list of points down."""
    counter = 1
    decimated = []
    while counter < len(list_in):
        if (counter % (factor-1)) / (factor-1) == 0:
            decimated.append(list_in[counter])
        counter += 1
    print(decimated)
    return decimated


def single_bit_generator(bits_per_wave, amplitude, theta, mode, sample_rate):
    """ this actually translates the bit to encode into a wave of the appropiate format"""
    length = np.pi * 2 * bits_per_wave
    if mode == "ASK":
        amplitude += 1  # double the amplitude
        encoded_bit = amplitude * np.sin(np.arange(0, length, length / sample_rate))
    elif mode == "PSK":
        encoding = int(theta) * np.pi  # 1pi is 180 degrees out of phase for a sine wave
        encoded_bit = amplitude * np.sin(np.arange(0, length, length / sample_rate) + encoding)
    return encoded_bit


def wave_creator(sample_rate, waves_per_bit, bits_to_encode, mode):
    """
    a utility function that takes our binary and puts it into a sine wave.
    frequency, number of peaks per second.
    sample_rate, total number of samples per second
    time, number of sets of the above.
    """
    theta = 0
    total_wave = []
    bits_encoded = 0
    amplitude = 1
    while bits_encoded < len(bits_to_encode):
        if mode == "ASK":
            amplitude = bits_to_encode[bits_encoded]
        elif mode == "PSK":
            theta = bits_to_encode[bits_encoded]
        sinewave = single_bit_generator(waves_per_bit, int(amplitude), theta, mode, sample_rate)
        for sample in sinewave:
            total_wave.append(sample)
        bits_encoded += 1
    return total_wave


def decode_phase_shift_keying(signal_in):
    """
    A phase shift key takes in our received wave, and checks it against our reference wave.
    This reference wave is a known value published by the operator of the transmitter.
    if we are in phase, that is a 1, out of phase by 180 degrees makes it a 0
    """
    buff_start = 0
    buff_end = 5
    decoded_bits = ""
    to_decode = signal_in[:5]
    # I am going to check to see if the section trend is positive or negative e.g. phase of 0 or pi
    while buff_end < len(to_decode):
        buff_section = to_decode[buff_start:buff_end]
        ave = 1
        buff_trend = 0
        peak = float(buff_section[ave])
        while ave < 5:
            local = float(buff_section[ave])
            buff_trend += local
            ave += 1
        buff_mean = buff_trend / ave
        if buff_mean > peak:
            decoded_bits = "{}0".format(decoded_bits)
        else:
            decoded_bits = "{}1".format(decoded_bits)
        buff_start = buff_end
        buff_end += 5
    return decoded_bits


def decode_amplitude_shift_keying(to_decode, frequency, sample_rate):
    """
    amplitude shift keying takes in the wave amplitude on the Y axies.
    If the aplitude is doubled, that makes it a 1, and if the amplitude is halved, it is a 0
    """
    """reference wave, if same == 0, if bigger == 1"""
    ref_amplitude = 1
    buff_start = 0
    buff_end = (sample_rate - 1)
    decoded_bits = ""
    while buff_end < len(to_decode):
        buff_section = np.sort(to_decode[buff_start:buff_end])
        ave = 1
        buff_total = 0
        while ave <= frequency:
            inverse_ave = ave * -1
            peak = float(buff_section[inverse_ave])
            buff_total = buff_total + peak
            ave += 1
        buff_mean = buff_total/frequency
        if buff_mean > 1.8 * ref_amplitude:
            decoded_bits = "{}1".format(decoded_bits)
        else:
            decoded_bits = "{}0".format(decoded_bits)
        buff_start = buff_end
        buff_end += sample_rate
    return decoded_bits
"""******************************************************************************************************************"""


def demodulate_phase_shift_keying(to_decode):
    """this function aims to determine if a given point is in phase or out of phase."""
    amplitude = 1
    length = 1
    encoding = 1  # e.g. in standard phase
    base_band = []
    sample_rate = 100
    index_start = 0
    index_end = index_start + sample_rate
    perfect_wave = (amplitude * np.sin(np.arange(0, length, length / sample_rate) + encoding))
    while index_end <= len(to_decode):
        buffer = to_decode[index_start:index_end]
        dot_prod = 0
        for i in buffer:
            dot_prod = dot_prod + (perfect_wave[(index_start%sample_rate)] * i)
            index_start += 1
        if dot_prod > 0:
            base_band.append(1)
        else:
            base_band.append(0)
        index_end += sample_rate
    message = stringify(base_band)
    return message


def polar_encoding(bit):
    """ helper function to turn 1 and 0 into 1 and -1"""
    if str(bit) == "1":
        polar = 1
    else:
        polar = -1
    return polar


def show_wave(to_show):
    """helper function to show the wave when I want to"""
    numpy_array = np.array(to_show)
    plt.plot(numpy_array)
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


def correlation_coefficient(X, Y, n):
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


