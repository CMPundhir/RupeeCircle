from django.db import models
from apps.mauth.models import BaseModel
from apps.mauth.models import CustomUser as User
from apps.mauth.middleware import get_current_authenticated_user
import datetime
import uuid

# Create your models here.


class TermsAndCondition(models.Model):
    id = models.AutoField(primary_key=True)
    tnc = models.CharField(max_length=255)


class LoanApplication(BaseModel, models.Model):
    STATUS_CHOICES = (('APPLIED', 'APPLIED'), ('UNDER BIDDING', 'UNDER BIDDING'), ('CLOSED', 'CLOSED'))
    REPAYMENT_CHOICES = (('DAILY', 'DAILY'), ('MONTHLY', 'MONTHLY'), ('QUARTERLY', 'QUARTELY'), ('ANNUALLY', 'ANNUALLY'))
    TYPE_CHOICES = (('OPEN BID', 'OPEN BID'), ('CLOSE BID', 'CLOSE BID'))

    id = models.AutoField(primary_key=True)
    loan_amount = models.IntegerField(null=False, blank=False)
    plan_id = models.CharField(max_length=1000, blank=True, unique=True)
    interest_rate = models.CharField(max_length=255, null=False, blank=False)
    tenure = models.IntegerField(null=True, blank=True)
    repayment_terms = models.CharField(max_length=1000, 
                                       choices=REPAYMENT_CHOICES,
                                       null=True, blank=True)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][1])
    installments = models.CharField(max_length=1000, null=True, blank=True)
    collateral = models.CharField(max_length=255, null=True, blank=True)
    late_pay_penalties = models.CharField(max_length=255, null=True, blank=True)
    prepayment_options = models.CharField(max_length=255, null=True, blank=True)
    default_remedies = models.CharField(max_length=1000, null=True, blank=True)
    privacy = models.CharField(max_length=1000, null=True, blank=True)
    governing_law = models.CharField(max_length=1000, null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='borrower')
    investors = models.ManyToManyField(User, blank=True)#, related_name='investor')
    tnc = models.ForeignKey(TermsAndCondition, on_delete=models.DO_NOTHING, null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][1])

    def __str__(self):
        return f'{self.id}'
    
    def save(self, *args, **kwargs):
        if LoanApplication.objects.all().count() == 0:
            self.plan_id = f'PLAN1'
        else:
            last_object = LoanApplication.objects.latest('id')#all().order_by('-id')[0]
            self.plan_id = f"PLAN{last_object.id + 1}"
        super(LoanApplication, self).save(*args, **kwargs)


class InvestmentProduct(BaseModel, models.Model):
    TYPE_CHOICES = (('FIXED ROI', 'FIXED ROI'), ('ANYTIME WITHDRAWAL', 'ANYTIME WITHDRAWAL'))
    PRINCIPAL_CHOICES = (('FIXED', 'FIXED'), ('VARIABLE', 'VARIABLE'))
    id = models.AutoField(primary_key=True)
    plan_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    min_amount = models.IntegerField(null=True, blank=True)
    minimum_locking = models.CharField(max_length=255, null=True, blank=True)
    amount = models.IntegerField(null=False, blank=False)
    investing_limit = models.IntegerField(null=True)
    principal_type = models.CharField(max_length=255, choices=PRINCIPAL_CHOICES, default=PRINCIPAL_CHOICES[0][1])
    interest_rate = models.CharField(max_length=255, null=False, blank=False)
    tenure = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][1])
    is_special_plan = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    allowed_investor = models.ManyToManyField(User, related_name='allowed_investor')
    investors_detail = models.ManyToManyField(User, related_name='investor_detail')
    investors = models.IntegerField(default=0)
    invested_amount = models.BigIntegerField(default=0)
    tnc = models.ForeignKey(TermsAndCondition, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f'{self.plan_id}'


    def save(self, *args, **kwargs):
        if InvestmentProduct.objects.all().count() == 0:
            self.plan_id = f'PLAN1'
        else:
            last_object = InvestmentProduct.objects.latest('id')#all().order_by('-id')[0]
            self.plan_id = f"PLAN{last_object.id + 1}"
        super(InvestmentProduct, self).save(*args, **kwargs)


class Installment(BaseModel, models.Model):
    STATUS_CHOICES = (('PENDING', 'PENDING'), ('PAID', 'PAID'))
    id = models.AutoField(primary_key=True)
    parent_loan = models.ForeignKey('Loan', on_delete=models.DO_NOTHING)
    due_date = models.DateField()
    principal = models.CharField(max_length=255, null=True, blank=True)
    interest = models.CharField(max_length=255, null=True, blank=True)
    total_amount = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][1])
    paid_date = models.DateField(blank=True, null=True)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)
    late_fee = models.CharField(max_length=255, null=True, blank=True)


