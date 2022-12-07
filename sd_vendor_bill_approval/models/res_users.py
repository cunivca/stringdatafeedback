
from odoo import fields, models


class ResUser(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    # New fields for custom rights
    approver_cfo = fields.Boolean("Schvalovatel CFO", default=False)
    payments_approver = fields.Boolean("Schvalovatel plateb", default=False)
