import base64
from typing import List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Disposition,
    Email,
    Personalization,
)
from src.shared.models.sendgrid_attachment_model import AttachmentModel

class SendgridService:
    def __init__(self, sendgrid_key: str, from_email:str):
        self._sendgrid_key = sendgrid_key
        self._from_email = from_email

    def send_email(self, to_emails: list, subject: str, html_content: str, attachments: List[AttachmentModel]) -> tuple:
        message = Mail(
            from_email=self._from_email,
            # to_emails=to_emails,
            subject=subject,
            html_content=html_content,
        )
        cc_email = self._from_email
        p = Personalization()
        if type(to_emails) == list:
            for email in to_emails:
                p.add_to(Email(email))
        else:
            p.add_to(Email(to_emails))
        
        p.add_cc(Email(cc_email))

        try:
            list_sendgrid_attachment = []
            for attachment in attachments:
                list_sendgrid_attachment.append(self.get_attachment(attachment))
            message.attachment = list_sendgrid_attachment
            message.add_personalization(p)
            sg = SendGridAPIClient(self._sendgrid_key)
            response = sg.send(message)
            return response.status_code, response.body, response.headers
        except Exception as e:
            err_message = f"Erro ao enviar email de:{self._from_email}, para: {to_emails}, assunto: {subject}, conteudo: {html_content}"
            print(e)
            return 400, err_message, {}
    
    def get_attachment(self, attachment_model: AttachmentModel) -> Attachment:
        with open(attachment_model.file_path, 'rb') as f:
            data = f.read()
            f.close()
        encoded_file = base64.b64encode(data).decode()

        attachedFile = Attachment(
            FileContent(encoded_file),
            FileName(attachment_model.file_name),
            FileType(attachment_model.file_type),
            Disposition('attachment')
        )
        return attachedFile