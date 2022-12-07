from odoo import fields, models


class AnalyticAccount(models.Model):

    _name = 'account.analytic.account'
    _inherit = 'account.analytic.account'

    # Add a new field for project owner
    project_owner = fields.Many2one('res.users', "Project Manager")
