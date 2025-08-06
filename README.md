
README

# Data-Scraping-with-Selenium-Dynamic-Filtering-using-Streamlit

## Introduction
The 'Redbus Data Scraping and Filtering with Streamlit Application' aims to revolutionize the transportation industry by providing a comprehensive solution for collecting, analyzing, and visualizing bus travel data. By utilizing Selenium for web scraping, this project automates the extraction of detailed information from Redbus, including bus routes, schedules, prices, and seat availability. By streamlining data collection and providing powerful tools for data-driven decision-making, this project can significantly improve operational efficiency and strategic planning in the transportation industry.

## Domain
**TRANSPORTATION**

## Skill-Takeaway
- Python scripting
- Selenium
- Data Collection
- Data Management using SQL
- Streamlit

## Technology Used
- Python 3.9
- MySQL 8.0
- Streamlit
- Selenium

## Features of Application

### Retrieve the Bus Information
Selenium is a powerful tool for automating web browsers, which is especially useful for web scraping tasks. If you want to retrieve bus details from RedBus, you can use Selenium to automate the process of searching for buses and extracting the relevant information. This involves interacting with web elements like input fields and buttons, waiting for the page to load, and extracting the desired details from the search results.

### Store data in database
The collected bus details data was transformed into pandas dataframes. Before that, a new database and tables were created using the MySQL connector. With the help of MySQL, the data was inserted into the respective tables. The database could be accessed and managed in the MySQL environment.

### Web app - Streamlit
With the help of Streamlit, you can create an interactive application similar to RedBus by designing a user-friendly interface that allows users to search for bus routes, view available buses, and get details like departure times and prices.

## Packages and Libraries
```python
pandas as pd
mysql.connector
import time
streamlit as slt
import datetime
from streamlit_option_menu import option_menu
from selenium import webdriver
```
<img width="1920" height="1200" alt="Screenshot (148)" src="https://github.com/user-attachments/assets/7920f9bf-57d1-44d3-8d80-592ea447dad2" />
