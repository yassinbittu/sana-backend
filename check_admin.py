from app import create_app
from app.models.user import User

app = create_app()
with app.app_context():
    # Check if admin user exists with the desired email
    admin = User.query.filter_by(email='iamyxn12@gmail.com').first()

    if admin:
        print('Admin user exists with correct email:', admin.email)
        print('Admin details:', admin.username, admin.email, admin.role)
    else:
        # Check if there's an admin user with different email
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            print('Found admin user with different email:', existing_admin.email)
            print('Updating email to iamyxn12@gmail.com...')
            existing_admin.email = 'iamyxn12@gmail.com'
            from app import db
            db.session.commit()
            print('Admin email updated successfully!')
        else:
            print('No admin user found. Creating one...')
            admin = User(
                username='admin',
                email='iamyxn12@gmail.com'
            )
            admin.set_password('admin123')  # Use the proper password setter
            admin.role = 'admin'
            from app import db
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully!')

    # Show final admin details
    final_admin = User.query.filter_by(email='iamyxn12@gmail.com').first()
    if final_admin:
        print('Final admin details:')
        print('  Username:', final_admin.username)
        print('  Email:', final_admin.email)
        print('  Role:', final_admin.role)
        print('  Password should be: admin123')