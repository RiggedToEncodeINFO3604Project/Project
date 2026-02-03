from flask import Blueprint, render_template, request, jsonify
import os
from google import genai

ai_portal_views = Blueprint('ai_portal_views', __name__, template_folder='../templates')

# Configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")
client = genai.Client(api_key=api_key)

@ai_portal_views.route('/ai-portal', methods=['GET'])
def ai_portal():
    return render_template('ai_portal.html')

@ai_portal_views.route('/ai-portal/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        response = client.models.generate_content(
            model='gemma-3-27b-it',
            contents=user_message
        )
        ai_response = response.text
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500