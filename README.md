# Trendyol-ETL-Pipeline

## Project Overview

The **Trendyol-ETL-Pipeline** is a Python-based ETL pipeline that scrapes product data from the Trendyol website, cleans the data, and uploads it to AWS S3. The project uses **BeautifulSoup** for web scraping, **pandas** for data cleaning, and **Apache Airflow** for orchestrating the ETL tasks. This pipeline is designed to extract product details such as:

- **Product Brand**
- **Product Name**
- **Product Description**
- **Rating Score**
- **Rating Count**
- **Price (TL)**

## Project Structure

The project is organized as follows:
```plaintext

e-commerce-etl-pipeline/
├── .env.example                # Example configuration file for AWS credentials, S3 bucket, etc.
├── README.md                   # Project description, usage, and setup guide.
├── requirements.txt            # List of required Python packages.
├── data/                       # Directory for storing required data or results (optional).
├── src/                        
│   ├── __init__.py             # Marks the directory as a Python package.
│   ├── aws_s3.py              # Logic for uploading cleaned data to AWS S3.
│   ├── cleaner.py             # Functions for cleaning scraped data.
│   └── scraper.py             # Web scraping logic using BeautifulSoup.
└── airflow/                    
    └── dags/         
        ├── hello_world.py      # Sample Airflow DAG.
        ├── trendyol_etl_pipeline.py  # Main DAG for the ETL process (Extract, Transform, Load).

```
## How It Works

### 1. **Data Extraction (Extract Task)**  
The `scraper.py` file contains the scraping logic which pulls product data from the Trendyol website using **BeautifulSoup**. It extracts the following details for each product:
- Product Brand
- Product Name
- Product Description
- Rating Score
- Rating Count
- Price (TL)

The `scrape_trendyol()` function is used to fetch product data from given page of Trendyol.

### 2. **Data Transformation (Transform Task)**  
The `cleaner.py` file handles the data cleaning process. It uses **pandas** to clean the scraped data, ensuring that there are no empty values and that the data is properly formatted before uploading.

### 3. **Data Loading (Load Task)**  
The `aws_s3.py` file uploads the cleaned data to **AWS S3** using the `boto3` library. The cleaned data is saved as a CSV file and uploaded to the specified S3 bucket.
### 4. **Apache Airflow**  
The ETL pipeline is orchestrated using **Apache Airflow**. The `trendyol_etl_pipeline.py` DAG defines the sequence of tasks:
- **Extract** task: Scrapes the Trendyol website.
- **Transform** task: Cleans the scraped data.
- **Load** task: Uploads the cleaned data to S3.

Airflow manages the execution and scheduling of these tasks.

## Prerequisites

Before running the project, ensure the following are installed:

- Python 3.x
- PostgreSQL database (or other databases you're using)
- AWS account with an S3 bucket (for storing the cleaned data)
- Python packages listed in `requirements.txt`

## Setup and Installation

Follow these steps to set up and install the project:

1. **Clone the Repository**:
   ```bash
     git clone https://github.com/your-username/e-commerce-etl-pipeline.git
     cd e-commerce-etl-pipeline
   ```
2. **Create and Activate a Virtual Environment (Optional but recommended)**:
   ```bash
     python3 -m venv venv
     source venv/bin/activate  # On macOS/Linux
     .\venv\Scripts\activate   # On Windows  
   ```
3. **Install dependencies**:
   ```bash
    pip3 install -r requirements.txt
   ```
4. **Set up the .env file**:\
   Copy the .env.example file to .env and update the following fields with your AWS credentials:
   - AWS_ACCESS_KEY_ID: Your AWS Access Key ID
   - AWS_SECRET_ACCESS_KEY: Your AWS Secret Access Key
   - AWS_REGION: The AWS region you are working in

5. **Install Apache Airflow**:\
   Follow the official [Apache Airflow installation guide](https://airflow.apache.org/docs/apache-airflow/stable/start.html) to set up Airflow on your 
   system. This guide provides step-by-step instructions for installation.
