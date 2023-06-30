import time
import calendar

from odoo import api, models

class SubsidiaryLedgerReport(models.AbstractModel):
    _name = 'report.account_cn.subsidiary_ledger'

    @api.model
    def _get_report_values(self, docids, data=None):
        initial_balance_data = self._get_initial_balance_data(
            data['company_id'],
            data['account_id'],
            data['date_from'],
        )
        period_amount_data = self._get_period_amount_data(
            data['company_id'],
            data['account_id'],
            data['date_from'],
            data['date_to'],
        )
        subsidiary_ledger = self._create_subsidiary_ledger(
            data,
            initial_balance_data,
            period_amount_data,
        )
        return {
            'data': data,
            'subsidiary_ledger': subsidiary_ledger,
        }

    def _get_initial_balance_data(
        self,
        company_id,
        account_id,
        initial_date,
        ):
        domain = [
            ('company_id', '=', company_id),
            ('account_id', '=', account_id),
            ('date', '<', initial_date),
        ]
        data = self.env['account.cn.voucher.line'].read_group(
            domain,
            fields=[
                'account_id',
                'debit:sum',
                'credit:sum',
            ],
            groupby=[
                'account_id',
            ],
            lazy=False
        )
        return data

    def _get_period_amount_data(
        self,
        company_id,
        account_id,
        date_from,
        date_to,
        ):
        domain = [
            ('company_id', '=', company_id),
            ('account_id', '=', account_id),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ]
        data = self.env['account.cn.voucher.line'].read_group(
            domain,
            fields=[
                'date',
                'date',
                'date',
                'voucher_id',
                'voucher_word',
                'voucher_number',
                'summary',
                'debit:sum',
                'credit:sum',
            ],
            groupby=[
                'date:year',
                'date:month',
                'date:day',
                'voucher_id',
                'voucher_word',
                'voucher_number',
                'summary',
            ],
            orderby='date:year ASC, date:month ASC, date:day ASC',
            lazy=False
        )
        return data

    def _create_subsidiary_ledger(
        self,
        data,
        initial_balance_data,
        period_amount_data,
        ):
        subsidiary_ledger = []
        initial_balance = {
            'date': time.strftime('%d %b %Y', time.strptime(data['date_from'], '%Y-%m-%d')),
            'voucher_id': None,
            'voucher_word_number': None,
            'summary': 'Initial balance',
            'debit': 0.0,
            'credit': 0.0,
            'orient': False,
            'balance': 0.0,
        }
        for ib in initial_balance_data:
            initial_balance['debit'] += ib['debit']
            initial_balance['credit'] += ib['credit']

        initial_balance['balance'] = initial_balance['debit'] - initial_balance['credit']
        subsidiary_ledger += [initial_balance]

        date_years = set()
        date_years.add(period_amount_data[0]['date:year'])
        date_months = set()
        date_months.add(period_amount_data[0]['date:month'])
        total_month = {
            'date': None,
            'voucher_id': None,
            'voucher_word_number': None,
            'summary': 'The month total',
            'debit': 0.0,
            'credit': 0.0,
            'orient': False,
            'balance': initial_balance['balance'],
        }
        total_year = {
            'date': None,
            'voucher_id': None,
            'voucher_word_number': None,
            'summary': 'The year total',
            'debit': 0.0,
            'credit': 0.0,
            'orient': False,
            'balance': 0.0,
        }
        for pa in period_amount_data:
            item = {
                'date': pa['date:day'],
                'voucher_id': pa['voucher_id'][0],
                'voucher_word_number': pa['voucher_word'][1] + '-' + pa['voucher_number'],
                'summary': pa['summary'],
                'debit': pa['debit'],
                'credit': pa['credit'],
                'orient': False,
                'balance': 0.0,
            }
            if pa['date:month'] in date_months:
                total_month['debit'] += item['debit']
                total_month['credit'] += item['credit']
                total_month['balance'] = total_month['balance'] + item['debit'] - item['credit']
                item['balance'] = total_month['balance']
                subsidiary_ledger += [item]
            elif pa['date:year'] in date_years:
                date_months.add(pa['date:month'])
                total_month['date'] = self._last_month_end(pa['date:day'])
                subsidiary_ledger += [dict(total_month)]
                total_year['date'] = total_month['date']
                total_year['debit'] += total_month['debit']
                total_year['credit'] += total_month['credit']
                total_year['balance'] = total_month['balance']
                subsidiary_ledger += [dict(total_year)]
                total_month['debit'] = item['debit']
                total_month['credit'] = item['credit']
                total_month['balance'] = total_month['balance'] + item['debit'] - item['credit']
                item['balance'] = total_month['balance']
                subsidiary_ledger += [item]
            else:
                date_months.add(pa['date:month'])
                date_years.add(pa['date:year'])
                total_month['date'] = self._last_year_end(pa['date:day'])
                subsidiary_ledger += [dict(total_month)]
                total_year['date'] = total_month['date']
                total_year['debit'] += total_month['debit']
                total_year['credit'] += total_month['credit']
                total_year['balance'] = total_month['balance']
                subsidiary_ledger += [dict(total_year)]
                total_month['debit'] = item['debit']
                total_month['credit'] = item['credit']
                total_month['balance'] = total_month['balance'] + item['debit'] - item['credit']
                item['balance'] = total_month['balance']
                subsidiary_ledger += [item]
                total_year['debit'] = 0.0
                total_year['credit'] = 0.0

        total_month['date'] = self._this_month_end(pa['date:day'])
        subsidiary_ledger += [total_month]
        total_year['date'] = total_month['date']
        total_year['debit'] += total_month['debit']
        total_year['credit'] += total_month['credit']
        total_year['balance'] = total_month['balance']
        subsidiary_ledger += [total_year]

        return subsidiary_ledger

    def _last_month_end(self, date):
        time_tuple = time.strptime(date, '%d %b %Y')
        e_year = str(time_tuple[0])
        e_month = str(time_tuple[1] - 1)
        e_day = str(calendar.monthrange(time_tuple[0], time_tuple[1] - 1)[1])
        e_date = time.strptime('-'.join([e_year, e_month, e_day]), '%Y-%m-%d')
        return time.strftime('%d %b %Y', e_date)

    def _last_year_end(self, date):
        time_tuple = time.strptime(date, '%d %b %Y')
        e_year = str(time_tuple[0] - 1)
        e_month = '12'
        e_day = '31'
        e_date = time.strptime('-'.join([e_year, e_month, e_day]), '%Y-%m-%d')
        return time.strftime('%d %b %Y', e_date)

    def _this_month_end(self, date):
        time_tuple = time.strptime(date, '%d %b %Y')
        e_year = str(time_tuple[0])
        e_month = str(time_tuple[1])
        e_day = str(calendar.monthrange(time_tuple[0], time_tuple[1])[1])
        e_date = time.strptime('-'.join([e_year, e_month, e_day]), '%Y-%m-%d')
        return time.strftime('%d %b %Y', e_date)
