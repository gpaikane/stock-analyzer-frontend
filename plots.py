import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def plot_ploty( df, ticker):
    df['ds'] = pd.to_datetime(df['ds'])

    # Define the cutoff date
    cutoff_date = pd.to_datetime(str(datetime.now().date()))

    # Split data into historical and forecast
    historical = df[df['ds'] < cutoff_date]
    forecast = df[df['ds'] >= cutoff_date]

    # Create the plot
    fig = go.Figure()

    # Historical data trace
    fig.add_trace(go.Scatter(
        x=historical['ds'], y=historical['yhat'],
        mode='lines',
        name='Historical',
        line=dict(color='blue')
    ))

    # Forecasted data trace
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color='orange', dash='dash')  # Dash style optional
    ))

    # Update layout
    fig.update_layout(
        title=f'Historical vs Forecasted Data for {ticker} using FB-PROPHET',
        xaxis_title='Date',
        yaxis_title='Value',
        template='plotly_white'
    )

    return fig