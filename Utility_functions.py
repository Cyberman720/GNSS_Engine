"""
This is a basic python script that takes in a sine wave, and converts it to bits
I will be implementing the three major types of shift keying to do this.
the object of this file is to be a function collection for a driver to use.
"""
import numpy as np
import matplotlib.pyplot as plt
import csv
import os


def ascii_binary_translator(translate_me):
    """
    this is a helper function that takes in either binary or Text and outputs the inverse.
    """
    if translate_me.isnumeric():
        translated = ''.join([chr(int(binary, 2)) for binary in translate_me.split(' ')])
    else:
        binary = ' '.join([f'{ord(char):08b}' for char in translate_me])
        translated = ("{}".format(binary)).replace(" ", "")
    return translated


def single_bit_generator(frequency, time, amplitude, theta, mode):
    if mode == "ASK":
        amplitude += 1
        encoded_bit = amplitude * np.sin(2 * np.pi * frequency * time + theta)
    return encoded_bit


def wave_creator(end_time, sample_rate, frequency, bits_to_encode, mode):
    """
    a utility function that takes our binary and puts it into a sine wave.
    frequency, number of peaks per second.
    sample_rate, total number of samples per second
    time, number of sets of the above.
    """
    start_time = 0
    theta = 0
    time = np.arange(start_time, end_time, 1 / sample_rate)
    total_wave = []
    bits_encoded = 0
    while bits_encoded < len(bits_to_encode):
        amplitude = bits_to_encode[bits_encoded]
        sinewave = single_bit_generator(frequency, time, int(amplitude), theta, mode)
        for i in sinewave:
            total_wave.append(i)
        bits_encoded += 1
    plt.plot(total_wave)
    plt.show()
    return total_wave


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
    array = []
    for i in data:
        array.append(i[0])
    return array


def phase_shift_keying():
    """
    A phase shift key takes in our received wave, and checks it against our reference wave.
    This reference wave is a known value published by the operator of the transmitter.
    if we are in phase, that is a 1, out of phase by 180 degrees makes it a 0
    """
    return


def amplitude_shift_keying():
    """
    amplitude shift keying takes in the wave amplitude on the Y axies.
    If the aplitude is doubled, that makes it a 1, and if the amplitude is halved, it is a 0
    """

    return


def frequency_shift_keying():
    """
    Frequency shift keying relys on the wave doubling or halving.
    doubling the frequency of our reference wave would be a 0 in our case, with satandard frequency being 1
    """

    return