class InvestmentRequest(BaseModel, models.Model):
    STATUS_CHOICES = (('PENDING', 'PENDING'), ('APPROVED', 'APPROVED'))
    TYPE_CHOICES = (('FIXED ROI', 'FIXED ROI'), ('ANYTIME WITHDRAWAL', 'ANYTIME WITHDRAWAL'), ('LOAN', 'LOAN'))
    id = models.AutoField(primary_key=True)
    loan_amount = models.IntegerField(default=0)
    tenure = models.IntegerField(null=True)
    interest_rate = models.IntegerField(null=True, blank=True)
    repayment_terms = models.CharField(max_length=255, null=True, blank=True)
    installments = models.IntegerField(null=True, blank=True)
    collateral = models.CharField(max_length=255, null=True, blank=True)
    late_pay_penalties = models.CharField(max_length=255, null=True, blank=True)
    prepayment_options = models.CharField(max_length=255, null=True, blank=True)
    # plan = models.ForeignKey(InvestmentProduct, on_delete=models.DO_NOTHING, null=True, blank=True)
    loan = models.ForeignKey(LoanApplication, on_delete=models.DO_NOTHING, null=True, blank=True)
    default_remedies = models.CharField(max_length=255, null=True, blank=True)
    privacy = models.CharField(max_length=255, null=True, blank=True)
    governing_law = models.CharField(max_length=255, null=True, blank=True)
    investor = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    borrower = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='loan_borrower', null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][1])
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][1])

    def __str__(self):
        return f'{self.id}'
    
    def save(self, *args, **kwargs):
        user = get_current_authenticated_user()
        self.created_by = user
        super(InvestmentRequest, self).save(*args, **kwargs)


class Loan(BaseModel, models.Model):
    STATUS_CHOICES = (('ONGOING', 'ONGOING'), ('PAID', 'PAID'))
    
    id = models.AutoField(primary_key=True)
    loan_amount = models.IntegerField(null=False, blank=False)
    loan_id = models.CharField(max_length=1000, blank=True, unique=True)
    minimum_locking = models.CharField(max_length=255, blank=True, null=True)
    tenure = models.IntegerField(null=True)
    product = models.ForeignKey(InvestmentProduct, on_delete=models.DO_NOTHING, null=True, blank=True)
    # interest_calculation_type = models.CharField(max_length=255, 
    #                                              choices=REPAYMENT_CHOICES, 
    #                                              default=REPAYMENT_CHOICES[1][0])
    interest_rate = models.CharField(max_length=255, null=False, blank=False)
    repayment_terms = models.CharField(max_length=255, 
                                      choices=LoanApplication.REPAYMENT_CHOICES, 
                                      default=LoanApplication.REPAYMENT_CHOICES[1][0], null=True, blank=True)
    installments = models.ManyToManyField(Installment, blank=True)
    collateral = models.CharField(max_length=255, null=True, blank=True)
    late_pay_penalties = models.CharField(max_length=255, null=True, blank=True)
    prepayment_options = models.CharField(max_length=255, null=True, blank=True)
    default_remedies = models.CharField(max_length=1000, null=True, blank=True)
    privacy = models.CharField(max_length=1000, null=True, blank=True)
    governing_law = models.CharField(max_length=1000, null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='final_loan_borrower')
    investor = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, related_name='final_loan_investor',null=True)
    type = models.CharField(max_length=255, choices=InvestmentRequest.TYPE_CHOICES, default=InvestmentRequest.TYPE_CHOICES[0][1])
    is_tnc_accepted = models.BooleanField(default=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][1])
    tnc = models.ForeignKey(TermsAndCondition, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f'{self.loan_id}'
    
    def save(self, *args, **kwargs):
        if Loan.objects.all().count() == 0:
            self.loan_id = f'LOAN1'
        else:
            last_object = Loan.objects.latest('id')#all().order_by('-id')[0]
            self.loan_id = f"LOAN{last_object.id + 1}"
        super(Loan, self).save(*args, **kwargs)


class Product(BaseModel, models.Model):
    TYPE_CHOICES = (('FIXED ROI', 'FIXED ROI'), ('ANYTIME WITHDRAWAL', 'ANYTIME WITHDRAWAL'), ('SIP', 'SIP'))
    PRINCIPAL_CHOICES = (('FIXED', 'FIXED'), ('VARIABLE', 'VARIABLE'))
    id = models.AutoField(primary_key=True)
    plan_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    min_amount = models.IntegerField(null=True, blank=True)
    max_amount = models.IntegerField(null=True, blank=True)
    minimum_locking = models.CharField(max_length=255, null=True, blank=True)
    # investing_limit = models.IntegerField(null=True)
    # principal_type = models.CharField(max_length=255, choices=PRINCIPAL_CHOICES, default=PRINCIPAL_CHOICES[0][1])
    interest_rate = models.FloatField()
    min_tenure = models.IntegerField(null=True, blank=True)
    max_tenure = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][1])
    is_special_plan = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    # allowed_investor = models.ManyToManyField(User, related_name='product_allowed_investors')
    # investors_detail = models.ManyToManyField(User, related_name='investor_detail')
    investors = models.IntegerField(default=0)
    invested_amount = models.BigIntegerField(default=0)
    tnc = models.ForeignKey(TermsAndCondition, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.plan_id
    
    def save(self, *args, **kwargs):
        # if InvestmentProduct.objects.all().count() == 0:
        if len(str(self.min_tenure)) < 2:
            min_tenure_in_id = f'0{self.min_tenure}'
        else:
            min_tenure_in_id = f'{self.min_tenure}'
        if len(str(self.max_tenure)) < 2:
            max_tenure_in_id = f'0{self.max_tenure}'
        else:
            max_tenure_in_id = f'{self.max_tenure}'
        rate = str(self.interest_rate)
        if len(rate) < 5:
            rate_in_id = f"0{rate.replace('.', '')}"
        else:
            rate_in_id = f"{rate.replace('.', '')}"
        # rate_in_id = f'{self.interest_rate}'
        self.plan_id = f'{self.type[0:2]}{min_tenure_in_id}{max_tenure_in_id}{rate_in_id}'
        # else:
        #     last_object = InvestmentProduct.objects.latest('id')#all().order_by('-id')[0]
        #     self.plan_id = f"PLAN{last_object.id + 1}"
        super(Product, self).save(*args, **kwargs)


class Payment(BaseModel, models.Model):
    STATUS_CHOICES = (('PENDING', 'PENDING'), ('PAID', 'PAID'))
    id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=100, blank=True, null=True)
    # investment = models.ForeignKey('Investment', on_delete=models.DO_NOTHING)
    investor = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    due_date = models.DateField()
    amount = models.FloatField()
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][1])


