def shift(register, feedback, output):
    """
    mimics the feedback loop for the G1 and G2 portions for a GPS goldcode.
    """

    # calculate output
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


def prn(sv, SV_table):
    """
    takes in sv number and will generate the G1+G2 ca code for it.
    """

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


def stringify(to_encode):
    """simple helper that turns list of binary values into string to send other places"""
    binary_string = ""
    for i in to_encode:
        binary_string = "{}{}".format(binary_string, i)
    return binary_string


def Create_gold_code(SV):
    """ the driver function that takes in the sat you are looking for and outputs the phony gold code for it"""
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
    f_prn = 10.23e6 / 10  # chipping frequency (1023b/s)

    # find ca code for sat 24, and make 0 into -1 to use in our wave form functions
    target_sat_CA = [0 if x == 0 else x for x in prn(SV, SV_table)]
    for i in target_sat_CA:
        sat_prn = target_sat_CA[int(i * f_prn) % 1023]
    binary_string = stringify(sat_prn)
    return binary_string