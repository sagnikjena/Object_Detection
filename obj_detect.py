# Restful API Script

from flask import Flask, request, redirect, render_template
from flask_caching import Cache
from flask_uploads import UploadSet, configure_uploads, ALL
import os
import shutil
import glob


cache = Cache(config={'CACHE_TYPE': 'null'})
app = Flask(__name__)
cache.init_app(app)
files = UploadSet('files', ALL)
app.config['UPLOADED_FILES_DEST'] = './static/uploaded_imgs'
configure_uploads(app, files)
OUTPUT_PATH = './static/result_imgs/detected'
roots_to_clear = [app.config['UPLOADED_FILES_DEST'], './static/result_imgs']


@app.route('/', methods=['GET', 'POST'])
def index():
    for root_to_clear in roots_to_clear:
        for root, dirs, files in os.walk(root_to_clear):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
    return render_template('home.html')


@app.route('/preview', methods=['GET', 'POST'])
def upload_and_preview():
    if request.method == 'POST' and 'media' in request.files:
        _ = files.save(request.files['media'])
        list_of_files = glob.glob(os.path.join(app.config['UPLOADED_FILES_DEST'], '*'))
        latest_file = max(list_of_files, key=os.path.getctime)
        global image_to_process
        image_to_process = latest_file
        img_to_render = os.path.join('..', latest_file)
        img_to_render = img_to_render.replace('\\', '/')
    else:
        img_to_render = '../static/images/no_image.png'
    paths = ['../static/images/no_image.png']

    return render_template('preview.html', img_name=img_to_render, img_paths=paths)


@app.route('/preview/detection', methods=['GET', 'POST'])
def obj_detect():

    if request.method == 'POST':
        from imageai.Detection import ObjectDetection
        model = ObjectDetection()
        model.setModelTypeAsRetinaNet()
        model.setModelPath("./model/resnet50_coco_best_v2.0.1.h5")
        model.loadModel()
        detections, paths = model.detectObjectsFromImage(input_image=image_to_process,
                                                         output_image_path=OUTPUT_PATH,
                                                         extract_detected_objects=True)
        img_to_render = os.path.join('..', image_to_process)
        img_to_render = img_to_render.replace('\\', '/')
        paths = [os.path.join('..', path) for path in paths]
        paths = [path.replace('\\', '/') for path in paths]
        for i, path in enumerate(paths):
            detections[i]['index'] = i
            detections[i]['path'] = path
        for detection in detections:
            detection['percentage_probability'] = round(detection['percentage_probability'], 2)
        return render_template('result.html', img_name=img_to_render, img_details=detections, num_obj=len(detections))


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == '__main__':
    # init()
    app.run()













