import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from package import mail


def save_picture(form_picture, resize, dest):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, f'static/{dest}', picture_fn)
    i = Image.open(form_picture)
    if resize != 'no':
        output_size = resize
        i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn, i.width, i.height



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, then ignore this message
'''
    mail.send(msg)
