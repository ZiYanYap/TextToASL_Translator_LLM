## TextToASL Translator
A Python Flask application that utilises prompt engineering technique on LLM to translate multilingual sentence to American Sign Language (ASL) simplified gloss and display the sign language video.

## Things to include in .env file
```
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxx
MONGODB_URI=mongodb+srv://<USERNAME>:<PASSWORD>@texttoasl-cluster.dhra8.mongodb.net/?retryWrites=true&w=majority&appName=TextToASL-Cluster
```

## To start scraping video files into local
```bash
python tools/video_scraper.py
```
