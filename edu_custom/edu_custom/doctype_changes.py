import frappe
from frappe.auth import LoginManager

def subscription_validate(self, method):
	check = frappe.db.get_value("Student", {"customer": self.customer}, "name")
	if not check:
		check_email = frappe.db.get_value("Customer", self.customer, "email_id")
		# if not check_email:
		# 	frappe.throw("Please enter customer email, as it is required for creating student.")
		doc = frappe.new_doc("Student")
		doc.first_name = self.customer
		doc.customer = self.customer
		doc.instructor = self.instructor
		doc.student_email_id = check_email
		doc.flags.ignore_mandatory=True
		doc.insert(ignore_permissions=True)
	else:
		frappe.db.set_value("Student", check, "instructor", self.instructor)


@frappe.whitelist(allow_guest=True)
def get_ratings(instructor=None, student_id=None):
	cond = ""
	if student_id:
		cond += " and student = '{}'".format(student_id)
	if instructor:
		cond += " and instructor = '{}'".format(instructor)
	return frappe.db.sql("select * from `tabStudent Rating` where 1=1 {}".format(cond), as_dict=1)

@frappe.whitelist(allow_guest=True)
def get_attendance(instructor=None, student_id=None):
	if student_id:
		customer = frappe.db.get_value("Student", {"name": student_id}, "customer")
		status = frappe.db.get_value("Subscription", {"customer": customer}, "status")
		if status != "Active": return "No Active Subscription"
	cond = ""
	if student_id:
		cond += " and student = '{}'".format(student_id)
	if instructor:
		cond += " and instructor = '{}'".format(instructor)
	return frappe.db.sql("select * from `tabStudent Attendance` where 1=1 {}".format(cond), as_dict=1)

@frappe.whitelist(allow_guest=True)
def create_student_rating(student_id, date, title, rating):
	doc = frappe.new_doc("Student Rating")
	doc.student = student_id
	doc.date = frappe.utils.getdate(date)
	doc.title = title
	doc.rating = rating
	doc.flags.ignore_mandatory=True
	doc.insert(ignore_permissions=True)
	return doc

@frappe.whitelist(allow_guest=True)
def login_instructor(usr, pwd):
	login_manager = LoginManager()
	login_manager.authenticate(usr,pwd)
	login_manager.post_login()
	if frappe.response['message'] == 'Logged In':
		instructor = frappe.db.get_value("Instructor", {"user": login_manager.user}, "name")
		if instructor: return instructor
	return "No Instructor Found."