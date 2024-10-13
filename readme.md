
# activate virtual enviuronment
source .virtualenvs/myvirtualenv/bin/activate

# Pull latest changes from default branch
git pull origin main  

# collect static files
python manage.py collectstatic

# run migrations
python manage.py migrate

pip install django

cd kwf/

pip install -r requirements.txt

python manage.py createsuperuser  # if it doesn't exist
