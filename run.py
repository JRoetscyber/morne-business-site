"""
Entry point — run with:
    python run.py
or via Flask CLI:
    flask --app run run --debug
"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
    )
