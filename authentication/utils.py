from django.core.mail import EmailMessage

class Util:

    @staticmethod
    def send_email(data):
        email_body = data.get('body')
        to = data.get('to')
        subject = data.get('subject')

        email = EmailMessage(
            to=[to,],
            subject=subject,
            body=email_body
        )
        email.send()
