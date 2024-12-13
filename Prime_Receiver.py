import numpy as np
import Utility_functions
from multiprocessing.pool import ThreadPool

def shift(register, feedback, output):
    """
    mimics the feedback loop for the G1 and G2 portions for a GPS goldcode.
    """
    # calculate the Xor portion of the code.
    out = [register[i - 1] for i in output]
    if len(out) > 1:
        out = sum(out) % 2
    else:
        out = out[0]
    # modulo 2 add feedback
    fb = sum([register[i - 1] for i in feedback]) % 2
    # shift to the right
    for i in reversed(range(len(register[1:]))):
        register[i + 1] = register[i]
    # put feedback in position 1
    register[0] = fb
    return out


def prn(sv):
    """
    takes in sv number and will generate the G1+G2 ca code for it.
    """
    SV_table = {
        1: [2, 6],
        2: [3, 7],
        3: [4, 8],
        4: [5, 9],
        5: [1, 9],
        6: [2, 10],
        7: [1, 8],
        8: [2, 9],
        9: [3, 10],
        10: [2, 3],
        11: [3, 4],
        12: [5, 6],
        13: [6, 7],
        14: [7, 8],
        15: [8, 9],
        16: [9, 10],
        17: [1, 4],
        18: [2, 5],
        19: [3, 6],
        20: [4, 7],
        21: [5, 8],
        22: [6, 9],
        23: [1, 3],
        24: [4, 6],
        25: [5, 7],
        26: [6, 8],
        27: [7, 9],
        28: [8, 10],
        29: [1, 6],
        30: [2, 7],
        31: [3, 8],
        32: [4, 9],
    }

    # init registers
    G1 = [1 for i in range(10)]
    G2 = [1 for i in range(10)]
    ca = []  # stuff output in here
    # create sequence
    for i in range(1023):
        g1 = shift(G1, [3, 10], [10])
        g2 = shift(G2, [2, 3, 6, 8, 9, 10], SV_table[sv])
        # modulo 2 add and append to the code
        ca.append((g1 + g2) % 2)
    return ca


def complete_sim(carrier_freq, prn_freq, sample_rate, target_sat, chirp_length):
    # Generate ~1ms of data for a plain carrier, and a GPS signal
    signal_with_prn = []
    pure_signal_wave = []
    prn_binary = prn(target_sat)
    for i in range(chirp_length):
        t = i * sample_rate
        c = np.sin(((np.pi * 2)*carrier_freq)*t)
        pure_signal_wave.append(c)
        prn_bit = int((t * prn_freq)/1023) % 1023
        signal_with_prn.append(c * prn_binary[prn_bit])
    return signal_with_prn


def sat_prn_reference_table(carrier_freq, prn_freq, sample_rate, chirp_length):
    """ Creates a reference wave for each sat, then appends to a master table."""
    print("BOOTING")
    reference_table = []
    target_sat = 1  # start at key 1 for the sat
    while target_sat < 33:  # less than the total number of GPS sats
        SV_reference = complete_sim(carrier_freq, prn_freq, sample_rate, target_sat, chirp_length)
        reference_table.append(SV_reference)
        print("BOOTING: Reference wave for sat {} Created".format(target_sat))
        target_sat += 1
    print("BOOTED")
    return reference_table


def message_prn_encode(message, target_sat, carrier_freq, prn_freq, sample_rate, chirp_length):
    """this is a function that brings the PRN and words together"""
    message_to_prn = []
    SV_inverse = []
    SV_reference_perfect = complete_sim(carrier_freq, prn_freq, sample_rate, target_sat, chirp_length)
    for i in SV_reference_perfect:
        inverted = i * -1
        SV_inverse.append(inverted)
    for i in message:
        chirps = 0
        while chirps < 20:
            if i == "1":
                message_to_prn = np.append(message_to_prn, SV_reference_perfect)
            if i == "0":
                message_to_prn = np.append(message_to_prn, SV_inverse)

            chirps += 1
    print("ENCODING: Message translated into sat {} PRN chirps".format(target_sat))
    return message_to_prn


def PRN_reader(sat_detected, signal, reference_table):
    """ this function takes in our known sat, and signal receved, and gets binary back."""
    print("\nThread for sat {}".format(sat_detected))
    window_end = 1023
    window_start = 0
    negs, posi = 0, 0
    synced = 0
    reference_wave = reference_table[sat_detected]
    working_word = []
    while window_end <= len(signal):
        working_signal = signal[window_start:window_end]
        R_value = Utility_functions.correlationCoefficient(reference_wave, working_signal, len(working_signal))
        if R_value < -0.85:
            negs += 1
            if synced == 1:
                window_start = window_end - 23
                window_end += 1000
        elif R_value > 0.85:
            posi += 1
            if synced == 1:
                window_start = window_end - 23
                window_end += 1000
        window_end += 1
        window_start += 1
        if negs == 20 or posi == 20:
            synced = 1
            # now it will think it is synced after twenty chirps
            if negs == 20:
                working_word.append(0)
            elif posi == 20:
                working_word.append(1)
            negs, posi = 0, 0
    binary_string = Utility_functions.stringify(working_word)
    return binary_string


def reading_decoded_multisat(sats_detected, read_words):
    counter = 0
    words = []
    while counter < len(sats_detected):
        Ascii = Utility_functions.ascii_binary_translator(read_words[counter])
        output = "SAT {} DECODED.\nMESSAGE FOLLOWS: {}".format((sats_detected[counter]+ 1), Ascii)
        words.append(output)
        counter += 1
    return words


def multi_sat_splitter(message, carrier_freq, prn_freq, sample_rate, chirp_length):
    """
    this function takes a message, splits it over multiple sats
    """
    sat_active = 1
    words_encoded = []
    for word in message.split(" "):
        print(word)
        binary_word = Utility_functions.ascii_binary_translator(word)
        encoded_word = message_prn_encode(binary_word, sat_active, carrier_freq, prn_freq, sample_rate, chirp_length)
        words_encoded.append(encoded_word)
        sat_active += 1
    return words_encoded


def wave_merger(waves):
    """
    this is a function that has the only objective of taking each array of things, and adding them all
    Ultimately giveing a superimposed wave format.
    """
    superimposed = []
    t = 0
    for wave in waves:
        while t < len(wave):
            if len(superimposed) > t:
                superimposed_value = superimposed[t] + wave[t]
                superimposed.append(superimposed_value)
            else:
                superimposed.append(wave[t])
            t += 1
    return superimposed

def demodulate(carrier_frequency, synced_signal_in, sample_rate):
    x_axies = 0
    base_band_signal = []
    for reading in synced_signal_in:
        t = x_axies * sample_rate
        comparison_wave = np.sin(((np.pi * 2) * carrier_frequency) * t)
        base_band = reading * comparison_wave
        x_axies += 1
        if base_band == reading:
            base_band_signal.append(1)
        else:
            base_band_signal.append(-1)
    print(base_band_signal)
    return base_band_signal



def prn_detector(prn_codes, demodulated_signal_portion):
    for prn_code in prn_codes:
        index = 0
        while index < demodulated_signal_portion:
            return