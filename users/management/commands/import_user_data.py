from django.core.management.base import BaseCommand
import json,datetime
from django.utils import timezone
from users.models import User, Purchase_History
from restaurant.models import Restaurant, Menu

class Command(BaseCommand):
    help = 'Import user data'

    def add_arguments(self, parser):
        parser.add_argument('--app', type=str)
        parser.add_argument('--data', type=str)

    def handle(self, *args, **options):
        app_name = options['app']
        data_str = options['data']

        # Parse the JSON data
        user_data = json.loads(data_str)

        # Set the default password
        default_password = 'admin'

        # Create User objects from the data and save to database
        for user in user_data:
           
            try:
                u = User.objects.create(username=user['name'], cash_balance=user['cashBalance'])
                u.set_password(default_password)
                u.save()
            except KeyError as e:
                print(f"Error creating user: {e}")
                continue
            for purchase in user['purchaseHistory']:
                try:
                    # Retrieve restaurant based on its name in the purchase history
                    restaurant = Restaurant.objects.get(name=purchase['restaurantName'])
                    # Retrieve menu item based on its name and restaurant_id
                    menu_item = Menu.objects.get(dish_name=purchase['dishName'], restaurant_id=restaurant.id)
                    # Create PurchaseHistory object and save to database
                   
                    purchase['transactionDate'] = datetime.datetime.strptime(purchase['transactionDate'], "%Y-%m-%d %H:%M:%S")
                    purchase['transactionDate'] = timezone.make_aware(purchase['transactionDate'], timezone.get_default_timezone())
                    Purchase_History.objects.create(user=u, restaurant=restaurant, menu=menu_item, transaction_amount=purchase['transactionAmount'], transaction_date=purchase['transactionDate'])
                except (KeyError, Restaurant.DoesNotExist, Menu.DoesNotExist) as e:
                    print(f"Error creating purchase history for user {u.username}: {e}")
                    continue
        