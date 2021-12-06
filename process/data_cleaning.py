import os
import csv
from geopy import distance
from select import select
import time
from email import utils as eutils
import datetime
from datetime import datetime as dt
from posixpath import split


class data_cleaning():
    def merge_data(self, path_list, to_path):
        merged_data = []
        print("Received file from:")

        for data in path_list:
            path = data[0]
            print("\t" + path)
            idxs= data[1]

            if os.path.exists(path):
                with open(path, "r") as f:
                    temp_rows = csv.reader(f)
                    next(temp_rows, None)
                    rows = []
                    for row in temp_rows:
                        # if row == None:
                        #     print(row)
                        if row[idxs[-1]] == "0" or row[idxs[-2]] == "0":
                            continue

                        if row[idxs[1]] != "NA":
                            if "/" in row[idxs[1]]:
                                split_day = row[idxs[1]].split("/")
                                year = split_day[2]
                                month = split_day[0] if len(split_day[0]) == 2 else "0" + split_day[0] 
                                day = split_day[1] if len(split_day[1]) == 2 else "0" + split_day[1]

                                date = year + "-" + month + "-" + day
                            elif "-" in row[idxs[1]]:
                                date = row[idxs[1]]
                        else:
                            continue

                        if row[idxs[2]] != "NA" and row[idxs[2]] != "NULL":
                            if len(row[idxs[2]]) == 4:
                                if ":" in row[idxs[2]]:
                                    split_time = row[idxs[2]].split(":")
                                    hour = split_time[0] if len(split_time[0]) == 2 else "0" + split_time[0]
                                    minute = split_time[1] if len(split_time[1]) == 2 else "0" + split_time[1]
                                else:
                                    hour = row[idxs[2]][:2]
                                    minute = row[idxs[2]][2:]
                            else:
                                hour = row[idxs[2]][:2] if row[idxs[2]][:2].isdigit() else "00"
                                minute = "00"
                        else:
                            continue

                        strtime = date + " " + hour + ":" + minute

                        if strtime[11:13] != "24":
                            parsed_time = dt.strptime(strtime, "%Y-%m-%d %H:%M")
                            time_stamp = parsed_time.timestamp()
                            # print(time_stamp)
                        else:
                            strtime = strtime[:11] + "00" + strtime[13:] 
                            parsed_time = dt.strptime(strtime, "%Y-%m-%d %H:%M") + datetime.timedelta(hours = 1)
                            time_stamp = parsed_time.timestamp()
                            # print(time_stamp)

                        # rows.append([row[idxs[i]] if i != 3 else row[idxs[i]].replace("\n", " ") for i in range(len(idxs))].insert(1, strtime))
                        new = [row[idxs[i]] if i != 3 else row[idxs[i]].replace("\n", " ").replace(",", "") for i in range(len(idxs))]
                        new.insert(1, strtime)
                        new.insert(2,str(int(time_stamp)))

                        if new == None:
                            print(new)
                        rows.append(new)

                merged_data.extend(rows[1:])
        
        with open(to_path, "w") as f:
            f.write("offense_id,datetime,timestamp,occur_date,occur_time,location,ucr_Literal,neighborhood,npu,lat,long")
            for row in merged_data:
                f.write('\n')
                f.write(row[0] + "," + 
                        row[1] + "," + 
                        row[2] + "," + 
                        row[3] + "," + 
                        row[4] + "," + 
                        row[5] + "," + 
                        row[6] + "," + 
                        row[7] + "," + 
                        row[8] + "," + 
                        row[9] + "," + 
                        row[10] 
                        )
            
            print("Data to file ['" + to_path + "'] written.\n")
            f.close()
        
    def selected_data(self, data, to_path, selected_idxs):
        with open(to_path, "w") as f:
            for d in data:
                row = [d[selected_idxs[i]] for i in range(len(selected_idxs))]
                new_line = ""
                for r in row:
                    new_line += (r + ",")
                f.write(new_line[:-1])
                f.write("\n")

            f.close()
        
        print("Data selected from [" + to_path + "] with indexs " + str([data[0][selected_idxs[i]] for i in range(len(selected_idxs))]) + ".")

    def import_data(self, single_path, selected_idxs=None):
        if selected_idxs:
            print("Retriving data from [" + single_path + "] with selected indexs are" + str(selected_idxs) + "...")
            if os.path.exists(single_path):
                with open(single_path, "r") as f:
                    rows = csv.reader(f)
                    data = []
                    for row in rows:
                        row = [row[selected_idxs[i]] for i in range(len(selected_idxs))]
                        data.append(row)
        
        else:
            print("Retriving data from [" + single_path + "]...")
            if os.path.exists(single_path):
                with open(single_path, "r") as f:
                    rows = csv.reader(f)

                    data = []
                    for row in rows:
                        data.append(row)

        return data
    
    def coordination_refine(self, data, to_path, idxs=None):
        latitudes = [float(row[1]) for row in data[1:]]
        longitudes = [float(row[2]) for row in data[1:]]

        min_lat = min(latitudes)
        max_lat = max(latitudes)
        min_lon = max(longitudes)
        max_lon = min(longitudes)

        origin = (min_lat, min_lon)

        with open(to_path, "w") as f:
            f.write(data[0][0] + "," + data[0][1] + "," + data[0][2] + "," + "x_dist,y_dist")
            for row in data[1:]:
                coordinate = (float(row[1]), float(row[2]))
                x_dist = distance.distance(origin, (origin[0], coordinate[1])).m
                y_dist = distance.distance(origin, (coordinate[0], origin[1])).m
                f.write("\n")
                f.write(row[0] + "," + row[1] + "," + row[2] + "," + str(x_dist) + "," + str(y_dist))
            f.close()

        print("Field of coordinates of data converted and saved to [" + to_path + "].")

        
    def timestamp_refine(self, data, to_path, idxs=None):
        timestamps = []
        for row in data[1:]:
            if int(row[0]) >= datetime.datetime(2009,1,1,0,0).timestamp():
                timestamps.append(int(row[0]))
        min_timestamps = min(timestamps)

        # timestamps.sort()
        # for i in timestamps[::-1]:
        #     print(i)

        # print(min_timestamps)


        with open(to_path, "w") as f:
            f.write(data[0][0] + "," + data[0][1] + "," + data[0][2] + ",modified_time," + data[0][4] + "," + data[0][5])
            for row in data[1:]:
                modified_time = (float(row[0]) - min_timestamps) / 60 / 10
                if modified_time < 0:
                    continue
                else:
                    f.write("\n")
                    f.write(row[0] + "," + row[1] + "," + row[2] + "," + str(modified_time) + "," + row[4] + "," + row[5])
            f.close()

        print("Field of timestamps of data converted and saved to [" + to_path + "].")
        


