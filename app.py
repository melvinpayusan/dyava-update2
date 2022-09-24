from flask import Flask, flash, redirect, render_template, request, session, send_from_directory, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, PasswordField,  EmailField, TextAreaField, IntegerField, BooleanField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
from flask_mail import Mail, Message
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_migrate import Migrate


app = Flask(__name__)
app.config["SECRET_KEY"] = "DYAVA (Dimiao Young Aspiring Visual Artists)"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dyava.db"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "dyava.artists@gmail.com"
app.config['MAIL_PASSWORD'] = "trbw rwyz mwib chnm"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.config["UPLOADED_PHOTOS_DEST"] = "static/images"
photos = UploadSet("photos", IMAGES)
configure_uploads(app, photos)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    middlename = db.Column(db.String(100))
    lastname = db.Column(db.String(100), nullable=False)
    profiles = db.relationship("Profiles", backref="artist")
    artworks = db.relationship("Artworks", backref="art")


class Authorize(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), nullable=False)


class Profiles(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(db.String())
    bio = db.Column(db.Text())
    medium = db.Column(db.String())
    style = db.Column(db.String())
    phone = db.Column(db.String())
    facebook = db.Column(db.String())
    instagram = db.Column(db.String())
    address = db.Column(db.String())
    gender = db.Column(db.String())
    age = db.Column(db.String())
    birthday = db.Column(db.String())
    birthplace = db.Column(db.String())
    civilstatus = db.Column(db.String())
    nationality = db.Column(db.String())
    citizenship = db.Column(db.String())
    height = db.Column(db.String())
    weight = db.Column(db.String())
    religion = db.Column(db.String())
    elementary = db.Column(db.String())
    secondary = db.Column(db.String())
    tertiary = db.Column(db.String())
    profile_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class Artworks(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    artpic = db.Column(db.String())
    title = db.Column(db.String())
    type = db.Column(db.String())
    materials = db.Column(db.String())
    size = db.Column(db.String())
    price = db.Column(db.String())
    forsale = db.Column(db.Boolean(), default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    art_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class ArtworkForm(FlaskForm):
    artpic = FileField("", validators=[FileAllowed(photos, "Only images are allowed!")])
    title = StringField("", validators=[Optional()], render_kw={"placeholder": "Title"})
    type = StringField("", validators=[Optional()], render_kw={"placeholder": "Type/Style"})
    materials = StringField("", validators=[Optional()], render_kw={"placeholder": "Medium or Materials Used"})
    size = StringField("", validators=[Optional()], render_kw={"placeholder": "Size"})
    price = IntegerField("", validators=[Optional()], render_kw={"placeholder": "Price"})
    forsale = BooleanField("", validators=[Optional()], render_kw={"placeholder": "For Sale? Check if yes!"})
    submit = SubmitField("Upload Artwork")
    submit2 = SubmitField("Save Changes")
    submit3 = SubmitField("Delete Artwork")


class ContactForm(FlaskForm):
    fullname = StringField("", validators=[DataRequired()], render_kw={"placeholder": "Full Name"})
    email = EmailField("", validators=[DataRequired()], render_kw={"placeholder": "Your Email Address"})
    phone = IntegerField("", validators=[DataRequired()], render_kw={"placeholder": "Your Phone Number"})
    subject = StringField("", validators=[Optional()], render_kw={"placeholder": "Subject"})
    message = TextAreaField("", validators=[DataRequired()], render_kw={"placeholder": "Type your message here: ", "rows" : 5})
    submit = SubmitField("Send Message")


class UpdateForm(FlaskForm):
    picture = FileField("", validators=[FileAllowed(photos, "Only images are allowed!"), Optional()])
    bio = TextAreaField("", validators=[Optional()], render_kw={"placeholder": "Bio: Describe yourself.", "rows" : 5})
    style = StringField("", validators=[Optional()], render_kw={"placeholder": "Art Styles/Genre"})
    medium = StringField("", validators=[Optional()], render_kw={"placeholder": "Art Medium/Materials"})
    phone = IntegerField("", validators=[Optional()], render_kw={"placeholder": "Phone Number: 09091234567"})
    facebook = StringField("", validators=[Optional()], render_kw={"placeholder": "Type your Facebook Name or link to your Page."})
    instagram = StringField("", validators=[Optional()], render_kw={"placeholder": "Type your Instagram Name or Username"})
    address = StringField("", validators=[Optional()], render_kw={"placeholder": "Adress: Purok, Barangay, Municipality, Province"})
    gender = StringField("", validators=[Optional()], render_kw={"placeholder": "Gender"})
    age = IntegerField("", validators=[Optional()], render_kw={"placeholder": "Age"})
    birthday = StringField("", validators=[Optional()], render_kw={"placeholder": "Birthday: MM/DD/YYYY"})
    birthplace = StringField("", validators=[Optional()], render_kw={"placeholder": "Birthplace"})
    civilstatus = StringField("", validators=[Optional()], render_kw={"placeholder": "Civil Status"})
    nationality = StringField("", validators=[Optional()], render_kw={"placeholder": "Nationality"})
    citizenship = StringField("", validators=[Optional()], render_kw={"placeholder": "Citizenship"})
    height = StringField("", validators=[Optional()], render_kw={"placeholder": "Height: 5'10"})
    weight = StringField("", validators=[Optional()], render_kw={"placeholder": "Weight: 50 KG"})
    religion = StringField("", validators=[Optional()], render_kw={"placeholder": "Religion"})
    elementary = TextAreaField("", validators=[Optional()], render_kw={"placeholder": "Elementary: Name of School", "rows" : 2})
    secondary = TextAreaField("", validators=[Optional()], render_kw={"placeholder": "Secondary: Name of School", "rows" : 2})
    tertiary = TextAreaField("", validators=[Optional()], render_kw={"placeholder": "Tertiary/Vocational: NameOfSchool - Course", "rows" : 2})
    submit1 = SubmitField("Update Profile")
    submit2 = SubmitField("Upload Profile Picture")


class SignUpForm(FlaskForm):
    username = StringField("", validators=[DataRequired()], render_kw={"placeholder": "Username"})
    email = EmailField("", validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField("", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    confirmation = PasswordField("", validators=[DataRequired(), EqualTo("password", message="Passwords must match!")], render_kw={"placeholder": "Confirm Password"})
    firstname = StringField("", validators=[DataRequired()], render_kw={"placeholder": "First Name"})
    middlename = StringField("", validators=[DataRequired()], render_kw={"placeholder": "Middle Name"})
    lastname = StringField("", validators=[DataRequired()], render_kw={"placeholder": "Last Name"})
    code = StringField("", validators=[DataRequired()], render_kw={"placeholder": "Registration Code"})
    submit = SubmitField("Create Account")

    def validate_username(self, username):
        existing_username = Users.query.filter_by(username=username.data).first()
        if existing_username:
            raise ValidationError("Username already exists!")

    def validate_email(self, email):
        existing_email = Users.query.filter_by(email=email.data).first()
        if existing_email:
            raise ValidationError("Email already exists!")

    def validate_code(self, code):
            existing_code = Authorize.query.filter_by(code=code.data).first()
            if not existing_code:
                raise ValidationError("Invalid Registration Code! It seems like you are not authorized to create a DYAVA account!")


class SignInForm(FlaskForm):
    username = StringField("", validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField("", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField("Sign In")

    def validate_username(self, username):
        existing_username = Users.query.filter_by(username=username.data).first()
        if not existing_username:
            raise ValidationError("Invalid Username!")


class ResetForm(FlaskForm):
    email = EmailField("", validators=[DataRequired()], render_kw={"placeholder": "Email Address"})
    submit = SubmitField("Reset Password")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = Users(username=form.username.data, email=form.email.data, password=hashed_password, firstname=form.firstname.data, middlename=form.middlename.data, lastname=form.lastname.data)
        db.session.add(new_user)
        db.session.commit()
        flash("You have successfully created an account with DYAVA!", "success")
        return redirect("/signin")
    return render_template("signup.html", form=form)


@app.route("/signin", methods=["GET", "POST"])
def sign_in():
    form = SignInForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You have successfully signed in! Welcome to DYAVA!")
                return redirect("/")
            else:
                flash("Invalid Password", "error")
    return render_template("signin.html", form=form)


@app.route("/reset", methods=["GET", "POST"])
def reset():
    flash("Sorry, this feature is not available yet. Please wait for the updates. Thank you!")
    return render_template("error.html")


@app.route("/signout")
@login_required
def sign_out():
    logout_user()
    flash("You have been signed out!")
    return redirect("/")


@app.route("/search")
def search():
    flash("Sorry, this feature is not available yet. Please wait for the updates. Thank you!")
    return render_template("error.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/gallery")
def gallery():
    arts = Artworks.query.order_by(Artworks.date.desc()).all()
    return render_template("gallery.html", arts=arts)


@app.route("/view-artwork/<int:id>")
def view_artwork(id):
    arts = Artworks.query.filter_by(id=id).all()
    art = Artworks.query.filter_by(id=id).first()
    return render_template("viewartwork.html", arts=arts, art=art)


@app.route("/view-artwork-shop/<int:id>")
def view_artwork_shop(id):
    arts = Artworks.query.filter_by(id=id).all()
    art = Artworks.query.filter_by(id=id).first()
    return render_template("viewartworkshop.html", arts=arts, art=art)


@app.route("/view-artwork-profile/<int:id>")
def view_artwork_profile(id):
    art = Artworks.query.filter_by(id=id).first()
    return render_template("viewartworkprofile.html", art=art)


@app.route("/shop")
def shop():
    arts = Artworks.query.filter_by(forsale=1).order_by(Artworks.date.desc()).all()
    return render_template("shop.html", arts=arts)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            fullname = form.fullname.data
            email = form.email.data
            phone = form.phone.data
            subject = form.subject.data
            message = form.message.data
            msg = Message(subject, sender=email, recipients=["dyava.artists@gmail.com"])
            msg.body = msg.html
            msg.html = """
                Name: {} <br>
                Email: {} <br>
                Phone: {} <br>
                Subject: {} <br>
                Message: {}
                """.format(fullname, email, phone, subject, message)
            mail.send(msg)
            flash("Message Sent! We will get back to you shortly. Thank you!", "success")
            return redirect("/contact")
        except:
            flash("Something went wrong while sending your message. Please try again!", "error")
    return render_template("contact.html", form=form)


@app.route("/artists-profile")
def artists_profile():
    profiles = Profiles.query.order_by(func.random()).all()
    return render_template("artistsprofile.html", profiles=profiles)


@app.route("/profile")
@login_required
def my_profile():
    check_profile_id = Profiles.query.filter_by(profile_id=current_user.id).first()
    if not check_profile_id:
        add_user = Profiles(profile_id=current_user.id)
        db.session.add(add_user)
        db.session.commit()
    profile = Profiles.query.filter_by(profile_id=current_user.id).all()
    arts = Artworks.query.filter_by(art_id=current_user.id).all()
    return render_template("profile.html", profile=profile, arts=arts)


@app.route("/view-profile/<int:id>")
def view_profile(id):
    profiles = Profiles.query.filter_by(profile_id=id).first()
    arts = Artworks.query.filter_by(art_id=id).all()
    return render_template("viewprofile.html", profiles=profiles, arts=arts)



@app.route("/uploads/<filename>")
def get_file(filename):
    return send_from_directory(app.config["UPLOADED_PHOTOS_DEST"],filename)


@app.route("/uploadart", methods=["GET", "POST"])
@login_required
def upload_art():
    form = ArtworkForm()
    try:
        if form.validate_on_submit():
            filename = photos.save(form.artpic.data)
            add = Artworks(art_id=current_user.id, artpic=filename, title=form.title.data, type=form.type.data, materials=form.materials.data, size=form.size.data, forsale=form.forsale.data, price=form.price.data)
            db.session.add(add)
            db.session.commit()
            flash("You have successfully uploaded your artwork", "success")
            return redirect("/profile")
    except:
        flash("Please choose a file!",)
    return render_template("uploadart.html", form=form)


@app.route("/edit-artwork/<int:id>", methods=["GET", "POST"])
@login_required
def edit_artwork(id):
    form = ArtworkForm()
    art = Artworks.query.get_or_404(id)
    if form.validate_on_submit():
        art.artpic = art.artpic
        art.title = form.title.data
        art.type = form.type.data
        art.materials = form.materials.data
        art.size = form.size.data
        art.forsale = form.forsale.data
        art.price = form.price.data
        db.session.add(art)
        db.session.commit()
        flash("You have successfully updated this artwork!")
        return redirect("/profile")

    form.title.data =  art.title
    form.type.data =  art.type
    form.materials.data =  art.materials
    form.size.data =  art.size
    form.forsale.data =  art.forsale
    form.price.data =  art.price

    return render_template("editartwork.html", form=form, art=art)


@app.route("/delete-artwork/<int:id>", methods=["POST"])
@login_required
def delete_artwork(id):
    form = ArtworkForm()
    art_to_delete = Artworks.query.get_or_404(id)
    try:
        db.session.delete(art_to_delete)
        db.session.commit()
        flash("Artwork deleted successfully!")
        return redirect("/profile")
    except:
        flash("Something went wrong while deleting the artwork. Please try again.")


@app.route("/uploadprofile", methods=["GET", "POST"])
@login_required
def upload_profile():
    form = UpdateForm()
    try:
        if form.validate_on_submit():
            update = Profiles.query.filter_by(profile_id=current_user.id).first()
            filename = photos.save(form.picture.data)
            update.picture = filename
            db.session.commit()
            flash("You have successfully updated your profile", "success")
            return redirect("/profile")
    except:
        flash("Please choose a file!",)
    return render_template("uploadprofile.html", form=form)


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    form = UpdateForm()
    profile = Profiles.query.filter_by(profile_id=current_user.id).first()
    if form.validate_on_submit():
        update = Profiles.query.filter_by(profile_id=current_user.id).first()
        update.bio = form.bio.data
        update.style = form.style.data
        update.medium = form.medium.data
        update.phone = form.phone.data
        update.facebook = form.facebook.data
        update.instagram = form.instagram.data
        update.address = form.address.data
        update.gender = form.gender.data
        update.age = form.age.data
        update.birthday = form.birthday.data
        update.birthplace = form.birthplace.data
        update.civilstatus = form.civilstatus.data
        update.nationality = form.nationality.data
        update.citizenship = form.citizenship.data
        update.religion = form.religion.data
        update.height = form.height.data
        update.weight = form.weight.data
        update.elementary = form.elementary.data
        update.secondary = form.secondary.data
        update.tertiary = form.tertiary.data

        db.session.commit()
        flash("You have successfully updated your profile", "success")
        return redirect("/profile")

    form.bio.data = profile.bio
    form.style.data = profile.style
    form.medium.data = profile.medium
    form.phone.data = profile.phone
    form.facebook.data = profile.facebook
    form.instagram.data = profile.instagram
    form.address.data = profile.address
    form.gender.data = profile.gender
    form.age.data = profile.age
    form.birthday.data = profile.birthday
    form.birthplace.data = profile.birthplace
    form.civilstatus.data = profile.civilstatus
    form.nationality.data = profile.nationality
    form.citizenship.data = profile.citizenship
    form.religion.data = profile.religion
    form.height.data = profile.height
    form.weight.data = profile.weight
    form.elementary.data = profile.elementary
    form.secondary.data = profile.secondary
    form.tertiary.data = profile.tertiary

    return render_template("update.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)