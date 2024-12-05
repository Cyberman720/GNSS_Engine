import Gold_code_creator
import Utility_functions
import GPS_freq_picker



def main():
    print("BOOTING")
    mode = "PSK"
    target_sat = 25
    carrier_freq = 154 * 10230000  # carrier frequency
    f_prn = 10230000  # PRN frequency
    sample_rate = 100000000  # sample rate, 100 GHz
    message_in_binary = Utility_functions.ascii_binary_translator("Hello World")
    prn_adapted_message = Gold_code_creator.message_PRN_encode(message_in_binary,
                                                               target_sat, carrier_freq, f_prn, sample_rate, 1023)
    print("Settings:\n Carrier_Frequency: {}\n "
          "PRN_Frequency: {}\n Sample_rate: {}".format(carrier_freq, f_prn, sample_rate))
    print("BOOTING")
    reference_table = Gold_code_creator.sat_prn_table(carrier_freq, f_prn, sample_rate, 1023)
    print("BOOTED")
    print("ACQUIRING")
    print(prn_adapted_message)
    sat_detected = Utility_functions.sat_detector(reference_table, prn_adapted_message, 1023)
    print("SIGNAL ACQUIRED")



main()
