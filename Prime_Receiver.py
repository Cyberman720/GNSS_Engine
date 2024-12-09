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


def sat_prn_table(carrier_freq, prn_freq, sample_rate, chirp_length):
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

def message_PRN_encode(message, target_sat, carrier_freq, prn_freq, sample_rate, chirp_length):
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




def sat_detector(reference_table, signal_in, chirp_length):
    """
        This is a function that determines the chance that the signal received is from a given sat.
        comparing the initial signal against all sats, we can determine what it came from.
    """
    sat = 0
    sats = []
    print("ACQUIRING")
    while sat < len(reference_table):
        receved_chirp = signal_in[:chirp_length]
        sat_reference = reference_table[sat]
        R_value = Utility_functions.correlationCoefficient(sat_reference, receved_chirp, chirp_length)
        sat += 1
        if abs(R_value) > 0.9:
            print("SIGNAL ACQUIRED")
            print("SAT: {} DETECTED".format((sat+1)))
            print("LIKELIHOOD: {}".format(R_value))
            sats.append(sat)
    return sats, R_value


def PRN_reader(sat_detected, signal, reference_table):
    """ this function takes in our known sat, and signal receved, and gets binary back."""
    print("READING SIGNAL")
    window_end = 1023
    window_start = 0
    negs, posi = 0, 0
    synced = 0
    reference_wave = reference_table[sat_detected]
    working_word = []
    while window_end <= len(signal):
        working_signal = signal[window_start:window_end]
        R_value = Utility_functions.correlationCoefficient(reference_wave, working_signal, len(working_signal))
        if R_value < -0.95:
            negs += 1
            if synced == 1:
                window_start = window_end - 23
                window_end += 1000
        elif R_value > 0.95:
            posi += 1
            if synced == 1:
                window_start = window_end - 23
                window_end += 1000
        if negs == 20 or posi == 20:
            synced = 1
            # now it will think it is synced after twenty chirps
            if negs == 20:
                working_word.append(0)
            if posi == 20:
                working_word.append(1)
            negs, posi = 0, 0

        window_end += 1
        window_start += 1
    binary_string = Utility_functions.stringify(working_word)
    return binary_string


def multi_sat_handler(sats_detected, signal, reference_table):
    """
    this handler pulls up a thread for each sat's PRN
    pulls up the PRN reader fucntion and feeds in a different sat in for each thread.
    it will them wave match for each sat.
    """
    count = 0
    args = []
    message_recived = []
    while count < len(sats_detected):
        SV_found = [sats_detected[count], signal, reference_table]
        args.append(SV_found)
        count += 1
    with ThreadPool() as pool:
        # call the same function with different data concurrently
        for message_read in pool.starmap(PRN_reader, args):
            # report the value to show progress
            message_recived.append(message_read)
        print("WORD READ")
        pool.close()
    return message_recived


def reading_decoded_multisat(sats_detected, read_words):
    counter = 0
    words = []
    while counter < len(sats_detected):
        Ascii = Utility_functions.ascii_binary_translator(read_words[counter])
        output = "SAT {} DECODED.\nMESSAGE FOLLOWS: {}".format(sats_detected[counter], Ascii)
        words.append(output)
        counter += 1
    return words
