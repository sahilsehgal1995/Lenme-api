from flask import render_template
from flask_mail import Message
from src import mail


def send_order_email(order_data):

    msg = Message("Your ShopKare Order Details",
                  sender='saurabh@hellonomnom.com',
                  recipients=['saurabh@hellonomnom.com'])

    msg.html = render_template('invoice.html', products=order_data['ordered_product'],
                               user=order_data['user'], total=order_data['total'],
                               pincode=order_data['pin_code'], address=order_data['address'])
    print(msg.html)
    # mail.send(msg)