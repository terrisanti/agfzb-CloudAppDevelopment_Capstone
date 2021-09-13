from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    Name = models.CharField(null=False, max_length=30)
    Description = models.CharField(max_length=100)

    def __str__(self):
        return "Name: " + self.Name + "," + \
               "Description: " + self.Description


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object

class CarModel(models.Model):
    """ CarModel Class"""
    YEAR_CHOICES = []
    for r in range((now().year), 1979, -1):
        YEAR_CHOICES.append((r, r))

    CAR_TYPES = (
        ('S', 'Sedan'),
        ('H', 'Hatchback'),
        ('V', 'SUV'),
        ('W', 'Wagon'),
        ('P', 'Sports'),
        ('T', 'Truck'),
    )
    CarMake = models.ForeignKey(CarMake, on_delete = models.CASCADE)
    CarName = models.CharField(null=False, max_length=30)
    DealerId = models.IntegerField(null=False)
    CarType = models.CharField(max_length=1, choices=CAR_TYPES, default='S')
    CarYear = models.IntegerField(choices=YEAR_CHOICES, default=now().year) 

    def __str__(self):
        return "Car Name: " + self.CarName
        

# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:
    """ CarDealer Class"""
    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer: " + self.full_name

# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:
    """ DealerReview Class"""
    def __init__(self, id, name, dealership, purchase, car_make, car_model, car_year, review, purchase_date, sentiment):
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.dealership = dealership
        self.id = id
        self.name = name
        self.purchase = purchase
        self.purchase_date = purchase_date
        self.review = review
        self.sentiment = sentiment
    
    def __str__(self):
        return "Name: " + self.name + "," + \
               "Review: " + self.review 