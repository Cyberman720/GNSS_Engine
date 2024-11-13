"""
This is a basic python script that takes in a sine wave, and converts it to bits
I will be implementing the three major types of shift keying to do this.
the object of this file is to be a function collection for a driver to use.
"""
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

def show_wave(to_show):
    """helper function to show the wave when i want to"""
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


def single_bit_generator(frequency, time, amplitude, theta, mode):
    if mode == "ASK":
        amplitude += 1  # double the amplitude
        encoded_bit = amplitude * np.sin(2 * np.pi * frequency * time + theta)
    elif mode == "PSK":
        encoding = int(theta) * 3  # 3 seems to move it 180 out of phase
        encoded_bit = amplitude * np.sin(2 * np.pi * frequency * time + encoding)
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
    amplitude = 1
    while bits_encoded < len(bits_to_encode):
        if mode == "ASK":
            amplitude = bits_to_encode[bits_encoded]
        elif mode == "PSK":
            theta = bits_to_encode[bits_encoded]
        sinewave = single_bit_generator(frequency, time, int(amplitude), theta, mode)
        for i in sinewave:
            total_wave.append(i)
        bits_encoded += 1
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
    empty = []
    for i in data:
        empty.append(i[0])
    arr = np.array(empty, dtype=np.float32)
    return arr


def decode_phase_shift_keying(to_decode, frequency, sample_rate):
    """
    A phase shift key takes in our received wave, and checks it against our reference wave.
    This reference wave is a known value published by the operator of the transmitter.
    if we are in phase, that is a 1, out of phase by 180 degrees makes it a 0
    """
    buff_start = 0
    buff_end = (sample_rate - 1)
    decoded_bits = ""

    # I am going to check to see if the section trend is positive or negative e.g. phase of 0 or 3
    while buff_end < len(to_decode):
        buff_section = to_decode[buff_start:buff_end]
        ave = 1
        buff_trend = 0
        while ave <= frequency:
            peak = float(buff_section[ave])
            buff_trend += peak
            print(buff_trend)
            ave += 1
        if buff_trend > 0:
            decoded_bits = "{}0".format(decoded_bits)
        else:
            decoded_bits = "{}1".format(decoded_bits)
        buff_start = buff_end
        buff_end += sample_rate
    return decoded_bits


def decode_amplitude_shift_keying(to_decode, frequency, sample_rate):
    """
    amplitude shift keying takes in the wave amplitude on the Y axies.
    If the aplitude is doubled, that makes it a 1, and if the amplitude is halved, it is a 0
    """
    """reference wave, if same == 0, if bigger == 1"""
    start_time = 0
    end_time = 1
    time = np.arange(start_time, end_time, 1 / sample_rate)
    theta = 0
    amplitude = 1
    reference_wave = amplitude * np.sin(2 * np.pi * frequency * time + theta)
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
        if buff_mean > 1.8*amplitude:
            decoded_bits = "{}1".format(decoded_bits)
        else:
            decoded_bits = "{}0".format(decoded_bits)
        buff_start = buff_end
        buff_end += sample_rate
    return decoded_bits


def decode_frequency_shift_keying():
    """
    Frequency shift keying relys on the wave doubling or halving.
    doubling the frequency of our reference wave would be a 0 in our case, with satandard frequency being 1
    """

    return
