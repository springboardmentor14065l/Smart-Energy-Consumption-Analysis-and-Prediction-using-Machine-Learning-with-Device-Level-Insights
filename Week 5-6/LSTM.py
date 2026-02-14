import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error,mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM,Dense,Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

df=pd.read_csv("understand the dataset.csv")

scaler=MinMaxScaler(feature_range=(0,1))
energy_scaled=scaler.fit_transform(df[['energy']])

def create_sequences(data,time_steps):
    X,y=[],[]
    for i in range(time_steps,len(data)):
        X.append(data[i-time_steps:i,0])
        y.append(data[i,0])
    return np.array(X),np.array(y)

TIME_STEPS=24
X,y=create_sequences(energy_scaled,TIME_STEPS)

split=int(0.8*len(X))
X_train,X_test=X[:split],X[split:]
y_train,y_test=y[:split],y[split:]

X_train=X_train.reshape((X_train.shape[0],X_train.shape[1],1))
X_test=X_test.reshape((X_test.shape[0],X_test.shape[1],1))

model=Sequential()
model.add(LSTM(64,return_sequences=True,input_shape=(TIME_STEPS,1)))
model.add(Dropout(0.2))
model.add(LSTM(32))
model.add(Dropout(0.2))
model.add(Dense(1))

model.compile(optimizer=Adam(learning_rate=0.001),loss='mean_squared_error')

early_stop=EarlyStopping(monitor='val_loss',patience=5,restore_best_weights=True)

model.fit(X_train,y_train,epochs=30,batch_size=32,validation_split=0.1,callbacks=[early_stop],verbose=1)

y_pred_scaled=model.predict(X_test)
y_test_actual=scaler.inverse_transform(y_test.reshape(-1,1))
y_pred_actual=scaler.inverse_transform(y_pred_scaled)

mae=mean_absolute_error(y_test_actual,y_pred_actual)
rmse=np.sqrt(mean_squared_error(y_test_actual,y_pred_actual))

print("LSTM MAE:",mae)
print("LSTM RMSE:",rmse)

model.save("lstm_energy_model.h5")
print("Model saved successfully")
