from flask import Flask, request, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Configuration
from io import BytesIO

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)


class File(db.Model):
    file_name = db.Column(db.String(300), primary_key=True)
    data = db.Column(db.LargeBinary)
    content_length = db.Column(db.String(300))


@app.route("/", methods=["GET"])
def hi():
    return jsonify({"check": "True"})


@app.route("/file", methods=["GET"])
def get_all_files():
    files = File.query.all()
    output = []
    for file in files:
        file_data = {}
        file_data["file_name"] = file.file_name
        output.append(file_data)
    return jsonify({"files": output})


@app.route("/file", methods=["POST"])
def upload():
    file = request.files["file"]
    file_data = File.query.filter_by(file_name=file.filename).first()
    if file_data:
        return jsonify({"success": "False"})

    new_file = File(file_name=file.filename, data=file.read())
    db.session.add(new_file)
    db.session.commit()
    return jsonify({"success": "True"})


@app.route("/download/<file_name>")
def download_file(file_name):
    file_data = File.query.filter_by(file_name=file_name).first()
    if not file_data:
        return jsonify({"success": "False"})
    return send_file(
        BytesIO(file_data.data), attachment_filename="open_me.png", as_attachment=True
    )


@app.route("/file/<file_name>", methods=["DELETE"])
def delete_file(file_name):
    file_data = File.query.filter_by(file_name=file_name).first()
    if not file_data:
        return jsonify({"success": "False"})
    db.session.query(File).filter_by(file_name=file_name).delete()
    db.session.commit()
    return jsonify({"success": "True"})


if __name__ == "__main__":
    app.run()
