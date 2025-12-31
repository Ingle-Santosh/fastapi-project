from pathlib import Path

# Directories
DATA_DIR = Path('data')
APP_DIR = Path('app')
MODEL_DIR = APP_DIR / 'models'

# File paths
DATA_FILE_PATH = DATA_DIR / 'car-details.csv'
MODEL_PATH = MODEL_DIR / 'model.joblib'

# create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print("Data file path:", DATA_FILE_PATH)
print("Model file path:", MODEL_PATH)
