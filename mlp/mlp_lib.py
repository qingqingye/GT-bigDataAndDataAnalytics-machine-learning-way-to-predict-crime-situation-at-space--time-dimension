import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.datasets import fetch_california_housing
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as Data
from matplotlib import pyplot as plt
from pathlib import Path
import seaborn as sns

class MLP:
    def __init__(self, test_size=0.3, random_state=42):
        self.test_size = test_size
        self.random_state = random_state
    def predict(self, sentiment_feature, predict_content, file_name_element):    
    # split test and train
        feature_names=['near 10', 'near 20', 'near 30', '6 days', 'same day of week']
        X_train, X_test, y_train, temp_y_test = train_test_split(sentiment_feature, predict_content, test_size=0.3, random_state=42)
        y_train = y_train[:, 0].reshape(-1)
        y_test = temp_y_test[:, 0].reshape(-1)
        # standard scaler
        scale = StandardScaler()
        X_train_s = scale.fit_transform(X_train)
        X_test_s = scale.fit_transform(X_test)
        featuredf = pd.DataFrame(data=X_train_s, columns=feature_names)
        featuredf["target"] = y_train
        featuredf.dropna(inplace=True)

        # heatmap for correlation between all the features and predict target
        datacor = np.corrcoef(featuredf.values,rowvar=0)
        datacor = pd.DataFrame(data=datacor,columns=featuredf.columns,index=featuredf.columns)
        plt.figure(figsize=(6,6))
        ax=sns.heatmap(datacor,square=True,annot=True,fmt=".3f",linewidths=5,cmap="YlGnBu",cbar_kws={"fraction":0.046,"pad":0.03})
        #plt.show()
        file_name = 'heatmap_' + file_name_element + '.png'
        plt.savefig("output\\" + file_name)

        # transfer dateframe to tensor which will be used by pytorch network
        # print(X_train_s, y_train, X_test_s, y_test)
        train_xt = torch.from_numpy(X_train_s.astype(np.float32))
        train_yt = torch.from_numpy(y_train.astype(np.float32))
        test_xt = torch.from_numpy(X_test_s.astype(np.float32))
        test_yt = torch.from_numpy(y_test.astype(np.float32))
        # tansfer data to data loader
        train_data = Data.TensorDataset(train_xt, train_yt)
        test_data = Data.TensorDataset(test_xt, test_yt)
        train_loader = Data.DataLoader(dataset=train_data, batch_size=64, shuffle=True, num_workers=0)


        # build the mlp model
        class MLPregression(nn.Module):
            def __init__(self):
                super(MLPregression, self).__init__()
                # define the first hid layer
                self.hidden1 = nn.Linear(in_features=5, out_features=100, bias=True)  # 2*100 2 features
                # define the second hid layer
                self.hidden2 = nn.Linear(100, 100)  # 100*100
                # the third hid layer
                self.hidden3 = nn.Linear(100, 50)  # 100*50
                # regression layer
                self.predict = nn.Linear(50, 1)  # 50*1  predict 

            def forward(self, x):
                x = F.relu(self.hidden1(x))
                x = F.relu(self.hidden2(x))
                x = F.relu(self.hidden3(x))
                output = self.predict(x)
                # print(output)
                return output[:, 0]


        mlpreg = MLPregression()
        # print(mlpreg)

        # define optimizer
        optimizer = torch.optim.Adam(mlpreg.parameters(), lr=0.01)
        loss_func = nn.MSELoss()
        train_loss_all = []
        for epoch in range(1000):
            train_loss = 0
            train_num = 0
            for step, (b_x, b_y) in enumerate(train_loader):
                output = mlpreg(b_x)
                loss = loss_func(output, b_y)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                train_loss += loss.item() * b_x.size(0)
                train_num += b_x.size(0)
            train_loss_all.append(train_loss / train_num)
        print(train_loss_all[-1], file_name_element)
        plt.figure(figsize=(10, 6))
        plt.plot(train_loss_all, "ro-", label="Train loss")
        plt.legend()
        plt.grid()
        plt.xlabel("epoch")
        plt.ylabel("loss")
        #plt.show()
        file_name = 'trainloss_' + file_name_element + '.png'
        plt.savefig("output\\"  + file_name)

        # predict
        pre_y = mlpreg(test_xt)
        pre_y = pre_y.data.numpy()
        output_content = []
        for i in range(len(temp_y_test)):
            print(pre_y[i])
            output_content.append(list(temp_y_test[i, 1:]) + [pre_y[i]])
        output_df = pd.DataFrame(output_content)
        output_df.to_csv('predict_result.csv')    

        #print(y_test, pre_y, "y and pre y ")
        mae = mean_absolute_error(y_test, pre_y)

        index = np.argsort(y_test)
        plt.figure(figsize=(12, 5))
        plt.plot(np.arange(len(y_test)), y_test[index], "r", label="original y")
        plt.scatter(np.arange(len(pre_y)), pre_y[index], s=3, c="b", label="prediction")
        plt.legend(loc="upper left")
        plt.grid()
        plt.xlabel("index")
        plt.ylabel("y")
        #plt.show()
        file_name = 'predict_' + file_name_element + '.png'
        plt.savefig("output\\" + file_name)