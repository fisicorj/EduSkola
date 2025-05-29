from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.mailersend.net',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='MS_3DEtSk@test-69oxl5ev8kzl785k.mlsender.net',
    MAIL_PASSWORD='mssp.HQrBq9L.jpzkmgq0dwm4059v.JjNQmNC',
    MAIL_DEFAULT_SENDER='skola@test-69oxl5ev8kzl785k.mlsender.net'
)

mail = Mail(app)

with app.app_context():
    msg = Message('Test', recipients=['fisicorj@gmail.com'])
    msg.body = 'Este é um teste'
    mail.send(msg)

