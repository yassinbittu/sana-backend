"""
Production Debugging & Login Fix Script
Run this to diagnose and fix login issues in production
"""
from app import create_app
from app.models.user import User
from app import db

app = create_app()

with app.app_context():
    print("\n" + "="*70)
    print("🔍 PRODUCTION LOGIN DEBUGGING")
    print("="*70)
    
    # Check configuration
    print("\n📋 Configuration Check:")
    print(f"  Flask Environment: {app.config.get('DEBUG')}")
    print(f"  Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
    print(f"  Admin Email (from config): {app.config.get('ADMIN_EMAIL')}")
    print(f"  Admin Username (from config): {app.config.get('ADMIN_USERNAME')}")
    
    # Check if admin exists with configured email
    admin_email = app.config.get('ADMIN_EMAIL', '').strip().lower()
    admin_username = app.config.get('ADMIN_USERNAME', 'admin').strip()
    admin_password = app.config.get('ADMIN_PASSWORD', '')
    
    print(f"\n🔐 Expected Admin Credentials:")
    print(f"  Email: {admin_email}")
    print(f"  Username: {admin_username}")
    print(f"  Password: {'*' * len(admin_password)}")
    
    # Check database
    print(f"\n💾 Database Check:")
    try:
        all_users = User.query.all()
        print(f"  Total users in database: {len(all_users)}")
        
        # Check for admin with expected email
        admin = User.query.filter_by(email=admin_email).first()
        if admin:
            print(f"\n  ✅ Admin user found with email '{admin_email}':")
            print(f"     Username: {admin.username}")
            print(f"     Role: {admin.role}")
            print(f"     Is Active: {admin.is_active}")
            
            # Test password
            is_valid = admin.check_password(admin_password)
            print(f"     Password Valid: {'✅ YES' if is_valid else '❌ NO'}")
            
            if not is_valid:
                print(f"\n  ⚠️  Password mismatch! Resetting...")
                admin.set_password(admin_password)
                db.session.commit()
                print(f"     ✅ Password reset successfully!")
        else:
            print(f"\n  ❌ No admin user found with email '{admin_email}'")
            
            # Check if there's an admin with different email
            any_admin = User.query.filter_by(role='admin').first()
            if any_admin:
                print(f"\n  Found admin with different email: {any_admin.email}")
                print(f"  Updating to configured email: {admin_email}")
                any_admin.email = admin_email
                any_admin.username = admin_username
                any_admin.set_password(admin_password)
                db.session.commit()
                print(f"  ✅ Admin user updated!")
            else:
                print(f"\n  Creating new admin user...")
                admin = User(
                    username=admin_username,
                    email=admin_email,
                    role='admin',
                    is_active=True
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                print(f"  ✅ Admin user created!")
        
        # Verify final state
        print(f"\n✨ Final Verification:")
        final_admin = User.query.filter_by(email=admin_email).first()
        if final_admin and final_admin.check_password(admin_password):
            print(f"  ✅ Admin login will work now!")
        else:
            print(f"  ❌ Still having issues!")
            
    except Exception as e:
        print(f"  ❌ Database Error: {str(e)}")
        db.session.rollback()

print("\n" + "="*70 + "\n")
