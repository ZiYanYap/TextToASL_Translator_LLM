# **TextToASL Translator**
A Python Flask application that utilizes **prompt engineering techniques on LLM** to translate multilingual text into **American Sign Language (ASL) simplified gloss** and display the corresponding sign language video.

This project leverages **Large Language Models (LLMs) for Named Entity Recognition (NER) and Word Sense Disambiguation (WSD)** to enhance translation accuracy.

---

## **Features**
✅ Translate multilingual sentences into ASL simplified gloss  
✅ Uses **LLM for NER and WSD** to improve translation accuracy  
✅ Displays **sign language videos** based on the translated gloss  
✅ Supports **video file scraping** for additional sign language datasets  

---

## **Installation**

### **1. Clone the Repository**
```bash
git clone https://github.com/ZiYanYap/TextToASL_Translator_LLM.git
cd TextToASL_Translator_LLM
```

### **2. Set Up a Virtual Environment**
```bash
python -m venv venv
```

#### **Activate the Virtual Environment**
- **Windows:**  
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux:**  
  ```bash
  source venv/bin/activate
  ```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

---

## **Configuration: `.env` File**
Create a `.env` file in the root directory and populate it with the following variables:
```env
DB_NAME=            # Name of the MongoDB database  
COLLECTION_NAME=    # Name of the collection within the database  
HUGGINGFACE_TOKEN=  # Your Hugging Face API token for LLM processing  
MONGODB_URI=        # Connection string for MongoDB  
```

---

## **Usage**

### **Run the Flask Application**
```bash
python app.py
```
Then, open a browser and go to:  
👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**  

### **Scrape Video Files for Local Use**
```bash
python -m scripts.video_scraper
```

---

## **Demo**
Check out this video:  
📺 **[YouTube Demo](https://youtu.be/uFBhRvmEjwM)**  

---

## **Contributing**
We welcome contributions! 🚀 If you’d like to improve this project, feel free to: <br />
✅ **Enhance translation accuracy** by refining the prompt engineering <br />
✅ **Expand language support** for more diverse sentence structures <br />
✅ **Improve the UI/UX** for a better user experience <br />
✅ **Optimize performance** and scalability <br />

### **Steps to Contribute**
1. **Fork the repository**
2. **Create a new branch:**
   ```bash
   git checkout -b feature-branch
   ```
3. **Make your changes and commit:**
   ```bash
   git commit -m "Added new feature X"
   ```
4. **Push your changes:**
   ```bash
   git push origin feature-branch
   ```
5. **Submit a Pull Request on GitHub!**

👉 Have suggestions or feedback? Feel free to open an issue!  

---

## **Acknowledgments**
This project is built using:
- **Flask** for the web framework  
- **Hugging Face Transformers** for LLM processing  
- **MongoDB** for data storage  
