# Import statements
import os
import csv
import requests
import json
import datetime
from practice_api import call_api
from flask import Flask, render_template, session, redirect, request, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError, SelectField, IntegerField, DateField, FieldList, FormField, FloatField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename

# Imports for login management
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Application configurations
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = 'hardtoguessstring'
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL') or "postgresql://localhost/SI364projectplanaslabot"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# App migrations
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# Login configuration
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

########################
######## Models ########
########################

## User-related Models
bakers_orders = db.Table('bakers_orders',
              db.Column('uid', db.Integer, db.ForeignKey('Users.id'), primary_key=True),
              db.Column('oid', db.Integer, db.ForeignKey('Orders.id'), primary_key=True)
)

# Special model for users to log in
class Users(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String)
    privilages = db.Column(db.Integer)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Orders(db.Model):
    __tablename__ = "Orders"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('Users.id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now().date())
    organization = db.Column(db.String(125))
    bread_type = db.Column(db.String(64))
    quantity = db.Column(db.Integer)
    bakers = db.relationship("Users", secondary=bakers_orders, lazy='dynamic', backref=db.backref('Orders', lazy=True))
    user = db.relationship("Users")

class Inventory(db.Model):
    __tablename__ = "Inventory"
    id = db.Column(db.Integer, primary_key=True)
    ingredient = db.Column(db.String(64))
    quantity = db.Column(db.Float)

class Bread_type(db.Model):
    __tablename__ = "Bread_type"
    id = db.Column(db.Integer, primary_key=True)
    bread_type = db.Column(db.String(64))

"""class Invoices(db.Model):
    __tablename__ = "Invoices"
    id = db.Column(db.Integer, primary_key=True)
    oid = db.Column(db.Integer, db.ForeignKey('Orders.id'))
    date = db.Column(db.Date)
    amount = db.Column(db.Float)
    paid = db.Column(db.Boolean)"""

########################
######## Forms #########
########################

#This form will take account info and create a new account in the registration form
class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    role = SelectField('What are you?:', choices=[('b', 'baker'), ('o', 'organization'), ('a', 'admin'), ('j', 'John')])
    submit = SubmitField('Register User')

    #Additional checking methods for the form
    def validate_email(self,field):
        if Users.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if Users.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')


#This form will take account info and log in a user
class LoginForm(FlaskForm):
    username = StringField('username', validators=[Required(), Length(1,255)])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

#Will take a spreadsheet of the current inventory and make it queryable by certain users
class InventoryInputForm(FlaskForm):
    file = FileField("Submit a CSV file here", validators=[FileAllowed(['csv'])])

def validate_quantity(form, field):
    if field.data % 20:
        raise ValidationError("Must be a multiple of 20")

class OrderBreadForm(FlaskForm):
    bread_type = SelectField("Enter a type of bread: ", choices=[("", ""), ("Vegan", "Vegan"), ("Chocolate Chip", "Clocolate Chip"), ("Zucchini", "Zucchini"), ("Blueberry", "Blueberry")], validators=[Required()])
    quantity = IntegerField("Enter a quantity as a multiple of 20: ", validators=[Required(), validate_quantity])

#User will place a new order with this form. Order will be added to database
class OrderInputForm(FlaskForm):
    organization = StringField("Enter your organization name: ", validators=[Required()])
    breads = FieldList(FormField(OrderBreadForm), min_entries=1)

#Users input information about orders and view function will return the related invoice
class QueryInvoiceForm(FlaskForm):
    invoices = SelectField("Select an invoice: ")

#Users input information about order and view function will return order information and status
class QueryOrdersForm(FlaskForm):
    orders = SelectMultipleField("Select an order: ")

def validate_quantity(form,field):
        if field.data > 2147483647:
            raise ValidationError("Quantity too big")

#User inputs inventory query and information about current inventory is returned
class InventoryUpadateForm(FlaskForm):
    ingredient = StringField("Enter Ingredient: ", validators=[Required()])
    quantity = FloatField("Enter quantity: ", validators=[Required(), validate_quantity])

########################
### Helper functions ###
########################
def get_or_create_ingredient(ingredient, quantity=0.0):
    i = Inventory.query.filter_by(ingredient=ingredient).first()
    if not i:
        i = Inventory(ingredient=ingredient, quantity=quantity)
        db.session.add(i)
        db.session.commit()        
    return i

def get_or_create_bread_type(bread_type):
    bread = Bread_type.query.filter_by(bread_type=bread_type).first()
    if not bread:
         bread = Bread_type(bread_type=bread_type)
         db.session.add(bread)
         db.session.commit()
    return bread

def my_recipe(flavor):
    '''ingredients['almond_milk'] = 1.0 #Inventory.query.find_by(ingredient = "almond milk").first().quantity
        ingredients['bananas'] += 12.0 #Inventory.query.find_by(ingredient = "bananas").first().quantity
        ingredients['nutmeg'] = 0.0,
        'millet' = 0.0,
        'maple_syrup' = 0.0,
        'flax_meal' = 0.0'''
    ingredients = {
        'bananas': 12.0,
        'salt': 4.0,
        'oat_flower': 8.0,
        'brown_sugar': 4.0,
        'baking_soda': 4.0,
        'baking_powder': 4.0,
        'cinnamon': 4.0,
        'coconut_oil': 1.0
    }
    if flavor == 'vegan':
        ingredients['almond_milk'] = 1.0
        ingredients['bananas'] += 12.0
        ingredients['nutmeg'] = 1.0
        ingredients['millet'] = 1.0
        ingredients['maple_syrup'] = 0.5
        ingredients['flax_meal'] = 2.0

    else:
        ingredients['eggs'] = 8.0
        ingredients['honey'] = 0.5
        ingredients['vanilla'] = 0.5
        ingredients['greek_yogurt'] = 4.0
        if flavor == 'Chocolate Chip':
            ingredients['chocolate_chip'] = 2.0
        elif flavor == 'Blueberry':
            ingredients['blueberries'] = 2.0
        elif flavor == 'Zucchini':
            ingredients['zucchini'] = 2.0
    return ingredients

########################
#### View functions ####
########################

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/secret')
@login_required
def secret():
    return "Only authenticated users can do this! Try to log in or contact the site admin."

## Login-related routes - provided
@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#gives the user an option of which page to go to
@app.route('/')
def index():
    plan = call_api("44.761527,-69.322662")
    if not plan:
        return page_not_found(404)
    breads = Bread_type.query.all()
    return render_template('index.html', plan=plan, breads=breads)

@app.route('/flavors', methods=["GET", "POST"])
def flavors():
    new_flavor = ""
    if request.method == "POST":
        new = request.form['new']
        new_flavor = get_or_create_bread_type(new).bread_type

    return render_template('flavors.html', flavor=new_flavor)

# This will calculate how many groceries I need to buy that week 
@app.route('/grocery_list',methods=["GET"])
@login_required
def grocery_list():
    try:
        d = datetime.datetime.today() - datetime.timedelta(days=7)
        orders = Orders.query.filter(Orders.date > d).all()
    except:
        return internal_server_error(500)
    total_needed = {}
    for order in orders:
        ingredients = my_recipe(order.bread_type)
        for i, q in ingredients.iteritems():
            if i in total_needed:
                total_needed[i] += q
            else:
                total_needed[i] = q
    inventory_entries = Inventory.query.all()
    inventory = {}
    for entry in inventory_entries:
        inventory[entry.ingredient] = entry.quantity
    for ingredient, quantity in inventory.iteritems():
        if ingredient in total_needed:
            temp = total_needed[ingredient]
            total_needed[ingredient] -= inventory[ingredient]
            inventory[ingredient] -= temp
            rows_changed = Inventory.query.filter_by(ingredient=ingredient).update(dict(quantity=inventory[ingredient]))
    dictlist = []
    for key, value in total_needed.iteritems():
        if value > 0:
            temp = [key,value]
            dictlist.append(temp)
    db.session.commit()
    return render_template('grocery_list.html', needed=dictlist)


# Combines all the orders from all the retailers so that I know the total amount of breads I need to make 
# Orders can also be placed in this view function. All orders can be seen.
@app.route('/orders',methods=["GET", "POST"])
@login_required
def orders():
    form = QueryOrdersForm()
    orders = Orders.query.filter_by(uid=current_user.id).all()
    choices = [(o.id, o.date) for o in orders]
    form.orders.choices = choices
    lst = []
    if request.method == "POST":
        try:
            if request.form['submit'] == "Submit":
                orders = request.form['orders']
                for order in orders:
                    o = Orders.query.filter_by(id=order).first()
                    lst.append(o)
        except:
            o = Orders.query.order_by(Orders.id.desc()).first()
            lst.append(o)
    return render_template('orders.html', form=form, orders=lst)
            
    
# Orders can also be placed in this view function. All orders can be seen.
@app.route('/order',methods=["GET", "POST"])
@login_required
def order():
    form = OrderInputForm()
    types = Bread_type.query.all()
    for i in range(3):
        form.breads.append_entry()
    if request.method == 'POST':
        org = request.form['organization']
        i = 0
        print form.breads.data
        for q, b in enumerate(form.breads.data):
            bread_type = b['bread_type']
            quantity = b['quantity']
            if bread_type and quantity:
                o = Orders(organization=org, uid=current_user.id, bread_type=bread_type, quantity=quantity)
                u = Users.query.filter_by(id=current_user.id).first()
                o.bakers.append(u) # just as a test, bakers do not have accounts yet
                db.session.add(o)
                db.session.commit()
        return redirect(url_for('orders'), code=307)
    return render_template('order.html', form=form)

# Takes in inventory sheet, and reroutes to the inventory route
@app.route('/new-inventory-entry',methods=["GET", "POST"])
@login_required
def inventory_entry():
    form = InventoryUpadateForm()
    if form.validate_on_submit():
        new_item = request.form['ingredient']
    return render_template('update_inventory.html', form=form)

# Takes in inventory sheet, and reroutes to the inventory route
@app.route('/inventory',methods=["GET", "POST"])
@login_required
def inventory():
    other_form = InventoryUpadateForm()
    form = InventoryInputForm()
    inventory_records = []

    if request.method == "POST":
        if request.form['submit'] == "Submit File":
            try:
                rows_deleted = db.session.query(Inventory).delete()
                db.session.commit()
            except:
                db.session.rollback()

            filename = secure_filename(form.file.data.filename)
            print filename
            form.file.data.save('inventory/' + filename)
            f = open('inventory/' + filename)
            reader = csv.reader(f)
        
            for row in reader:
                print row
                ingredient = row[0]
                quantity = row[1]    
                i = Inventory(ingredient=ingredient, quantity=quantity)
                db.session.add(i)
            db.session.commit
        elif request.form['submit'] == "Get or Create":
            ingredient = get_or_create_ingredient(request.form['ingredient'])
            inventory_record = [[ingredient.ingredient, ingredient.quantity]]
            return render_template('inventory.html', form=form, other_form=other_form, inventory_records=inventory_record)
        else:
            ingredient_to_delete = request.form['ingredient']
            i = Inventory.query.filter_by(ingredient=ingredient_to_delete).first()
            db.session.delete(i)
            db.session.commit()
            #return render_template('inventory.html', form=form, other_form=other_form, inventory_records=inventory_record)

    q = Inventory.query.all()
    for record in q:
        inventory_records.append([record.ingredient, record.quantity])

    return render_template('inventory.html', form=form, other_form=other_form, inventory_records=inventory_records)
    
if __name__ == '__main__':
    #print str(datetime.date.month) + "/" + str(datetime.date.day) + "/" + str(datetime.date.year)
    #print datetime.datetime.now().date()
    db.create_all()
    app.run()
    #manager.run()
