import sys
from app.app import create_app
from app.core.db import db
from app.models import Admin  


app = create_app()

def add_admin(email, password):
    """Add a new admin to the database."""
    with app.app_context():
        if Admin.query.filter_by(email=email).first():
            print(f"Admin with email {email} already exists.")
            return
        
        admin = Admin(email=email)
        admin.set_password(password)
        
        db.session.add(admin)
        try:
            db.session.commit()
            print(f"Admin {email} added successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding admin: {e}")

def delete_admin(email):
    """Function to delete an admin"""
    with app.app_context():
        admin = Admin.query.filter_by(email=email).first()
        if not admin:
            print(f"No admin found with email: {email}")
        else:
            db.session.delete(admin)
            db.session.commit()
            print(f"Admin {email} deleted successfully!")

def show_usage():
    print("Usage:")
    print("python cli.py add-admin <email> <password>")
    print("python cli.py delete-admin <email>")

# Main function to handle the CLI arguments
if __name__ == "__main__":
    if len(sys.argv) < 3:
        show_usage()
    else:
        command = sys.argv[1]
        if command == "add-admin" and len(sys.argv) == 4:
            email = sys.argv[2]
            password = sys.argv[3]
            add_admin(email, password)
        elif command == "delete-admin" and len(sys.argv) == 3:
            email = sys.argv[2]
            delete_admin(email)
        else:
            show_usage()
