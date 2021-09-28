import numpy as np 
import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# PCOS_inf = pd.read_csv('PCOS_infertility.csv')
data = pd.read_excel('C:/Users/Isha Patel/OneDrive/Desktop/PROJECTS/HackJNU/PCOS_data_without_infertility.xlsx', sheet_name="Full_new")

data.columns = [col.strip() for col in data.columns]

#Assiging the features (X)and target(y)

X=data.iloc[: , :-1] #droping out index from features too
y=data.iloc[: , -1:]


#Splitting the data into test and training sets

X_train,X_test, y_train, y_test = train_test_split(X,y, test_size=0.2) 

#Fitting the RandomForestClassifier to the training set

rfc = RandomForestClassifier(n_estimators = 20, criterion = 'entropy',random_state = 42)
rfc.fit(X_train, y_train)

#Making prediction and checking the test set

# pred_rfc = rfc.predict(X_test)
# accuracy = accuracy_score(y_test, pred_rfc)
pred = rfc.predict([[20, 80, 12, 18, 15, 5, 0, 0, 1, 0, 0, 1, 1, 1, 0, 110, 80 ]])    
print(pred)

pickle.dump(rfc, open('model.pkl','wb'))
