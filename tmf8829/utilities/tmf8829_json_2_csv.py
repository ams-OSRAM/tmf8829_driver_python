# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************

# Revision log 
# 0.1 Initial revision
# 1.0 Updatae to newer json file format logger VERSION = 0x0003

''' Convert a json file to csv'''

import sys
import time
import json
import csv
import gzip
from tkinter import filedialog as tk_fd

histogram_counter = 0

def writeFrameData(data:dict) -> None:

    global histogram_counter

    if not "Result_Set" in data:
        return

    for frame in data["Result_Set"]:
            
        if "results" in frame:
            histogram_counter = 0
            pixel = 0

            row_key = []
            row_key.append("#PIXEL")

            # generate row with keys
            for pixelkey in frame["results"][0][0].keys():
                if pixelkey == 'noise':
                    row_key.append("noise")
                if pixelkey == 'xtalk':
                    row_key.append("xtalk")
                if pixelkey == 'peaks':
                    for i, pixelpeak in enumerate(frame["results"][0][0]['peaks']):
                        for pixelpeakkey in pixelpeak:
                            if pixelpeakkey == 'distance':
                                row_key.append(f"distance{i}")
                            if pixelpeakkey == 'snr':
                                row_key.append(f"snr{i}")
                            if pixelpeakkey == 'signal':
                                row_key.append(f"signal{i}")
            csvout.writerow(row_key)
            
            # log the results

            for result in frame["results"]:
                for result_line in result:
                    row_val = []
                    row_val.append(f"#PIXEL{pixel:04}")
                    if 'noise' in result_line:
                        row_val.append(result_line["noise"])
                    if 'xtalk' in result_line:
                        row_val.append(result_line["xtalk"])
                    if 'peaks' in result_line:
                        for peak in result_line["peaks"]:
                            if 'distance' in peak:
                                row_val.append(peak["distance"])
                            if 'snr' in peak:
                                row_val.append(peak["snr"])
                            if 'signal' in peak:
                                row_val.append(peak["signal"])
                    csvout.writerow(row_val)
                    pixel += 1

        
        if "mp_histo" in frame:
            row_key = []
            row_key.append("#RAWBIN")
            for i in range(64):
                row_key.append(i)
            csvout.writerow(row_key)

            for mp_data in frame["mp_histo"]:
                for histogram in mp_data:
                    row_val = []
                    row_val.append(f"#RAW{histogram_counter:03}")
                    histogram_counter +=1 
                    for value in histogram["bin"]:
                        row_val.append(value)
                    csvout.writerow(row_val)
                    
        histogram_counter = 0
        if "mp_histo_LR" in frame:
            row_key = []
            row_key.append("#RAWBIN")
            for i in range(64):
                row_key.append(i)
            csvout.writerow(row_key)

            for mp_data in frame["mp_histo_LR"]:
                for histogram in mp_data:
                    row_val = []
                    row_val.append(f"#RAWLR{histogram_counter:03}")
                    histogram_counter +=1 
                    for value in histogram["bin"]:
                        row_val.append(value)
                    csvout.writerow(row_val)

def dumpSection( data:dict, section_name:str, section_tag:str ) -> None:
    if section_name in data.keys():
        row_key = []
        row_value = []
        row_key.append(section_tag)
        row_value.append(section_tag)
        for key, value in data[section_name].items():
            row_key.append(key)
            row_value.append(value)
        csvout.writerow(row_key)
        csvout.writerow(row_value)

if __name__ == "__main__":

    if len(sys.argv) == 1:
        filenames = tk_fd.askopenfilenames(title='Open files', initialdir='./', filetypes=[('Json File', '.json .gz')])

        if len(filenames) == 0:
            print("Aborted by user.")
            sys.exit()
    else:                                  
        if len(sys.argv) < 3:
            print("Missing argument!")
            print("Usage : tmf8830_json_2_csv.py inputfile.json/json.gz outputfile.csv")
            sys.exit()
        filenames = []
        filenames.append(sys.argv[1])

    # record start time
    start = time.time()

    for file in filenames:

        if file[-2:] == "gz":                      # Check if we have a gzip compressed file or an uncompressed json file    
            with gzip.open(file,"r") as gzip_data: # Open the gzip archive
                json_data = gzip_data.read()               # Read the gzip data into json_data ( byte array )
            json_str = json_data.decode("utf-8")           # Decode the byte array -> string
            measurement_data = json.loads(json_str)        # Read the json data

        elif file[-4:] == "json":
            with open(file) as json_file:
                measurement_data = json.load(json_file)

        # open CSV writer
        if len(sys.argv) == 1:    
            if (file[-2:] == "gz"):
                csv_file_name = file.replace("json.gz","csv")
            elif (file[-4:] == "json"):
                csv_file_name = file.replace("json","csv")

            f = open(csv_file_name,'w', encoding='UTF8', newline='' )
        else:
            f = open(sys.argv[2],'w', encoding='UTF8', newline='' )

        f.write( "sep=,\n")
        csvout = csv.writer( f, delimiter=',')

        if 'configuration' in measurement_data:
            dumpSection(measurement_data, "configuration", "#CONFIG")
        writeFrameData(measurement_data)

        if len(sys.argv) == 1:
            print("Data written to {}".format(csv_file_name))
        else:
            print("Data written to {}".format(sys.argv[2]))

        # csv file close
        f.close()

    # record end time
    end = time.time()
    print("Conversion finished in {:.3f}".format(end-start), "s")