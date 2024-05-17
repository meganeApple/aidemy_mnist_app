import os
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image

import numpy as np


classes = ["0","1","2","3","4","5","6","7","8","9"]
image_size = 28

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    # 条件'.' in filenameは、変数filenameの中に.という文字が存在するかどうか
    # 条件filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONSは、
    # 変数filenameの.より後ろの文字列がALLOWED_EXTENSIONSのどれかに該当するかどうか
    # rsplit()は基本的には split()と同じ

model = load_model('./model.h5')#学習済みモデルをロード


@app.route('/', methods=['GET', 'POST']) # GETやPOSTはHTTPメソッドの一種
def upload_file():
    if request.method == 'POST': # requestはウェブ上のフォームから送信したデータを扱うための関数
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            #受け取った画像を読み込み、np形式に変換
            # img = image.load_img(filepath, grayscale=True, target_size=(image_size,image_size))
            # grayscaleに対応していないKerasのバージョンのため、一部修正↓
            img = image.load_img(filepath, color_mode='grayscale', target_size=(image_size, image_size))
            img = image.img_to_array(img)
            data = np.array([img])
            #変換したデータをモデルに渡して予測する
            result = model.predict(data)[0]
            predicted = result.argmax()
            pred_answer = "これは " + classes[predicted] + " です"

            return render_template("index.html",answer=pred_answer)
            # render_templateの引数にanswer=pred_answerと渡すことで、
            # index.htmlに書いたanswerにpred_answerを代入することができる

    return render_template("index.html",answer="")
    # POSTリクエストがなされないとき（単にURLにアクセスしたとき）には
    # index.htmlのanswerには何も表示しない


# if __name__ == "__main__":
#     app.run()
#     # 最後にapp.run()が実行され、サーバが立ち上がる

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)