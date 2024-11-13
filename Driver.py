import Utility_functions


def main():
    working_file_wave = "encoded-PSK"
    to_encode =Utility_functions.ascii_binary_translator("hello world")
    mode = "PSK"
    frequency = 4
    end_time = 1
    sample_rate = 50
    #to_decode = Utility_functions.load_wave(working_file_wave)
    to_decode = Utility_functions.wave_creator(end_time, sample_rate, frequency, to_encode, mode)
    Utility_functions.show_wave(to_decode)
    decoded = Utility_functions.decode_phase_shift_keying(to_decode, frequency, sample_rate)
    print(decoded)
    ASCII = Utility_functions.ascii_binary_translator(decoded)
    print(ASCII)
main()
