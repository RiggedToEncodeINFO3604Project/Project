from flask import Blueprint, render_template, request, jsonify
import os
import asyncio
from App.rag_chatbot.gemini_client import chat

ai_portal_views = Blueprint('ai_portal_views', __name__, template_folder='../templates')


@ai_portal_views.route('/ai-portal', methods=['GET'])
def ai_portal():
    return render_template('ai_portal.html')


@ai_portal_views.route('/ai-portal/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Run the async RAG chat function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(chat([], user_message))
            ai_response = result.answer
            return jsonify({'response': ai_response})
        finally:
            loop.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
