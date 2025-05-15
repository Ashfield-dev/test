# Download Manager

A Flask-based web application for managing downloads with features like queue management, bandwidth control, and progress tracking.

## Features

- Web-based interface for managing downloads
- Queue management with priority support
- Bandwidth control
- Progress tracking
- CSV import/export functionality
- Dark/Light theme support

## Requirements

- Python 3.7+
- Flask
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/download-manager.git
cd download-manager
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python run.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Configuration

The application can be configured through the following environment variables:

- `FLASK_ENV`: Set to 'development' or 'production'
- `MAX_WORKERS`: Maximum number of concurrent downloads
- `DEFAULT_BANDWIDTH_LIMIT`: Default bandwidth limit in bytes/second

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Structure

```
project/
├── app/
│   ├── core/           # Core functionality
│   │   ├── download_manager.py
│   │   ├── telegram.py
│   │   └── logger.py
│   ├── web/           # Web interface
│   │   └── routes/
│   ├── static/        # Static files
│   └── templates/     # HTML templates
├── instance/         # Instance-specific data
├── logs/            # Application logs
└── temp_downloads/  # Temporary download directory
```

## Features in Detail

### Download Management
- Concurrent downloads with configurable worker count
- Priority-based queue system
- Bandwidth limiting
- File integrity verification

### Telegram Integration
- Real-time download notifications
- File sharing capability
- Progress updates
- Error notifications
- Support for large files (up to 2GB)

### Web Interface
- Modern, responsive design
- Real-time progress updates
- Queue management
- Download history

## Acknowledgments

- Built with Flask and Pyrogram
- Uses modern Python async features
- Implements best practices for download management
