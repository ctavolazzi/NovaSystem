# Django REST Starter

Welcome to Django REST Starter! This repository provides a starting point for building RESTful APIs using the Django REST framework

## File Structure
```
django-rest-starter/
├── main/
│   ├── __init__.py
│   ├── asgi.py
│   ├── local_settings.py
│   ├── production_settings.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── requirements.txt
├── README.md
├── manage.py
```

## Getting Started

1. Clone this repository to your local machine:
   ```shell
   git clone https://github.com/Grey-A/django-rest-starter.git
   ```

2. Navigate to the project directory:
   ```shell
   cd django-rest-starter
   ```

3. Set up a virtual environment (recommended) and install dependencies:
   ```shell
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```shell
   python manage.py migrate
   ```

5. Run the development server:
   ```shell
   python manage.py runserver
   ```

## Configuration

This project includes two settings files:

- `production_settings.py`: Configuration for when the app is live on railway, it uses PostgreSQL. 
  
NOTE: Remember to change the secret key on railway, you can use websites like `https://djecrety.ir/` to generate your new secret key

- `local_settings.py`: Configuration for local development uses a randomly generated secret key with sqlite db
  
NOTE: The DJANG_ENV variable from Railway is used to determine which settings file to use.

## Contributing

Contributions are welcome! If you find a bug, have a feature request, or want to contribute improvements, feel free to open an issue or submit a pull request.