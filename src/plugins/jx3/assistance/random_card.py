import datetime
import random

def get_card():
    today = datetime.date.today().strftime('%Y-%m-%d')
    random.seed(today)
    return random.randint(1, 5)