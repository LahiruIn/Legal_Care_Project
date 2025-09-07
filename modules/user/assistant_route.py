from flask import Blueprint, request, jsonify, render_template, session, flash
from flask_mysqldb import MySQL
from .main import get_answer
from .translate import detect_language, translate_to_english, translate_from_english  
import logging

assistant_bp = Blueprint(
    "assistant_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/user_static",
)

chat_history = []


mysql = None

def init_mysql(app, mysql_instance):
    global mysql
    mysql = mysql_instance


def save_chat_to_db(user_id, role, content):
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO chat_history (user_id, role, content) VALUES (%s, %s, %s)",
            (user_id, role, content),
        )
        mysql.connection.commit()
    except Exception as e:
        flash(f"Error saving chat: {str(e)}", "error")


def fetch_chat_history(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT role, content FROM chat_history WHERE user_id = %s ORDER BY created_at ASC", (user_id,))
        rows = cur.fetchall()
        chat_history = [{"role": row[0], "content": row[1]} for row in rows]
        return chat_history
    except Exception as e:
        flash(f"Error fetching chat history: {str(e)}", "error")
        return []

@assistant_bp.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    user_input = data.get("question", "")
    user_id = session.get("user_id")

    if not user_input:
        return jsonify({"answer": "⚠️ No question provided."})

    # Detect  language
    user_lang = detect_language(user_input)

    # If the language is not English, translate the question to English
    if user_lang != "en":
        translated_question = translate_to_english(user_input)
    else:
        translated_question = user_input

    # Add the user input to the chat history
    chat_history.append({"role": "user", "content": user_input})

    try:
        # Get AI response based on the user input and chat history
        response, context = get_answer(translated_question, chat_history)

        # If the user's language is not English, translate the response to their language
        if user_lang != "en":
            translated_response = translate_from_english(response, user_lang)
        else:
            translated_response = response

        # Add assistant response to the chat history
        chat_history.append({"role": "assistant", "content": translated_response})

        # Save both user and assistant chats to the database
        save_chat_to_db(user_id, "user", user_input)
        save_chat_to_db(user_id, "assistant", translated_response)

    except Exception as e:
        response = f"⚠️ Error generating response: {str(e)}"
        chat_history.append({"role": "assistant", "content": response})

    # Return the AI response and chat history in JSON format
    return jsonify({"answer": translated_response, "chat_history": chat_history, "context": context})

@assistant_bp.route("/start_new_chat", methods=["POST"])
def start_new_chat():
    global chat_history
    chat_history = []  # Clear current chat history to start fresh
    return jsonify({"message": "New chat started!"})

@assistant_bp.route("/get_chat_history", methods=["GET"])
def get_chat_history():
    user_id = session.get("user_id")
    if user_id:
        # Fetch chat history from the database
        history = fetch_chat_history(user_id)
        return jsonify({"chat_history": history})
    else:
        return jsonify({"message": "User not logged in."})

@assistant_bp.route("/download_chat", methods=["GET"])
def download_chat():
    user_id = session.get("user_id")
    if user_id:
        # Fetch chat history from the database
        history = fetch_chat_history(user_id)
        
        # Format chat history into a downloadable text
        chat_text = ""
        for chat in history:
            chat_text += f"{chat['role'].capitalize()}: {chat['content']}\n\n"
        
        # Create a response to download the file
        response = jsonify({"message": "Download initiated."})
        response.headers["Content-Disposition"] = "attachment; filename=chat_history.txt"
        response.headers["Content-Type"] = "text/plain"
        response.data = chat_text
        
        return response
    else:
        return jsonify({"message": "User not logged in."})

@assistant_bp.route("/")
def index():
    # Render the initial page for the AI assistant
    return render_template("index.html", chat_history=chat_history)

