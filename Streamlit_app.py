import streamlit as st
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from datetime import datetime

# DB credentials
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'Redbus%402025'
DB_NAME = 'redbus_data'

# MySQL connection string using SQLAlchemy
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

# Streamlit App
st.set_page_config(page_title="Redbus Bus Data", layout="wide")
st.title(" 🚌 Redbus Bus Details")

@st.cache_data(ttl=300)
def load_data():
    query = "SELECT * FROM bus_details ORDER BY scraped_date DESC"
    df = pd.read_sql(query, engine)
    return df

df = load_data()
# ✅ Optional: Debug - display sample data from DB
#st.write("✅ Sample data from DB:")
#st.write(df.head())
# Sidebar filters
st.sidebar.header("🔍 Filter Options")

# Date filter
#dates = sorted(df['scraped_date'].dropna().unique(), reverse=True)
#selected_date = st.sidebar.selectbox("Select Date", dates)
#df = df[df['scraped_date'] == selected_date]

# Route filter (from-to)
df['route'] = df['route_link'].str.extract(r'bus-tickets/([a-zA-Z0-9-]+)')
df[['from_city', 'to_city']] = df['route'].str.split('-to-', expand=True)

from_options = sorted(df['from_city'].dropna().unique())
to_options = sorted(df['to_city'].dropna().unique())

col1, col2 = st.sidebar.columns(2)
from_city = col1.selectbox("From", ['All'] + from_options)
to_city = col2.selectbox("To", ['All'] + to_options)

if from_city != 'All':
    df = df[df['from_city'] == from_city]
if to_city != 'All':
    df = df[df['to_city'] == to_city]

# Bus type filter
bustypes = sorted(df['bustype'].dropna().unique())
bustype_selected = st.sidebar.multiselect("Bus Type", options=bustypes)

if bustype_selected:
    df = df[df['bustype'].isin(bustype_selected)]
    
# Govt/Private filter
govt_keywords = ['ksrtc', 'apsrtc', 'tsrtc', 'msrtc', 'rsrtc', 'gsrtc', 'osrtc']
df['bus_type_category'] = df['busname'].str.lower().apply(
    lambda x: 'Government' if any(gov in x for gov in govt_keywords) else 'Private'
)
bus_type_choice = st.sidebar.radio("Bus Ownership Type", ['All', 'Government', 'Private'])
if bus_type_choice != 'All':
    df = df[df['bus_type_category'] == bus_type_choice]

# Price filter
price_range = st.sidebar.slider("Price Range", 0, 10000, (0, 10000))
df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]

# Rating filter
df['star_rating'] = df['star_rating'].fillna(0)
rating_range = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)
df = df[df['star_rating'] >= rating_range]

# Seats filter
seats_range = st.sidebar.slider("Minimum Seats Available", 0, int(df['seats_available'].max()), 0)
df = df[df['seats_available'] >= seats_range]

# Final Display Table
#st.markdown(f"### 🎯 Showing {len(df)} Buses for {selected_date}")
st.markdown(f"### 🎯 Showing {len(df)} Buses")

st.dataframe(df[['busname', 'bustype', 'departing_time', 'reaching_time', 'duration', 'price', 'star_rating', 'seats_available',]], use_container_width=True)

# Download CSV
#csv = df.to_csv(index=False)
#st.download_button("📥 Download CSV", csv, "redbus_filtered.csv", "text/csv")
