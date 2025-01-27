import streamlit as st
import requests
import time
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

st.set_page_config(page_title="Token Analysis", layout="wide")

def fetch_token_data(token_name):
    start_time = time.time()
    response = requests.get(f"http://156.67.111.168:5000/fetch_and_get_basic_info/{token_name}")
    end_time = time.time()
    response_time = end_time - start_time
    if response.status_code == 200:
        return response.json(), response_time
    else:
        st.error(f"Error fetching data: {response.status_code}")
        return None, response_time

def create_sentiment_chart(data):
    categories = ['News', 'Instagram', 'Twitter Profile', 'Twitter Hashtag']
    scores = [
        data['sentiment_data'].get('news_score', 0),
        data['sentiment_data'].get('insta_score', 0),
        data['sentiment_data'].get('twitter_profile_score', 0),
        data['sentiment_data'].get('twitter_hashtag_score', 0)
    ]

    colors = ['#636EFA', '#00CC96', '#EF553B', '#AB63FA']

    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "xy"}, {"type": "domain"}]])

    bar_chart = go.Bar(
        x=scores,
        y=categories,
        orientation='h',
        marker_color=colors
    )

    pie_chart = go.Pie(
        labels=categories,
        values=scores,
        marker=dict(colors=colors),
        hole=0.4
    )

    fig.add_trace(bar_chart, row=1, col=1)
    fig.add_trace(pie_chart, row=1, col=2)

    fig.update_layout(
        title='Sentiment Analysis',
        xaxis_title='Score',
        yaxis_title='Category',
        height=500,
        width=1000,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def create_supply_distribution_chart(data):
    total_supply = data['tokenomics_info'].get('Total Supply', 0)
    circulating_supply = data['tokenomics_info'].get('Circulating Supply', 0)
    tokens_locked = data['utility_info'].get('Tokens Locked', 0)

    # If we don't have circulating supply, we can't create a meaningful chart
    if circulating_supply == 0:
        return None

    other_supply = max(0, total_supply - circulating_supply - tokens_locked)

    labels = ['Circulating Supply', 'Locked Tokens', 'Other']
    values = [circulating_supply, tokens_locked, other_supply]

    # Remove any labels and values that are zero
    labels = [label for label, value in zip(labels, values) if value > 0]
    values = [value for value in values if value > 0]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
    fig.update_layout(
        title='Token Supply Distribution',
        height=400,
        width=700,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def display_token_info(data):
    st.markdown(f"""
        <div class="stMetric">
            <strong>Token Name:</strong> {data['basic_info'].get('Token Name', 'N/A')}
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class="stMetric">
            <strong>Token Symbol:</strong> {data['basic_info'].get('Token Symbol', 'N/A')}
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class="stMetric">
            <strong>Website:</strong> {data['basic_info'].get('Website Link', 'N/A')}
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class="stMetric">
            <strong>Explorer:</strong> {data['basic_info'].get('Explorer', 'N/A')}
        </div>
    """, unsafe_allow_html=True)

def display_tokenomics(data):
    st.markdown(f"""
        <div class="stMetric">
            <strong>Total Supply:</strong> {data['tokenomics_info'].get('Total Supply', 'N/A'):,}
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class="stMetric">
            <strong>Circulating Supply:</strong> {data['tokenomics_info'].get('Circulating Supply', 'N/A'):,}
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class="stMetric">
            <strong>Token Price (USD):</strong> ${data['tokenomics_info'].get('Token Price (USD)', 'N/A'):,.2f}
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class="stMetric">
            <strong>Market Cap (USD):</strong> ${data['tokenomics_info'].get('Market Cap (USD)', 'N/A'):,.2f}
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class="stMetric">
            <strong>Total Volume (USD):</strong> ${data['tokenomics_info'].get('Total Volume (USD)', 'N/A'):,.2f}
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div class="stMetric">
            <strong>All Time High (USD):</strong> ${data['tokenomics_info'].get('All Time High (USD)', 'N/A'):,.2f}
        </div>
    """, unsafe_allow_html=True)

def display_token_utility(data):
    utility_info = data.get('utility_info', {})
    
    st.markdown(f"""
        <div class="stMetric">
            <strong>Tokens Locked:</strong> {utility_info.get('Tokens Locked', 'N/A')}
        </div>
    """, unsafe_allow_html=True)
    
    staking_ratio = utility_info.get('Staking Ratio', 'N/A')
    if isinstance(staking_ratio, (int, float)):
        staking_ratio = f"{staking_ratio:.2%}"
    st.markdown(f"""
        <div class="stMetric">
            <strong>Staking Ratio:</strong> {staking_ratio}
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="stMetric">
            <strong>Token Nature:</strong> {utility_info.get('Token Nature', 'N/A')}
        </div>
    """, unsafe_allow_html=True)
    
    avg_trading_volume = utility_info.get('Average Trading Volume 24 hrs', 'N/A')
    if isinstance(avg_trading_volume, (int, float)):
        avg_trading_volume = f"${avg_trading_volume:,.2f}"
    st.markdown(f"""
        <div class="stMetric">
            <strong>Average Trading Volume (24h):</strong> {avg_trading_volume}
        </div>
    """, unsafe_allow_html=True)
    
    category = utility_info.get('Category', 'Category not found')
    st.markdown(f"""
        <div class="stMetric">
            <strong>Category:</strong> {category}
        </div>
    """, unsafe_allow_html=True)

def main():
    st.title("Token Analysis")

    st.markdown("""
    <style>
    .main {
        background-color: #F5F5F5;
    }
    h1 {
        color: #333;
    }
    .stMetric {
        background-color: #FFF;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .section {
        margin-top: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.header("Fetch Token Data")
    token_name = st.sidebar.text_input("Enter token name:", "bitcoin")
    compare = st.sidebar.checkbox("Compare with another token")

    if compare:
        token_name2 = st.sidebar.text_input("Enter second token name:", "ethereum")
    else:
        # Clear the second token data when comparison is turned off
        if 'data2' in st.session_state:
            del st.session_state.data2
        if 'response_time2' in st.session_state:
            del st.session_state.response_time2

    if st.sidebar.button("Analyze Token(s)"):
        with st.spinner("Fetching data..."):
            data1, response_time1 = fetch_token_data(token_name)
            if compare:
                data2, response_time2 = fetch_token_data(token_name2)
            else:
                data2, response_time2 = None, None

        if data1:
            st.sidebar.success(f"Data fetched successfully in {response_time1:.2f} seconds!")
            st.session_state.data1 = data1
            st.session_state.response_time1 = response_time1

            if compare and data2:
                st.sidebar.success(f"Second token data fetched successfully in {response_time2:.2f} seconds!")
                st.session_state.data2 = data2
                st.session_state.response_time2 = response_time2

    if "data1" in st.session_state:
        data1 = st.session_state.data1
        response_time1 = st.session_state.response_time1

        compare = 'data2' in st.session_state

        if compare:
            data2 = st.session_state.data2
            response_time2 = st.session_state.response_time2

        # Basic Information
        st.subheader("Basic Information")
        if compare:
            col1, col2 = st.columns(2)
            with col1:
                display_token_info(data1)
            with col2:
                display_token_info(data2)
        else:
            display_token_info(data1)

        st.markdown("<div class='section'></div>", unsafe_allow_html=True)

        # Tokenomics
        st.subheader("Tokenomics")
        if compare:
            col1, col2 = st.columns(2)
            with col1:
                display_tokenomics(data1)
            with col2:
                display_tokenomics(data2)
        else:
            display_tokenomics(data1)

        st.markdown("<div class='section'></div>", unsafe_allow_html=True)

        # Supply Distribution Chart
        st.subheader("Supply Distribution")
        if compare:
            col1, col2 = st.columns(2)
            with col1:
                supply_distribution_chart1 = create_supply_distribution_chart(data1)
                if supply_distribution_chart1:
                    st.plotly_chart(supply_distribution_chart1, use_container_width=True)
                else:
                    st.write("Insufficient data to create supply distribution chart.")
            with col2:
                supply_distribution_chart2 = create_supply_distribution_chart(data2)
                if supply_distribution_chart2:
                    st.plotly_chart(supply_distribution_chart2, use_container_width=True)
                else:
                    st.write("Insufficient data to create supply distribution chart.")
        else:
            supply_distribution_chart = create_supply_distribution_chart(data1)
            if supply_distribution_chart:
                st.plotly_chart(supply_distribution_chart, use_container_width=True)
            else:
                st.write("Insufficient data to create supply distribution chart.")

        st.markdown("<div class='section'></div>", unsafe_allow_html=True)

        # Sentiment Analysis
        st.subheader("Sentiment Analysis")
        if compare:
            col1, col2 = st.columns(2)
            with col1:
                sentiment_chart1 = create_sentiment_chart(data1)
                st.plotly_chart(sentiment_chart1, use_container_width=True)
            with col2:
                sentiment_chart2 = create_sentiment_chart(data2)
                st.plotly_chart(sentiment_chart2, use_container_width=True)
        else:
            sentiment_chart = create_sentiment_chart(data1)
            st.plotly_chart(sentiment_chart, use_container_width=True)

        st.markdown("<div class='section'></div>", unsafe_allow_html=True)

        # Token Utility
        st.subheader("Token Utility")
        if compare:
            col1, col2 = st.columns(2)
            with col1:
                display_token_utility(data1)
            with col2:
                display_token_utility(data2)
        else:
            display_token_utility(data1)

        st.markdown("<div class='section'></div>", unsafe_allow_html=True)

        # Recent News Headlines
        st.subheader("Recent News Headlines")
        if compare:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"News for {data1['basic_info']['Token Name']}:")
                for headline, url in data1.get('headlines', []):
                    st.markdown(f"- [{headline}]({url})")
            with col2:
                st.write(f"News for {data2['basic_info']['Token Name']}:")
                for headline, url in data2.get('headlines', []):
                    st.markdown(f"- [{headline}]({url})")
        else:
            for headline, url in data1.get('headlines', []):
                st.markdown(f"- [{headline}]({url})")

        st.markdown("<div class='section'></div>", unsafe_allow_html=True)

        # Overall Score
        st.subheader("Overall Score")
        if compare:
            col1, col2 = st.columns(2)
            col1.metric(f"{data1['basic_info']['Token Name']} Score", f"{data1.get('overall_score', 'N/A'):.2f}")
            col2.metric(f"{data2['basic_info']['Token Name']} Score", f"{data2.get('overall_score', 'N/A'):.2f}")
        else:
            st.metric("Score", f"{data1.get('overall_score', 'N/A'):.2f}")

if __name__ == "__main__":
    main()
