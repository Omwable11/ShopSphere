from app import app, db
from app.models import Product

with app.app_context():
    # Delete old products (optional)
    Product.query.delete()

    products = [
        Product(
            name="iPhone 16",
            description="Apple smartphone",
            price=79999,
            image="https://picsum.photos/300?random=1",
            stock=10
        ),
        Product(
            name="Samsung Galaxy S25",
            description="Samsung flagship phone",
            price=74999,
            image="https://picsum.photos/300?random=2",
            stock=15
        ),
        Product(
            name="Dell Laptop",
            description="Dell Inspiron Laptop",
            price=65999,
            image="https://picsum.photos/300?random=3",
            stock=8
        ),
        Product(
            name="Sony Headphones",
            description="Wireless Noise Cancelling",
            price=9999,
            image="https://picsum.photos/300?random=4",
            stock=20
        )
    ]

    db.session.add_all(products)
    db.session.commit()

    print("✅ Products inserted successfully!")