class Investment(BaseModel, models.Model):
    INTEREST_PAYMENT = (('DAILY', 'DAILY'), ('MONTHLY', 'MONTHLY'), ('QUARTERLY', 'QUARTERLY'), ('ANNUALLY', 'ANNUALLY'))
    id = models.AutoField(primary_key=True)
    principal = models.IntegerField()
    # investment_id = models.CharField(max_length=100)
    interest_rate = models.FloatField()
    tenure = models.IntegerField()
    product = models.ForeignKey('NewProduct', on_delete=models.DO_NOTHING)
    investor = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    interest_payment = models.CharField(max_length=100, choices=INTEREST_PAYMENT, default=INTEREST_PAYMENT[1][0])
    installments = models.ManyToManyField(Payment)

    # def save(self, *args, **kwargs):
    #     all_investments = Investment.objects.all()
    #     if len(all_investments) == 0:
            
    #     self.investment_id = f"INV{self.product.plan_id}"
    #     super(Product, self).save(*args, **kwargs)


class Param(models.Model):
    id = models.AutoField(primary_key=True)
    min_amount = models.IntegerField()
    max_amount = models.IntegerField()
    min_tenure = models.IntegerField()
    max_tenure = models.IntegerField()
    min_interest = models.FloatField()
    max_interest = models.FloatField()


class NewProduct(BaseModel, models.Model):
    TYPE_CHOICES = (('FIXED', 'FIXED'), ('FLEXI', 'FLEXI'))
    id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    month = models.IntegerField()
    interest_rate = models.FloatField()

    def save(self, *args, **kwargs):
        # if self.type == self.TYPE_CHOICES[1][1]:
        #     self.month = 0
        if len(NewProduct.objects.all()) == 0:
            self.product_id = f"PLAN{self.type}{self.month}{1}"
        else:
            product_exist = NewProduct.objects.filter(id=self.id).exists()
            if product_exist:
                pass
            else:
                latest_id = NewProduct.objects.latest('id')
                self.product_id = f"PLAN{self.type}{self.month}{latest_id.id}"
        super(NewProduct, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_id

