from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountCnReportFolderModel(models.Model):
    _name = "account.cn.report.folder.model"
    _description = "Report Folder Model Line"

    name = fields.Char(string="Comment")
    sequence = fields.Integer(
        default=10,
    )
    report_folder_id = fields.Many2one(
        "account.cn.report.folder",
        required=True,
    )
    report_model_id = fields.Many2one(
        "account.cn.report.model",
        required=True,
    )

    def to_be(self):
        pass
