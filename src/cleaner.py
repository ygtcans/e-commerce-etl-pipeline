import pandas as pd


def clean(file_path):
    df = pd.read_csv(file_path)
    
    # Remove rows with missing values
    df = df.dropna()

    # Check and remove duplicate rows
    df= df.drop_duplicates()
    
    # Format the column correctly as a int
    df["Rating Count"] = df["Rating Count"].astype(int)
    
    # Format the 'Price (TL)' column correctly
    df["Price (TL)"] = (
        df["Price (TL)"]
        .str.replace(".", "", regex=False)  # Remove the thousands separator
        .str.replace(",", ".", regex=False)  # Correct the decimal separator
        .str.split(" ") 
        .str[0]  # Take the first part before any spaces
        .astype(float)  # Convert to float type
    )

    return df

def main():
    print(clean("data/raw_data.csv"))

if __name__ == "__main__":
    main()
