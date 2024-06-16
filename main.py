import os
from flask import Flask, render_template, request, flash,send_file
from werkzeug.utils import secure_filename
import cv2
from fpdf import FPDF

ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def image_to_pdf(image_path, pdf_filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.image(image_path, 0, 0, 210, 297)  # A4 size: 210x297 mm
    pdf.output(os.path.join(app.config['STATIC_FOLDER'], pdf_filename))

def processImage(filename, operation):
    print(f"Operation is {operation} and filename is {filename}")
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Unable to read image {filename}")
        return None

    base_filename = filename.rsplit('.', 1)[0]
    new_filename = None

    try:
        match operation:
            case "cgray":
                img_processed = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                new_filename = f"{base_filename}_gray.png"
            case "cwebp":
                new_filename = f"{base_filename}.webp"
                img_processed = image
            case "cjpg":
                new_filename = f"{base_filename}.jpg"
                img_processed = image
            case "cpng":
                new_filename = f"{base_filename}.png"
                img_processed = image
            case "cpdf":
                new_filename = f"{base_filename}.pdf"
                # Convert image to PDF
                image_to_pdf(image_path, new_filename)
            case _:
                print(f"Invalid operation: {operation}")
        
        if new_filename:
            new_image_path = os.path.join(app.config['STATIC_FOLDER'], new_filename)
            if operation != "cpdf":
                cv2.imwrite(new_image_path, img_processed)
        
        return new_filename

    except Exception as e:
        print(f"Error processing image: {e}")
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return render_template("index.html")

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return render_template("index.html")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_filename = processImage(filename, operation)
            
        if new_filename:
                if operation == "cpdf":
                    return send_file(os.path.join(app.config['STATIC_FOLDER'], new_filename), as_attachment=True)
                else:
                    flash(f"Your image has been processed and is available <a href='/static/{new_filename}' target='_blank'>here</a>")
        else:
                flash("Error processing image")

        return render_template("index.html")

    return render_template("index.html")

#if __name__ == "__main__":
    #app.run(debug=True, port=5001)
