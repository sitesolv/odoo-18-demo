from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProjectReportingView(models.Model):
    _name = 'project.reporting.view'
    _description = 'Project Reporting View'
    _auto = False

    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    project_name = fields.Char(string='Project Name', readonly=True)
    client_name = fields.Char(string='Client', readonly=True)
    total_income = fields.Float(string='Total Income', readonly=True)
    total_expense = fields.Float(string='Total Expense', readonly=True)
    net_profit = fields.Float(string='Net Profit', readonly=True)
    profit_margin = fields.Float(string='Profit Margin %', readonly=True)
    status = fields.Char(string='Status', readonly=True)
    active = fields.Boolean(string='Active', readonly=True)

    def init(self):
        """Create the SQL view for project reporting"""
        try:
            _logger.info(f"Starting creation of SQL view: {self._table}")
            
            # Drop existing view
            self.env.cr.execute("""
                DROP VIEW IF EXISTS %s
            """ % self._table)
            
            # First try to create a simple view to check if tables exist
            self.env.cr.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name IN ('project_income', 'project_expense')
            """)
            tables_exist = self.env.cr.fetchone()[0]
            _logger.info(f"Found {tables_exist} tables (project_income, project_expense)")
            
            if tables_exist >= 2:
                # Create the full SQL view with income/expense data
                self.env.cr.execute("""
                    CREATE OR REPLACE VIEW %s AS (
                        SELECT
                            row_number() OVER () as id,
                            p.id as project_id,
                            p.name as project_name,
                            COALESCE(partner.name, 'No Client') as client_name,
                            COALESCE(income_summary.total_income, 0) as total_income,
                            COALESCE(expense_summary.total_expense, 0) as total_expense,
                            COALESCE(income_summary.total_income, 0) - COALESCE(expense_summary.total_expense, 0) as net_profit,
                            CASE 
                                WHEN COALESCE(income_summary.total_income, 0) > 0 
                                THEN ((COALESCE(income_summary.total_income, 0) - COALESCE(expense_summary.total_expense, 0)) / COALESCE(income_summary.total_income, 1)) * 100
                                ELSE 0 
                            END as profit_margin,
                            CASE 
                                WHEN COALESCE(income_summary.total_income, 0) - COALESCE(expense_summary.total_expense, 0) > 0 THEN 'Profitable'
                                WHEN COALESCE(income_summary.total_income, 0) - COALESCE(expense_summary.total_expense, 0) < 0 THEN 'Loss'
                                ELSE 'Break Even'
                            END as status,
                            p.active as active
                        FROM project_project p
                        LEFT JOIN res_partner partner ON p.partner_id = partner.id
                        LEFT JOIN (
                            SELECT 
                                project_id, 
                                SUM(amount) as total_income
                            FROM project_income 
                            GROUP BY project_id
                        ) income_summary ON p.id = income_summary.project_id
                        LEFT JOIN (
                            SELECT 
                                project_id, 
                                SUM(amount) as total_expense
                            FROM project_expense 
                            GROUP BY project_id
                        ) expense_summary ON p.id = expense_summary.project_id
                        WHERE p.active = true
                        ORDER BY net_profit DESC
                    )
                """ % self._table)
                _logger.info(f"Successfully created full SQL view: {self._table}")
            else:
                # Create a simple fallback view if income/expense tables don't exist
                self.env.cr.execute("""
                    CREATE OR REPLACE VIEW %s AS (
                        SELECT
                            row_number() OVER () as id,
                            p.id as project_id,
                            p.name as project_name,
                            COALESCE(partner.name, 'No Client') as client_name,
                            0.0 as total_income,
                            0.0 as total_expense,
                            0.0 as net_profit,
                            0.0 as profit_margin,
                            'No Data' as status,
                            p.active as active
                        FROM project_project p
                        LEFT JOIN res_partner partner ON p.partner_id = partner.id
                        WHERE p.active = true
                    )
                """ % self._table)
                _logger.warning(f"Created fallback SQL view: {self._table} (income/expense tables not found)")
            
        except Exception as e:
            _logger.error(f"Error creating SQL view {self._table}: {e}")
            # Create a minimal fallback view
            try:
                self.env.cr.execute("""
                    CREATE OR REPLACE VIEW %s AS (
                        SELECT
                            id,
                            id as project_id,
                            name as project_name,
                            'No Client' as client_name,
                            0.0 as total_income,
                            0.0 as total_expense,
                            0.0 as net_profit,
                            0.0 as profit_margin,
                            'Error' as status,
                            active
                        FROM project_project
                        WHERE active = true
                        LIMIT 1
                    )
                """ % self._table)
                _logger.warning(f"Created minimal fallback SQL view: {self._table}")
            except Exception as e2:
                _logger.error(f"Failed to create even minimal view: {e2}")
