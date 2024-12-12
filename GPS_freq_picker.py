import numpy as np
import matplotlib.pyplot as plt
def noise_removal():
    """
    this is a function who takes in a noisy signal and subtracts the prn's goldcode (G2) to get a clearer wave." \
    Logically when we are aiming to break out our Xor briged  goldcodes, adding them agin in the same fasion will
    reverse the code.
    leaving us with the known "G2" of the sat we are looking for but importantly our Coarse aquisition "G2"

    Our variables must be a goldcode for a sat of our choosing, use the PRN fuction of Gold_code_creator.
    and noisy signal will be our sampled antenna
    """
