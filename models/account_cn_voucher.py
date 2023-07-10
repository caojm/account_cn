from odoo import api, fields, models


class AccountCnVoucher(models.Model):
    _name = "account.cn.voucher"
    _description = "Accounting Voucher"
    _check_company_auto = True

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    company_currency_id = fields.Many2one(
        string="Company Currency",
        related="company_id.currency_id",
        readonly=True,
    )
    accounting_book_id = fields.Many2one(
        "account.cn.accounting.book",
        required=True,
        default=lambda self: self.env.user.accounting_book_id,
        check_company=True,
    )
    date = fields.Date(
        default=fields.Date.today,
        required=True,
        states={
            "posted": [("readonly", True)],
            "cancel": [("readonly", True)],
        },
        copy=False,
    )
    word_id = fields.Many2one(
        "account.cn.voucher.word",
        required=True,
        default=lambda self: self.env.user.voucher_word_id,
        check_company=True,
    )
    name_id = fields.Many2one(
        "account.cn.voucher.type",
        default=lambda self: self.env.user.voucher_type_id,
    )
    number = fields.Char(
        compute="_compute_number",
        store=True,
        readonly=False,
    )
    attachment = fields.Integer()
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        required=True,
        readonly=True,
        copy=False,
        default="draft",
    )
    amount_total = fields.Monetary(
        string="Amount",
        compute="_compute_amount",
        store=True,
        readonly=True,
        currency_field="company_currency_id",
    )
    line_ids = fields.One2many(
        "account.cn.voucher.line",
        "voucher_id",
        string="Entries",
        copy=True,
    )

    @api.depends(
        "line_ids.currency_id",
        "line_ids.debit",
        "line_ids.credit",
    )
    def _compute_amount(self):
        for voucher in self:
            amount_total = 0.0
            for line in voucher.line_ids:
                amount_total += line.debit
            voucher.amount_total = amount_total

    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s-%s (%s)" % (record.word_id.name, record.number, record.date)
            result.append((record.id, rec_name))
        return result

    @api.depends(
        "date",
        "word_id",
    )
    def _compute_number(self):
        seq = self.word_id.voucher_number_sequence_id._get_current_sequence(self.date)
        self.number = seq.sequence_id.get_next_char(seq.number_next_actual)

    @api.model
    def create(self, vals):
        new_record = super().create(vals)
        new_record.number = new_record.word_id.voucher_number_sequence_id.next_by_id(
            new_record.date
        )
        return new_record

    def write(self, vals):
        if "word_id" in vals or "date" in vals:
            Word = self.env["account.cn.voucher.word"]
            old_seq = self.word_id.voucher_number_sequence_id._get_current_sequence(
                self.date
            )
            new_seq = Word.browse(
                vals.get("word_id", self.word_id.id)
            ).voucher_number_sequence_id._get_current_sequence(
                vals.get("date", self.date)
            )
            if new_seq != old_seq:
                vals["number"] = new_seq.sequence_id.next_by_id(
                    vals.get("date", self.date)
                )
            else:
                vals["number"] = self.number
        super().write(vals)
