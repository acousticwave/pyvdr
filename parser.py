import pynmea2
import numpy as np
import pandas as pd
import datetime
import os

# Path of a VDR
path_file = 'vdr/DUMP_2022-05-06_0333.log'

# Ouput file
path_output_csv = 'output.csv'



# Sentence type to be used as a time reference 
time_sentence = "ZDA"
time_interval = 10     # [s], unit of $ZDA is 1 second


# Ignore the following sentence (Talker ID and sentence type should be described)
sentence_ignore  = ["IIHTC", "PAALR"]


# Parse the following sentence types
sentence_use = ["GGA",\
                "VBW",\
                "HDT",\
                "ROT",\
                "VTG",\
                "RPM",\
                "RSA",\
                "HTD",\
                "HTC",\
                "XTE",\
               ]


# Note that "utc_data_time" is for allocating UTC time
field_parse  = ["utc_date_time",\
                "lat", "lat_dir", "lon", "lon_dir",\
                "lon_water_spd",\
                "heading",\
                "rate_of_turn",\
                "true_track", "spd_over_grnd_kts",\
                "speed",\
                "rsa_starboard", "rsa_port",\
                "htd_selected_steer_mode", "htd_cmd_rud_angle", "htd_cmd_rud_dir", "htd_cmd_heading_steer", "htd_cmd_track",\
                "htc_selected_steer_mode", "htc_cmd_heading_steer", "htc_cmd_track",\
                "cross_track_err_dist", "correction_dir",\
               ]

# Process DM -> DD the following fields
process_dm_to_sd = ['lat', 'lon']


# TODO: Not implemented yet
#float16_save = []



# Prefix and separator
prefix0 = '$'                   # Prefix of NMEA Sentence
separator = ','                 # Separator between sentence type and the first field
separator_pos_correct = 6       # Position of the first separator(",")


# A data dictionary. Parsed data for one time cycle (by 'time_sentence') is updated here
data_dict = {v: None for v in field_parse}


# Open the file
file = open(path_file, encoding='utf-8')

# Read sentence in 'file' line-by-line
idx = 0
for line in file.readlines():


        # Find position of the prefix
        pos_prefix = line.find(prefix0)
        # Cut string ahead of the prefix (Cut characters until prefix ("$"))
        line = line[pos_prefix:]
        # Find the first position of 'separator'
        pos_separator = line.find(separator)


        # Correct position of separator
        if pos_separator == separator_pos_correct:

            try:

                # Parse a line
                msg = pynmea2.parse(line)

                # Fields (defined in 'pynmea2/types/talker.py')
                msg_fields = msg.fields

                # A parsed msg dictionary and keys
                msg_dict = msg.__dict__
                msg_dict_keys = msg_dict.keys()


                # 'Talker' and 'sentence_type' exist in the parsed line
                if ('talker' in msg_dict_keys) and ('sentence_type' in msg_dict_keys):
                    


                    # 1. Ignore sentences defined in "sentence_ignore"
                    if msg_dict['talker'] + msg_dict['sentence_type'] in sentence_ignore:
                        pass
                        # print("$", msg_dict['talker'] + msg_dict['sentence_type'], "is ignored")



                    # 2. Time and data -> Output file
                    elif msg_dict['sentence_type'] == time_sentence:
                       
                        # Date and time stamp
                        #TODO: define a new function in 'nmea_utils.py'
                        time_stamp = pynmea2.timestamp(msg_dict['data'][0])
                        date_stamp = datetime.datetime.strptime(msg_dict['data'][1] + msg_dict['data'][2] + msg_dict['data'][3], "%d%m%Y").date()
                        date_time_stamp = datetime.datetime.strptime(str(date_stamp) + " " + str(time_stamp), "%Y-%m-%d %H:%M:%S")

                        # Time stamp -> 'data_dict'
                        data_dict["utc_date_time"] = str(date_time_stamp)

                        # 'data_dict' -> Output file
                        if idx % time_interval == 0:
                            # Data ('data_dict') -> Output file
                            #- Generate an output file if not exists
                            if not os.path.exists(path_output_csv):
                                df = pd.DataFrame.from_dict(data_dict, orient="index").T
                                df.to_csv(path_output_csv, index = False, mode='a')
                            #- Overwrite to the output file if exists
                            else:
                                df = pd.DataFrame.from_dict(data_dict, orient="index").T
                                df.to_csv(path_output_csv, index = False, mode='a', header=False)
                        else:
                            pass

                        idx = idx + 1


                        # TODO: Initialization of certain fields is required if the fields are not valid

        

                    # 3. Keep update the data dictionary ('data_dict') 
                    else:
                        # If sentence type of the msg is matched with one in 'sentence_use'
                        if msg_dict['sentence_type'] in sentence_use:

                            # Iterate elements in 'field_parse'
                            for parse in field_parse:

                                # Iterate fields of the given msg 
                                for i, msg_field in enumerate(msg_fields):

                                    # If match, update 'data_dict'
                                    if parse == msg_field[1]:
                                        if msg_field[1] in process_dm_to_sd:
                                            data_dict[parse] = pynmea2.dm_to_sd(msg_dict['data'][i])
                                        else:
                                            data_dict[parse] = msg_dict['data'][i]
                                    else:
                                        pass
                        else:
                            pass
                
                else:
                    pass



            except pynmea2.ParseError as e:
                # print('Parse error: {}'.format(e))
                continue
            
        else:
            # print("Wrong position of the separator")
            pass