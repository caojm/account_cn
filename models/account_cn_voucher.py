from odoo import api, fields, models


class AccountCnVoucher(models.Model):
    _name = "account.cn.voucher"
    _description = "Accounting Voucher"
    _check_company_auto = True


    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    company_currency_id = fields.Many2one(
        string='Company Currency',
        related='company_id.currency_id', readonly=True,
    )
    accounting_book_id = fields.Many2one(
        'account.cn.accounting.book',
        required=True,
        check_company=True,
    )
    date = fields.Date()
    word_id = fields.Many2one(
        'account.cn.voucher.word',
        # required=True,
        check_company=True,
    )
    number = fields.Char()
    attachment = fields.Integer()
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        default='draft',
    )
    amount_total= fields.Monetary(
        string='Amount',
        compute='_compute_amount', store=True, readonly=True,
        currency_field='company_currency_id',
    )
    line_ids = fields.One2many('account.cn.voucher.line', 'voucher_id', string='Entries')


    @api.depends(
        'line_ids.currency_id',
        'line_ids.debit',
        'line_ids.credit',
        )
    def _compute_amount(self):
        for voucher in self:
            amount_total = 0.0
            for line in voucher.line_ids:
                amount_total += line.debit
            voucher.amount_total = amount_total
