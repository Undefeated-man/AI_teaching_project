from werkzeug.utils import secure_filename
import os
import speech2text as s2t
from time import sleep

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload'
#ALLOWED_EXTENSIONS = set(['wav', 'm4a', 'pcm', 'amr'])

taskId = ""

# upload file
@app.route('/upload', methods=['GET', "POST"])
def upload_file():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
   if request.method == 'POST':
      if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])
      f = request.files['file']
      # f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
      #print("test"+secure_filename(f.filename).split(".")[-1])
      f.save(os.path.join(app.config['UPLOAD_FOLDER'],"test.m4a"))
   return render_template('wait.html')

# return file
@app.route("/flask_file", methods=['GET'])
def flask_file():
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"upload")
    filename = [i for i in os.listdir(filepath) if "m4a" in i][0]
    file = os.path.join(filepath, filename)

    return send_file(file)

# redirect
@app.route("/wait", methods = ['GET'])
def redirect_page():
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"upload")
    filename = [i for i in os.listdir(filepath) if "m4a" in i][0]
    filetype = filename.split(".")[-1]
    global taskId
    taskId = str(s2t.post_speech(pth = "http://47.107.34.101:5000/flask_file", filetype = filetype)).split('"')[-2]
    while(1):
        result = str(s2t.get_result(taskId)).encode("utf-8")
        if "Running" in str(result):
            break
        else:
            sleep(10)

    return redirect("http://47.107.34.101:5000/result")

# return the result
@app.route("/result", methods=['GET'])
def result_return():
    result = s2t.get_result(taskId)

    return render_template("result.html", result = result)



if __name__ == '__main__':
   app.run(port=6666, debug=True)