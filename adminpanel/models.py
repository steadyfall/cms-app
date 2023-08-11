from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator


class Zone(models.Model):
    location = models.CharField(
        verbose_name="Name of the zone/location", max_length=64, unique=True, null=False
    )
    date_created = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_default_pk(cls):
        zone, created = cls.objects.get_or_create(location="Unknown")
        return zone.pk

    def __str__(self):
        return f"{self.location}"


class Plant(models.Model):
    zone = models.ForeignKey(
        Zone,
        default=Zone.get_default_pk,
        on_delete=models.SET_DEFAULT,
        related_name="plants_under",
    )
    name = models.CharField(
        verbose_name="Name of the plant", max_length=128, unique=True, null=False
    )
    date_created = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_default_pk(cls):
        plant, created = cls.objects.get_or_create(
            zone=Zone.objects.get(pk=Zone.get_default_pk()), name="Unknown"
        )
        return plant.pk

    def __str__(self):
        return f"{self.name} ({self.zone})"


class Case(models.Model):
    amount = models.PositiveIntegerField(
        verbose_name="Amount of particular case (in mL)",
        default=0,
        validators=[MinValueValidator(99), MaxValueValidator(1_000_000_000)],
        null=False,
        unique=False,
    )
    _total = models.PositiveIntegerField(
        verbose_name="No. of units of given case",
        default=0,
        name="count",
        validators=[MaxValueValidator(1_000_000_000)],
        null=False,
        unique=False,
    )
    for_plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name="all_cases",
        verbose_name="Case for plant",
    )
    date_created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def totalCases(self):
        return self._total

    @totalCases.setter
    def set_totalCases(self, value):
        if isinstance(value, str):
            if value.isdigit():
                pass
            else:
                raise TypeError(
                    "You passed a non-digit string, which is not acceptable."
                )
            self._total = int(value)
        elif isinstance(value, int):
            self._total = value
        else:
            raise TypeError("Unacceptable value. Try again.")

    def __str__(self):
        def prettyAmount(amt):
            quotient = amt / 1000
            remainder = amt % 1000
            leftSide = len(str(amt // 1000))
            if amt < 1000:
                return f"{amt} mL"
            elif remainder == 0:
                return f"{amt//1000} L"
            elif remainder % 100 == 0:
                leftSide += 1
            elif remainder % 10 == 0:
                leftSide += 2
            else:
                leftSide += 3
            # .format method : "{num:.{p}} L".format(num=amt/1000, p=leftSide)
            return f"{amt/1000:.{leftSide}} L"

        return f"{prettyAmount(self.amount)} Case"
