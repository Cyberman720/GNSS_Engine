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


def single_bit_generator(bits_per_wave, amplitude, theta, mode, sample_rate):
    """ this actually translates the bit to encode into a wave of the appropiate format"""
    length = np.pi * 2 * bits_per_wave
    if mode == "ASK":
        amplitude += 1  # double the amplitude
        encoded_bit = amplitude * np.sin(np.arange(0, length, length / sample_rate))
    elif mode == "PSK":
        encoding = int(theta) * 3  # 3 seems to move it 180 out of phase
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


def wave_step_down(list, carrier_freq, target_freq):
    edited = []
    factor = carrier_freq/target_freq
    for i in list:
        x = i / factor
        edited.append(x)
    return edited

def sat_detector(reference_table, signal_in, chirp_length):
    sat = 0
    start = 0
    while sat < 33:
        if np.correlate(reference_table[start: chirp_length],signal_in[chirp_length]) < 0.9:
            start += chirp_length
            print("sat: {}".format(sat))
            print("likelyhood: {}".format(np.correlate(reference_table[start: chirp_length],signal_in[chirp_length])))
            sat += 1
    print("sat found!")
    print("sat: {}".format(sat))
    print("likelyhood: {}".format(np.correlate(reference_table[start: chirp_length], signal_in[chirp_length])))
    return sat





def decode_phase_shift_keying(signal_in):
    """
    A phase shift key takes in our received wave, and checks it against our reference wave.
    This reference wave is a known value published by the operator of the transmitter.
    if we are in phase, that is a 1, out of phase by 180 degrees makes it a 0
    """
    buff_start = 0
    buff_end = 5
    decoded_bits = ""
    to_decode = signal_in[1:5]
    # I am going to check to see if the section trend is positive or negative e.g. phase of 0 or 3
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


def decode_frequency_shift_keying():
    """
    Frequency shift keying relys on the wave doubling or halving.
    doubling the frequency of our reference wave would be a 0 in our case, with satandard frequency being 1
    """

    return
