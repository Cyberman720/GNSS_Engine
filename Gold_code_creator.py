from scipy.signal import periodogram
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np

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



def sat_modified(prn_binary):
    counter = 0
    while counter < len(prn_binary):
        if prn_binary[counter] == 0:
            prn_binary[counter] = -1
        counter += 1
    return prn_binary


def complete_sim(carrier_freq, prn_freq, sample_rate, target_sat, chirp_length):
    # Generate ~1ms of data for a plain carrier, and a GPS signal
    signal_with_prn = []
    pure_signal_wave = []
    prn_binary = prn(target_sat)
    prn_binary_mod = sat_modified(prn_binary)
    for i in range(chirp_length):
        t = i * sample_rate
        c = np.sin(((np.pi * 2)*carrier_freq)*t)
        pure_signal_wave.append(c)
        prn_bit = int(t * prn_freq) % 1023
        signal_with_prn.append(c * prn_binary[prn_bit])
    return signal_with_prn


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


def sat_prn_table(carrier_freq, prn_freq, sample_rate, chirp_length):
    """ Creates a reference wave for each sat, then appends to a master table."""
    reference_table = []
    target_sat = 20
    while target_sat < 30:
        SV_reference = complete_sim(carrier_freq, prn_freq, sample_rate, target_sat, chirp_length)
        reference_table.append(SV_reference)
        print("BOOTING: Reference wave for sat {} Created".format(target_sat))
        target_sat += 1
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
