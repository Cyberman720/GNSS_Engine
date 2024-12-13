import numpy as np


def input_data_poller():
    """" this is going to be a function that polls the auduino, reads the message an breaks it up into usable stuff """

"""
def GPS_Time_Sync(signal_in, sample_rate, carrier_frequency):
    """ a critical function to GPS time match, syncing frequency and phase """
    time = 0
    temportal_shift = 0
    while time < len(signal_in):
        phase_shift = (np.arcsin(signal_in[time])/((2*np.pi)*carrier_frequency))/(time * sample_rate)
        temportal_shift += phase_shift
        time += 1
        average_shift = temportal_shift / time
        break
    time = 0
    while time < 11:
        print("shift")
        print(average_shift)
        print("reference")
        print(signal_in[time])
        print("synthasized")
        print(np.sin((((np.pi * 2)*carrier_frequency)*((time*sample_rate) / average_shift))))
        print("time")
        print(time)
        time += 1
        print("\n")

    return average_shift

"""
