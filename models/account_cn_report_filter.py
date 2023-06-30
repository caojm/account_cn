from odoo import api, fields, models


class AccountCnReportFilter(models.Model):
    _name = "account.cn.report.filter"
    _description = "Report Filter"


    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    account_id = fields.Many2one('account.account')
    account_tag_id = fields.Many2one('account.account.tag')
    amount_type = fields.Selection(
        selection=[
            ('movement', 'Movement'),
            ('balance', 'Balance'),
        ]
    )
    orientation = fields.Selection(
        selection=[
            ('debit', 'Debit'),
            ('credit', 'Credit'),
        ]
    )
    aggregation = fields.Selection(
        selection=[
            ('plus', '+'),
            ('minus', '-'),
        ]
    )
    reclassify = fields.Boolean(
        required=True,
        default=False,
    )
    item_ids = fields.Many2many('account.cn.report.item')
