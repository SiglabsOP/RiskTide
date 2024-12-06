import os
import time
from kaggle.api.kaggle_api_extended import KaggleApi
import shutil
from datetime import datetime, timedelta
import threading

# Set the Kaggle API credentials (you only need to do this once)
os.environ['KAGGLE_CONFIG_DIR'] = os.path.expanduser("~/.kaggle")

# Initialize the Kaggle API
api = KaggleApi()
api.authenticate()

# Define the dataset to download (the dataset URL can be found on Kaggle)
dataset = 'gkitchen/s-and-p-500-spy'

# Define the download location (relative or absolute path)
download_location = './SPY_data'  # You can change this to a preferred path

# Define the path for the last run timestamp file
last_run_file = 'last_run.txt'

# Define the path for the spy_data.csv file
spy_data_file = 'spy_data.csv'

# Function to download dataset
def download_spy_dataset():
    # Check if directory exists, create if not
    if not os.path.exists(download_location):
        os.makedirs(download_location)
    
    print(f"Starting download of {dataset}...")
    api.dataset_download_files(dataset, path=download_location, unzip=True)
    print(f"Download complete! Files are saved in {download_location}")

    # Find the downloaded file (assuming there's only one CSV file)
    downloaded_files = [f for f in os.listdir(download_location) if f.endswith('.csv')]

    if downloaded_files:
        downloaded_file = downloaded_files[0]
        print(f"Renaming the downloaded file: {downloaded_file} to 'spy_data.csv'")

        # Rename the file to 'spy_data.csv'
        renamed_file_path = os.path.join(download_location, 'spy_data.csv')
        os.rename(os.path.join(download_location, downloaded_file), renamed_file_path)

        # Move the file to the directory where the script is running from
        current_directory = os.getcwd()  # Get the current script directory
        final_path = os.path.join(current_directory, 'spy_data.csv')

        # Move the renamed file to the script's directory
        shutil.move(renamed_file_path, final_path)
        print(f"Moved the file to {final_path}")
    else:
        print("Error: No CSV file found in the downloaded files.")

# Function to check if the script should download the dataset
def should_download():
    # Check if the spy_data.csv file exists
    if not os.path.exists(spy_data_file):
        print(f"{spy_data_file} not found. Downloading dataset...")
        return True

    # Check if the last_run.txt exists
    if os.path.exists(last_run_file):
        # Read the last run time
        with open(last_run_file, 'r') as f:
            last_run = f.read().strip()

        # Convert the last run time to a datetime object
        last_run_time = datetime.strptime(last_run, '%Y-%m-%d %H:%M:%S')

        # Check if more than a month has passed
        if datetime.now() - last_run_time > timedelta(days=30):
            print("More than a month has passed since the last download. Downloading dataset...")
            return True
        else:
            print("Less than a month since last download. Skipping download.")
            return False
    else:
        print("No last run timestamp found. Downloading dataset...")
        return True

# Function to record the current time as the last run time
def record_last_run_time():
    with open(last_run_file, 'w') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Main function
def main():
    # Check if the dataset needs to be downloaded
    if should_download():
        download_thread = threading.Thread(target=download_spy_dataset)
        download_thread.start()
 
        download_thread.join()  # Wait for the download to finish

        # Record the current time as the last run time
        record_last_run_time()

# Run the script
main()
