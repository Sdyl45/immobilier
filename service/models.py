
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models import Sum
from django.utils.timezone import now, localdate
from datetime import timedelta

# ======================
# ROLE
# ======================

class Role(models.Model):
    ADMINISTRATOR = 'administrator'
    PROPERTY_MANAGER = 'property_manager'
    MAINTENANCE_STAFF = 'maintenance_staff'

    ROLE_CHOICES = [
        (ADMINISTRATOR, 'Administrator'),
        (PROPERTY_MANAGER, 'Property Manager'),
        (MAINTENANCE_STAFF, 'Maintenance Staff'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


# ======================
# USER (REMPLACE CLIENT)
# ======================

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) if password else user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(unique=True)
    adresse = models.TextField(blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True)
    password = models.CharField(max_length=200, blank=True) # password
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    token=models.CharField(max_length=200, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


# ======================
# PROPRIETE
# ======================

class Propriete(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('Apartment', 'Apartement'),
        ('Single_Family_Home', 'FamilyHome'),
        ('Commercial', 'commercial'),
    ]

    property_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    total_units = models.IntegerField()
    purchase_date = models.DateField(auto_now_add=True, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='proprietes/', blank=True, null=True)

    def __str__(self):
        return self.property_name

    @classmethod
    def total_proprietes(cls):
        return cls.objects.count()

# ======================
# UNITE
# ======================

class Unite(models.Model):
    TYPE_UNITE_CHOICES = [
        ('appartement', 'Appartement'),
        ('maison', 'Maison'),
        ('bureau', 'Bureau'),
        ('magasin', 'Magasin'),
    ]
    STATUS_CHOICES = [
        ('occupied', 'Occupied'),
        ('vacant', 'Vacant')
    ]

    status = models.CharField(max_length=10,choices=STATUS_CHOICES, default='vacant')
    numero_unite = models.CharField(max_length=10)
    type_unite = models.CharField(max_length=20, choices=TYPE_UNITE_CHOICES)
    superficie = models.DecimalField(max_digits=10, decimal_places=2)
    loyer = models.DecimalField(max_digits=10, decimal_places=2)
    propriete = models.ForeignKey(
        Propriete,
        on_delete=models.CASCADE,
        related_name="units"
    )

    def __str__(self):
        return f"Unite{self.id} - {self.status}"

    @classmethod
    def total_unites(cls):
        return cls.objects.count()


    @classmethod
    def vacant_units(cls):
        return cls.total_units() - cls.occupied_units()

    @classmethod
    def occupancy_rate(cls):
        total = cls.total_units()
        if total == 0:
            return 0
        return (cls.occupied_units() / total) * 100

    @classmethod
    def total_revenue(cls):
        result = cls.objects.filter(
            leases__is_active=True
        ).aggregate(total=Sum("loyer"))

        return result["total"] or 0

    @classmethod
    def occupancy_rate(cls):
        total_unites = cls.total_unites()
        active_leases = Lease.objects.count()
        if total_unites == 0:
            return 0
        return (active_leases/total_unites) * 100



# ======================
# TENANT
# ======================

class Tenant(models.Model):
    TYPE_IDENTITE_CHOICES = [
        ('carte_identite', 'CarteCNI'),
        ('passeport', 'Passeport'),
        ('autre', 'Autre'),
    ]
    STATUS_CHOICES = [
        ('active_current', 'Active current'),
        ('active_late', 'Active late'),
        ('expiring_soon_current', 'Expiring soon current'),
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active_current')
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=255)
    pays = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    type_identite = models.CharField(max_length=20, choices=TYPE_IDENTITE_CHOICES)
    numero_identite = models.CharField(max_length=255)
    date_naissance = models.DateField(auto_now_add=True, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.status}"

    @classmethod
    def total_tenants(cls):
        return cls.objects.count()



# ======================
# LEASE
# ======================


class Lease(models.Model):

    PAYMENT_FREQUENCY_CHOICES = (
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    )

    LEASE_STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    )

    tenant = models.ForeignKey(Tenant,on_delete=models.CASCADE,related_name='leases')
    id_property = models.ForeignKey(Propriete,on_delete=models.CASCADE,null=True)
    unit = models.ForeignKey(Unite,on_delete=models.CASCADE,related_name='leases')
    date_start = models.DateField()
    date_end = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10,decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10,decimal_places=2)
    payment_frequency = models.CharField(max_length=20,        choices=PAYMENT_FREQUENCY_CHOICES,default='monthly')
    payment_due_date = models.PositiveSmallIntegerField(help_text="Day of month payment is due (1-28)")
    late_fee = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    grace_period = models.PositiveSmallIntegerField(blank=True,null=True,help_text="Grace period in days")
    special_terms = models.TextField(blank=True,null=True)
    status = models.CharField(max_length=20,choices=LEASE_STATUS_CHOICES,default='active')
    # ⚠️ Conservé pour compatibilité, mais synchronisé avec status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_start']

    # --------------------
    # STRING REPRESENTATION
    # --------------------
    def __str__(self):
        return f"Lease {self.id} - {self.unit} - {self.tenant}"

    # --------------------
    # PROPERTIES
    # --------------------
    @property
    def is_expired(self):
        return self.date_end < now().date()

    @property
    def is_current(self):
        today = now().date()
        return (
            self.status == 'active'
            and self.date_start <= today
            and self.date_end >= today
        )

    @property
    def is_upcoming(self):
        return self.date_start > now().date()

    # --------------------
    # CLASS METHODS (DASHBOARD)
    # --------------------
    @classmethod
    def active_leases(cls):
        today = now().date()
        return cls.objects.filter(
            status='active',
            date_start__lte=today,
            date_end__gte=today
        )

    @classmethod
    def expiring_soon(cls, days=60):
        today = now().date()
        return cls.objects.filter(
            status='active',
            date_end__range=(today, today + timedelta(days=days))
        )

    @classmethod
    def upcoming_leases(cls):
        return cls.objects.filter(
            date_start__gt=now().date()
        )

    @classmethod
    def total_bails(cls):
        return cls.objects.count()

    @classmethod
    def total_monthly_revenue(cls):
        return cls.active_leases().aggregate(
            total=models.Sum('monthly_rent')
        )['total'] or 0

    # --------------------
    # SAVE OVERRIDE (SYNC STATUS / IS_ACTIVE)
    # --------------------
    def save(self, *args, **kwargs):
        today = now().date()

        if self.date_end < today:
            self.status = 'expired'
            self.is_active = False
        elif self.date_start <= today <= self.date_end:
            self.status = 'active'
            self.is_active = True

        super().save(*args, **kwargs)

