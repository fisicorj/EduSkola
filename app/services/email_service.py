import logging
from app.extensions import mail
from flask_mail import Message
from flask import current_app

# Configura logging
logger = logging.getLogger('email_logger')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)  # ou DEBUG para mais verboso

def enviar_email(destinatario, assunto, corpo_html):
    with current_app.app_context():
        msg = Message(assunto, recipients=[destinatario])
        msg.html = corpo_html 
        
        logger.info(f"Tentando enviar e-mail para: {destinatario}")
        logger.debug(f"Assunto: {assunto}")
        logger.debug(f"Corpo: {corpo_html}")

        try:
            mail.send(msg)
            logger.info(f"E-mail enviado com sucesso para: {destinatario}")
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail para {destinatario}: {e}", exc_info=True)
