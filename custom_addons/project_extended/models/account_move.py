from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        """Override to trigger project income creation when invoice is posted"""
        result = super()._post(soft=soft)
        # After posting, check if any existing payments should create project income
        for move in self:
            if move.move_type in ('out_invoice', 'out_refund'):
                move._check_existing_payments_for_project_income()
                # Also update related projects' amount due
                move._update_related_projects_amount_due()
        return result

    def write(self, vals):
        """Override to trigger project amount due updates when invoice changes"""
        result = super().write(vals)
        
        # Check if relevant fields changed
        trigger_fields = ['state', 'amount_residual', 'payment_state']
        if any(field in vals for field in trigger_fields):
            # Update related projects' amount due
            for move in self:
                if move.move_type in ('out_invoice', 'out_refund'):
                    move._update_related_projects_amount_due()
        
        return result

    def _check_existing_payments_for_project_income(self):
        """Check if this invoice has payments that should create project income"""
        # Find all payments that have reconciled this invoice
        payment_lines = self.line_ids.mapped('matched_debit_ids.debit_move_id') + \
                       self.line_ids.mapped('matched_credit_ids.credit_move_id')
        
        payments = self.env['account.payment'].search([
            ('move_id', 'in', payment_lines.mapped('move_id').ids)
        ])
        
        for payment in payments:
            if payment.payment_type == 'inbound':
                payment._create_project_income_from_payment()

    def _update_related_projects_amount_due(self):
        """Find and update projects related to this invoice"""
        if self.move_type in ('out_invoice', 'out_refund'):
            projects = self._find_related_projects()
            if projects:
                # Force recomputation of amount_due
                projects.refresh_amount_due()

    def _find_related_projects(self):
        """Find projects related to this invoice"""
        projects = self.env['project.project']
        
        try:
            # Method 1: Through sale order lines
            if self.invoice_line_ids:
                sale_lines = self.invoice_line_ids.mapped('sale_line_ids')
                if sale_lines:
                    # Find projects through tasks
                    tasks = self.env['project.task'].search([
                        ('sale_line_id', 'in', sale_lines.ids)
                    ])
                    projects |= tasks.mapped('project_id')
                    
                    # Find projects through sale orders
                    sale_orders = sale_lines.mapped('order_id')
                    for order in sale_orders:
                        if hasattr(order, 'project_id') and order.project_id:
                            projects |= order.project_id
            
            # Method 2: Through invoice origin/reference
            if self.invoice_origin:
                origin_projects = self.env['project.project'].search([
                    ('name', 'ilike', self.invoice_origin)
                ])
                projects |= origin_projects
                
            if self.ref:
                ref_projects = self.env['project.project'].search([
                    ('name', 'ilike', self.ref)
                ])
                projects |= ref_projects
                
        except Exception as e:
            # Log the error but don't break the process
            pass
        
        return projects

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def reconcile(self):
        """Override reconciliation to trigger project income creation in real-time"""
        result = super().reconcile()
        
        # After reconciliation, check for payments that need project income creation
        self._trigger_payment_income_creation()
        
        # Also update related projects' amount due
        self._update_related_projects_amount_due_from_lines()
            
        return result

    def remove_move_reconcile(self):
        """Handle reconciliation removal"""
        result = super().remove_move_reconcile()
        
        # After removing reconciliation, reprocess payments
        self._trigger_payment_income_creation()
        
        # Also update related projects' amount due
        self._update_related_projects_amount_due_from_lines()
        
        return result

    def _trigger_payment_income_creation(self):
        """Trigger project income creation for related payments"""
        # Find invoice moves
        invoice_moves = self.mapped('move_id').filtered(
            lambda m: m.move_type in ('out_invoice', 'out_refund')
        )
        
        # Find payment moves  
        payment_moves = self.mapped('move_id').filtered(
            lambda m: m.move_type == 'entry'
        )
        
        # Find payments related to these moves
        payments = self.env['account.payment'].search([
            ('move_id', 'in', payment_moves.ids),
            ('payment_type', '=', 'inbound')
        ])
        
        for payment in payments:
            payment._create_project_income_from_payment()

    def _update_related_projects_amount_due_from_lines(self):
        """Update projects' amount due from move lines"""
        # Get all invoice moves from these lines
        invoice_moves = self.mapped('move_id').filtered(
            lambda m: m.move_type in ('out_invoice', 'out_refund')
        )
        
        # Update amount due for each invoice's related projects
        for move in invoice_moves:
            move._update_related_projects_amount_due()

class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    @api.model_create_multi
    def create(self, vals_list):
        """Trigger project income creation when partial reconciliation happens"""
        partials = super().create(vals_list)
        
        # Process each partial reconciliation
        for partial in partials:
            self._process_partial_reconcile(partial)
        
        return partials

    def write(self, vals):
        """Handle partial reconciliation updates"""
        result = super().write(vals)
        
        for partial in self:
            self._process_partial_reconcile(partial)
            
        return result

    def unlink(self):
        """Handle partial reconciliation removal"""
        # Store payment info before deletion
        payment_ids = []
        for partial in self:
            payment_moves = [partial.debit_move_id.move_id, partial.credit_move_id.move_id]
            payments = self.env['account.payment'].search([
                ('move_id', 'in', [m.id for m in payment_moves if m]),
                ('payment_type', '=', 'inbound')
            ])
            payment_ids.extend(payments.ids)
        
        result = super().unlink()
        
        # Reprocess payments after unlink
        payments = self.env['account.payment'].browse(payment_ids)
        for payment in payments:
            payment._create_project_income_from_payment()
            
        return result

    def _process_partial_reconcile(self, partial):
        """Process a partial reconciliation to trigger income creation"""
        # Get the moves involved
        debit_move = partial.debit_move_id.move_id
        credit_move = partial.credit_move_id.move_id
        
        # Find the payment move
        payment_move = None
        invoice_move = None
        
        if debit_move.move_type in ('out_invoice', 'out_refund'):
            invoice_move = debit_move
            payment_move = credit_move
        elif credit_move.move_type in ('out_invoice', 'out_refund'):
            invoice_move = credit_move
            payment_move = debit_move
        
        if payment_move:
            # Find the payment record
            payment = self.env['account.payment'].search([
                ('move_id', '=', payment_move.id),
                ('payment_type', '=', 'inbound')
            ], limit=1)
            
            if payment:
                payment._create_project_income_from_payment()
        
        # Update amount due for the invoice's related projects
        if invoice_move:
            invoice_move._update_related_projects_amount_due()
