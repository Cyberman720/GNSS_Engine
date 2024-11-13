import Utility_functions


def main():
    frequency = 10
    time = 1
    cycles = 1  # how many sine cycles per resolution
    resolution = 5000  # how many datapoints to generate (poll rate on A->D)
    wave = Utility_functions.wave_creator(time, cycles, resolution, frequency)
    print(wave)
    print(Utility_functions.load_wave("test_wave"))



main()
