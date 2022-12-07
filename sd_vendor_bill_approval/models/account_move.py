
import json
# import simplejson
from datetime import datetime
from lxml import etree


from odoo import api, fields, models, exceptions


import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(funcName)s | %(lineno)s | %(levelname)s | %(message)s",
)

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    # New custom fields
    projects_approver = fields.Many2one('res.users', 'Schvalovatel projektů')
    cfo_approver = fields.Many2one('res.users', 'Schvalovatel CFO')
    payments_approver = fields.Many2one('res.users', 'Schvalovatel plateb')

    project_approved_date = fields.Date('Projekt schválen dne', readonly=True, default=False)
    cfo_approved_date = fields.Date('CFO schválil dne', readonly=True, default=False)
    payment_approved_date = fields.Date('Platby schváleny dne', readonly=True, default=False)

    approve_state = fields.Selection(
        [
            ('nova', 'Nová'),
            ('ke_schvaleni', 'Ke schválení'),
            ('cfo', 'Ke schválení CFO'),
            ('platba', 'Ke schválení platby'),
            ('schvaleno', 'Schválená k platbě'),
            ('zamitnuta', 'Zamítnuta')
         ],
        string="Stav schválení",
        default='nova',
        readonly=True
    )

    # =========================================== Model methods ===========================================

    @api.onchange('invoice_line_ids')
    def onchange_line_ids(self):
        """Assign Project Approver from analytic account if there is only one"""

        # In case there are more, noone is assigned
        projects_owners = []

        # Iterate all invoice lines
        for line in self.invoice_line_ids:

            # Not on every line has to be assigned analytic
            if not line.analytic_distribution:
                continue

            # Get dict with values {id_of_analytic_account: percentage}
            all_analytics = line.analytic_distribution

            # Find all users using id
            for key in all_analytics.keys():
                account = self.env['account.analytic.account'].search([('id', '=', key)])

                # If there is account without project_owner return and clear project_approver
                if not account.project_owner:
                    self.projects_approver = False
                    return

                projects_owners.append(account.project_owner)

        if not projects_owners:
            self.projects_approver = False
            return

        # Filter only unique users
        user_ids = list(set([user.id for user in projects_owners]))

        # If there are more project owners
        if len(user_ids) > 1:
            self.projects_approver = False
            return

        # At last, if there's only one unique project owner, assign him to account.move
        user_id = user_ids[0]
        user = self.env['res.users'].search([('id', '=', user_id)])
        self.projects_approver = user

    @api.onchange('projects_approver')
    def onchange_projects_approver(self):
        """If is a new projects_approver approve date has to be set to False"""
        self.project_approved_date = False

    @api.onchange('cfo_approver')
    def onchange_cfo_approver(self):
        """If is a new cfo_approver approve date has to be set to False"""
        self.cfo_approved_date = False

    @api.onchange('payments_approver')
    def onchange_payments_approver(self):
        """If is a new payments_approver approve date has to be set to False"""
        self.payment_approved_date = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Change view to readonly and vice versa"""

        # Zdroj https://www.odoo.com/forum/help-1/make-entire-form-read-only-odoo-14-188649
        # todo opravit, neprovolava se

        _logger.info("Zavolana metoda fields_view_get")

        res = super(AccountMove, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        # In these states we want user to be able to
        if self.approve_state in ("nova", "zamitnuta") and self.state == 'draft':

            _logger.info("Odemykam polozky")

            # Get the view architecture of record
            doc = etree.XML((res['arch']))

            # Applies only if it is form view
            if view_type == "form":

                # Get all the fields navigating through xpath
                for node in doc.xpath("//field"):

                    # Get all the existing modifiers of each field
                    modifiers = json.loads(node.get('modifiers'))

                    # Add readonly=True attribute in modifier for each field
                    modifiers['readonly'] = True

                    # set the newly added modifiers to the field
                    node.set("modifiers", json.dumps(modifiers))

                # Update the view architecture of record with new architecture
                res['arch'] = etree.tostring(doc)

        elif self.approve_state in ("ke_schvaleni", "cfo", "platba", "schvaleno") and self.state == 'draft':

            _logger.info("Uzamykam polozky")

            doc = etree.XML((res['arch']))
            if view_type == "form":
                for node in doc.xpath("//field"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['readonly'] = False
                    node.set("modifiers", json.dumps(modifiers))
                res['arch'] = etree.tostring(doc)

        _logger.info("Vracim res")

        return res

    # =========================================== Button actions ===========================================

    def action_to_new(self):
        """Change Vendor Bill state to New"""
        self.approve_state = "nova"

    def action_to_approval(self):
        """Change Vendor Bill state to ke_schvaleni"""

        if not self.projects_approver:
            raise exceptions.AccessError(
                "Přijatá faktura může jít ke schválení až tehdy, když je přiřazený vlastník projektu.")

        self.approve_state = "ke_schvaleni"

        # todo poslat emailovou notifikaci vlastnikovi projektu

    def action_to_approval_cfo(self):
        """Change Vendor Bill state to cfo"""

        # Assign first found cfo approver
        if not self.cfo_approver:
            for user in self.env['res.users'].search([]):
                if user.approver_cfo:
                    self.cfo_approver = user
                    break
        else:
            user = self.cfo_approver
        if not user:
            raise exceptions.AccessDenied(
                "Faktura nemůže být přiřazená na schvalovatele CFO, protože v systému neexistuje.")

        self.approve_state = "cfo"
        self.project_approved_date = datetime.today()

    def action_to_approval_payment(self):
        """Change Vendor Bill state to platba"""

        # Check rights for cfo
        user = self._get_current_user()
        if not user.approver_cfo:
            raise exceptions.AccessDenied("Tuto akci může provést jen Schvalovatel CFO.")

        # Assign first found Payment Approver
        if not self.payments_approver:
            for user in self.env['res.users'].search([]):
                if user.payments_approver:
                    self.payments_approver = user
                    break
        else:
            user = self.payments_approver
        if not user:
            raise exceptions.AccessDenied("V systému nemá žádný uživatel přiřazené právo Schvalovatel plateb.")

        self.approve_state = "platba"
        self.cfo_approved_date = datetime.today()

    def action_approve_payment(self):
        """Change Vendor Bill state to schvaleno"""

        user = self._get_current_user()

        # User must have cfo rights or payments approval rights
        if not user.approver_cfo and not user.payments_approver:
            raise exceptions.AccessDenied("Tuto akci může provést jen Schvalovatel CFO nebo Schvalovatel plateb.")

        # User with payment approval cannot put Vendor bill from state cfo to payment approved
        if self.approve_state == "cfo" and not user.approver_cfo:
            raise exceptions.AccessDenied("Tuto akci lze provést jen pokud přijatou fakturu schválí Schvalovatel CFO.")

        self.approve_state = "schvaleno"
        self.payment_approved_date = datetime.today()

    def action_reject(self):
        """Change Vendor Bill state to zamitnuta"""
        self.approve_state = "zamitnuta"

        # Edit date of change if any of these user does this button action
        user = self._get_current_user()
        if self.projects_approver == user:
            self.project_approved_date = datetime.today()
        elif self.cfo_approver == user:
            self.cfo_approved_date = datetime.today()
        elif self.payments_approver == user:
            self.payment_approved_date = datetime.today()

    # =========================================== Custom methods ===========================================

    def _get_current_user(self):
        """Get current user and returns him"""
        context = self._context
        current_uid = context.get('uid')
        return self.env['res.users'].browse(current_uid)


