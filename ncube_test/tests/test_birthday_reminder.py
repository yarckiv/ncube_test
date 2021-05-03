# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from datetime import date

from odoo.tests import Form
from odoo.addons.hr.tests.common import TestHrCommon
from odoo import fields


class TesBirthdayReminder(TestHrCommon):

    def test_1_reminder(self):
        current_date = date.today()
        birthday = fields.Date.from_string('1990-%s-25' %
                                           str(current_date.month + 1))
        config = self.env['ir.config_parameter']
        config.set_param('hr.reminder_number_days', 4)
        Employee = self.env['hr.employee'].with_user(self.res_users_hr_officer)
        employee_form = Form(Employee)
        employee_form.name = 'Pol Polson'
        employee_form.work_email = 'pol@example.com'
        employee_form.birthday = birthday
        employee_form.incl_birthday_list = True
        employee_form.user_id = self.res_users_hr_officer
        employee = employee_form.save()
        num_days = config.get_param('hr.reminder_number_days')
        reminder = birthday.replace(year=current_date.year) -\
                   relativedelta(days=int(num_days))
        self.assertEqual(employee.name, 'Pol Polson')
        self.assertEqual(employee.next_birthday, birthday.replace(
                                                    year=current_date.year))
        self.assertEqual(employee.birthday_reminder_day, reminder)
