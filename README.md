# Finance Agent: AI-Powered Stock Analysis Tool

## Project Overview

Finance Agent is an interactive web application built with Streamlit that provides AI-powered stock analysis and comparison tools for investors. The application leverages financial data APIs and the powerful Llama3 large language model via Groq's API to deliver comprehensive stock analysis in seconds.

## Features

- **Single Stock Analysis**: Get detailed insights about individual stocks including:
  - Current price and key financial metrics
  - Interactive price history charts
  - AI-generated comprehensive analysis covering financial performance, market position, and investment outlook
  
- **Stock Comparison**: Compare multiple stocks with:
  - Side-by-side metric comparison tables
  - Normalized price performance charts
  - AI-generated comparative analysis highlighting strengths and weaknesses of each company

- **Industry Presets**: Quick access to pre-configured groups of stocks in major sectors:
  - Tech Giants
  - Semiconductors
  - Automotive
  - Banking
  - Custom groupings

## Target Users

Finance Agent is designed for:

- Individual investors looking for quick, intelligent insights about stocks
- Financial advisors who need to quickly compare investment options
- Students learning about market analysis
- Anyone interested in stock market investments who wants AI-assisted research

## Installation Requirements

### Prerequisites

- Python 3.8 or higher
- A Groq API key (sign up at [groq.com](https://groq.com))

### Required Libraries

```
pip install streamlit
pip install plotly
pip install pandas
pip install yfinance
pip install requests
pip install python-dotenv
```

### Environment Setup

1. Clone the repository
2. Create a `.env` file in the root directory
3. Add your Groq API key to the `.env` file:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

## Running the Application

Execute the following command in the project directory:

```
streamlit run app.py
```

The application will launch in your default web browser.

## Usage Guide

1. **For Single Stock Analysis**:
   - Enter a stock ticker symbol (e.g., AAPL for Apple)
   - Click "Analyze Stock"
   - Review the metrics, charts, and AI analysis

2. **For Stock Comparison**:
   - Select an industry preset or choose "Custom"
   - For custom comparisons, enter ticker symbols separated by commas
   - Click "Compare Stocks"
   - Review the comparison table, performance chart, and AI-generated comparison

## Notes

- The application requires an active internet connection to fetch stock data and access the Groq API
- Analysis quality depends on data availability for the selected stocks
- API rate limits may apply for both stock data and AI-generated content
