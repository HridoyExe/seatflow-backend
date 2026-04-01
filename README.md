# 🪑 SeatFlow: Advanced Restaurant Table & Food Booking System

**SeatFlow** is a robust, industry-grade backend solution designed to handle real-world restaurant operations. It features high-concurrency seat booking, dynamic food ordering, and secure payment integration using a professional Service Layer architecture.

---

## 🏗️ System Architecture
This project follows **Clean Architecture** principles to ensure maintainability and scalability:
- **Service Layer**: All business logic (validations, calculations) is decoupled from views and models into dedicated `services.py` modules.
- **Thin Views**: API views only handle request parsing and response formatting, delegating complexity to services.
- **Signals & Domain Events**: Automatic state updates (like recalculating booking totals) are handled via asynchronous-ready Django signals.
- **Global Error Handling**: A universal exception handler ensures every API response follows a consistent, professional JSON structure.

---

## 🔥 Key Professional Features
- **🛡️ Concurrency-Safe Booking**: Robust validation preventing overlapping time-slot reservations for the same table.
- **💳 Payment Integration**: Full integration with **SSLCommerz**, featuring secure callbacks and transaction state synchronization.
- **⚡ Performance Optimized**: Utilizes database-level optimizations including `select_related`, `prefetch_related`, and `annotate` to solve N+1 query problems.
- **📝 Automated Documentation**: Fully documented interactive API using **drf-spectacular** (Swagger/Redoc).
- **🧪 Quality Assurance**: Comprehensive unit test suite covering critical business rules (booking limits, seat availability).
- **☁️ Cloud-Ready Media**: Seamless integration with **Cloudinary** for scalable image storage and **WhiteNoise** for static content.

---

## 🛠️ Technology Stack
- **Backend**: Python 3.11, Django 6.0, Django REST Framework
- **Auth**: Djoser, SimpleJWT (JWT Auth)
- **Database**: PostgreSQL (Supabase/Neon ready)
- **Utilities**: SSLCommerz SDK, Cloudinary, Django-Filter, Drf-Spectacular
- **DevOps**: Vercel deployment ready, WhiteNoise

---

## 🚀 Getting Started

### 1. Clone & Environment
```bash
git clone https://github.com/<your-username>/SeatFlow
cd SeatFlow
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file based on the boilerplate:
- `DATABASE_URL`, `SECRET_KEY`, `CLOUD_NAME`, `SSL_STORE_ID`, etc.

### 3. Setup Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run & Test
```bash
python manage.py test  # Run the unit tests
python manage.py runserver
```

Explore the API at `http://127.0.0.1:8000/swagger/`

---

## 🤝 Contact & Credits
**Developed by Hridoy**  
*Aspiring Full-Stack Software Engineer dedicated to writing clean, maintainable, and human-readable code.*

---
