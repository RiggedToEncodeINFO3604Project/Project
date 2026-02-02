from flask import Blueprint, render_template, request, jsonify
import os
import google.genai as genai

ai_portal_views = Blueprint('ai_portal_views', __name__, template_folder='../templates')

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'AIzaSyBnUQz1Qr6VfVkCZLOn7XJTA02DY8vamow'))

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
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(user_message)
        ai_response = response.text
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500