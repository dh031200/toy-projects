from io import BytesIO
import qrcode
import numpy as np
from flask import Flask, send_file

app = Flask(__name__)

def make_qr(link):
    qr_text = link
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2
    )
    qr.add_data(link)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    imgByteArr = BytesIO()
    qr_img.save(imgByteArr, format='png')
    imgByteArr.seek(0)
    return imgByteArr

@app.route('/qr/<msg>')
def send_qr(msg):
    return send_file(make_qr(msg), mimetype="image/png")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7313)
