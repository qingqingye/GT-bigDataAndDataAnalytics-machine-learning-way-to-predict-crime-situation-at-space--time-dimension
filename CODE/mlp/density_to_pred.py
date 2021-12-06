import numpy as np
import pandas as pd
from mlp_lib import MLP
import math
import datetime

def top_60_neighbor_features(row, my_ind, my_x, my_y):
    neighbors = []
    for i in range(1, 901):
        if i == my_ind:
            continue
        density_ind = i * 3
        x_ind = density_ind -2    
        y_ind = density_ind -1
        
        #print(row[x_ind], row[y_ind])
        float_density = float(row[density_ind])
        if math.isnan(float_density):
            #print('isnan, find neighbors')
            break
        neighbor_x = row[x_ind]
        neighbor_y = row[y_ind]
        # mahantan distance    
        distance = abs(my_x - neighbor_x) + abs(my_y -  neighbor_y)
        neighbors.append([distance, row[density_ind]])
    neighbors.sort(key=lambda x:x[0])
    neighbors = np.array(neighbors)
    return [np.sum(neighbors[0:10, 1])/10, np.sum(neighbors[10:30, 1])/20, np.sum(neighbors[30:60, 1])/30]    


def same_location_feature(df_space, my_x, my_y, my_timestamp):
        time_temp = my_timestamp*600+1230786000
        d = datetime.datetime.fromtimestamp(time_temp)
        weekday = d.strftime("%w")
        df_target = df_space[(df_space[0] == my_x) & (df_space[1]==my_y)]
        # get 3000 time stamp for one location
        near_day = []
        same_weekday = []
        for i in range(1, 3001):
            time_ind = i * 2
            time_f = df_target[time_ind] * 600 + 1230786000
            try:
                d1 = datetime.datetime.fromtimestamp(time_f)
                if (d-d1).days <=3:
                    density_ind = time_ind + 1
                    #int(d,d1,"sameday")
                    near_day.append(df_target[density_ind])
                if weekday == d1.strftime("%w"):
                    #print(weekday, "weekday")
                    same_weekday.append(df_target[density_ind])
            except:
                break
        return near_day, same_weekday


def get_feature_result():
    result = []
    # [[距离：density],[]... ]
    # same timestamp differnt location density feature
    location_features = []
    days_features = []
    allfeatures = []
    col_names = [i for i in range(2701)] # plan to get max 900 location grid, 2700/3(x,y,density)=900
    # timestamp x,y,density; x,y,density; 

    lines = 0
    df_time = pd.read_csv('timegroup_from_stkde_small.csv', header=None, names=col_names)
    df_space = pd.read_csv('spacegroup_from_stkde_small.csv', header=None, names=[i for i in range(6000)])

    for index, row in df_time.iterrows():
        # one row is one timestamp
        print("timestamp", row[0])
        my_timestamp = row[0]
        # if lines > 10:
        #     break
        for gird_ind in range(1, 901):
            density_ind = gird_ind * 3
            x_ind = density_ind -2
            y_ind = density_ind -1
            
            float_density = float(row[density_ind])
            if math.isnan(float_density):
                #print('isnan for result')
                break

            near_day, same_weekday = same_location_feature(df_space, row[x_ind], row[y_ind], my_timestamp)
            if len(near_day)==0 or len(same_weekday)==0:
                #print('pass')
                continue
            
            days_features.append([sum(near_day)/len(near_day), sum(same_weekday)/len(same_weekday)])
            location_features.append(top_60_neighbor_features(row, gird_ind, row[x_ind], row[y_ind]))
            result.append([row[density_ind], row[x_ind], row[y_ind], my_timestamp])
            allfeatures.append(location_features[-1] + days_features[-1])
            #lines += 1

    #print(location_features)
    df_loc_features = pd.DataFrame(allfeatures)
    df_loc_features.to_csv("loc_day_features.csv")

    df_result = pd.DataFrame(result)
    df_result.to_csv("result.csv")

    return result, allfeatures

    #df_space = pd.read_csv('spacegroup_from_stkde.csv', header=None)
  

    # df = pd.read_csv(file, header=0, usecols=['Series_Complete_Yes', 'Series_Complete_12Plus', 'Series_Complete_18Plus', 'Series_Complete_65Plus','sentiment140', 'n'])
    # return df['Series_Complete_Yes'][13:335], df[['sentiment140','n']][13:335]


if __name__ == "__main__":
    result, all_features  = get_feature_result()
    #print(vaccine_df)
    result_density = np.array(result)
    feature_df = pd.DataFrame(all_features)
    mlp = MLP()
    mlp.predict(feature_df, result_density, "density_predict")

