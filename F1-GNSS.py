import numpy as np
import Utility_functions
"""*************************************************GOLD CODE CREATION***********************************************"""


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


"""*************************************************SINE WAVE CREATION***********************************************"""


def single_bit_generator(bits_per_wave, amplitude, theta, sample_rate):
    """ this actually translates the bit to encode into a wave of the appropiate format"""
    length = np.pi * 2 * bits_per_wave
    encoding = int(theta) * np.pi  # 1pi is 180 degrees out of phase for a sine wave
    encoded_bit = amplitude * np.sin(np.arange(0, length, length / sample_rate) + encoding)
    return encoded_bit


def wave_creator(sample_rate, waves_per_bit, bits_to_encode):
    """
    this function takes in:
        sample_rate
        waves_per_bit
        Bits_to_encode
    """
    total_wave = []
    bits_encoded = 0
    amplitude = 1
    while bits_encoded < len(bits_to_encode):
        theta = bits_to_encode[bits_encoded] # theta is either 0 or 1
        sinewave = single_bit_generator(waves_per_bit, int(amplitude), theta, sample_rate)
        # sine wave is a list of points sample_rate in length and of waves_per_bit*2pi in length
        bits_encoded += 1
    return total_wave


"""*************************************************MESSAGE ENCODING*************************************************"""


def prn_encode_to_wave():
    """
    this function takes in a prn message created using out prn creator, and feeds it into wave creator.
    wave creator will then make a sine wave with the corrosponding pattern for the PRN code.
    """
    number_of_gps_sats = 32
    waves_per_bit = 1
    sample_rate = 10
    sat_point = 1
    list_of_prn_encoded_waves = []
    while sat_point <= number_of_gps_sats:
        prn_binary_list = prn(sat_point)
        prn_wave = wave_creator(sample_rate, waves_per_bit, prn_binary_list)
        list_of_prn_encoded_waves.append(prn_wave)
        sat_point += 1
    return list_of_prn_encoded_waves


def chirp_prn_wave_as_bits(selected_sat_wave, bits_to_encode):
    chip = 0
    chirp_length = 20
    chipped_wave = []
    for bit in bits_to_encode:
        while chip < chirp_length:
            polar_encoding = Utility_functions.polar_encoding(bit)
            for reading in selected_sat_wave:
                inverse_point = reading * polar_encoding  # this will flip the point
                chipped_wave.append(inverse_point)
            chip += 1
    return chipped_wave


"""*************************************************MESSAGE DECODING*************************************************"""


def demodulate_phase_shift_keying(to_decode, reference_wave, sample_rate):
    """this function aims to determine if a given point is in phase or out of phase."""
    base_band = []
    index_start = 0
    index_end = index_start + sample_rate
    while index_end <= len(to_decode):
        buffer = to_decode[index_start:index_end]
        dot_prod = 0
        for i in buffer:
            dot_prod = dot_prod + (reference_wave[(index_start%sample_rate)] * i)
            index_start += 1
        if dot_prod > 0:
            base_band.append(1)
        else:
            base_band.append(0)
        index_end += sample_rate
    message = Utility_functions.stringify(base_band)
    return message



"""*************************************************Settings*********************************************************"""
