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
    target_sat = 25
    carrier_freq = 154 * 10230000  # carrier frequency
    f_prn = 10230000  # PRN frequency
    sample_rate = 10000000  # sample rate, 10 GHz
    message_in_binary = Utility_functions.ascii_binary_translator("Hello world")
    prn_adapted_message = Prime_Receiver.message_PRN_encode(message_in_binary,
                                                               target_sat, carrier_freq, f_prn, sample_rate, 1023)
    print("Settings:\n Carrier_Frequency: {}\n "
          "PRN_Frequency: {}\n Sample_rate: {}".format(carrier_freq, f_prn, sample_rate))
    reference_table = Prime_Receiver. sat_prn_table(carrier_freq, f_prn, sample_rate, 1023)
    sats_detected, likelihood = Prime_Receiver.sat_detector(reference_table, prn_adapted_message, 1023)
    read_words = Prime_Receiver.multi_sat_handler(sats_detected, prn_adapted_message, reference_table)
    print("TRANSLATING MESSAGE")
    for i in Prime_Receiver.reading_decoded_multisat(sats_detected, read_words):
        print(i)
    
main()

