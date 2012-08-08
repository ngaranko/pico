
import os
import shutil
import Image
from flask import Flask, render_template
from flaskext.mail import Mail, Message

app = Flask(__name__)

app.debug = True

app.config.from_object('settings')

mail=Mail(app)

directory = os.path.join(os.path.dirname(__file__), 'static')
directory_original = app.config.get('CARD_DIRECTORY')

@app.route("/", defaults={'pic': None})
@app.route("/f/<pic>")
def hello(pic):
    cache_pics()
    pics = sorted(os.listdir(directory))
    if len(pics) == 0:
        return "No pictures found"

    if pic is None or not pic in pics:
        pic = pics[0]

    index = pics.index(pic) + 1
    next_pic = pics[index]

    cached = cache_image(pic)

    return render_template('pic.html', **{'pic': pic,
                                          'next_pic': next_pic,
                                          'cached': cached
                                          })

@app.route("/send/<pic>")
def send_to_me(pic):
    return send(pic)

@app.route("/send_to_family/<pic>")
def send_to_family(pic):
    return send(pic, app.config.get('FAMILY'))

@app.route("/send_to_family_small/<pic>")
def send_to_family_small(pic):
    cached = cache_image(pic)
    if cached:
        return send_to_family('tmp/%s' % pic)
    return send_to_family(pic)

def send(pic, to=app.config.get('ME')):
    msg = Message(
        'Hello',
        sender=app.config.get('MAIL_USERNAME'),
        recipients=to)
    msg.body = "This is the email body"

    with app.open_resource(os.path.join(directory, pic)) as fp:
        msg.attach(pic, "image/jpg", fp.read())
    mail.send(msg)
    return '<script type="text/javascript">window.close();</script>'

def cache_image(pic):
    picfile = os.path.join(directory, pic)

    picfile_cached = '%s/tmp/%s' % (directory, pic)

    if not os.path.exists(picfile_cached):
        if os.path.exists(directory_original):
            shutil.copy('%s/%s' % (directory_original,
                                   pic),
                        '%s/%s' % (directory,
                                   pic))
            print 'Copied %s' % pic

        im = Image.open(picfile)

        im5 = im.resize((2048, 1364), Image.ANTIALIAS)
        im5.save(picfile_cached)
        return True

    return True

def cache_pics():
    if os.path.exists(directory_original):
        for fi in os.listdir(directory_original):
            cache_image(fi)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
