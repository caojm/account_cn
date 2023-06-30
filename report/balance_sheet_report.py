import time
import calendar

from odoo import api, models

class SubsidiaryLedgerReport(models.AbstractModel):
    _name = 'report.account_cn.balance_sheet'

    @api.model
    def _get_report_values(self, docids, data=None):
        opening_data = self._get_opening_data(
            data['company_id'],
            data['date_from'],
            data['posted'],
        )
        closing_data = self._get_closing_data(
            data['company_id'],
            data['date_to'],
            data['posted'],
        )
        data['report_model'] = 'BS'
        report_data = {}
        report_data['OB'] = opening_data
        report_data['CB'] = closing_data
        bs_data = self._create_balance_sheet(
            data,
            report_data,
        )
        return {
            'data': data,
            'bs_data': bs_data,
        }

    def _get_opening_data(
        self,
        company_id,
        opening_date,
        posted,
        ):
        domain = [
            ('company_id', '=', company_id),
            ('date', '<', opening_date),
        ]
        if posted:
            domian += [('voucher_state', '=', 'posted')]
        data = self.env['account.cn.voucher.line'].read_group(
            domain,
            fields=[
                'account_id',
                'partner_id',
                'debit:sum',
                'credit:sum',
            ],
            groupby=[
                'account_id',
                'partner_id',
            ],
            lazy=False
        )
        return data

    def _get_closing_data(
        self,
        company_id,
        closing_date,
        posted,
        ):
        domain = [
            ('company_id', '=', company_id),
            ('date', '<=', closing_date),
        ]
        if posted:
            domian += [('voucher_state', '=', 'posted')]
        data = self.env['account.cn.voucher.line'].read_group(
            domain,
            fields=[
                'account_id',
                'partner_id',
                'debit:sum',
                'credit:sum',
            ],
            groupby=[
                'account_id',
                'partner_id',
            ],
            lazy=False
        )
        return data

    def _create_balance_sheet(
        self,
        data,
        report_data
        ):
        report_model = self.env['account.cn.report.model'].search(
            [
                ('code', '=', data['report_model']),
            ],
            limit=1,
        )
        bs_data = {}
        if report_model.ensure_one():
            for item in report_model.item_ids:
                if item.input:
                    bs_data[item.code] = item.input
                elif not item.measure_id.id:
                    bs_data[item.code] = item.name
                elif len(item.filter_ids) == 0:
                    bs_data[item.code] = None
                else:
                    #bs_data[item.code] = item.filter_ids
                    data_source = report_data[item.measure_id.code]
                    bs_data[item.code] = 0.0
                    for f in item.filter_ids:
                        data_source_filtered = filter(lambda r: r['account_id'][0] == f.account_id.id, data_source)
                        if f.reclassify:
                            if f.amount_type == 'balance':
                                if f.orientation == 'debit':
                                    balance_data = sum([x['debit'] - x['credit'] for x in data_source_filtered if x['debit'] - x['credit'] > 0.0 ])
                                    if f.aggregation == 'plus':
                                        bs_data[item.code] += balance_data
                                    else:
                                        bs_data[item.code] -= balance_data
                                else:
                                    balance_data = sum([x['debit'] - x['credit'] for x in data_source_filtered if x['debit'] - x['credit'] < 0.0 ])
                                    if f.aggregation == 'plus':
                                        bs_data[item.code] -= balance_data
                                    else:
                                        bs_data[item.code] += balance_data
                            else:
                                if f.orientation == 'debit':
                                    movement_data = sum([x['debit'] for x in data_source_filtered if x['debit'] > 0.0])
                                    if f.aggregation == 'plus':
                                        bs_data[item.code] += movement_data
                                    else:
                                        bs_data[item.code] -= movement_data
                                else:
                                    movement_data = sum([x['credit'] for x in data_source_filtered if x['credit'] > 0.0])
                                    if f.aggregation == 'plus':
                                        bs_data[item.code] += movement_data
                                    else:
                                        bs_data[item.code] -= movement_data
                        else:
                            if f.amount_type == 'balance':
                                balance_data = sum([x['debit'] - x['credit'] for x in data_source_filtered])
                                if f.orientation == 'debit':
                                    if balance_data > 0.0:
                                        if f.aggregation == 'plus':
                                            bs_data[item.code] += balance_data
                                        else:
                                            bs_data[item.code] -= balance_data
                                    else:
                                        continue
                                else:
                                    if balance_data < 0.0:
                                        if f.aggregation == 'plus':
                                            bs_data[item.code] -= balance_data
                                        else:
                                            bs_data[item.code] += balance_data
                                    else:
                                        continue
                            else:
                                if f.orientation == 'debit':
                                    movement_data = sum([x['debit'] for x in data_source_filtered])
                                    if f.aggregation == 'plus':
                                        bs_data[item.code] += movement_data
                                    else:
                                        bs_data[item.code] -= movement_data
                                else:
                                    movement_data = sum([x['credit'] for x in data_source_filtered])
                                    if f.aggregation == 'plus':
                                        bs_data[item.code] += movement_data
                                    else:
                                        bs_data[item.code] -= movement_data
        return bs_data
