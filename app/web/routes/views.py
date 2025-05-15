from flask import Blueprint, render_template

# Create blueprint
views = Blueprint('views', __name__)

@views.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@views.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy'} 