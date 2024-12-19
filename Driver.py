import F1_GNSS
import numpy as np

import Utility_functions

"""
This is the main driver that uses files, Prime Receiver and Utility functions.
the purpose is to have the fiddly stuff separate and open the door to making a UI or some other form of control.
Written by Henry Rogers.
10/12/2024
"""


def main():
    print("\nBOOTING...")
    sample_rate = 100
    encoding = 1
    length = 1
    amplitude = 1
    target_sat = 25
    print("SETTINGS SET")
    print("GENERATEING: MESSAGE TO BINARY")
    binary_message = Utility_functions.ascii_binary_translator("HELLO WORLD")
    sat_2_message = Utility_functions.ascii_binary_translator("Funky Stuff")
    print("GENERATEING: GOLD CODE")
    print("GENERATEING: SINE WAVE")
    reference_sine = (amplitude * np.sin(np.arange(0, length, length / sample_rate) + encoding))
    list_of_encoded_waves = F1_GNSS.prn_encode_to_wave()
    print("MESSAGE BEING ENCODED AS CHIRPS")
    message_encoded_wave = F1_GNSS.chirp_prn_wave_as_bits(list_of_encoded_waves[target_sat], binary_message)
    sat_2_encoded_wave = F1_GNSS.chirp_prn_wave_as_bits(list_of_encoded_waves[2],sat_2_message)
    print("SUPERIMPOSING WAVES")
    super_wave = F1_GNSS.superimpose_waves(message_encoded_wave, sat_2_encoded_wave)
    print("DEMODULATING...")
    demodulated_wave = F1_GNSS.demodulate_phase_shift_keying(super_wave, reference_sine, sample_rate)
    print("INTERGRATING CHIRPS")
    binary_read_message = F1_GNSS.de_chip_message(demodulated_wave)
    print(binary_read_message)
    print("PERFORMING CDMA shift")
    messages = F1_GNSS
    print("READING BINARY")
    word = Utility_functions.ascii_binary_translator(binary_read_message)
    print("MESSAGE FOLLOWS:\n{}".format(word))

main()

