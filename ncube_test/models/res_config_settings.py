# -*- coding: utf-8 -*-
from ast import literal_eval

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    reminder_partner_ids = fields.Many2many('res.partner',
                                            'reminder_list_partner_rel',
                                            string='Special Reminder List')
    number_days = fields.Integer(string='Number of days',
                                 config_parameter='hr.reminder_number_days')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'hr.reminder_partner_list', self.reminder_partner_ids.ids)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        partner_ids = self.env['ir.config_parameter'].sudo(
                                        ).get_param('hr.reminder_partner_list')
        res.update(reminder_partner_ids=[(6, 0, literal_eval(partner_ids))
                                         ] if partner_ids else False)
        return res
