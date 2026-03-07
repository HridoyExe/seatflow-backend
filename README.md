# 🪑 SeatFlow 

SeatFlow is a complete, professional backend solution for a restaurant table seat-booking and food-ordering system. Designed with Django and Django REST Framework (DRF), it allows users to browse menus, book specific seats, pre-order food items, and complete payments seamlessly.

## ✨ Key Features
* **User Authentication:** 
  * Registration, Login, and User Profile management using `Djoser`.
  * Secure token-based authentication using Postman and SimpleJWT.
* **Menu Management:**
  * Categorized menu items.
  * Search, filter, and order menu items by name, price, rating, etc.
  * Automatic review aggregation and average rating calculation.
* **Advanced Booking System:**
  * Seat reservation categorized by diverse sections.
  * Define expected `booking_date`, `start_time` and `end_time`.
  * Prevent booking overlapping times or already-paid seats.
* **Order Customization:**
  * Users can attach food orders (Order Items) to their specific seat booking.
  * The system automatically recalculates the total `amount` payable on the booking every time a food item is added or removed.
* **Payment Simulation:**
  * Auto-generation of Booking Codes.
  * Order/Booking cancellations are automatically blocked once the payment is "SUCCESS".
* **Interactive API Documentation:**
  * fully readable API endpoints structured via `Swagger` (`drf_yasg`) & Redoc.

## 🛠️ Technology Stack
* **Python 3.x**
* **Django 6.0.2**
* **Django REST Framework (DRF)**
* **Djoser** (For Authentication)
* **SimpleJWT** (For JWT Tokens)
* **Drf-Yasg** (Swagger API Documentation)

## 🗃️ Project Structure
The project is split into several modular apps keeping concerns separated strictly:
* `accounts`: Handles Custom User Models, Roles (Admin/User), and standard Auth Views.
* `menu`: Handles Categories, Menu Items, Reviews, and Menu Image uploads.
* `booking`: Handles Sections, Seats, Bookings, and specific Order Items linked to bookings.
* `payment`: Deals with Payment objects linked 1-to-1 with Bookings.
* `api`: General router/urls consolidator.

## 🚀 How to Run Locally

### 1. Clone & Setup Environment
```bash
git clone <your-repository-url>
cd SeatFlow
python -m venv .seatflow_env
```
Activate the environment:
* **Windows:** `.seatflow_env\Scripts\activate`
* **Mac/Linux:** `source .seatflow_env/bin/activate`

### 2. Install Requirements
```bash
pip install -r requirements.txt
```
*(If `requirements.txt` is not available, manual installation of modules like django, djangorestframework, djoser, djangorestframework-simplejwt, and drf-yasg is required).*

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create a Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 5. Run the Server
```bash
python manage.py runserver
```

### 6. Explore APIs
After running the server, you can view all structured API endpoints and test them directly via the browser at:
* **Swagger UI:** [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
* **ReDoc UI:** [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

---
***Developed with ❤️ by Hridoy***
