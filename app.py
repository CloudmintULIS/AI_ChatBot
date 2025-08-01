from flask import Flask, render_template, request, jsonify
from models import db, Message
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat_history.db"
db.init_app(app)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

today = datetime.now().strftime("%d/%m/%Y")
chat_history = [
    {
        "role": "system",
        "content": (
            f"Hôm nay là {today}. Bạn là trợ lý AI thân thiện, trả lời ngắn gọn, súc tích, dễ hiểu. "
            "Nếu người dùng yêu cầu mở YouTube (ví dụ: 'Mở YouTube bài Hãy trao cho anh'), "
            "hãy trả về đúng JSON như sau: "
            '{"action": "open_youtube", "query": "Hãy trao cho anh"}'
        )
    }
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():
    user_message = request.json["message"]
    chat_history.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=chat_history,
            temperature=0.7,
            max_tokens=200
        )
        bot_reply = response.choices[0].message.content
    except Exception as e:
        print("❌ Lỗi OpenAI:", e)
        bot_reply = "Xin lỗi, tôi gặp lỗi khi xử lý."

    chat_history.append({"role": "assistant", "content": bot_reply})

    # ❌ Tạm thời không ghi DB để tránh lỗi SQLite
    # new_msg = Message(user_message=user_message, ai_response=bot_reply)
    # db.session.add(new_msg)
    # db.session.commit()

    # ✅ Nếu GPT trả về JSON (ví dụ: { "action": "open_youtube", ... }) thì gửi lại nguyên dạng
    try:
        parsed = json.loads(bot_reply)
        if isinstance(parsed, dict) and "action" in parsed:
            return jsonify(parsed)
    except:
        pass

    return jsonify({"reply": bot_reply})

@app.route("/history")
def history():
    messages = Message.query.all()
    return render_template("history.html", messages=messages)

@app.route("/ping")
def ping():
    return "OK"

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
