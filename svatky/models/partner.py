import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    """Inhertied model from res.partner"""

    # 1. Private attributes
    _inherit = "res.partner"

    # 2. Default methods
    # 3. Field declarations
    forename = fields.Char(string="First Name", required=True)
    surname = fields.Char(string="Last Name", required=True)
    nationality = fields.Many2one('res.country', string="Nationality")
    vocative_forename = fields.Char(string="Vocative First Name")
    vocative_surname = fields.Char(string="Vocative Last Name")
    name_day = fields.Date(string="Name Date")

    name = fields.Char(compute="_compute_name", store=True)

    # 4. Compute, inverse and search methods

    @api.onchange("forename", "nationality")
    def _onchange_partner(self):
        """Set vocative_forename according to the partner.nameday vocative"""

        if not self.forename or not self.nationality:
            self.vocative_forename = None
        else:
            nameday = self.env['partner.nameday'].search([
                ('name', '=', self.forename),
                ('country_id', '=', self.nationality.id)
            ])
            if nameday:
                self.vocative_forename = nameday[0].vocative
                self.name_day = nameday[0].date

    @api.depends("forename", "surname", "is_company")
    def _compute_name(self):
        """Set Name as concatenate forename and surname"""

        for record in self:
            if not record.is_company and record.forename and record.surname:
                record.name = record.forename + " " + record.surname
            else:
                record.name = record.name

    # 5. Selection methods
    # 6. Constrains and onchange methods
    # 7. CRUD methods (ORM overrides)

    @api.model
    def create(self, vals):
        """Override create method to replace name with forename + surname"""

        vals['name'] = f"{vals['forename']} {vals['surname']}"

        rec = super(Partner, self).create(vals)
        return rec

    # 8. Action methods
    # 9. Business methods