if __name__ == "__main__":
    oper = data_cleaning()

    path = "../refined_data/COBRA_2009_2019.csv"

    path_list = [
        # offense_id  occur_date occur_time location ibr_code(UCR_NUM) UC2_Literal neighborhood npu lat long
        # ["../refined_data/COBRA_2021.csv", [0,2,5,10,11,12,13,14,15,16]],
        # ["../refined_data/COBRA_2020_1.csv", [0,2,3,9,15,14,16,17,18,19]],
        # ["../refined_data/COBRA_2020_2.csv", [0,2,3,9,13,12,14,15,16,17]],
        # ["../refined_data/COBRA_2009_2019.csv", [0,2,3,9,13,12,15,16,17,18]]

        # offense_id  occur_date occur_time location UC2_Literal neighborhood npu lat long
        ["../refined_data/COBRA_2009_2019.csv", [0,2,3,9,12,15,16,17,18]],
        ["../refined_data/COBRA_2020_1.csv", [0,2,3,9,14,16,17,19,18]],
        ["../refined_data/COBRA_2020_2.csv", [0,2,3,9,12,14,15,16,17]],
        ["../refined_data/COBRA_2021.csv", [0,2,5,10,12,13,14,15,16]],
    ]

    raw_path = "../refined_data/raw_merged.csv"
    selected_path = "../refined_data/data_xyt.csv"
    
    # oper.merge_data(path_list, raw_path)

    # selected_idxs = [0,2,9,10]
    # data = oper.import_data(raw_path)
    # oper.selected_data(data, selected_path, selected_idxs)

    selected_path = "../refined_data/refined_data.csv"

    indexs_with_time = [0,1,2,3,4,5]
    data = oper.import_data(selected_path, indexs_with_time)

    refined_data_path = "../refined_data/refined_data.csv"
    oper.timestamp_refine(data, refined_data_path)
    # for d in data:
    #     print(d)
























        #All labels:
        # Report Number
        # Report Date
        # Occur Date
        # Occur Time
        # Possible Date
        # Possible Time
        # Beat
        # Apartment Office Prefix
        # Apartment Number
        # Location
        # Shift Occurence
        # Location Type
        # UCR Literal
        # UCR #
        # IBR Code
        # Neighborhood
        # NPU
        # Latitude
        # Longitude

        #Selected labels:
        # Report Number
        # Occur Date
        # Occur Time
        # Location
        # IBR Code
        # UCR Literal
        # Neighborhood
        # NPU
        # Latitude
        # Longitude


        #### Other files
        # offense_id
        # rpt_date
        # occur_date
        # occur_day
        # occur_day_num
        # occur_time
        # poss_date
        # poss_time
        # beat
        # zone
        # location
        # ibr_code
        # UC2_Literal
        # neighborhood
        # npu
        # lat
        # long


        #### Selected labels(Other files)
        # offense_id
        # occur_date
        # occur_time
        # location
        # ibr_code(UCR_NUM)
        # UC2_Literal
        # neighborhood
        # npu
        # lat
        # long