from datetime import datetime
import csv
import geopy
from geopy import distance
from geopy.units import kilometers, meters
from data_processing import convert_from_processed, convert_from_stked

file_path = ".\\data_from_stkde.csv"
time = []
with open(file_path, "r") as f:
    rows = list(csv.reader(f))
    for row in rows[1:]:
        time.append(float(row[5]))
# data = [(3, 45, 0),(246, 309, 14532)]
time = list(set(time))

time.sort()

for t in time[::-1]:
    print(datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))


# file_path = ".\\refined_data.csv"
# # 24641.926253 30961.045007 668298.0
# x = []
# with open(file_path, "r") as f:
#     rows = list(csv.reader(f))
#     for row in rows[1:]:
#         x.append(float(row[3]))

# x.sort()

# for i in x:
#     print(i)
