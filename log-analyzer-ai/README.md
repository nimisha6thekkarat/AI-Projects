Setup Instructions
------------------

1. Set Up the Environment

Create a virtual environment and install dependencies:

On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows:
```bash
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

3. Create a `.env` File

Inside the project directory, create a `.env` file with the following content:

    ZYTE_API_KEY=your_zyte_key
    PROJECT_ID=your_project_id
    OPENAI_API_KEY=your_openai_key
    SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

4. Run the App

    streamlit run streamlit_app.py

Then open your browser at: http://localhost:8501