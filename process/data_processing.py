import csv
import geopy
from geopy import distance
from geopy.units import kilometers, meters
from datetime import datetime
file_path = ".\\cse6242project\\densitySpaceTime\\outFiles\\stkde.txt"
to_path = ".\\data_from_stkde.csv"
time_group_path = ".\\timegroup_from_stkde_small.csv"
space_group_path = ".\\spacegroup_from_stkde_small.csv"

# non_group = open(to_path, "w")
# non_group.write("from_lat,from_lon,from_time,to_lat,to_lon,to_time,possibility\n")
time_group = open(time_group_path, "w")
space_group = open(space_group_path, "w")

## 3, 246  |  45, 309  |  0, 14532

def convert_from_stked(x, y, t):
    x = (x - 3)*101.407
    y = (y - 45)*117.277
    t = t*45.988026

    return x, y, t


def convert_from_processed(x, y, t):

    origin = geopy.Point(33.606995, -84.284975)
    point = distance.distance(meters=x).destination(point=origin, bearing=270)
    point = distance.distance(meters=y).destination(point=point, bearing=0)

    lat = point[0]
    lon = point[1]

    time_stamp = int((t*60*10 + 1230786000.0)/60)*60

    # date = dt.strftime("%Y-%m-%d")
    # time = dt.strftime("%H:%M:%S")

    return lat, lon, time_stamp


if __name__ ==  "__main__":
    time_dict = {}
    space_dict = {}


    max_lat = 0
    min_lat = 100
    max_lon = -100
    min_lon = 0
    with open(file_path, "r") as f:
        rows = list(csv.reader(f))
        length = len(rows)
        cnt = 0
        res = []
        max_t = 0
        for x, y, t, p in rows:
            p = float(p)

            from_x = float(x) - 3
            to_x = float(x)

            from_y = float(y) - 3
            to_y = float(y)

            from_t = float(t) - 1
            to_t = float(t)

            if (to_t * 45.988026 * 600 + 1230786000.0) < 1325394000.0:

                processed_from_x, processed_from_y, processed_from_t = convert_from_stked(from_x, from_y, from_t)
                processed_to_x, processed_to_y, processed_to_t = convert_from_stked(to_x, to_y, to_t)

                processed_to_x = round(processed_to_x, 3)
                processed_to_y = round(processed_to_y, 3)
                processed_to_t = round(processed_to_t, 3)

                space_key = str(processed_to_x) + "|" + str(processed_to_y)
                time_key = str(processed_to_t)

                if time_key in time_dict:
                    time_dict[time_key].append((processed_to_x, processed_to_y, p))
                else:
                    time_dict[time_key] = [(processed_to_x, processed_to_y, p)]
                
                if space_key in space_dict:
                    space_dict[space_key].append((processed_to_t, p))
                else:
                    space_dict[space_key] = [(processed_to_t, p)]

            # lat_from_x, lon_from_y, from_t = convert_from_processed(processed_from_x,processed_from_y,processed_from_t)
            # lat_to_x, lon_to_y, to_t = convert_from_processed(processed_to_x,processed_to_y,processed_to_t)

            # non_group.write(str(lat_from_x) + "," + str(lon_from_y) + "," + str(from_t) + "," + str(lat_to_x) + "," + str(lon_to_y) + "," + str(to_t) + "," + str(p) + "\n")
            
            # print("Lat from: [" + str(lat_from_x) + "] to: [" + str(lat_to_x) + "],\n" + "Lon from: [" + str(lon_from_y) + "] to: [" + str(lon_to_y) + "],\n" + "Time from: [" + str(dt_from_t) + "] to: [" + str(dt_to_t) + "],\n")
            # res.append([processed_from_x, processed_from_y, processed_from_t, processed_to_x, processed_to_y, processed_to_t, p])
            # min_lat = min(min_lat, lat_from_x)
            # max_lat = min(max_lat, lat_to_x)

            # min_lon = min(min_lon, lon_from_y)
            # max_lon = min(max_lon, lon_to_y)
            
            cnt += 1
            print(length-cnt, "records left.")

        # print(min_lat, max_lat, min_lon, max_lon)

        print("Step 1 finished.")

    time_length = len(time_dict.keys())
    cnt = 0
    for key in time_dict.keys():
        cnt += 1
        time_dict[key].sort()
        time_group.write(key + ",")
        for place in time_dict[key]:
            time_group.write(str(place[0]) + "," + str(place[1]) + "," + str(place[2]) + ",")

        time_group.write("\n")
        print(time_length-cnt, "records left.")

    print("Step 2 finished.")

    space_length = len(space_dict.keys())
    cnt = 0
    for key in space_dict.keys():
        cnt += 1
        space_dict[key].sort()
        x, y = key.split("|")
        space_group.write(x + "," + y + ",")
        for time in space_dict[key]:
            space_group.write(str(time[0]) + "," + str(time[1]) + ",")

        space_group.write("\n")
        print(space_length-cnt, "records left.")

    print("Step 3 finished.")

    # print(time_dict)
    # print(space_dict)









# print(convert_from_processed(x[0],y[0],t[0]))


















