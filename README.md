# Coderr Backend

Coderr is a Django REST Framework backend for a freelancer marketplace platform.

The API allows customers and business users to register, manage profiles, publish offers, create orders, write reviews, and retrieve general platform statistics.

## Features

- User registration and login with token authentication
- Customer and business user profiles
- Offer management for business users
- Offer details with basic, standard, and premium packages
- Order creation based on offer details
- Order status management by business users
- Review system for customer feedback
- Platform statistics via base info endpoint
- Django admin interface support
- Automated tests using Django and DRF test tools

## Tech Stack

- Python
- Django 6.0.4
- Django REST Framework 3.17.1
- SQLite for local development
- DRF Token Authentication
- Django TestCase / DRF APITestCase

## Project Structure

core/
├── settings.py
├── urls.py
├── asgi.py
└── wsgi.py

auth_app/
profiles_app/
offers_app/
orders_app/
reviews_app/
base_app/

Each app contains an api/ folder for API-specific files such as serializers, views, urls, and permissions.

## Installation

Clone the repository:
```bash
git clone <repository-url>
cd <project-folder>
```
Create and activate a virtual environment:
```bash
python -m venv env
```
On Windows:
```bash
env\Scripts\activate
```
On macOS/Linux:
```bash
source env/bin/activate
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Apply migrations:
```bash
python manage.py migrate
```
Create a superuser:
```bash
python manage.py createsuperuser
```
Start the development server:
```bash
python manage.py runserver
```
The backend will be available at:
```bash
http://127.0.0.1:8000/
```
The admin panel is available at:
```bash
http://127.0.0.1:8000/admin/
```
## Authentication

The API uses DRF Token Authentication.

After registration or login, the response contains a token:
```bash
{
  "token": "your-token",
  "username": "exampleUsername",
  "email": "example@mail.de",
  "user_id": 1
}
```
Authenticated requests must include the token in the request header:

Authorization: Token your-token


## Important Business Rules

### User Types

Users are separated into two profile types:

customer
business

The user type is stored in the UserProfile model.

### Profiles

Each registered user automatically receives a profile.

Profile data combines fields from Django's built-in User model and the custom UserProfile model.

Users can only update their own profile.

### Offers

Only business users can create offers.

Each offer must contain exactly three offer details:

basic
standard
premium

Offer details contain package-specific data such as price, delivery time, revisions, features, and offer type.

Offer details can be updated individually through the offer PATCH endpoint by passing the offer_type.

### Orders

Only customer users can create orders.

Orders are created from an existing OfferDetail.

When an order is created, the relevant offer detail data is copied into the order.

This means orders are stored as snapshots. If the original offer or offer detail is changed later, existing orders keep their original title, price, delivery time, revisions, features, and offer type.

Only the assigned business user can update the order status.

Only staff users can delete orders.

### Reviews

Only customer users can create reviews.

A customer can review a business user only once.

Only the creator of a review can update or delete it.

Reviews can be filtered by:

business_user_id
reviewer_id

Reviews can be ordered by:

rating
updated_at

### Base Info

The base info endpoint returns general platform statistics:
```bash
{
  "review_count": 0,
  "average_rating": 0.0,
  "business_profile_count": 0,
  "offer_count": 0
}
```
The average rating is rounded to one decimal place.

## Running Tests

Run all tests:
```bash
python manage.py test
```
Run tests for a specific app:
```bash
python manage.py test auth_app
python manage.py test profiles_app
python manage.py test offers_app
python manage.py test orders_app
python manage.py test reviews_app
python manage.py test base_app
```

## Media Files

Uploaded files such as profile images and offer images are stored in the local media/ directory during development.

The media/ directory should not be committed to Git.

Required settings:

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

## Environment and Database

For local development, SQLite is used by default.

The local database file should not be committed to Git:

db.sqlite3

Recommended .gitignore entries:

env/
venv/
__pycache__/
*.pyc
db.sqlite3
.coverage
htmlcov/
.env
media/

## Development Notes

- The backend is separated from any frontend application.
- The Django project folder is named core.
- Each app has its own API routing.
- Each app contains an api/ folder for serializers, views, urls, and permissions where needed.
- Serializers explicitly define their fields.
- Permissions are handled per app and per endpoint where needed.
- Business logic is kept out of models where possible.
- The Django admin interface is available and configured for the main models.