from random import randint, choice
from datetime import datetime

from models import db, User, Freetime, Task
from app import app

db.drop_all()
db.create_all()

# users
names = ("Bob", "Bill", "Sam", "Sally", "Tim", "Rob") #6
users = [User.register(f"{n}@gmail.com", f"{randint(10, 99)}n{randint(10, 99)}", n) for n in names]
db.session.add_all(users)
db.session.commit()

# freetimes
def get_time():
    """generates datetime objects of random times"""
    year = randint(2020, 2030)
    month = randint(1, 12)
    day = randint(1, 28)
    hour = randint(0, 23)
    minute = randint(0, 59)
    return datetime(year, month, day, hour, minute)

freetimes = [Freetime(user_id=choice(users).id, start_time=get_time(), end_time=get_time()) for _ in range(24)]
db.session.add_all(freetimes)

# tasks
tasks = []
for _ in range(24):
    user = choice(users)
    titles = ["Dishes", "Laundry", "Vacuum Living Room", "Walk Dog", "Make Dinner", "Learn Boxing"]
    title = choice(titles)
    description = f"{title} description for {user.name}... more stuff & instructions"
    tasks.append(Task(title=title, description=description, user_id=user.id))

db.session.add_all(tasks)
db.session.commit()

# blocks
block_values = []
for _ in range(48):
    task = choice(tasks)
    task.freetimes.append(choice(freetimes))

db.session.commit()
