import csv

path = "./data_from_stkde.csv"
to_path = "./filtered_data.csv"

f = open(path, "r")
w = open(to_path, "w")

w.write("from_lat,from_lon,from_time,to_lat,to_lon,to_time,possibility\n")

rows = csv.reader(f)
next(rows, None)

space_dict = {}
for row in rows:
    if float(row[5]) < 1293858000:
        w.write(row[0] + "," + row[1] + "," + row[2] + "," + row[3] + "," + row[4] + "," + row[5] + "," + row[6] + "\n")
        
w.close()

