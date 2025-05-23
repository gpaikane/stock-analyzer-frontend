import time

import streamlit as st
import bridge
import plots
import pandas as pd
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)


class EndPoints(Enum):
    GET_TOP_FUNDAMENTALS = "get_top_fundamentals",
    GET_FUNDAMENTAL_VALUES = "get_fundamentals_values",
    GET_TICKER = "get_ticker",
    GET_COMPANY_DETAILS = "get_company_details",
    GET_NEWS = "get_news",
    GET_SUMMARY = "generate_summary",
    GET_FORECAST = "get_forecasted_data",
    GET_ASYNC_RESULTS = "get_async_results",
    NONE = "none"


st.title("Company Evaluation Tool")

company_input = st.text_input(
    "Enter **Company** name and **Country** where it is listed:",
    placeholder = "e.g. Persistent Systems from India"
)

# Dropdown for selecting number of parameters
num_params = st.selectbox(
    "On how many parameters you want to evaluate the company (max 10) ?",
    options = list(range(1, 11)),
    index = 4  # Default to 5 (0-based index)
)

def create_placeholder(message):
    placeholder = st.empty()
    # Show progress
    placeholder.info(f" {message}... Please wait")
    return placeholder

def write_placeholder(placeholder, message):
    placeholder.markdown(message)
    return placeholder

def poll_endpoint_with_params(endpoint, task_id):

    polling_count = 0
    poll_result = bridge.call_endpoint_with_params(endpoint, task_id = task_id)

    while poll_result['status'] != "completed":
        time.sleep(15)
        polling_count += 1
        if polling_count > 16:
            return  None
        poll_result = bridge.call_endpoint_with_params(endpoint, task_id=task_id)
        logging.info("poll_result------- " +  str(poll_result))

    return  poll_result["result"]

def  initiate_fundamental_calculation(ticker_name):

    logging.info("getting top fundamentals")
    fundamentals = bridge.call_endpoint_with_params(EndPoints.GET_TOP_FUNDAMENTALS.value,
                                                 fundamental_count=int(num_params))
    logging.info("calculating fundamental values")
    task = bridge.call_endpoint_with_params(EndPoints.GET_FUNDAMENTAL_VALUES.value, fundamentals=fundamentals,
                                            ticker_name=ticker_name)
    logging.info("Fundamental Task id: "+ task["task_id"])
    task_id = task["task_id"]
    return  task_id, ticker_name

def  initiate_company_news_search_and_summary(company_input):

    logging.info("getting company and country suffix")
    company, suffix = bridge.call_endpoint_with_params(EndPoints.GET_COMPANY_DETAILS.value, text=company_input.strip())

    logging.info("getting company news")
    news_task = bridge.call_endpoint_with_params(EndPoints.GET_NEWS.value, company=company, suffix=suffix)
    logging.info("News Task id: "+ news_task["task_id"])
    task_id = news_task["task_id"]
    return  task_id


def  initiate_final_summary(fundamentals_values, news, ticker):

    logging.info("getting company summarized opinion")
    summary_task = bridge.get_endpoint_with_data(EndPoints.GET_SUMMARY.value, fundamentals_values=fundamentals_values,
                                            new_summary=news,
                                            ticker=ticker)

    print("summary_task-----", summary_task)
    logging.info("Summary Task id: "+ summary_task["task_id"])
    task_id = None if summary_task is None else summary_task["task_id"]
    return  task_id


def display_final_summary(summary_placeholder, ticker, task_id):
    if(task_id is None):
        write_placeholder(summary_placeholder, "")
        st.write(f"Summarized opinion could not be generated for {ticker}")
        return

    logging.info("getting final summary")
    final_result = poll_endpoint_with_params(EndPoints.GET_ASYNC_RESULTS.value, task_id)

    logging.info("summary--- " + f"{final_result}")
    write_placeholder(summary_placeholder, "")

    if final_result != "" and final_result is not None and len(final_result) !=0:
        st.markdown(f"**Summarized opinion on short and long term investment for:  {ticker}**")
        st.markdown(final_result)
    else:
        st.write(f"Summarized opinion could not be generated for {ticker}")


