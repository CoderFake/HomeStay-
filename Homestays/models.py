from django.db import models


class Homestays(models.Model):
    name = models.CharField(max_length=100, unique=True)
    area = models.FloatField()
    address = models.CharField(max_length=254)
    price = models.FloatField()
    discount = models.FloatField()
    max_capacity = models.IntegerField()
    status = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    map_key = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Homestay"
        verbose_name_plural = "Homestays"


class HomestayImages(models.Model):
    image_key = models.CharField(max_length=100)
    homestay = models.ForeignKey(Homestays, on_delete=models.CASCADE, related_name='homestay_images')

    class Meta:
        verbose_name = "Homestay Image"
        verbose_name_plural = "Homestay Images"


class Facilities(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_key = models.CharField(max_length=100)
    description = models.TextField()
    homestay = models.ForeignKey(Homestays, on_delete=models.CASCADE, related_name='facilities')

    class Meta:
        verbose_name = "Facility"
        verbose_name_plural = "Facilities"


class Rooms(models.Model):
    ROOM_TYPES = (
        ('bedroom', 'Bedroom'),
        ('living_room', 'Living Room'),
        ('kitchen', 'Kitchen'),
        ('dining_room', 'Dining Room'),
        ('bathroom', 'Bathroom'),
        ('balcony', 'Balcony'),
        ('laundry_room', 'Laundry Room')
    )

    name = models.CharField(max_length=100, choices=ROOM_TYPES)
    amount = models.IntegerField()
    homestay = models.ForeignKey('Homestays', on_delete=models.CASCADE, related_name="rooms")

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"