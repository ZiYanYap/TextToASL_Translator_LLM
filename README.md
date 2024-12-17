## TextToASL Translator
A Python Flask application that utilises prompt engineering technique on LLM to translate multilingual sentence to American Sign Language (ASL) simplified gloss and display the sign language video.

## Things to include in .env file
```
DB_NAME=
COLLECTION_NAME=
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxx
MONGODB_URI=mongodb+srv://<USERNAME>:<PASSWORD>@...
```

## To start scraping video files into local
```bash
python tools/video_scraper.py
```
