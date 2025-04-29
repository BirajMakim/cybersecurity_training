# Cybersecurity Training Platform

A modern web-based platform for cybersecurity training and awareness, built with Django and Bootstrap.

## Features

- Interactive training modules with progress tracking
- Different difficulty levels (Basic, Intermediate, Advanced)
- Real-time progress monitoring
- Time tracking for each module
- User activity logging
- Responsive dashboard interface
- Module categories including:
  - Introduction to Cybersecurity
  - Password Security & Authentication
  - Phishing Awareness
  - Network Security Fundamentals
  - Secure Web Browsing
  - Data Protection & Privacy
  - And more...

## Tech Stack

- Python 3.8+
- Django 5.2
- Bootstrap 5.3
- SQLite (Development)
- Bootstrap Icons

## Installation

1. Clone the repository:
```bash
git clone https://github.com/BirajMakim/cybersecurity_training.git
cd cybersecurity_training
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Load initial training modules:
```bash
python manage.py add_training_modules
```

7. Run the development server:
```bash
python manage.py runserver
```

Visit http://localhost:8000 in your browser.

## Project Structure

```
cybersecurity_training/
├── accounts/            # User authentication and profiles
├── dashboard/           # Main dashboard views
├── modules/            # Training modules and progress tracking
├── static/            # Static files (CSS, JS, images)
├── templates/         # HTML templates
└── manage.py         # Django management script
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 