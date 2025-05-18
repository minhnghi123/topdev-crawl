from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy (to be used in your Flask app)
db = SQLAlchemy()

class JobType(db.Model):
    __tablename__ = 'jobType'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

class SkillOld(db.Model):
    __tablename__ = 'skill_old'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

class Level(db.Model):
    __tablename__ = 'level'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

class ContractType(db.Model):
    __tablename__ = 'contractType'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    Logo = db.Column(db.Text)
    name = db.Column(db.Text, nullable=False)
    shortdescription = db.Column(db.Text)
    curent_job_opening = db.Column(db.Integer)
    industry = db.Column(db.Text)
    size = db.Column(db.Text)
    nationality = db.Column(db.Text)
    tech_stack = db.Column(db.Text)
    website = db.Column(db.Text)
    Social_media = db.Column(db.Text)
    address = db.Column(db.Text)
    description = db.Column(db.Text)
    banner = db.Column(db.Text)
    short_address = db.Column(db.Text)
    followers = db.Column(db.Integer)
    about_images = db.Column(db.Text)

class Job(db.Model):
    __tablename__ = 'job'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    name_company = db.Column(db.Text, nullable=False)
    id_company = db.Column(db.Integer)
    address = db.Column(db.Text)
    salary = db.Column(db.Text)
    date_expire = db.Column(db.Text)
    experience = db.Column(db.Text)
    skill_id = db.Column(db.Integer)
    job_type_id = db.Column(db.Integer)
    level_id = db.Column(db.Integer)
    contract_type = db.Column(db.Integer)
    description = db.Column(db.Text)
    logo = db.Column(db.Text)

class JobCompany(db.Model):
    __tablename__ = 'job_company'
    id_job = db.Column(db.Integer, primary_key=True)
    id_company = db.Column(db.Integer)

class JobJobTypes(db.Model):
    __tablename__ = 'job_jobtypes'
    job_id = db.Column(db.Integer, primary_key=True)
    job_type_id = db.Column(db.Integer)

class JobLevels(db.Model):
    __tablename__ = 'job_levels'
    job_id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer)

class JobSkills(db.Model):
    __tablename__ = 'job_skills'
    job_id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer)

class CompanySkills(db.Model):
    __tablename__ = 'company_skills'
    company_id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer)

class Skill(db.Model):
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.Text)
    company_id = db.Column(db.Integer)