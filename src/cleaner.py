import pandas as pd
import logging

class DataCleaner:
    def __init__(self, file_path="data/raw_data.csv", output_path="data/cleaned_data.csv"):
        """
        Initialize the DataCleaner with a default output file name.

        Args:
            file_path (str): Path to the raw data CSV file. Defaults to 'raw_data.csv'.
            output_path (str): Path to save the cleaned data. Defaults to 'cleaned_data.csv'.
        """
        self.file_path = file_path
        self.output_path = output_path
        self.df = None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.info("DataCleaner initialized.")

    def clean(self):
        """
        Load, clean, and save the data from the specified file path.
        """
        try:
            # Load data
            self.df = pd.read_csv(self.file_path)
            self.logger.info(f"Data loaded from {self.file_path}.")
        except Exception as e:
            self.logger.error(f"Error loading data from {self.file_path}: {e}")
            return
        
        try:
            # Format the 'Rating Score' column correctly (replace NaN with 0)
            self.df["Rating Score"] = pd.to_numeric(self.df["Rating Score"], errors="coerce").fillna(0).astype(float)
            self.logger.info("'Rating Score' column formatted.")

            # Format the 'Rating Count' column as an int
            self.df["Rating Count"] = pd.to_numeric(self.df["Rating Count"], errors="coerce").fillna(0).astype(int)
            self.logger.info("'Rating Count' column formatted.")

            # Remove rows with missing critical values
            rows_before_drop = len(self.df)
            self.df = self.df.dropna(subset=["Product Brand", "Product Name", "Price (TL)"])
            rows_after_drop = len(self.df)
            rows_dropped = rows_before_drop - rows_after_drop
            if rows_dropped > 0:
                self.logger.info(f"{rows_dropped} rows with missing critical values were removed.")
            else:
                self.logger.info("No rows with missing critical values were found.")

            # Check and remove duplicate rows
            rows_before_drop_duplicates = len(self.df)
            self.df = self.df.drop_duplicates()
            rows_after_drop_duplicates = len(self.df)
            rows_dropped_duplicates = rows_before_drop_duplicates - rows_after_drop_duplicates
            if rows_dropped_duplicates > 0:
                self.logger.info(f"{rows_dropped_duplicates} duplicate rows were removed.")
            else:
                self.logger.info("No duplicate rows found.")

            # Format the 'Price (TL)' column correctly
            self.df["Price (TL)"] = (
                self.df["Price (TL)"]
                .str.replace(".", "", regex=False)  # Remove the thousands separator
                .str.replace(",", ".", regex=False)  # Correct the decimal separator
                .str.split(" ")
                .str[0]  # Take the first part before any spaces
                .fillna(0)  # Replace empty strings with 0
                .astype(float)  # Convert to float type
            )
            self.logger.info("'Price (TL)' column formatted.")

            # Save cleaned data to the output path
            self.df.to_csv(self.output_path, index=False)
            self.logger.info(f"Cleaned data saved to {self.output_path}.")
            
            return self.df
        
        except Exception as e:
            self.logger.error(f"Error during cleaning process: {e}")
            