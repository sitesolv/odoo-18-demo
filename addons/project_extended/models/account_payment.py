from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    # Add a field to show if this payment has created project income
    project_income_created = fields.Boolean(
        string='Project Income Created',
        compute='_compute_project_income_created',
        store=True
    )
    
    @api.depends('reconciled_invoice_ids', 'state')
    def _compute_project_income_created(self):
        for payment in self:
            income_count = self.env['project.income'].search_count([
                ('payment_id', '=', payment.id)
            ])
            payment.project_income_created = income_count > 0

    @api.model_create_multi
    def create(self, vals_list):
        payments = super().create(vals_list)
        # Schedule immediate and delayed processing
        for payment in payments:
            if payment.payment_type == 'inbound':
                # Immediate attempt
                payment._create_project_income_from_payment()
                # Schedule for later to catch reconciliations that happen after creation
                self._schedule_delayed_processing(payment.id)
                # Update related projects' amount due
                payment._update_related_projects_amount_due()
        return payments

    def write(self, vals):
        result = super().write(vals)
        # Trigger on multiple field changes that could affect income creation
        trigger_fields = ['state', 'reconciled_invoice_ids', 'amount', 'partner_id', 'move_id']
        if any(field in vals for field in trigger_fields):
            for payment in self:
                if payment.payment_type == 'inbound':
                    payment._create_project_income_from_payment()
                    # Update related projects' amount due
                    payment._update_related_projects_amount_due()
        return result

    def action_post(self):
        """Override to trigger project income creation when payment is posted"""
        result = super().action_post()
        for payment in self:
            if payment.payment_type == 'inbound':
                payment._create_project_income_from_payment()
                # Also schedule delayed processing
                self._schedule_delayed_processing(payment.id)
                # Update related projects' amount due
                payment._update_related_projects_amount_due()
        return result

    @api.model
    def _schedule_delayed_processing(self, payment_id):
        """Schedule delayed processing using a commit-safe approach"""
        # Use Odoo's built-in scheduler to process after commit
        def delayed_func():
            try:
                with self.env.registry.cursor() as new_cr:
                    new_env = self.env(cr=new_cr)
                    payment = new_env['account.payment'].browse(payment_id)
                    if payment.exists() and payment.payment_type == 'inbound':
                        payment._create_project_income_from_payment()
                        new_cr.commit()
            except Exception as e:
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning("Delayed processing failed for payment %s: %s", payment_id, str(e))
        
        self.env.cr.postcommit.add(delayed_func)

    @api.model  
    def _delayed_process_payment(self, payment_id):
        """Process payment after a delay to catch late reconciliations"""
        try:
            payment = self.browse(payment_id)
            if payment.exists() and payment.payment_type == 'inbound':
                payment._create_project_income_from_payment()
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning("Delayed processing failed for payment %s: %s", payment_id, str(e))

    def action_create_project_income_manually(self):
        """Manual action to create project income from payment"""
        self.ensure_one()
        
        import logging
        _logger = logging.getLogger(__name__)
        
        _logger.info("Manual trigger for payment %s", self.name)
        
        if not self.reconciled_invoice_ids:
            # Try to find invoices manually first
            reconciled_invoices = self._find_reconciled_invoices_manually()
            if not reconciled_invoices:
                raise UserError(_("This payment has no reconciled invoices."))
        
        projects_found = []
        for invoice in self.reconciled_invoice_ids:
            project = self._get_project_from_invoice(invoice)
            if project:
                payment_amount = self._calculate_payment_amount_for_invoice(invoice)
                if payment_amount > 0:
                    self._create_project_income_entry(project, invoice, payment_amount)
                    projects_found.append(project.name)
        
        if projects_found:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': _("Project income created for projects: %s") % ', '.join(projects_found),
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _("No projects found for this payment's invoices."),
                    'sticky': False,
                }
            }

    def action_debug_payment_info(self):
        """Debug action to show payment and reconciliation info"""
        self.ensure_one()
        
        reconciled_invoices = self.reconciled_invoice_ids
        manual_invoices = self._find_reconciled_invoices_manually()
        
        message = f"""
Payment: {self.name}
State: {self.state}
Type: {self.payment_type}
Amount: {self.amount}

Reconciled Invoices (field): {len(reconciled_invoices)}
{[inv.name for inv in reconciled_invoices]}

Manual Found Invoices: {len(manual_invoices)}
{[inv.name for inv in manual_invoices]}

Project Income Created: {self.project_income_created}
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'info',
                'message': message,
                'sticky': True,
            }
        }

    def _create_project_income_from_payment(self):
        """
        Create project income entries when a payment is made for invoices
        that are linked to projects through sale orders
        """
        if self.payment_type != 'inbound':
            return
        
        import logging
        _logger = logging.getLogger(__name__)
        
        try:
            # Get all invoices reconciled with this payment
            reconciled_invoices = self.reconciled_invoice_ids
            
            # If no reconciled invoices found through the field, try to find them manually
            if not reconciled_invoices:
                reconciled_invoices = self._find_reconciled_invoices_manually()
            
            _logger.info("Payment %s: Found %d reconciled invoices", self.name, len(reconciled_invoices))
            
            for invoice in reconciled_invoices:
                # Find the project related to this invoice through sale order
                project = self._get_project_from_invoice(invoice)
                
                if project:
                    _logger.info("Payment %s: Found project %s for invoice %s", self.name, project.name, invoice.name)
                    
                    # Calculate the payment amount allocated to this invoice
                    payment_amount = self._calculate_payment_amount_for_invoice(invoice)
                    
                    _logger.info("Payment %s: Calculated amount %s for invoice %s", self.name, payment_amount, invoice.name)
                    
                    if payment_amount > 0:
                        # Create project income entry
                        self._create_project_income_entry(project, invoice, payment_amount)
                        _logger.info("Payment %s: Created project income entry", self.name)
                else:
                    _logger.warning("Payment %s: No project found for invoice %s", self.name, invoice.name)
                    
        except Exception as e:
            # Log the error but don't break the payment process
            _logger.error("Failed to create project income from payment %s: %s", self.name, str(e), exc_info=True)

    def _find_reconciled_invoices_manually(self):
        """
        Manually find reconciled invoices by looking at move line reconciliations
        """
        invoices = self.env['account.move']
        
        if not self.move_id:
            return invoices
            
        # Get payment move lines
        payment_lines = self.move_id.line_ids.filtered(
            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable')
        )
        
        # Find reconciled move lines
        for line in payment_lines:
            # Check both directions of reconciliation
            reconciled_lines = line.matched_debit_ids.mapped('credit_move_id') + \
                             line.matched_credit_ids.mapped('debit_move_id')
            
            for reconciled_line in reconciled_lines:
                if reconciled_line.move_id.move_type in ('out_invoice', 'out_refund'):
                    invoices |= reconciled_line.move_id
        
        # Also check partial reconciliations
        partial_reconciles = self.env['account.partial.reconcile'].search([
            '|',
            ('debit_move_id', 'in', payment_lines.ids),
            ('credit_move_id', 'in', payment_lines.ids)
        ])
        
        for partial in partial_reconciles:
            # Get the other side of the reconciliation
            other_line = partial.debit_move_id if partial.credit_move_id in payment_lines else partial.credit_move_id
            if other_line.move_id.move_type in ('out_invoice', 'out_refund'):
                invoices |= other_line.move_id
        
        return invoices

    def _get_project_from_invoice(self, invoice):
        """
        Find the project related to an invoice through various methods:
        1. Through sale order lines with project_id
        2. Through sale order with project_id
        3. Through analytic distribution
        4. Through invoice origin (sale order reference)
        """
        project = False
        
        # Method 1: Check if invoice has sale order lines with project_id
        if hasattr(invoice, 'invoice_line_ids'):
            for line in invoice.invoice_line_ids:
                if hasattr(line, 'sale_line_ids'):
                    for sale_line in line.sale_line_ids:
                        if hasattr(sale_line, 'project_id') and sale_line.project_id:
                            project = sale_line.project_id
                            break
                        # Also check product project
                        if hasattr(sale_line, 'product_id') and sale_line.product_id.project_id:
                            project = sale_line.product_id.project_id
                            break
                if project:
                    break
        
        # Method 2: Check sale order project_id
        if not project and hasattr(invoice, 'invoice_line_ids'):
            for line in invoice.invoice_line_ids:
                if hasattr(line, 'sale_line_ids'):
                    for sale_line in line.sale_line_ids:
                        if hasattr(sale_line, 'order_id') and sale_line.order_id.project_id:
                            project = sale_line.order_id.project_id
                            break
                if project:
                    break
        
        # Method 3: Check through invoice origin (sale order name)
        if not project and hasattr(invoice, 'invoice_origin') and invoice.invoice_origin:
            # Try to find sale order by name
            sale_orders = self.env['sale.order'].search([
                ('name', '=', invoice.invoice_origin)
            ])
            for sale_order in sale_orders:
                if sale_order.project_id:
                    project = sale_order.project_id
                    break
                # Also check if any line has a project
                for line in sale_order.order_line:
                    if hasattr(line, 'project_id') and line.project_id:
                        project = line.project_id
                        break
                    if hasattr(line, 'product_id') and line.product_id.project_id:
                        project = line.product_id.project_id
                        break
                if project:
                    break
        
        # Method 4: Check through analytic distribution (fallback)
        if not project:
            # Try to find project through analytic account
            for line in invoice.invoice_line_ids:
                if hasattr(line, 'analytic_distribution') and line.analytic_distribution:
                    # Get analytic accounts from distribution
                    analytic_account_ids = []
                    for account_id in line.analytic_distribution.keys():
                        try:
                            analytic_account_ids.append(int(account_id))
                        except (ValueError, TypeError):
                            continue
                    
                    if analytic_account_ids:
                        # Find projects with these analytic accounts
                        projects = self.env['project.project'].search([
                            ('account_id', 'in', analytic_account_ids)
                        ], limit=1)
                        if projects:
                            project = projects[0]
                            break
        
        return project

    def _calculate_payment_amount_for_invoice(self, invoice):
        """
        Calculate the amount of this payment that goes to the specific invoice
        This handles both full and partial payments accurately
        """
        if not self.move_id or not invoice:
            return 0
        
        # Get payment move lines that affect receivable/payable accounts
        payment_lines = self.move_id.line_ids.filtered(
            lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable')
        )
        
        total_allocated = 0
        
        for payment_line in payment_lines:
            # Find reconciliations with this specific invoice
            debit_reconciles = payment_line.matched_debit_ids.filtered(
                lambda r: r.credit_move_id.move_id == invoice
            )
            credit_reconciles = payment_line.matched_credit_ids.filtered(
                lambda r: r.debit_move_id.move_id == invoice
            )
            
            # Sum up the amounts allocated to this invoice
            for reconcile in debit_reconciles:
                total_allocated += reconcile.amount
            
            for reconcile in credit_reconciles:
                total_allocated += reconcile.amount
        
        # If no specific reconciliation found, fall back to proportional calculation
        if total_allocated == 0 and len(self.reconciled_invoice_ids) > 0:
            total_invoice_amount = sum(abs(inv.amount_total) for inv in self.reconciled_invoice_ids)
            if total_invoice_amount > 0:
                total_allocated = (abs(invoice.amount_total) / total_invoice_amount) * abs(self.amount)
        
        return total_allocated

    def _create_project_income_entry(self, project, invoice, amount):
        """
        Create a project income entry
        """
        # Check if an income entry already exists for this payment and invoice
        existing_income = self.env['project.income'].search([
            ('payment_id', '=', self.id),
            ('invoice_id', '=', invoice.id),
        ], limit=1)
        
        if existing_income:
            # Income entry already exists, skip
            return
        
        # Prepare description from memo or default
        description = self.memo or f'Payment {self.name} for Invoice {invoice.name}'
        
        # Create the income entry
        income_vals = {
            'project_id': project.id,
            'client_id': self.partner_id.id,
            'amount': amount,
            'date': self.date,
            'description': description,
            'payment_id': self.id,
            'invoice_id': invoice.id,
            'source_type': 'payment',
        }
        
        self.env['project.income'].create(income_vals)

    @api.model
    def cron_sync_payments_to_project_income(self):
        """
        Scheduled action to sync any missed payments to project income
        This ensures all payments are eventually captured
        """
        # Find paid inbound payments that haven't created project income yet
        payments_to_sync = self.search([
            ('state', '=', 'paid'),
            ('payment_type', '=', 'inbound'),
            ('project_income_created', '=', False),
            ('date', '>=', fields.Date.subtract(fields.Date.today(), days=30))  # Last 30 days
        ])
        
        count = 0
        for payment in payments_to_sync:
            try:
                payment._create_project_income_from_payment()
                count += 1
            except Exception as e:
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning("Failed to sync payment %s: %s", payment.name, str(e))
        
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info("Synced %d payments to project income", count)
        
        return count

    def action_sync_all_project_payments(self):
        """
        Manual action to sync all payments for all projects
        Useful for initial setup or bulk sync
        """
        self.ensure_one()
        
        # Find all paid inbound payments
        all_payments = self.search([
            ('state', '=', 'paid'),
            ('payment_type', '=', 'inbound'),
        ])
        
        synced_count = 0
        for payment in all_payments:
            try:
                # Force re-creation even if already exists (for testing)
                payment._create_project_income_from_payment()
                synced_count += 1
            except Exception:
                pass
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _("Processed %d payments for project income sync") % synced_count,
                'sticky': False,
            }
        }

    def _update_related_projects_amount_due(self):
        """Update amount due for projects related to this payment"""
        try:
            # Find invoices related to this payment
            related_invoices = self.reconciled_invoice_ids
            
            # Update amount due for projects related to these invoices
            for invoice in related_invoices:
                if hasattr(invoice, '_update_related_projects_amount_due'):
                    invoice._update_related_projects_amount_due()
                    
        except Exception:
            # Don't break the payment process if amount due update fails
            pass
