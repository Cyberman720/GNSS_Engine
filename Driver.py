import Utility_functions


def main():
    to_encode =Utility_functions.ascii_binary_translator("hello world")
    mode = "PSK"
    waves_per_bit = 1
    measured_frequency = 1545420000
    bits_per_second = 50
    frequency_per_bit = measured_frequency / bits_per_second
    time_observed = 30
    sample_rate = 11500
    total_samples = sample_rate * time_observed
    #to_decode = Utility_functions.load_wave(working_file_wave)
    to_decode = Utility_functions.wave_creator(total_samples, frequency_per_bit, to_encode, mode)
    decoded = Utility_functions.decode_phase_shift_keying(to_decode, frequency_per_bit, total_samples)
    print(decoded)
    ASCII = Utility_functions.ascii_binary_translator(decoded)
    print(ASCII)
main()
