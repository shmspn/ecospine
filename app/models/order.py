from datetime import datetime

class Order:
    def __init__(self, product_id, customer_name, phone):
        self.product_id = product_id
        self.customer_name = customer_name
        self.phone = phone
        self.status = 'new'
        self.ordered_at = datetime.now()