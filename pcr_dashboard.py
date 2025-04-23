import requests
import streamlit as st

# Enhanced headers to simulate a proper browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.nseindia.com/',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json'
}

@st.cache_data(ttl=300)
def fetch_pcr():
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    session = requests.Session()
    session.headers.update(headers)

    # Get data from the API
    try:
        session.get("https://www.nseindia.com")  # Initiating the session
        response = session.get(url)

        # Check if response is empty or invalid
        if response.status_code != 200:
            st.error(f"Failed to fetch data, status code: {response.status_code}")
            return None, None, None

        # Try to parse JSON data
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            st.error("Error decoding the response. It might not be in JSON format.")
            return None, None, None

        # Process the data
        total_put_oi = 0
        total_call_oi = 0
        for item in data["records"]["data"]:
            if 'PE' in item and 'CE' in item:
                total_put_oi += item['PE']['openInterest']
                total_call_oi += item['CE']['openInterest']

        if total_call_oi == 0:
            st.warning("No data available for Call Open Interest.")
            return None, None, None

        pcr = total_put_oi / total_call_oi
        return round(pcr, 2), total_put_oi, total_call_oi

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None, None, None

# Streamlit dashboard
st.title("📊 Live Put-Call Ratio (PCR) Dashboard")
st.caption("Based on NIFTY Options from NSE")

pcr_value, put_oi, call_oi = fetch_pcr()

if pcr_value is not None:
    st.metric("PCR", pcr_value)
    st.metric("Total PUT OI", f"{put_oi:,}")
    st.metric("Total CALL OI", f"{call_oi:,}")

    if pcr_value > 1:
        st.success("📉 Bearish Bias (More Puts)")
    elif pcr_value < 1:
        st.info("📈 Bullish Bias (More Calls)")
    else:
        st.warning("🔁 Neutral Sentiment")
