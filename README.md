## TextToASL Translator
A Python Flask application that utilises prompt engineering technique on LLM to translate multilingual sentence to American Sign Language (ASL) simplified gloss and display the sign language video.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/YOUR_USERNAME/TextToASL_Translator_LLM.git
    ```
2. Navigate to the project directory:
    ```bash
    cd TextToASL_Translator_LLM
    ```
3. Create a virtual environment:
    ```bash
    python -m venv venv
    ```
4. Activate the virtual environment:
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
5. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Things to include in .env file
```
DB_NAME=
COLLECTION_NAME=
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxx
MONGODB_URI=mongodb+srv://<USERNAME>:<PASSWORD>@...
```

## Usage
1. Run the Flask application:
    ```bash
    python app.py
    ```
2. Open your web browser and go to `http://127.0.0.1:5000/` to access the application.

## To start scraping video files into local
```bash
python -m scripts.video_scraper
```

## Contributing
1. Fork the repository.
2. Create a new branch:
    ```bash
    git checkout -b feature-branch
    ```
3. Make your changes and commit them:
    ```bash
    git commit -m "Description of your changes"
    ```
4. Push to the branch:
    ```bash
    git push origin feature-branch
    ```
5. Open a pull request on GitHub.
