import wget
import os

# Function to download a dataset from the Stanford Large Network Dataset Collection
def download_dataset(dataset_url, save_directory):
    # Ensure the save directory exists, create it if it doesn't
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Extract the dataset name from the URL
    dataset_name = dataset_url.split('/')[-1]

    # Set the path to save the dataset
    save_path = os.path.join(save_directory, dataset_name)

    # Download the dataset
    print(f"Downloading dataset from {dataset_url}...")
    wget.download(dataset_url, out=save_path)
    print("\nDownload completed.")

    return save_path

if __name__ == "__main__":
    # Example: Download the Facebook social network dataset
    facebook_dataset_url = "https://snap.stanford.edu/data/facebook_combined.txt.gz"
    save_directory = "datasets"
    downloaded_file_path = download_dataset(facebook_dataset_url, save_directory)
    print(f"Dataset downloaded and saved to: {downloaded_file_path}")