# ======================
# INVOICE
# ======================

class Invoice(models.Model):

    INVOICE_TYPE_CHOICES = (
        ('rent', 'Loyer'),
        ('charge', 'Charge'),
        ('other', 'Autre'),
    )

    INVOICE_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
    )

    id_lease = models.ForeignKey(Lease,on_delete=models.CASCADE,related_name='invoices')
    # --------------------
    # DATES
    # --------------------
    date = models.DateField(default=localdate)
    due_date = models.DateField()
    # --------------------
    # FINANCIAL
    # --------------------
    amount = models.DecimalField(max_digits=10,decimal_places=2, help_text="Amount in FCFA")
    invoice_type = models.CharField(max_length=20,choices=INVOICE_TYPE_CHOICES)
    status = models.CharField(max_length=20,choices=INVOICE_STATUS_CHOICES,default='pending')
   # --------------------
    # META
    # --------------------
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-date']
    # --------------------
    # STRING
    # --------------------
    def __str__(self):
        return f"Invoice {self.id} - {self.invoice_type}"
    # --------------------
    # PROPERTIES
    # --------------------
    @property
    def is_overdue(self):
        return self.status != 'paid' and self.due_date < now().date()
    # --------------------
    # CLASS METHODS (COMPATIBLES AVEC TES VIEWS)
    # --------------------
    @classmethod
    def total_invoices(cls):
        """
        TOTAL MONTANT FACTURÉ (FCFA)
        """
        return cls.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0

    @classmethod
    def total_paid(cls):
        return cls.objects.filter(
            status='paid'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

    @classmethod
    def total_pending(cls):
        return cls.objects.filter(
            status='pending'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

    @classmethod
    def total_overdue(cls):
        return cls.objects.filter(
            status='overdue'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

    # --------------------
    # SAVE OVERRIDE (AUTO OVERDUE)
    # --------------------
    def save(self, *args, **kwargs):
        if self.status != 'paid' and self.due_date < now().date():
            self.status = 'overdue'
        super().save(*args, **kwargs)
# ======================
# PAIEMENT
# ======================


class Paiement(models.Model):

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Espèces'),
        ('bank_transfer', 'Virement bancaire'),
        ('mobile_money', 'Mobile Money'),
        ('card', 'Carte de crédit'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('late', 'Late'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    )

    invoice = models.ForeignKey(
        'Invoice',
        on_delete=models.CASCADE,
        related_name='paiements'
    )

    due_date = models.DateField()
    payment_date = models.DateTimeField(default=now)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    transaction_reference = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Paiement {self.id} - {self.status}"

    # -------------------------
    # DASHBOARD CALCULATIONS
    # -------------------------
    @classmethod
    def nombre_paiements(cls):
        return cls.objects.count()

    @classmethod
    def total_received(cls):
        return cls.objects.filter(
            status='paid'
        ).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0

    @classmethod
    def total_paid(cls):
        return cls.objects.filter(status='paid').count()

    @classmethod
    def total_pending(cls):
        return cls.objects.filter(status='pending').count()

    @classmethod
    def total_late(cls):
        return cls.objects.filter(status='late').count()

    @classmethod
    def collection_rate(cls):
        total = cls.objects.count()
        if total == 0:
            return 0
        return round((cls.total_paid() / total) * 100, 2)

#------------------
#maintenance
#----------------------


class Maintenance(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    unit = models.ForeignKey(Unite,on_delete=models.CASCADE,related_name="maintenances")
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

    @classmethod
    def total_maintenance(cls):
        return cls.objects.count()