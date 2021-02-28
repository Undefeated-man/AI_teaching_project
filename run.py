from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import speech2text as s2t
from time import sleep

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload/'

# upload file
@app.route('/upload')
def upload_file():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
   if request.method == 'POST':
      f = request.files['file']
      # f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
      f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename("test"+f.filename.split(".")[-1])))
      return render_template('wait.html')

# return file
@app.route("/flask_file")
def flask_file():
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"upload")
    filename = os.listdir(os.getcwd())[0]
    file = os.path.join(filepath, filename)
    
    return send_file(file)

# redirect
@app.route("/wait", methods = ['GET'])
def redirect():
    filename = os.listdir(os.getcwd())[0]
    filetype = filename.split(".")[-1]
    global taskId = str(s2t.post_speech(pth = "http://47.107.34.101:6666/file", filetype = filetype)).split('"')[-2]
    while(1):
        result = get_result(taskId)
        if result["msg"][0]["task_status"] != "Running":
            break
        else:
            sleep(10)
            
    return redirect("/result")

# return the result
@app.route("/result")
def result_return():
    result = get_result(taskId)
    
    return render_template("result.html", result = result)


if __name__ == '__main__':
   app.run(port=6666, debug=True)