import time

from services.dbServices.firebase_services import db
from services.paymentServices.productsInfo import *
from services.helperFunctions import *


def saveSessionDetails(checkout_session):
    try:
        # Save the checkout session details to the database
        db.collection('StripeServicePaymentDetails').document(checkout_session.id).set(checkout_session.to_dict())

        # Update SuccessPaymentDetails collection
        if checkout_session.payment_status == 'paid':
            # Get User_Id, Product_id, Product_type from metadata
            metadata = checkout_session.metadata
            user_id = metadata['user_id']
            product_id = metadata['product_id']
            product_type = metadata['payment_type']
            transaction_id = metadata['transaction_Id']

            if product_type == 'service':
                order_data = {
                    'id': transaction_id,
                    'createdAt': int(time.time() * 1000),
                    'orderStatus': 'Processing',
                    'productName': ProductsName.get(product_id, ''),
                    'productCategoryName': ProductsCategory.get(product_id, ''),
                    'productSubcategoryName': ProductsSubCategory.get(product_id, ""),
                    'paymentPlatformName': 'Stripe',
                    'orderNumber': generate_order_number(),
                    'orderTotalAmount': checkout_session.amount_total
                }

                # Add order_data to listActiveOrders in AppUsers Collection
                field_path = f'listActiveOrders.{transaction_id}'
                db.collection('AppUsers').document(user_id).update({
                    field_path: order_data
                })
                db.collection('PaidOrders').document(transaction_id).set(order_data)

            elif product_type == 'subscription':
                # Add Update activeSubscriptionId and isSubscriptionActive  in AppUsers Collection
                db.collection('AppUsers').document(user_id).update({
                    'activeSubscriptionId': product_id,
                    'isSubscriptionActive': True
                })

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, you can return or raise the error depending on your use case
        return f"Failed to save session details due to error: {e}"
