from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCnReportFolder(models.Model):
    _name = "account.cn.report.folder"
    _description = "Report Folder"

    name = fields.Char()
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.user.accounting_book_id.currency_id,
    )
    date_from = fields.Date(
        required=True,
    )
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    last_update = fields.Datetime()
    posted_only = fields.Boolean(
        default=False,
    )
    exact_match = fields.Boolean(
        default=False,
    )
    accounting_book_ids = fields.Many2many(
        "account.cn.accounting.book",
        compute="_compute_accounting_book_ids",
        store=True,
        readonly=False,
        required=True,
        default=lambda self: self.env.user.accounting_book_id,
        domain="[('currency_id', '=', currency_id)]",
    )
    company_ids = fields.Many2many(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    folder_model_ids = fields.One2many(
        "account.cn.report.folder.model",
        "report_folder_id",
    )
    folder_checker_ids = fields.One2many(
        "account.cn.report.folder.checker",
        "report_folder_id",
    )

    @api.depends("currency_id")
    def _compute_accounting_book_ids(self):
        self.ensure_one()
        self.accounting_book_ids = self.accounting_book_ids.filtered(
            lambda r: r.currency_id == self.currency_id
        )
