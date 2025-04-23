import requests
from bs4 import BeautifulSoup
import streamlit as st

# URL for Nifty option chain data
url = 'https://www.nseindia.com/live_market/dynaContent/live_analysis/option_chain/optionKeys.jsp?symbol=NIFTY'

# Enhanced headers to simulate a real browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.nseindia.com/',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json'
}

# Function to fetch and parse the data
def fetch_pcr():
    try:
        # Initiating a session to simulate a real browser
        session = requests.Session()
        session.headers.update(headers)

        # Make an initial request to get the cookies
        session.get("https://www.nseindia.com")  # This should set the session cookies

        # Send the request to fetch data
        response = session.get(url)

        # Check if the request was successful
        if response.status_code != 200:
            st.error(f"Failed to fetch data, status code: {response.status_code}")
            return None, None, None

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table containing the data
        table = soup.find('table', {'id': 'octable'})

        total_put_oi = 0
        total_call_oi = 0

        # Extract Open Interest (OI) data for Put and Call options
        for row in table.find_all('tr')[2:]:  # Skip the header rows
            cols = row.find_all('td')
            if len(cols) > 10:
                try:
                    put_oi = int(cols[8].text.strip().replace(',', ''))  # PUT OI
                    call_oi = int(cols[9].text.strip().replace(',', ''))  # CALL OI

                    total_put_oi += put_oi
                    total_call_oi += call_oi
                except ValueError:
                    continue  # Skip rows with invalid data

        if total_call_oi == 0:
            st.warning("No data available for Call Open Interest.")
            return None, None, None

        # Calculate PCR (Put-Call Ratio)
        pcr = total_put_oi / total_call_oi
        return round(pcr, 2), total_put_oi, total_call_oi

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None, None, None
