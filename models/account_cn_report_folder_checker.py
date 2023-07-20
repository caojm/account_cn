from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCnReportFolderChecker(models.Model):
    _name = "account.cn.report.folder.checker"
    _description = "Report Folder Checker Line"

    name = fields.Char()
    sequence = fields.Integer(
        default=10,
    )
    report_folder_id = fields.Many2one(
        "account.cn.report.folder",
        required=True,
    )
    report_checker_id = fields.Many2one(
        "account.cn.report.checker",
        required=True,
    )
