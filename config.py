import os
from dotenv import load_dotenv

load_dotenv()

env = {
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    "DATASET_PATH": "data/data.csv",
    "FAISS_STORE": "store",
    "SCRAPPER_OUTFILE": "data/data.txt",
}
