
# First-Party
from address.models import AddressField
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from hashid_field import HashidAutoField
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField

# Local
from .managers import UserManager


class Account(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
        default='',
    )
    address = AddressField(
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    email = models.EmailField(
        blank=True,
        null=True,
    )
    phone = PhoneNumberField(
        blank=True,
        null=True,
    )
    is_public = models.BooleanField(
        default=False,
    )
    is_teacher = models.BooleanField(
        default=False,
    )
    is_medical = models.BooleanField(
        default=False,
    )
    comments = models.TextField(
        max_length=2000,
        blank=True,
        default='',
    )
    notes = models.TextField(
        max_length=2000,
        blank=True,
        default='',
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    user = models.OneToOneField(
        'app.User',
        on_delete=models.CASCADE,
        related_name='account',
        null=True,
        unique=True,
    )

    def __str__(self):
        return f"{self.name}"


class School(models.Model):

    LEVEL = Choices(
        (510, 'ps', 'Preschool'),
        (520, 'elem', 'Elementary'),
        (530, 'intmidjr', 'Intermediate/Middle/Junior High'),
        (540, 'hs', 'High School'),
        (550, 'elemhigh', 'Elementary-High Combination'),
        (555, 'secondary', 'Secondary'),
        (560, 'a', 'Adult'),
        (570, 'ug', 'Ungraded'),
    )
    GRADE = Choices(
        (-1, 'p', 'Preschool'),
        (0, 'k', 'Kindergarten'),
        (1, 'first', 'First Grade'),
        (2, 'second', 'Second Grade'),
        (3, 'third', 'Third Grade'),
        (4, 'fourth', 'Fourth Grade'),
        (5, 'fifth', 'Fifth Grade'),
        (6, 'sixth', 'Sixth Grade'),
        (7, 'seventh', 'Seventh Grade'),
        (8, 'eighth', 'Eighth Grade'),
        (9, 'ninth', 'Ninth Grade'),
        (10, 'tenth', 'Tenth Grade'),
        (11, 'eleventh', 'Eleventh Grade'),
        (12, 'twelfth', 'Twelfth Grade'),
    )
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=255,
        blank=False,
    )
    level = models.IntegerField(
        blank=True,
        null=True,
        choices=LEVEL,
    )
    nces_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
    )
    low_grade = models.IntegerField(
        blank=True,
        choices=GRADE,
        null=True,
    )
    high_grade = models.IntegerField(
        blank=True,
        choices=GRADE,
        null=True,
    )
    grades = ArrayField(
        models.IntegerField(
            choices=GRADE,
        ),
        blank=True,
        null=True,
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    city = models.CharField(
        max_length=255,
        blank=False,
        default='',
    )
    state = models.CharField(
        max_length=255,
        blank=False,
        default='',
    )
    zipcode = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    county = models.CharField(
        max_length=255,
        blank=True,
    )
    phone = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    website = models.URLField(
        blank=True,
        default='',
    )
    lat = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )
    lon = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    # search_vector = SearchVectorField(
    #     null=True,
    # )

    def __str__(self):
        return f"{self.name}"

    def location(self):
        return (self.lat, self.lon)

    def grades_display(self):
        return [self.GRADE[x] for x in self.grades]

    def should_index(self):
        return True

    # class Meta:
    #     indexes = [
    #         GinIndex(fields=['search_vector'])
    #     ]


class Student(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    name = models.CharField(
        max_length=100,
        blank=False,
        default='',
        help_text="""Please add your student's name or initials.  Will remain private!""",
    )
    GRADE = Choices(
        (-1, 'p', 'Preschool'),
        (0, 'k', 'Kindergarten'),
        (1, 'first', 'First Grade'),
        (2, 'second', 'Second Grade'),
        (3, 'third', 'Third Grade'),
        (4, 'fourth', 'Fourth Grade'),
        (5, 'fifth', 'Fifth Grade'),
        (6, 'sixth', 'Sixth Grade'),
        (7, 'seventh', 'Seventh Grade'),
        (8, 'eighth', 'Eighth Grade'),
        (9, 'ninth', 'Ninth Grade'),
        (10, 'tenth', 'Tenth Grade'),
        (11, 'eleventh', 'Eleventh Grade'),
        (12, 'twelfth', 'Twelfth Grade'),
    )
    grade = models.IntegerField(
        blank=False,
        choices=GRADE,
        help_text='Grade',
    )
    school = models.ForeignKey(
        'app.School',
        on_delete=models.CASCADE,
        related_name='schools',
    )
    account = models.ForeignKey(
        'app.Account',
        on_delete=models.CASCADE,
        related_name='schools',
    )


class Email(models.Model):
    id = HashidAutoField(
        primary_key=True,
    )
    KIND = Choices(
        (100, 'inbound', 'Inbound'),
        (200, 'outbound', 'Outbound'),
    )
    kind = models.IntegerField(
        blank=True,
        null=True,
        choices=KIND,
    )
    headers = models.TextField(
        blank=True,
        null=True,
        verbose_name='Headers',
    )
    dkim = models.TextField(
        blank=True,
        null=True,
        verbose_name='DomainKeys Identified Mail',
    )
    to_email = models.TextField(
        blank=True,
        null=True,
        verbose_name='To',
    )
    cc = models.TextField(
        blank=True,
        null=True,
        verbose_name='cc',
    )
    text = models.TextField(
        blank=True,
        null=True,
        verbose_name='Text',
    )
    html = models.TextField(
        blank=True,
        null=True,
        verbose_name='HTML',
    )
    from_email = models.TextField(
        blank=True,
        null=True,
        verbose_name='From',
    )
    sender_ip = models.TextField(
        blank=True,
        null=True,
        verbose_name='Sender IP',
    )
    spam_report = models.TextField(
        blank=True,
        null=True,
        verbose_name='Spam report',
    )
    envelope = models.TextField(
        blank=True,
        null=True,
        verbose_name='Envelope',
    )
    attachments = models.TextField(
        blank=True,
        null=True,
        verbose_name='Attachments',
    )
    subject = models.TextField(
        blank=True,
        null=True,
        verbose_name='Subject',
    )
    spam_score = models.TextField(
        blank=True,
        null=True,
        verbose_name='Spam score',
    )
    charsets = models.TextField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Charsets',
    )
    SPF = models.TextField(
        blank=True,
        null=True,
        verbose_name='Sender Policy Framework',
    )
    user = models.ForeignKey(
        'app.User',
        on_delete=models.SET_NULL,
        related_name='emails',
        null=True,
        blank=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )


class User(AbstractBaseUser):
    id = HashidAutoField(
        primary_key=True,
    )
    username = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        unique=True,
    )
    data = models.JSONField(
        null=True,
        editable=False,
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        default='(Unknown)',
        verbose_name="Name",
        editable=False,
    )
    email = models.EmailField(
        blank=True,
        null=True,
        editable=False,
    )
    picture = models.URLField(
        max_length=512,
        blank=True,
        default='https://www.kidsallin.com/static/app/unknown_small.png',
        verbose_name="Picture",
        editable=False,
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_admin = models.BooleanField(
        default=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [
    ]

    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return str(self.name)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
