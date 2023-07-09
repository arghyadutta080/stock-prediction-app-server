import os
import numpy as np
import pandas as pd
import yfinance as yf
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

from rest_framework.views import APIView
from rest_framework.response import Response

class HelloWorldView(APIView):
    def get(self, request):
        return Response({"message": "Hello, World!"})
    

class StockPredictionView(APIView):
    
    def get(self, request):
        # Get stock symbol from query parameters
        stock_symbol = request.query_params.get('symbol')

        # Validate stock symbol
        if not stock_symbol:
            return Response({'error': 'Stock symbol is required.'}, status=400)

        # Last 5 years data with interval of 1 day
        data = yf.download(tickers=stock_symbol, period='5y', interval='1d')

        # Extract the 'Open' prices from the data
        opn = data[['Open']]

        # Check if 'opn' is empty
        if opn.empty:
            return Response({'error': 'No data available for the given stock symbol.'}, status=404)

        # Using StandardScaler for normalizing data
        scaler = StandardScaler()
        ds_scaled = scaler.fit_transform(np.array(opn).reshape(-1, 1))

        # Creating dataset in time series for LSTM model
        def create_dataset(dataset, step):
            X_train, y_train = [], []
            for i in range(len(dataset) - step - 1):
                a = dataset[i:(i+step), 0]
                X_train.append(a)
                y_train.append(dataset[i + step, 0])
            return np.array(X_train), np.array(y_train)

        # Defining the time step for LSTM
        time_step = 100

        # Creating the training dataset
        X_train, y_train = create_dataset(ds_scaled, time_step)

        # Reshaping the data to fit into the LSTM model
        X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)

        # Load the saved model
        model = load_model(os.path.join(os.getcwd(), 'Stock.h5'))

        # Predicting the next 30 days price
        future_input = ds_scaled[-time_step:].reshape(1, time_step, 1)
        predicted_prices = []
        stock_prices = []
        current_price = data['Open'].iloc[-1]  # Get the current stock price

        for day in range(1, 31):
            prediction = model.predict(future_input)
            predicted_price = scaler.inverse_transform(prediction)[0][0]
            predicted_prices.append(predicted_price)
            current_price += current_price * (predicted_price / 100)  # Calculate the next day's stock price based on the predicted percentage change
            stock_prices.append(current_price)
            prediction = prediction.reshape(1, 1, 1)  # Reshape prediction to match future_input dimensions
            future_input = np.append(future_input[:, 1:, :], prediction, axis=1)

        return Response({
            'symbol': stock_symbol,
            'predicted_prices': predicted_prices,
            'days': list(range(1, 31)),
            'stock_prices': stock_prices
        }, status=200)    



