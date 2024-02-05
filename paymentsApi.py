import pprint

from flask import Blueprint, request, jsonify
from flask_cors import CORS
import stripe

from services.paymentServices.saveSessionDetails import *

pa = Blueprint('pa', __name__, template_folder='templates')
CORS(pa)
stripe.api_key = "sk_test_51Nfo0yAwqpCFthEviCvKEjXSdkmyBqNEVZ4OClDhtYbB0ISYKs973pdZVokCMkKvvGrhAsMY062u6jvHAyg7YYYD00np4pMLUl"  # development key
# stripe.api_key = "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"  # production key


@pa.post('/purchase')
def purchase():
    data = request.get_json()
    print(data)
    print("I was called to purchase")
    return jsonify({'message': 'success'}), 200


@pa.route('/get-products', methods=['GET'])
def get_products():
    products = stripe.Product.list()
    return jsonify(products)


@pa.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        # Extract success and cancel URLs from the POST data
        data = request.get_json()
        success_url = data.get('success_url')
        cancel_url = data.get('cancel_url')

        # Ensure the URLs are provided
        if not success_url or not cancel_url:
            return jsonify(error="success_url and cancel_url are required!"), 400

        # Create a new checkout session for a payment
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Premium Plus',
                    },
                    'unit_amount': 1999,  # $19.99 in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 400


@pa.route('/one-time-checkout', methods=['POST'])
def create_one_time_checkout_session():
    try:
        data = request.json

        # Validating the required fields
        required_fields = ['product_name', 'amount', 'success_url', 'cancel_url', 'user_email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing {field} in request.'}), 400

        # Adding session_id placeholder to success and cancel URLs
        success_url = data['success_url'] + "/success?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = data['cancel_url'] + "/cancel?session_id={CHECKOUT_SESSION_ID}"

        # Getting metadata from user (if provided) or setting it as an empty dict
        metadata = data.get('metadata', {})

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': data['product_name'],
                        },
                        'unit_amount': int(data['amount'] * 100),  # Convert the amount to cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=data['user_email'],  # Adding the customer email
            metadata = metadata  # Adding the metadata
        )
        return jsonify({'checkout_url': checkout_session.url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pa.route('/verify-stripe-payment', methods=['POST'])
def verify_payment():
    try:
        data = request.json
        checkout_session_id = data.get('checkout_session_id')
        print(checkout_session_id)


        if not checkout_session_id:
            return jsonify({'error': 'checkout_session_id is required'}), 400

        # Retrieve the checkout session to verify
        checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)
        pprint.pprint(checkout_session)

        # Save all this data to your database
        saveSessionDetails(checkout_session)

        # pprint.pprint(checkout_session)

        # Assuming that after successful payment, Stripe's checkout session will have payment_status as 'paid'
        if checkout_session.payment_status == 'paid':
            # Extracting important details
            details = {
                'id': checkout_session.id,
                'object': checkout_session.object,
                'created': checkout_session.created,
                'customer_email': checkout_session.customer_email,
                'payment_intent': checkout_session.payment_intent,
                'payment_status': checkout_session.payment_status,
                'currency': checkout_session.currency,
                'amount_total': checkout_session.amount_total,
                'metadata': checkout_session.metadata,  # if there's any custom metadata you've added
                #  any other attributes you need
            }

            return jsonify({
                'status': 'success',
                'message': 'Payment successful!',
                'session_details': details
            })

        else:
            # Payment was not successful or it's still pending
            return jsonify({
                'status': 'failure',
                'message': 'Payment was not successful'
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500