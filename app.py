from fastapi import FastAPI, Request
import smtplib
from email.mime.text import MIMEText
import requests

app = FastAPI()

# CONFIG
EMAIL_SENDER = "sendermail199920@gmail.com"
EMAIL_PASSWORD = "jqdt lieu vtbj dldu"
EMAIL_RECEIVER = "charly59000@orange.fr"

def send_mail(subject, msg):
    message = MIMEText(msg)
    message["Subject"] = subject
    message["From"] = EMAIL_SENDER
    message["To"] = EMAIL_RECEIVER

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(message)
    server.quit()

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    signal = data.get("signal", "")

    if signal == "BUY_CONFIRM":
        msg = "🟡 Confirmation BUY BTC M15"
        send_mail("BTC BUY", msg)   

    elif signal == "SELL_CONFIRM":
        msg = "🟡 Confirmation SELL BTC M15"
        send_mail("BTC SELL", msg)

    elif signal == "BUY_DANGER":
        msg = "🔴 Danger BUY BTC"
        send_mail("BTC DANGER", msg)

    elif signal == "SELL_DANGER":
        msg = "🔴 Danger SELL BTC"
        send_mail("BTC DANGER", msg)

    return {"status": "ok"}
