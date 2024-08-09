from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash
import time
import sqlite3

db = SqliteDatabase('banking.db')

class BaseModel(Model):
    class Meta:
        database = db

class Bank(BaseModel):
    username = CharField(primary_key=True)
    password = TextField()
    surname = CharField()
    name = CharField()
    patronymic = CharField(null=True)
    passport = CharField(unique=True)
    passport_issued_by = CharField()
    passport_issue_date = CharField()
    id_number = CharField(unique=True)
    birth_place = CharField()
    birth_date = CharField()
    registration_city = CharField()
    current_address = CharField()
    phone = CharField()
    email = CharField()
    citizenship = CharField()
    disability = CharField(null=True)
    gender = CharField()
    marital_status = CharField()
    pensioner = CharField()

class Credits(BaseModel):
    credit_id = AutoField()
    username = ForeignKeyField(Bank, backref='credits')
    amount = FloatField()
    rate = CharField()
    term = CharField()
    status = CharField()
    last_update_time = FloatField()
    paid_amount = FloatField(default=0)
    accumulated_interest = FloatField(default=0)
    created_at = FloatField(default=time.time)  # Добавляем поле created_at со значением по умолчанию

    class Meta:
        db_table = 'credits'
        
class BankAccount(BaseModel):
    username = ForeignKeyField(Bank, backref='bank_account')
    balance = FloatField(default=0.0)

    class Meta:
        db_table = 'bank_accounts'


def initialize_db():
    db.create_tables([Bank, Credits, BankAccount], safe=True)

def update_account(username, email, phone, address):
    try:
        account = Bank.get(Bank.username == username)
        account.email = email
        account.phone = phone
        account.current_address = address
        # Обновите здесь другие поля, если это необходимо
        account.save()
        return True
    except Exception as e:
        return str(e)

def add_account(username, password, surname, name, patronymic, passport, passport_issued_by, passport_issue_date, id_number, birth_place, birth_date, registration_city, current_address, phone, email, citizenship, disability, gender, marital_status, pensioner):
    hashed_password = generate_password_hash(password)
    try:
        return Bank.create(username=username, password=hashed_password, surname=surname, name=name, patronymic=patronymic, passport=passport, passport_issued_by=passport_issued_by, passport_issue_date=passport_issue_date, id_number=id_number, birth_place=birth_place, birth_date=birth_date, registration_city=registration_city, current_address=current_address, phone=phone, email=email, citizenship=citizenship, disability=disability, gender=gender, marital_status=marital_status, pensioner=pensioner)
    except IntegrityError as e:
        return str(e)

def get_account(username):
    return Bank.get_or_none(Bank.username == username)

def check_account(username, password):
    account = get_account(username)
    if account and check_password_hash(account.password, password):
        return True
    return False

def apply_for_credit(username, amount, rate, term):
    user = get_account(username)
    if user:
        # Преобразование процентной ставки в десятичную дробь, если она передана в виде строки, например "5%"
        if isinstance(rate, str) and rate.endswith('%'):
            rate = float(rate.strip('%')) / 100
        # Создание записи о кредите в базе данных
        Credits.create(
            username=user,
            amount=amount,
            rate=rate,
            term=term,
            status="active",
            last_update_time=time.time(),
            accumulated_interest=0,
            paid_amount=0
        )
        return True
    return False

def update_credit_interests():
    current_time = time.time()
    # Перебор всех активных кредитов
    for credit in Credits.select().where(Credits.status == 'active'):
        # Определение длительности "года" в секундах в зависимости от срока кредита
        term_mapping = {'1 год': 100, '2 года': 200, '3 года': 300}
        year_seconds = term_mapping.get(credit.term, 100)
        
        # Расчет общей суммы процентов для начисления за весь срок кредита
        total_interest = credit.amount * (float(credit.rate) * year_seconds / 100)
        
        # Расчет количества прошедших интервалов с момента последнего обновления
        intervals_passed = (current_time - credit.last_update_time) // 10
        
        if intervals_passed > 0:
            # Расчет процентов за интервал
            interest_per_interval = total_interest / (year_seconds / 10)
            # Начисление процентов за прошедшие интервалы
            credit.accumulated_interest += interest_per_interval * intervals_passed
            # Обновление времени последнего обновления
            credit.last_update_time = current_time - ((current_time - credit.last_update_time) % 10)
            credit.save()
            
            if (current_time - credit.created_at) >= year_seconds:
                if credit.status == 'active' and (credit.amount + credit.accumulated_interest) > credit.paid_amount:
                    credit.status = 'due'  # Статус, означающий что кредит к погашению, но проценты больше не капают
                    credit.save()
                elif credit.status == 'active' and (credit.amount + credit.accumulated_interest) <= credit.paid_amount:
                    credit.status = 'expired'  # Статус для полностью погашенных кредитов
                    credit.save()


def get_credits(username):
    user = get_account(username)
    if user:
        credits = Credits.select().where(Credits.username == user)
        return [credit for credit in credits]
    return []

def make_credit_payment(credit_id, payment_amount):
    credit = Credits.get_or_none(Credits.credit_id == credit_id, (Credits.status == 'active') | (Credits.status == 'due'))
    if credit:
        # Получаем аккаунт пользователя, ассоциированный с кредитом
        user_account = BankAccount.get_or_none(BankAccount.username == credit.username)
        if user_account and user_account.balance >= payment_amount:
            # Вычитаем сумму платежа из баланса пользователя
            user_account.balance -= payment_amount
            user_account.save()
            
            # Обновляем сумму выплат по кредиту
            credit.paid_amount += payment_amount
            remaining_amount = (credit.amount + credit.accumulated_interest) - credit.paid_amount
            if remaining_amount <= 0:
                credit.status = 'closed'  # Закрываем кредит, если он полностью выплачен
            credit.save()
            
            return f"Кредит успешно погашен. Оставшаяся сумма кредита: {max(0, remaining_amount):.2f}. Ваш текущий баланс: {user_account.balance:.2f}"
        else:
            return "На вашем счету недостаточно средств для погашения кредита."
    return "Кредит не найден или уже закрыт."


def close_credit(credit_id):
    credit = Credits.get_or_none(Credits.credit_id == credit_id)
    if credit:
        credit.status = 'closed'
        credit.save()

def check_username_exists(username):
    return Bank.select().where(Bank.username == username).exists()

def check_passport_exists(passport):
    return Bank.select().where(Bank.passport == passport).exists()

def get_all_accounts():
    # Возвращает список имен пользователей
    return [account.username for account in Bank.select(Bank.username)]

def check_id_number_exists(id_number):
    return Bank.select().where(Bank.id_number == id_number).exists()

def get_account_details(username):
    try:
        account = BankAccount.get(BankAccount.username == username)
        return account
    except BankAccount.DoesNotExist:
        return None

def top_up_account(username, amount):
    try:
        account, created = BankAccount.get_or_create(username=username)
        account.balance += amount
        account.save()
        return True
    except Exception as e:
        print(e)  # В реальном приложении используйте логирование
        return False
    
def delete_user(username):
    conn = sqlite3.connect('banking.db')
    c = conn.cursor()
    c.execute('DELETE FROM bank WHERE username = ?', (username,))
    conn.commit()
    conn.close()