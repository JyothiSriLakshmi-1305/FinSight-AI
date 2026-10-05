import csv
import random
from datetime import datetime, timedelta

output_file = r'd:\Major Project\Finsight\data\sample_transactions.csv'

categories_rules = {
    'Rent': {'amount': lambda: random.randint(12000, 15000), 'freq': 1, 'merchants': ['Landlord'], 'desc': ['Monthly Rent']},
    'Food & Dining': {'amount': lambda: random.randint(100, 2000), 'freq': 15, 'merchants': ['Swiggy', 'Zomato', 'Local Cafe', 'Starbucks'], 'desc': ['Lunch', 'Dinner', 'Coffee', 'Food Delivery']},
    'Transport': {'amount': lambda: random.randint(50, 500), 'freq': 10, 'merchants': ['Uber', 'Ola', 'Metro'], 'desc': ['Office commute', 'Cab ride', 'Metro recharge']},
    'Utilities': {'amount': lambda: random.randint(500, 3000), 'freq': 4, 'merchants': ['BESCOM', 'Jio', 'Airtel'], 'desc': ['Electricity Bill', 'Internet', 'Mobile Recharge']},
    'Shopping': {'amount': lambda: random.randint(500, 5000), 'freq': 3, 'merchants': ['Amazon', 'Flipkart', 'Myntra'], 'desc': ['Clothes', 'Electronics', 'Online Shopping']},
    'Medical & Health': {'amount': lambda: random.randint(200, 1000), 'freq': 1, 'merchants': ['Apollo Pharmacy', 'Practo'], 'desc': ['Medicines', 'Consultation']},
    'Entertainment': {'amount': lambda: random.randint(200, 1500), 'freq': 4, 'merchants': ['PVR Cinemas', 'Netflix'], 'desc': ['Movie ticket', 'Streaming']},
    'Education': {'amount': lambda: random.randint(1000, 5000), 'freq': 1, 'merchants': ['Coursera', 'Udemy'], 'desc': ['Online course', 'Books']},
    'Insurance': {'amount': lambda: 2500, 'freq': 1, 'merchants': ['LIC', 'HDFC Life'], 'desc': ['Life Insurance']},
    'Subscriptions': {'amount': lambda: random.choice([649, 119, 1500]), 'freq': 3, 'merchants': ['Netflix', 'Spotify', 'Gym'], 'desc': ['Subscription']},
    'Personal Care': {'amount': lambda: random.randint(300, 1500), 'freq': 2, 'merchants': ['Urban Company', 'Nykaa'], 'desc': ['Salon service', 'Skincare']},
    'Travel': {'amount': lambda: random.randint(2000, 15000), 'freq': 0.5, 'merchants': ['MakeMyTrip', 'Indigo'], 'desc': ['Flight ticket']},
    'Miscellaneous': {'amount': lambda: random.randint(100, 2000), 'freq': 2, 'merchants': ['Local Store', 'Amazon'], 'desc': ['Random items']},
}

payment_methods = ['UPI', 'Cash', 'Card', 'Net Banking']
transactions = []

for month in range(1, 13):
    multiplier = 1.0 + (month - 1) * 0.02
    for cat, rules in categories_rules.items():
        freq = rules['freq']
        if freq < 1:
            if random.random() > freq:
                continue
            freq = 1
            
        for _ in range(int(freq)):
            day = random.randint(1, 28)
            date = datetime(2024, month, day)
            amount = int(rules['amount']() * multiplier)
            merchant = random.choice(rules['merchants'])
            desc = random.choice(rules['desc'])
            
            if cat == 'Rent':
                date = datetime(2024, month, 1)
            elif cat == 'Subscriptions':
                date = datetime(2024, month, 5)
                amount = rules['amount']()
                if amount == 649: merchant = 'Netflix'; desc = 'Netflix Subscription'
                elif amount == 119: merchant = 'Spotify'; desc = 'Spotify Subscription'
                else: merchant = 'Gold Gym'; desc = 'Gym Membership'
            elif cat == 'Insurance':
                date = datetime(2024, month, 10)
                amount = 2500
                
            pm = random.choice(payment_methods)
            if amount < 500: pm = random.choice(['UPI', 'Cash'])
            elif amount > 5000: pm = random.choice(['Card', 'Net Banking'])
            
            transactions.append([date.strftime('%Y-%m-%d'), amount, cat, pm, desc, merchant])
            
    if month == 8:
        transactions.append(['2024-08-15', 185000, 'Medical & Health', 'Net Banking', 'Hospital Bill', 'Apollo Hospital'])

transactions.sort(key=lambda x: x[0])

with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['date', 'amount', 'category', 'payment_method', 'description', 'merchant'])
    writer.writerows(transactions)

print(f"Generated {len(transactions)} transactions.")
