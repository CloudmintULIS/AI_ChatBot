from flask import Flask, render_template, request, jsonify
from models import db, Message
from openai import OpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat_history.db"
db.init_app(app)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chat_history = [{"role": "system", "content": "Bạn là trợ lý AI thân thiện, trả lời ngắn gọn"}]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():
    user_message = request.json["message"]
    chat_history.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=chat_history,
            temperature=0.7,
            max_tokens=200
        )
        bot_reply = response.choices[0].message.content
    except:
        bot_reply = "Xin lỗi, tôi gặp lỗi."

    chat_history.append({"role": "assistant", "content": bot_reply})

    # Lưu vào CSDL
    new_msg = Message(user_message=user_message, ai_response=bot_reply)
    db.session.add(new_msg)
    db.session.commit()

    return jsonify({"reply": bot_reply})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

