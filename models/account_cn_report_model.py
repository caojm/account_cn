from odoo import api, fields, models


class AccountCnReportModel(models.Model):
    _name = "account.cn.report.model"
    _description = "Report Model"
    _sql_constraints = [
        ("report_model_code_uq", "UNIQUE (code)", "Code must be unique."),
    ]

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    code = fields.Char(
        required=True,
        copy=False,
    )
    name = fields.Char()
    template_id = fields.Many2one(
        "ir.ui.view",
        domain="[('type', '=', 'qweb'), ('name', '=ilike', '%.account_cn')]",
    )
    item_ids = fields.One2many("account.cn.report.item", "report_model_id")
