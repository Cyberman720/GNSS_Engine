import Utility_functions


def main():
    binary_to_translate = "0100100001100101011011000110110001101111001000000" \
                          "1110111011011110111001001101100011001000010000100001010"
    binary_to_translate = Utility_functions.ascii_binary_translator("hello world")
    mode = "ASK"
    frequency = 4
    end_time = 15
    sample_rate = 50
    wave = Utility_functions.wave_creator(end_time, sample_rate, frequency, binary_to_translate, mode)
    Utility_functions.save_wave(wave, "encoded-ASK")

main()
