import os
from pathlib import Path
from dotenv import load_dotenv

def main():
    repo_root = Path(__file__).resolve().parent.parent
    
    # Load .env file
    env_path = repo_root / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # Handle the difference in environment variable names
    if "KAGGLE_USER_NAME" in os.environ and "KAGGLE_USERNAME" not in os.environ:
        os.environ["KAGGLE_USERNAME"] = os.environ["KAGGLE_USER_NAME"]
        
    if "KAGGLE_API_KEY" in os.environ and "KAGGLE_KEY" not in os.environ:
        os.environ["KAGGLE_KEY"] = os.environ["KAGGLE_API_KEY"]
        
    # Import kaggle after setting env vars so it picks them up
    import kaggle

    data_dir = repo_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    kaggle.api.authenticate()
    
    print("Downloading Billboard Hot 100 dataset...")
    kaggle.api.dataset_download_files('ludmin/billboard', path=str(data_dir), unzip=True)
    
    print("Downloading Global Music Artists dataset...")
    kaggle.api.dataset_download_files('harshdprajapati/worldwide-music-artists-dataset-with-image', path=str(data_dir), unzip=True)
    
    print("Datasets downloaded successfully.")

if __name__ == "__main__":
    main()
