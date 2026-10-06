#!/usr/bin/env python3
"""CatVision - Flask Application
Whisker Labs AI/ML Security CTF Challenge
"""
import os
import uuid
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from werkzeug.utils import secure_filename
import model

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload
UPLOAD_FOLDER = Path("uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
CHALLENGE_FILES_FOLDER = Path("challenge_files")

# Ensure directories exist
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Get flag from environment variable
FLAG = os.getenv(
    "CTF_FLAG",
    "NOVA{cats_can_be_adversarial}"
)

def allowed_file(filename):
    """Check if file extension is allowed."""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    """Main route - display upload form and handle image classification."""
    if request.method == "POST":
        # Check if file was uploaded
        if "image" not in request.files:
            flash("No file selected", "error")
            return render_template("index.html", result=None)
        
        file = request.files["image"]
        # Check if filename is empty
        if file.filename == "":
            flash("No file selected", "error")
            return render_template("index.html", result=None)
        
        # Validate file
        if not allowed_file(file.filename):
            flash("Invalid file type. Only PNG, JPG, JPEG, and WEBP are allowed.", "error")
            return render_template("index.html", result=None)
        
        # Generate unique filename to avoid path traversal and collisions
        file_ext = file.filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = UPLOAD_FOLDER / unique_filename
        
        try:
            # Save file
            file.save(str(file_path))
            
            # Perform prediction
            prediction_result = model.predict(str(file_path))
            
            # Delete uploaded file after prediction if possible
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass  # Best effort cleanup
            
            # Check if backdoor was triggered
            if prediction_result["class"] == "administrator_cat":
                # Reveal flag
                return render_template(
                    "index.html",
                    result=prediction_result,
                    flag=FLAG,
                    triggered=True
                )
            else:
                return render_template(
                    "index.html",
                    result=prediction_result,
                    triggered=False
                )
        
        except Exception as e:
            # Clean up file on error
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass
            
            # Return friendly error message without exposing stack trace
            flash("Error processing image. Please ensure the image is valid and not corrupt.", "error")
            return render_template("index.html", result=None)
    
    return render_template("index.html", result=None)

@app.route("/artifact")
def download_artifact():
    """Securely serve the model artifact."""
    try:
        return send_from_directory(
            str(CHALLENGE_FILES_FOLDER),
            "catvision_model.json",
            as_attachment=True
        )
    except FileNotFoundError:
        abort(404)
    except Exception:
        abort(404)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False
    )
