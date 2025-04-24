import os
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"  # Using LLama3 model from Groq

# Configure page
st.set_page_config(
    page_title="Finance Agent",
    page_icon="📊",
    layout="wide"
)

class FinanceAgent:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
    
    def get_stock_data(self, ticker_symbol):
        """Retrieve key financial data for a stock"""
        try:
            stock = yf.Ticker(ticker_symbol)
            
            # Basic info
            info = stock.info
            history = stock.history(period="1y")
            
            # Compile relevant financial data
            financial_data = {
                "company_name": info.get("longName", "N/A"),
                "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "eps": info.get("trailingEPS", "N/A"),
                "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
                "recommendation": info.get("recommendationKey", "N/A"),
                "target_price": info.get("targetMeanPrice", "N/A")
            }
            
            # Calculate price change if history data is available
            if len(history) > 1:
                financial_data["price_change_1y"] = ((history["Close"][-1] / history["Close"][0]) - 1) * 100
            else:
                financial_data["price_change_1y"] = "N/A"
            
            return financial_data, None
        except Exception as e:
            return None, f"Error retrieving data for {ticker_symbol}: {str(e)}"
    
    def groq_generate(self, prompt):
        """Generate text using Groq API"""
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(GROQ_API_URL, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error generating content: {str(e)}"
    
    def analyze_stock(self, ticker_symbol):
        """Generate comprehensive analysis for a stock"""
        data, error = self.get_stock_data(ticker_symbol)
        
        if error:
            return error
        
        # Format the data for Groq
        prompt = f"""
        As a financial analyst, provide a comprehensive analysis of {data['company_name']} ({ticker_symbol}) with the following data:
        
        MARKET OVERVIEW:
        - Current Price: ${data['current_price']}
        - 52-Week Range: ${data['52w_low']} - ${data['52w_high']}
        - Market Cap: ${data['market_cap']}
        
        FINANCIAL METRICS:
        - P/E Ratio: {data['pe_ratio']}
        - EPS: ${data['eps']}
        - 1-Year Price Change: {data['price_change_1y']}%
        
        ANALYST INSIGHTS:
        - Recommendation: {data['recommendation']}
        - Target Price: ${data['target_price']}
        
        Follow this structure:
        1. Executive Summary (2-3 sentences)
        2. Financial Performance Analysis
        3. Market Position
        4. Future Outlook & Risks
        5. Investment Perspective
        
        Keep the analysis professional but easy to understand for regular investors.
        Use bullet points for key insights.
        """
        
        # Generate analysis using Groq
        return self.groq_generate(prompt)
    
    def compare_stocks(self, ticker_list):
        """Compare multiple stocks in the same industry"""
        all_data = {}
        for ticker in ticker_list:
            data, error = self.get_stock_data(ticker)
            if data:
                all_data[ticker] = data
            else:
                return f"Error processing {ticker}: {error}"
        
        # Prepare comparison prompt
        companies = ", ".join([f"{all_data[t]['company_name']} ({t})" for t in ticker_list])
        
        metrics_table = "| Company | Price | P/E | Market Cap | 1Y Change | Recommendation |\n"
        metrics_table += "| ------- | ----- | --- | ---------- | --------- | -------------- |\n"
        
        for ticker in ticker_list:
            data = all_data[ticker]
            price_change = data.get('price_change_1y', 'N/A')
            price_change_str = f"{price_change:.2f}%" if isinstance(price_change, (int, float)) else price_change
            
            metrics_table += f"| {data['company_name']} | ${data['current_price']} | {data['pe_ratio']} | ${data['market_cap']} | {price_change_str} | {data['recommendation']} |\n"
        
        prompt = f"""
        As a financial analyst, compare these companies: {companies}
        
        Here are their key metrics:
        
        {metrics_table}
        
        Provide a comparative analysis with:
        1. Industry Overview (brief)
        2. Company-by-Company Performance
        3. Investment Outlook
        
        Keep the analysis simple, clear and accessible for regular investors.
        Highlight key strengths and weaknesses for each company.
        """
        
        # Generate analysis using Groq
        return self.groq_generate(prompt)

# Initialize the Finance Agent
@st.cache_resource
def get_finance_agent():
    return FinanceAgent()

try:
    agent = get_finance_agent()
    
    # Header
    st.title("📊 Finance Agent")
    st.markdown("Your personal AI-powered stock analyst")
    
    # Create tabs for different analysis types
    tab1, tab2 = st.tabs(["Single Stock Analysis", "Compare Stocks"])
    
    # Single Stock Analysis Tab
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            ticker_symbol = st.text_input("Enter Stock Ticker Symbol (e.g., AAPL, MSFT, GOOGL)", key="single_stock").upper()
        
        with col2:
            analyze_button = st.button("Analyze Stock", key="analyze_single")
        
        if ticker_symbol and analyze_button:
            with st.spinner(f'Analyzing {ticker_symbol}...'):
                try:
                    # Get stock data
                    data, error = agent.get_stock_data(ticker_symbol)
                    
                    if error:
                        st.error(error)
                    else:
                        # Show company name
                        st.subheader(f"{data['company_name']} ({ticker_symbol})")
                        
                        # Key metrics in columns
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Current Price", f"${data['current_price']}")
                        col2.metric("Market Cap", f"${data['market_cap']}")
                        col3.metric("P/E Ratio", f"{data['pe_ratio']}")
                        
                        # Price chart
                        st.subheader("Price History (1 Year)")
                        stock_history = yf.Ticker(ticker_symbol).history(period="1y")
                        
                        if not stock_history.empty:
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=stock_history.index, 
                                y=stock_history['Close'],
                                mode='lines',
                                name='Price',
                                line=dict(color='#0052cc', width=2)
                            ))
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # AI Analysis
                        st.subheader("AI Analysis")
                        analysis = agent.analyze_stock(ticker_symbol)
                        st.markdown(analysis)
                            
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    # Compare Stocks Tab
    with tab2:
        st.subheader("Compare Multiple Stocks")
        
        # Industry presets
        industry_options = {
            "Custom": [],
            "Tech Giants": ["AAPL", "MSFT", "GOOGL", "AMZN"],
            "Semiconductors": ["NVDA", "AMD", "INTC", "TSM"],
            "Automotive": ["TSLA", "F", "GM", "TM"],
            "Banking": ["JPM", "BAC", "C", "WFC"],
        }
        
        selected_option = st.selectbox("Select Industry or Custom", list(industry_options.keys()))
        
        if selected_option == "Custom":
            ticker_input = st.text_input("Enter ticker symbols separated by commas (e.g., AAPL,MSFT,GOOGL)")
            if ticker_input:
                ticker_list = [t.strip().upper() for t in ticker_input.split(',')]
            else:
                ticker_list = []
        else:
            ticker_list = industry_options[selected_option]
            st.write(f"Selected tickers: {', '.join(ticker_list)}")
        
        compare_button = st.button("Compare Stocks")
        
        if ticker_list and len(ticker_list) >= 2 and compare_button:
            with st.spinner(f'Comparing {", ".join(ticker_list)}...'):
                try:
                    # Get data for each stock
                    all_data = {}
                    error_occurred = False
                    
                    for ticker in ticker_list:
                        data, error = agent.get_stock_data(ticker)
                        if error:
                            st.error(error)
                            error_occurred = True
                            break
                        all_data[ticker] = data
                    
                    if not error_occurred:
                        # Create comparison table
                        comparison_data = []
                        for ticker in ticker_list:
                            data = all_data[ticker]
                            price_change = data.get('price_change_1y', 'N/A')
                            price_change_str = f"{price_change:.2f}%" if isinstance(price_change, (int, float)) else price_change
                            
                            comparison_data.append({
                                'Company': f"{data['company_name']} ({ticker})",
                                'Price': f"${data['current_price']}",
                                'P/E': data['pe_ratio'],
                                'Market Cap': f"${data['market_cap']}",
                                '1Y Change': price_change_str,
                                'Recommendation': data['recommendation']
                            })
                        
                        st.subheader("Comparison Metrics")
                        comparison_df = pd.DataFrame(comparison_data)
                        st.table(comparison_df)
                        
                        # Price comparison chart
                        st.subheader("Price Performance (1 Year)")
                        
                        fig = go.Figure()
                        for ticker in ticker_list:
                            stock_history = yf.Ticker(ticker).history(period="1y")
                            if not stock_history.empty:
                                # Normalize to percentage change
                                first_price = stock_history['Close'].iloc[0]
                                normalized_prices = (stock_history['Close'] / first_price - 1) * 100
                                
                                fig.add_trace(go.Scatter(
                                    x=stock_history.index,
                                    y=normalized_prices,
                                    mode='lines',
                                    name=ticker
                                ))
                        
                        fig.update_layout(
                            height=400,
                            yaxis_title="% Change",
                            legend_title="Companies"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # AI Analysis
                        st.subheader("AI-Powered Comparison")
                        comparison = agent.compare_stocks(ticker_list)
                        st.markdown(comparison)
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        elif ticker_list and compare_button:
            st.warning("Please select at least 2 stocks for comparison")

except Exception as e:
    st.error(f"Failed to initialize Finance Agent: {str(e)}")
    st.info("Please check your .env file and ensure GROQ_API_KEY is properly set")
