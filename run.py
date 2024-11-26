from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)  # Using port 5001 to avoid conflict with video service 