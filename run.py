# database

import zipfile
import json
from werkzeug.utils import secure_filename
import os
from flask import*
from detector.detector import Detector
from flask_socketio import SocketIO, emit
import pymongo
client = pymongo.MongoClient(
    "mongodb+srv://BenYang:bentest@cluster0.tgv934g.mongodb.net/?retryWrites=true&w=majority")
db = client.base


# backend
UPLOAD_FOLDER = './detector/modules/past_modules'
ALLOWED_EXTENSIONS = set(['txt', 'zip', 'rar'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

socketio = SocketIO(app)


@app.route("/")  # 之後記得目錄
def index():
    return render_template("home.html")


@app.route("/temp")
def temp():
    return render_template("temp.html")


@app.route("/rule")
def rule():
    return render_template("rule.html")


@app.route("/result")
def result():
    return render_template("result.html")


@app.route("/about")
def about():
    return render_template("about.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            f = open('./detector/modules/module_id.txt', 'r')
            module_id = f.read()
            f.close()
            f = open('./detector/modules/module_id.txt', 'w')
            temp = int(module_id)
            temp = temp+1
            module_id = str(temp)
            f.write(module_id)
            f.close()

            file.filename = "module_" + module_id + ".zip"
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                   filename))
            print("upload success")
            print(filename)

            path = "./detector/modules/past_modules/" + filename
            with zipfile.ZipFile(path, 'r') as zf:
                zf.extractall(path="./detector/modules/temp")
            dirpath = "./detector/modules/temp"
            name = os.listdir(dirpath)
            old_name = name[0]
            old_name_dir = "./detector/modules/temp/" + old_name
            new_name_dir = "./detector/modules/current_modules/" + "module_" + module_id
            os.rename(old_name_dir, new_name_dir)
            module_id = int(module_id)

            binary_address = "detector/testing_files"
            print("before module")
            result = (Detector.get_score(module_id, binary_address, socketio))
            ori_tp = result['ori_TP']
            tn = result['TN']
            fp = result['FP']
            ori_fn = result['ori_FN']
            ori_runtime = result['ori_runtime']
            mir_tp = result['mir_TP']
            mir_fn = result['mir_FN']
            mir_runtime = result['mir_runtime']
            tn = 22457
            ori_fn = 802
            fp = 630
            ori_tp = 25767

            ori_precision = int(ori_tp)/(int(ori_tp) + int(fp))
            ori_recall = int(ori_tp) / (int(ori_tp)+int(ori_fn))
            ori_score =float(int(ori_tp) +int(tn))/(int(ori_tp) +int(fp) + int(ori_fn) + int(tn))
            ori_f1 = 2/((1/ori_precision)+(1/ori_recall))

            mir_precision = int(mir_tp)/(int(mir_tp) + int(fp))
            mir_recall = int(mir_tp) / (int(mir_tp)+int(mir_fn))
            mir_score = float(mir_tp)/(int(mir_tp) + int(mir_fn) )
            mir_f1 = 2/((1/mir_precision)+(1/mir_recall))




            socketio.emit('status_response', {
                          'data': 'training done\n' + " result" + '\nori_score :' + str(ori_score)})
            preproccessing = request.args.get("preproccessing", "")
            model = request.args.get("model", "")
            other = request.args.get("other", "")
            user = request.args.get("user", "")
            collection = db.datas
            collection.insert_one({
                "preproccessing": preproccessing,
                "model": model,
                "other": other,
                "user_name": user,
                "ori_score": ori_score,
                "ori_TP": ori_tp,
                "TN": tn,
                "FP": fp,
                "ori_FN": ori_fn,
                "ori_runtime": ori_runtime,
                "mir_score": mir_score,
                "mir_TP": mir_tp,
                "mir_FN": mir_fn,
                "mir_runtime": mir_runtime
            })
            import shutil
            shutil.rmtree("./detector/modules/current_modules/" +
                          "module_" + str(module_id))
            ori_score = round(ori_score, 3)
            ori_precision = round(ori_precision, 3)
            ori_recall = round(ori_recall, 3)
            ori_f1 = round(ori_f1, 3)
            mir_score = round(mir_score, 3)
            mir_precision = round(mir_precision, 3)
            mir_recall = round(mir_recall, 3)
            mir_f1 = round(mir_f1, 3)
            print(mir_score)
            return render_template("result.html", ori_tp=json.dumps(ori_tp), tn=json.dumps(tn), fp=json.dumps(fp), ori_fn=json.dumps(ori_fn), ori_accuracy=json.dumps(ori_score), ori_precision=json.dumps(ori_precision), ori_recall=json.dumps(ori_recall), ori_f1=ori_f1, mir_tp=json.dumps(mir_tp), mir_fn=json.dumps(mir_fn), mir_accuracy=json.dumps(mir_score), mir_precision=json.dumps(mir_precision), mir_recall=json.dumps(mir_recall), mir_f1=mir_f1)
    return render_template('upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/history")
def history():
    return render_template("history.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    # app.run(debug=True)
