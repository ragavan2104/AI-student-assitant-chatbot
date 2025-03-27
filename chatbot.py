from flask import Flask, request, jsonify, render_template, Response
from openai import OpenAI  # Updated import
import PyPDF2
from googletrans import Translator
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)  # Updated initialization

# Initialize translator
translator = Translator()

# Initialize Flask app
app = Flask(__name__)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

# Global variable to store PDF text
pdf_text = ""

# Path to the PDF file
pdf_file_path = "Excel.pdf"
pdf_text = extract_text_from_pdf(pdf_file_path)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Chat route
@app.route('/chat', methods=['POST'])
def chat():
    global pdf_text
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"response": "Please enter a valid question."})

    try:
        prompt = f"""
        You are a helpful assistant providing information about Excel engineering colleges in Tamil Nadu, India.
        The following is the content of a PDF about colleges in Tamil Nadu:
        
        {pdf_text}
        
        Answer the following question based on the content above: {user_input}
        
        """

        # Updated OpenAI API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Excel Engineering College."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        # Updated response access
        response_content = response.choices[0].message.content.strip()

        # Clean the response
        cleaned_response = clean_response(response_content)

        try:
            # Translate the response and extract the text
            translated_response = translator.translate(cleaned_response, dest='ta').text  # 'ta' for Tamil
        except Exception as e:
            print(f"Translation error: {e}")
            translated_response = cleaned_response

        return jsonify({"response": cleaned_response, "translated_response": translated_response})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

# Function to clean the response
def clean_response(response):
    unwanted_phrases = [
        "There are a total of",
        "listed in the provided PDF content",
        ""
    ]
    for phrase in unwanted_phrases:
        response = response.replace(phrase, "")

    response = " ".join(response.split())
    
    return response

# File upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    global pdf_text
    if 'file' not in request.files:
        return jsonify({"response": "No file part"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"response": "No selected file"})
    
    if file and file.filename.endswith('.pdf'):
        pdf_text = extract_text_from_pdf(file)
    else:
        return jsonify({"response": "Unsupported file type"})
    
    return jsonify({"response": "File uploaded and text extracted successfully"})

# Speech-to-text route
@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the file temporarily
        file_path = "temp_audio.wav"
        file.save(file_path)

        # Transcribe the audio using OpenAI Whisper (updated API call)
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        os.remove(file_path)  # Clean up the temporary file

        return jsonify({"text": transcript.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Text-to-speech route
@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Generate speech using OpenAI TTS (updated API call)
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )

        return Response(response.content, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)