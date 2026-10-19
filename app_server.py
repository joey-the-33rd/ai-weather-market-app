from app import app
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
