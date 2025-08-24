# CSS styles for the application


def get_css_styles():
    return """
    <style>
                :root {
      color-scheme: light dark; /* Supports both light and dark modes */
    }
        .main-header {
            font-size: 2rem;
            font-weight: bold;
            color: light-dark(#333333, #7aeb34);
            text-align: center;
            margin-bottom: 1rem;
        }
        .metric-card {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin: 0.5rem 0;
        }
        .operation-button {
            width: 100%;
            margin: 0.25rem 0;
        }
        .stButton > button {
            width: 100%;
        }
    </style>
    """
