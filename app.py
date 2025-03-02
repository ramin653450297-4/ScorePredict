from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
import requests
from fastapi import FastAPI

app = FastAPI()

# ใส่ค่าที่ได้จาก LINE Developers
LINE_CHANNEL_ACCESS_TOKEN = "erX0p/vwazO5SRAxfZDJXWLUTGPXnMT657H+a7o3rarIXacwAp3U/767CDyDoBd7D5wVza6rFzgru6VRqT6pH0oZ1GdVPP1ZvpTGYp4kK1bE0gfm2Zcm9R4Y+4o0GY78vvwCFFL7lyH1ePW5xFZUVwdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "4695a6e8320bb25a86cb76e84c42133c"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# เก็บข้อมูลผู้ใช้
user_data = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK", 200

# ฟังก์ชันสร้าง Quick Reply
def quick_reply_options(choices, question):
    quick_reply_buttons = [QuickReplyButton(action=MessageAction(label=choice, text=choice)) for choice in choices]
    return TextSendMessage(text=question, quick_reply=QuickReply(items=quick_reply_buttons))

# ฟังก์ชันรับข้อความจาก LINE
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip().lower()

    if user_text == "ทำนายผล":
        user_data[user_id] = {}
        line_bot_api.reply_message(event.reply_token, quick_reply_options(["male", "female"], "📌 เพศของคุณคืออะไร?"))
        return

    user_info = user_data.get(user_id, {})

    if "gender" not in user_info:
        user_info["gender"] = user_text
        line_bot_api.reply_message(event.reply_token, quick_reply_options(["group A", "group B", "group C", "group D", "group E"], "📌 เชื้อชาติของคุณคืออะไร?"))
        return

    if "race_ethnicity" not in user_info:
        user_info["race_ethnicity"] = user_text
        line_bot_api.reply_message(event.reply_token, quick_reply_options(["bachelor's degree", "some college", "master's degree", "associate's degree", "some high school", "high school"], "📌 ระดับการศึกษาของผู้ปกครองคืออะไร?"))
        return

    if "parental_level_of_education" not in user_info:
        user_info["parental_level_of_education"] = user_text
        line_bot_api.reply_message(event.reply_token, quick_reply_options(["standard", "free/reduced"], "📌 ประเภทอาหารกลางวันของคุณคืออะไร?"))
        return

    if "lunch" not in user_info:
        user_info["lunch"] = user_text
        line_bot_api.reply_message(event.reply_token, quick_reply_options(["none", "completed"], "📌 เคยเข้าอบรมเตรียมสอบหรือไม่?"))
        return

    if "test_preparation_course" not in user_info:
        user_info["test_preparation_course"] = user_text
        prediction_result = predict_student_performance(user_info)

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"📊 ผลการทำนายของคุณ: {prediction_result}"))

        del user_data[user_id]
        return

# ฟังก์ชันเรียก API ทำนายผล
def predict_student_performance(user_info):
    try:
        response = requests.post("https://muffynxx.pythonanywhere.com/predict", json=user_info)
        result = response.json()
        return result.get("prediction", "ไม่สามารถทำนายได้")
    except:
        return "เกิดข้อผิดพลาดในการเชื่อมต่อ API"

if __name__ == "__main__":
    app.run(port=5000)
