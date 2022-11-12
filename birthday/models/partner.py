import logging
from datetime import datetime

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    """Inhertied model from res.partner"""

    # 1. Private attributes
    _inherit = "res.partner"

    # 2. Default methods
    # 3. Field declarations
    birthday = fields.Date(string="Birthday Date")
    birthday_notification = fields.Boolean(default=False)

    # 4. Compute, inverse and search methods
    # 5. Selection methods
    # 6. Constrains and onchange methods
    # 7. CRUD methods (ORM overrides)
    # 8. Action methods
    # 9. Business methods
    def send_birthday_wish(self):
        today_date = datetime.today().date()
        for partner in self.env['res.partner'].search([]):
            if partner.birthday_notification:
                if today_date.day == partner.birthday.day and today_date.month == partner.birthday.month:
                    template_id = self.env.ref('birthday_mail_template')
                    template_id.send_mail(partner.id, force_send=True)
