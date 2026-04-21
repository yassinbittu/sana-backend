from app import create_app
from app.models.user import User

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email='iamyxn12@gmail.com').first()
    
    if admin:
        print(f"Admin user found: {admin.username}")
        print(f"Admin email: {admin.email}")
        print(f"Admin role: {admin.role}")
        print(f"Admin is_active: {admin.is_active}")
        print(f"Password hash: {admin.password_hash}")
        
        # Test password verification
        test_password = 'admin123'
        is_valid = admin.check_password(test_password)
        print(f"\nPassword check result for '{test_password}': {is_valid}")
        
        if not is_valid:
            print("\n❌ Password verification failed!")
            print("Resetting password to 'admin123'...")
            admin.set_password(test_password)
            from app import db
            db.session.commit()
            print("✅ Password reset successfully!")
            
            # Verify it works now
            is_valid = admin.check_password(test_password)
            print(f"Password check after reset: {is_valid}")
    else:
        print("Admin user not found!")