def display_news_search_and_summary(news_placeholder, ticker, task_id):
    logging.info("getting company news")
    new_summary_result = poll_endpoint_with_params(EndPoints.GET_ASYNC_RESULTS.value, task_id)
    write_placeholder(news_placeholder, "")
    if new_summary_result == "" or new_summary_result is None or len(new_summary_result) ==0:

        st.markdown(f"**News summary of {ticker} could not be generated**")
        return None
    else:
        st.markdown(f"**Here is the news summary of {ticker}:**")
        st.markdown(new_summary_result)
        return new_summary_result


def display_fundamental_calculation(ticker, placeholder, task_id):

    fundamentals_values = poll_endpoint_with_params(EndPoints.GET_ASYNC_RESULTS.value, task_id)
    logging.info("final fundamentals: " + str(fundamentals_values))

    if fundamentals_values is None or len(fundamentals_values) == 0  :
        write_placeholder(placeholder, "")
        st.markdown(f"**Fundamentals of {ticker} could not be calculated, please submit the request again:**")
        return None, None

    df = pd.DataFrame([fundamentals_values])
    df.index = ["Result"]
    final_fundamental_df = df.T
    if len(final_fundamental_df) == 0:
        write_placeholder(placeholder, "")
        st.markdown(f"**Fundamentals of {ticker} could not be calculated, please submit the request again:**")
        return  None, None
    else:
        write_placeholder(placeholder, f"**Here are {ticker} fundamentals:**")
        st.write(final_fundamental_df)
        return  final_fundamental_df, fundamentals_values

if __name__ == "__main__":
    # Submit button
    if st.button("Submit"):
        if company_input.strip() == "":
            st.warning("Please enter a valid company name and country.")
        else:
            # Display the captured inputs
            st.markdown(f"**Company & Country:** {company_input}")
            st.markdown(f"**Number of Parameters Chosen:** {num_params}")

        fundamentals_task_id = None
        fundamentals_values = None
        fundamental_placeholder = None
        news_task_id = None
        news_summary = None

        logging.info("getting ticker")
        ticker = bridge.call_endpoint_with_params(EndPoints.GET_TICKER.value, text=company_input.strip())
        logging.info("TICKER:", ticker)
        fundamental_placeholder = create_placeholder("Calculating fundamentals it may take few minutes...")

        try:
            #Initiate  Fundamentals Calculations
            fundamentals_task_id, ticker = initiate_fundamental_calculation(ticker)
        except Exception as e:
            logging.exception(e)
            write_placeholder(fundamental_placeholder, "")
            st.markdown(f"**Fundamentals of {ticker} could not be calculated, please submit the request again:**")

        try:
            #Initiate Search News
            news_task_id = initiate_company_news_search_and_summary(company_input)
        except Exception as e:
            logging.exception(e)
            st.markdown(f"**News summary for {ticker} could not be generated due to lack of data:**")

        #Get forecast
        logging.info("getting company forecast")
        forecast = None
        try:
            forecast = bridge.call_endpoint_with_params(EndPoints.GET_FORECAST.value, ticker=ticker)
        except Exception as e:
            forecast = None

        if fundamentals_task_id is not None:
            #Get and display calculated fundamentals_values
            _, fundamentals_values = display_fundamental_calculation(ticker,fundamental_placeholder,fundamentals_task_id)


        if news_task_id is not None:
            #Get and display news summary
            news_placeholder = create_placeholder("Searching for news to generate summary...")
            news_summary = display_news_search_and_summary(news_placeholder,ticker, news_task_id)
            write_placeholder(news_placeholder, "")


        # Display forecast
        if(forecast is not None):
            fig = plots.plot_ploty(pd.DataFrame(forecast), ticker=ticker)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('**Forecast Could noy be generated due to lack of data')

        if news_summary is not None or (fundamentals_values is not None and len(fundamentals_values) != 0):
            if news_summary is None:
                news_summary = ""
            if fundamentals_values is None or len(fundamentals_values)==0:
                fundamentals_values = dict()
            summary_placeholder = create_placeholder("Generating final summary:")

            try:
                #Initiate Final Summary
                summary_task_id = initiate_final_summary(fundamentals_values, news_summary, ticker)
            except Exception as e:
                st.markdown(f"**Final summary for {ticker} could not be generated due to lack of data:**")
                logging.info(e)
                write_placeholder(summary_placeholder, "")
            else:
                #Display Final Summary
                display_final_summary(summary_placeholder, ticker, summary_task_id)
        else:
            st.markdown(f"**Final summary for {ticker} could not be generated due to lack of data:**")