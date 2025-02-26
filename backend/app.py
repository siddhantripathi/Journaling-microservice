from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/generate-journal', methods=['POST', 'OPTIONS'])
def generate_journal():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.json
    feeling = data.get('feeling')
    
    prompt = f"""
    User input: {feeling}.
    Your job is to write a journal entry that classifies how the user feels over the course of time(multiple emotions), eventually need to log in firebase.
    Keep it >150 words.
    """
    
    response = model.generate_content(prompt)
    return jsonify({'journal_entry': response.text})

if __name__ == '__main__':
    app.run(debug=True)