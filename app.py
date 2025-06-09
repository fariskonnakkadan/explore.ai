import os
import google.generativeai as genai
from flask import Flask, render_template, request, url_for
import markdown2

app = Flask(__name__)

# --- Configure your Google Gemini API Key ---
# It's recommended to set this as an environment variable for security.
# In your terminal: export GEMINI_API_KEY="YOUR_API_KEY"
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# if not GEMINI_API_KEY:
#     raise ValueError("No GEMINI_API_KEY set for Flask application")

genai.configure(api_key=GEMINI_API_KEY)

# Create the Gemini model instance using a valid model name
model = genai.GenerativeModel('gemini-1.5-flash-latest')

@app.route('/')
def index():
    """Renders the landing page with the search box."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def handle_search():
    """
    Handles the search form submission.
    Fetches related topics from Gemini and displays them.
    This function is stateless and does not use global variables.
    """
    topic = request.form.get('topic')
    if not topic:
        return render_template('index.html', error="Please provide a topic.")

    try:
        # Prompt for Gemini to generate 100 related topics
        prompt = f"List out 100 topics related to '{topic}'. The topics should be concise and in a numbered list."
        response = model.generate_content(prompt)
        
        # Process the response to get a list of topics
        related_topics = response.text.strip().split('\n')
        # Clean up the list to remove numbering, asterisks, and extra spaces
        related_topics = [
            item.split('. ', 1)[-1].strip() for item in related_topics if '. ' in item
        ]

        return render_template('results.html', topic=topic, related_topics=related_topics)

    except Exception as e:
        # Handle potential API errors
        return render_template('index.html', error=f"An error occurred: {e}")

@app.route('/topic/<topic_name>')
def get_topic_explanation(topic_name):
    """
    Fetches a detailed explanation for a selected topic from Gemini.
    The original search context is passed as a URL query parameter.
    """
    # Get the original search context from the URL query parameter
    original_search = request.args.get('context', '')

    try:
        # Create a more contextual prompt
        if original_search:
            prompt = (
                f"Explain '{topic_name}' in the context of '{original_search}' using a top-down and bottom-up approach. "
                f"Start with a high-level overview: what it is and why it's important. "
                f"Then break down its key components, how it works, and any relevant technical details. "
                f"Format the response in Markdown."
            )
        else:
            prompt = (
                f"Explain '{topic_name}' using a top-down and bottom-up approach. "
                f"Start with a high-level overview: what it is and why it's important. "
                f"Then break down its key components, how it works, and any relevant technical details. "
                f"Format the response in Markdown."
            )

        response = model.generate_content(prompt)
        
        # Convert the Markdown response to HTML
        explanation_html = markdown2.markdown(response.text)

        return render_template('topic.html', topic_name=topic_name, explanation=explanation_html)

    except Exception as e:
        return render_template('index.html', error=f"An error occurred: {e}")

if __name__ == '__main__':
    # Using port 8001 as specified
    app.run(debug=True, port=8001)