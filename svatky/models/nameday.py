from odoo import fields, models, api


class NameDay(models.Model):
    """Model for partner.nameday"""

    # 1. Private attributes
    _name = "partner.nameday"
    _description = "Represents a nameday entity"

    # 2. Default methods
    # 3. Field declarations
    name = fields.Char(string="Name")
    country_id = fields.Many2one('res.country', string="Country")
    date = fields.Date(string="Date")
    vocative = fields.Char(string="Vocative", readonly=True)

    # 4. Compute, inverse and search methods
    @api.onchange("country")
    def _onchange_country(self):
        """If the country is CZ fill field vocative"""
        if self.country_id.code == "CZ":
            self.vocative = self.vocative
        else:
            self.vocative = None

    # 5. Selection methods
    # 6. Constrains and onchange methods
    # 7. CRUD methods (ORM overrides)
    # 8. Action methods
    # 9. Business methods
