# -*- coding: utf-8 -*-

from ast import literal_eval
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _description = 'Extend model for birthday reminder'

    incl_birthday_list = fields.Boolean(string='Include in Birthday '
                                               'Reminder List')
    next_birthday = fields.Date(string='Next Birthday', readonly=True,
                                search='_search_next_birthday',
                                compute='_compute_next_birthday')
    birthday_reminder_day = fields.Date(string='Birthday Remind Date',
                                        readonly=True,
                                        search='_search_birthday_reminder',
                                        compute='_compute_next_birthday')

    @api.depends('birthday')
    def _compute_next_birthday(self):
        for emp in self:
            if not emp.birthday:
                emp.birthday_reminder_day = emp.next_birthday = False
            else:
                current_date = date.today()
                rem_days = self._get_config_param('hr.reminder_number_days')
                cur_birthday = emp.birthday.replace(year=current_date.year)
                next_bd = cur_birthday if cur_birthday >= current_date \
                    else cur_birthday.replace(year=current_date.year + 1)
                next_bd_rem = next_bd - relativedelta(days=int(rem_days))
                emp.next_birthday = next_bd
                emp.birthday_reminder_day = next_bd_rem if \
                    next_bd_rem >= current_date else \
                    next_bd_rem.replace(year=current_date.year + 1)

    def _run_birthday_reminder(self):
        reminder_candidates = self._search_birthday_reminder('=',
                                                    fields.Date.to_string(
                                                        date.today()))[0][2]
        if reminder_candidates:
            candidates = self.browse(reminder_candidates)
        else:
            return
        all_recipients = literal_eval(self._get_config_param(
            'hr.reminder_partner_list'))
        can_partners = candidates.mapped(lambda c: c.user_id.partner_id).ids
        recipients = set(all_recipients).difference(can_partners)
        if recipients:
            # todo -- use .with_context(lang=lang) for choose language
            template = self.env.ref('ncube_test.remind_birthday_email')
            birthday_person = ', '.join(candidates.mapped('name'))
            template_body = template.body_html
            template_body = template_body.replace('birthday_person',
                                                  birthday_person)
            template_body = template_body.replace('birthday_date',
                                                  fields.Date.to_string(
                                                      candidates[0].birthday))
            mail = self.env['mail.mail'].sudo().create({
                'author_id': self.env.user.partner_id.id,
                'email_from': template.email_from,
                'email_to': template.email_to,
                'reply_to': template.email_from,
                'subject': template.subject,
                'body_html': template_body,
                'auto_delete': template.auto_delete,
                'recipient_ids': [(4, r_id) for r_id in recipients]
            })
            mail.send()

    def _search_birthday_reminder(self, operator, value):
        empl_ids = self.search([])
        dt = fields.Date.from_string(value)
        res = []
        for empl in empl_ids:
            if empl.birthday_reminder_day:
                if operator == '=' and empl.birthday_reminder_day == dt:
                    res.append(empl.id)
                elif operator == '!=' and empl.birthday_reminder_day:
                    res.append(empl.id)
                elif operator == '>' and empl.birthday_reminder_day > dt:
                    res.append(empl.id)
                elif operator == '<' and empl.birthday_reminder_day < dt:
                    res.append(empl.id)
                elif operator == '>=' and empl.birthday_reminder_day >= dt:
                    res.append(empl.id)
                elif operator == '<=' and empl.birthday_reminder_day <= dt:
                    res.append(empl.id)
            elif not value and operator == '=':
                if not empl.birthday_reminder_day:
                    res.append(empl.id)
        return [('id', 'in', res)]

    def _search_next_birthday(self, operator, value):
        empl_ids = self.search([])
        dt = fields.Date.from_string(value)
        res = []
        for empl in empl_ids:
            if empl.next_birthday:
                if operator == '=' and empl.next_birthday == dt:
                    res.append(empl.id)
                elif operator == '!=' and empl.next_birthday:
                    res.append(empl.id)
                elif operator == '>' and empl.next_birthday > dt:
                    res.append(empl.id)
                elif operator == '<' and empl.next_birthday < dt:
                    res.append(empl.id)
                elif operator == '>=' and empl.next_birthday >= dt:
                    res.append(empl.id)
                elif operator == '<=' and empl.next_birthday <= dt:
                    res.append(empl.id)
            elif not value and operator == '=':
                if not empl.next_birthday:
                    res.append(empl.id)
        return [('id', 'in', res)]

    def _get_config_param(self, param_name):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        if param_name:
            return get_param(param_name)
