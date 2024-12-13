import Utility_functions
import Prime_Receiver

"""
This is the main driver that uses files, Prime Receiver and Utility functions.
the purpose is to have the fiddly stuff seperate and open the door to making a UI or some other form of control.
Written by Henry Rogers.
10/12/2024
"""

def main():
    print("\nBOOTING...")
    carrier_freq = 1545 * 1023000  # carrier frequency
    f_prn = 10230000  # PRN frequency
    sample_rate = 1000000  # sample rate, 1 GHz
    chirp_length = 1023  # how long is one PRN chirp according to gps spec
    print("Primary Settings:\n Carrier_Frequency: {}\n "
          "PRN_Frequency: {}\n Sample_Rate: {}\n Chirp_Length: {}".format(carrier_freq,
                                                                          f_prn, sample_rate, chirp_length))

    multi_sat_message = Prime_Receiver.multi_sat_splitter("H", carrier_freq,
                                                          f_prn, sample_rate, chirp_length)
    multiplex_wave = Prime_Receiver.wave_merger(multi_sat_message)
    reference_table = Prime_Receiver.sat_prn_reference_table(carrier_freq, f_prn, sample_rate, chirp_length)
    base_band_signal = Prime_Receiver.demodulate(carrier_freq, multiplex_wave, sample_rate)
    #resampled_base_band = Prime_Receiver.down_sample_synced(carrier_freq, sample_rate, f_prn)
    stringy = Utility_functions.stringify(base_band_signal)
    word = Utility_functions.ascii_binary_translator(stringy)
    print(word)

main()

