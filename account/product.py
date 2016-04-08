# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from string import ascii_uppercase

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'property_account_income_categ': fields.property(
            type='many2one',
            relation='account.account',
            string="Income Account",
            help="This account will be used for invoices to value sales."),
        'property_account_expense_categ': fields.property(
            type='many2one',
            relation='account.account',
            string="Expense Account",
            help="This account will be used for invoices to value expenses."),
    }

#----------------------------------------------------------
# Products
#----------------------------------------------------------

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'taxes_id': fields.many2many('account.tax', 'product_taxes_rel',
            'prod_id', 'tax_id', 'Customer Taxes',
            domain=[('parent_id','=',False),('type_tax_use','in',['sale','all'])]),
        'supplier_taxes_id': fields.many2many('account.tax',
            'product_supplier_taxes_rel', 'prod_id', 'tax_id',
            'Supplier Taxes', domain=[('parent_id', '=', False),('type_tax_use','in',['purchase','all'])]),
        'property_account_income': fields.property(
            type='many2one',
            relation='account.account',
            string="Income Account",
            help="This account will be used for invoices instead of the default one to value sales for the current product."),
        'property_account_expense': fields.property(
            type='many2one',
            relation='account.account',
            string="Expense Account",
            help="This account will be used for invoices instead of the default one to value expenses for the current product."),
    }

    def create(self, cr, uid, vals, context=None):
        print 'add create function'

        account_obj = self.pool.get('account.account')
        data_obj = self.pool.get('ir.model.data')
        
        #sequence for Product Account Income
        if vals.get('sale_ok'):
            print 'INCOME'
            tmp_account_ids = account_obj.search(cr, uid, [('code','=','20')])
            tmp_account = account_obj.browse(cr, uid, tmp_account_ids)

            account_type_id = data_obj.xmlid_to_res_id(cr, uid, 'account.data_account_type_income')

            for idx in ascii_uppercase:
                if str(vals['name'][:1].upper()) == idx:
                    #call the respective sequence
                    code = self.pool.get('ir.sequence').get(cr, uid, 'account.income.sequence') or '/'
                    account_id = account_obj.create(cr, uid, {
                                                                'code': code,
                                                                'name': vals['name'],
                                                                'parent_id': tmp_account.id,
                                                                'type': 'other',
                                                                'user_type': account_type_id})
                    vals['property_account_income'] = account_id
                    print vals['property_account_income']
                    break

        #sequence for Product Account Expense
        if vals.get('sale_ok') == False:
            print 'EXPENSE'
            tmp_account_ids = account_obj.search(cr, uid, [('code','=','22')])
            tmp_account = account_obj.browse(cr, uid, tmp_account_ids)

            account_type_id = data_obj.xmlid_to_res_id(cr, uid, 'account.data_account_type_expense')

            for idx in ascii_uppercase:
                if str(vals['name'][:1].upper()) == idx:
                    #call the respective sequence
                    code = self.pool.get('ir.sequence').get(cr, uid, 'account.expense.sequence') or '/'
                    account_id = account_obj.create(cr, uid, {
                                                                'code': code,
                                                                'name': vals['name'],
                                                                'parent_id': tmp_account.id,
                                                                'type': 'other',
                                                                'user_type': account_type_id})
                    vals['property_account_expense'] = account_id
                    break

        ctx = dict(context or {}, mail_create_nolog=True)
        res = super(product_template, self).create(cr, uid, vals, context=ctx)
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
