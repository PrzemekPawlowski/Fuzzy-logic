import math

def counting_estimators(time_window, AoT, Rise_speed_synchro, Fall_speed_synchro):
    # Counting the rise and fall band
    index = time_window.index(max(time_window))
    tmp = index
    rise_counter = 0
    fall_counter = 0

    for item in time_window[:index]:
        if item > 100:
            rise_counter += 1
    rise_counter += 1

    for item in reversed(time_window):
        if item > 50 and item < time_window[index]:
            fall_counter += 1
    fall_counter -= 1

    halfMax = (max(time_window) / 2)
    for i in time_window:
        if i > halfMax:
            AoT += i

    BetaSum1 = 0
    BetaSum2 = 0
    BetaValues = []
    for index, value in enumerate(time_window):
        if (max(time_window) == value):
            BetaValues = time_window[index:index + 6]
            break

    for index, value in enumerate(BetaValues):
        BetaSum2 += math.log(value)
        if (index > 0):
            BetaSum1 += index * math.log(value)

    Beta = (2 * BetaSum1 - 5 * BetaSum2) / 35
    Beta *= 1000

    if fall_counter <= 0 or rise_counter <= 0:
        rise_counter = 0
        fall_counter = 0
    else:
        Rise_speed_synchro = math.floor(max(time_window) / rise_counter)
        Fall_speed_synchro = math.floor((max(time_window) / fall_counter) * 8)

    return AoT, Beta, Rise_speed_synchro, Fall_speed_synchro

def data_processing_from_tssi_file(file_path):
    f1 = open(file_path, 'r')
    f2 = open("3_ADCabc.txt", 'w')

    lines = [line.lstrip() for line in f1] # Reads into a list, file line by line, removing spaces
    i = 0

    AoT_CH1 = 0
    AoT_CH2 = 0
    AoT_CH3 = 0

    time_window_CH1 = []
    time_window_CH2 = []
    time_window_CH3 = []

    Beta_CH1 = 0
    Beta_CH2 = 0
    Beta_CH3 = 0

    Rise_speed_synchro_CH1 = 0
    Rise_speed_synchro_CH2 = 0
    Rise_speed_synchro_CH3 = 0

    Fall_speed_synchro_CH1 = 0
    Fall_speed_synchro_CH2 = 0
    Fall_speed_synchro_CH3 = 0

    flag_CH1 = 0
    flag_CH2 = 0
    flag_CH3 = 0

    cnt_CH1 = 20
    cnt_CH2 = 20
    cnt_CH3 = 20

    for line in lines:
        i += 1
        parts = line.split(' ')

        first, second = parts

        ADCA = second[:12].strip()
        ADCA = ADCA.replace('L', '0').replace('H', '1')
        ADCA = int(ADCA, 2) # Convert to decimals

        ADCB = second[12:24].strip()
        ADCB = ADCB.replace('L', '0').replace('H', '1')
        ADCB = int(ADCB, 2)

        ADCC = second[24:36].strip()
        ADCC = ADCC.replace('L', '0').replace('H', '1')
        ADCC = int(ADCC, 2)

        if ADCA > 100:
            flag_CH1 = 1
        if ADCB > 100:
            flag_CH2 = 1
        if ADCC > 100:
            flag_CH3 = 1

        if flag_CH1 == 1:
            cnt_CH1 -= 1
            time_window_CH1.append(ADCA)
            if cnt_CH1 == 0:
                AoT_CH1, Beta_CH1, Rise_speed_synchro_CH1, Fall_speed_synchro_CH1 = counting_estimators(time_window_CH1,
                                                                                                        AoT_CH1,
                                                                                                        Rise_speed_synchro_CH1,
                                                                                                        Fall_speed_synchro_CH1)
                cnt_CH1 = 20
                flag_CH1 = 0

        if flag_CH2 == 1:
            cnt_CH2 -= 1
            time_window_CH2.append(ADCB)
            if cnt_CH2 == 0:
                AoT_CH2, Beta_CH2, Rise_speed_synchro_CH2, Fall_speed_synchro_CH2 = counting_estimators(time_window_CH2,
                                                                                                        AoT_CH2,
                                                                                                        Rise_speed_synchro_CH2,
                                                                                                        Fall_speed_synchro_CH2)
                cnt_CH2 = 20
                flag_CH2 = 0

        if flag_CH3 == 1:
            cnt_CH3 -= 1
            time_window_CH3.append(ADCC)
            if cnt_CH3 == 0:
                AoT_CH3, Beta_CH3, Rise_speed_synchro_CH3, Fall_speed_synchro_CH3 = counting_estimators(time_window_CH3,
                                                                                                        AoT_CH3,
                                                                                                        Rise_speed_synchro_CH3,
                                                                                                        Fall_speed_synchro_CH3)
                cnt_CH3 = 20
                flag_CH3 = 0

        if flag_CH1 == 1 or flag_CH2 == 1 or flag_CH3 == 1:
            f2.write(first.rjust(7) + " " + str(ADCA).rjust(7) + " " + str(ADCB).rjust(7) + str(ADCC).rjust(7) + '\n')

        # (and time_window_CH1 and time_window_CH2 and time_window_CH3) ->
        # Checks if arrays are not empty, if they are not, their contents are written to the file
        if flag_CH1 == 0 and flag_CH2 == 0 and flag_CH3 == 0 and time_window_CH1 and time_window_CH2 and time_window_CH3:
            f2.write("\n CHANNEL 1 -------" + '\n')
            f2.write("DMAX: " + str(max(time_window_CH1)) + '\n')
            f2.write("Beta: " + str(math.floor(Beta_CH1)) + '\n')
            f2.write("Rise_speed_synchro: " + str(Rise_speed_synchro_CH1) + '\n')
            f2.write("Fall_speed_synchro: " + str(Fall_speed_synchro_CH1) + '\n')
            f2.write("AoT: " + str(AoT_CH1) + '\n' + '\n')
            time_window_CH1.clear()
            AoT_CH1 = 0
            Beta_CH1 = 0
            Rise_speed_synchro_CH1 = 0
            Fall_speed_synchro_CH1 = 0

            f2.write("CHANNEL 2 -------" + '\n')
            f2.write("DMAX: " + str(max(time_window_CH2)) + '\n')
            f2.write("Beta: " + str(math.floor(Beta_CH2)) + '\n')
            f2.write("Rise_speed_synchro: " + str(Rise_speed_synchro_CH2) + '\n')
            f2.write("Fall_speed_synchro: " + str(Fall_speed_synchro_CH2) + '\n')
            f2.write("AoT: " + str(AoT_CH2) + '\n' + '\n')
            time_window_CH2.clear()
            AoT_CH2 = 0
            Beta_CH2 = 0
            Rise_speed_synchro_CH2 = 0
            Fall_speed_synchro_CH2 = 0

            f2.write("CHANNEL 3 -------" + '\n')
            f2.write("DMAX: " + str(max(time_window_CH3)) + '\n')
            f2.write("Beta: " + str(math.floor(Beta_CH3)) + '\n')
            f2.write("Rise_speed_synchro: " + str(Rise_speed_synchro_CH3) + '\n')
            f2.write("Fall_speed_synchro: " + str(Fall_speed_synchro_CH3) + '\n')
            f2.write("AoT: " + str(AoT_CH3) + '\n' + '\n')
            time_window_CH3.clear()
            AoT_CH3 = 0
            Beta_CH3 = 0
            Rise_speed_synchro_CH3 = 0
            Fall_speed_synchro_CH3 = 0

    print('A data file has been created')

file = '3_channels.txt'
data_processing_from_tssi_file(file)
