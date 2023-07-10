from odoo import api, fields, models


class AccountCnReportModle(models.Model):
    _name = "account.cn.report.model"
    _description = "Report Model"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    code = fields.Char()
    name = fields.Char()
    item_ids = fields.One2many("account.cn.report.item", "report_model_id")
