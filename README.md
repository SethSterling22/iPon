# iPon - Yadiel Rivera, David Mendez, Sebastián Sterling
Ride-Sharing Platform

*  Install Python:
Use python 3.12, as this is the version used in this project.

*  Set up a virtual environment:
python -m venv venv
source venv/bin/activate

*  Install all dependencies:
pip install -r requirements.txt

*  Make migrations:
python manage.py makemigrations
python manage.py migrate

*  Run the server:
python manage.py runserver 0.0.0.0:8000
