from operator import methodcaller, ne
from flask import Flask, render_template, redirect, url_for, request, json, jsonify, session, flash, make_response
from flask_login.utils import logout_user
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from SE_Fall2020_EHR import app, db, login
from SE_Fall2020_EHR.models import *
import math

# @login.user_loader
# def load_user(id):
# 	return User.query.get(id)

#???? json.dumps or jsonify ????
#---------------------Home----------------------
#---------------------Home----------------------
@app.route('/')
@app.route('/index')
def home():
	if current_user.is_authenticated:
		return redirect(url_for(f'{current_user.role.value}Home'))
	return render_template('index.html')

#-------------------Register--------------------
#-------------------Register--------------------

@app.route('/register', methods=['POST'])
def register():
	"""
		patient: register by (national)id
		doctor/nurse: register by (license)id
	"""
	# try:
	if current_user.is_authenticated:
		return redirect(url_for(f'{current_user.role.value}Home'))
	role = request.form['role']
	first_name = request.form['firstName']
	last_name = request.form['lastName']
	id = request.form['id']
	phone = request.form['phone']
	email = request.form['email']
	password = request.form['password']
	if role != "patient":
		department = request.form['department']
	# user = User.query.get(id)
	# if user:
	# 	return ""
	# generate random unique user_id and create new user
	user = User(id=id, first_name=first_name, last_name=last_name, role=role, email=email, phone=phone, password_hash=generate_password_hash(password))
	db.session.add(user)
	# update corresponding table
	if role == "patient":
		patient = Patient(id=id)
		db.session.add(patient)
	elif role == "doctor":
		doctor = Doctor(id=id, department_id = department)
		db.session.add(doctor)
	elif role == "nurse":
		nurse = Nurse(id=id, department_id = department)
		db.session.add(nurse)
	db.session.commit()
	return make_response(jsonify({"ret":0}), 200)
	# except:
	# 	db.session.rollback()
	# 	return "1"


#--------------------Login---------------------
#--------------------Login---------------------

@app.route('/login', methods=['GET','POST'])
def login():
	"""
		patient login with: national id + password
		doctor/patient login with: license id + password
	"""
	if request.method == 'GET':
		if current_user.is_authenticated:
			return redirect(url_for(f'{current_user.role.value}Home'))
		return render_template('login.html')
	if request.method == 'POST':
		if not current_user.is_authenticated:
			id = request.form['id']
			password = request.form['password']
			try:
				user = User.query.get(id)
				if not user:
					# flash("Unregistered ID or wrong password")
					return "Unregistered user"
				if not user.check_password(password):
					return "Password incorrect"
				login_user(user)
			except:
				# flash("Unknown error, sorry!")
				return "Unknown error"

		return redirect(url_for(f'{current_user.role.value}Home'))

#--------------------Logout---------------------
#--------------------Logout---------------------

@app.route('/logout', methods=['GET'])
def logout():
	logout_user()
	return redirect(url_for('home'))


#--------------------home---------------------
#--------------------home---------------------
@app.route('/patientHome', methods=['GET'])
@login_required
def patientHome():
	return render_template('PatientHome.html')


#--------------------get hospital list data---------------------
#--------------------get hospital list data---------------------

@app.route('/hospitalData', methods=['GET', 'POST'])
def hospitalData():
	# try:
	if request.method == "GET":
		return redirect(url_for('GoToHospitalList'))
	curr_page = int(request.form['currPage']) 
	page_size = int(request.form['pageSize']) 

	# temporory data
	# curr_page=1
	# page_size=12

	n_offset = (curr_page-1) * page_size + 1
	# query for hospitals
	hospital_count = Hospital.query.count()
	page_count = math.ceil(hospital_count / page_size)
	rawHospitals = Hospital.query.offset(n_offset).limit(page_count)
	print(rawHospitals)
	hospital_ids = [res.id for res in rawHospitals]
	hospital_names = [res.name for res in rawHospitals]
	hospital_addresses = [res.address for res in rawHospitals]
	hospital_phones = [res.phone for res in rawHospitals]
	# return data
	return make_response(jsonify(
		[{"id":hospital_ids[i],
		  "name": hospital_names[i],
		  "address": hospital_addresses[i],
		  "phone": hospital_phones[i]} for i in range(page_count)]), 200)


@app.route('/hospitalListPage',methods=['GET'])
def GoToHospitalList():
	return render_template('hospitalListPage.html')