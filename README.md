# 🛒 ShopSphere - E-Commerce Website

A full-stack E-Commerce web application built using **Flask**, **PostgreSQL**, **SQLAlchemy**, **Bootstrap**, and **Jinja2**. ShopSphere provides a complete online shopping experience with user authentication, product management, shopping cart, wishlist, order tracking, reviews, invoice generation, and an admin dashboard with analytics.

---

## 🚀 Features

### 👤 User Features
- User Registration & Login
- Secure Password Authentication
- User Profile Management
- Profile Picture Upload
- Change Password
- Browse Products
- Search Products
- Category Filter
- Price Sorting
- Product Details
- Shopping Cart
- Wishlist
- Checkout
- Order History
- Order Status Tracking
- Product Reviews & Ratings
- Download Invoice (PDF)

### 🛠️ Admin Features
- Admin Dashboard
- Product Management (CRUD)
- Manage Orders
- Update Order Status
- Dashboard Analytics
  - Total Products
  - Total Users
  - Total Orders
  - Total Revenue
  - Recent Orders
  - Order Status Pie Chart

---

## 🖥️ Tech Stack

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Jinja2 Templates
- Chart.js

### Backend
- Python
- Flask
- SQLAlchemy

### Database
- PostgreSQL

### Libraries Used
- Flask
- Flask-SQLAlchemy
- Werkzeug
- ReportLab
- Chart.js

---

## 📂 Project Structure

```
ShopSphere/
│
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   └── uploads/
│   ├── templates/
│   ├── models.py
│   ├── routes.py
│   ├── config.py
│   └── __init__.py
│
├── migrations/
├── run.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/ShopSphere.git
cd ShopSphere
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure PostgreSQL

Create a PostgreSQL database named:

```
shopsphere
```

Update the database URI in `app/config.py`:

```python
SQLALCHEMY_DATABASE_URI = "postgresql://username:password@localhost:5432/shopsphere"
```

### Run Database Migrations

```bash
flask db upgrade
```

### Run the Application

```bash
python run.py
```

Open your browser:

```
http://127.0.0.1:5000
```

---

## 📸 Screenshots

Add screenshots here after uploading them.

### Home Page

```
images/home.png
```

### Product Details

```
images/product.png
```

### Shopping Cart

```
images/cart.png
```

### User Profile

```
images/profile.png
```

### Admin Dashboard

```
images/dashboard.png
```

### Invoice PDF

```
images/invoice.png
```

---

## 📈 Future Improvements

- Email Notifications
- Coupon & Discount System
- Forgot Password
- Product Recommendations
- Sales Reports
- Payment Gateway Integration
- Product Inventory Alerts

---

## 👨‍💻 Author

**Om Wable**

- GitHub: https://github.com/yourusername
- LinkedIn: https://linkedin.com/in/your-linkedin

---

## 📄 License

This project is licensed under the MIT License.

---

⭐ If you found this project useful, consider giving it a star on GitHub!
