from app import db
from catalyst.models import User, Customer

db.drop_all()
db.create_all()

# create customer
customer_id = 'MOCK'
customer = Customer(id=customer_id, name='Mock customer', database_name='catalyst')
db.session.add(customer)
db.session.commit()
print('Customer created')


# create first user
user_mail='frdhont@gmail.com'
user = User(email=user_mail, first_name='Frederik', last_name='Dhont', customer=customer_id)
user.set_password('testpassword')
db.session.add(user)
db.session.commit()
print('User created')

# create schemas in the customer database: loadfiles & loadfiles_validated


