# Project Extended - Invoice Payment Integration

This module extends the project management system to automatically create project income entries when invoice payments are received.

## Features

### Real-Time Project Income Creation
- **Automatic**: Project income entries are created immediately when:
  - A payment is posted and marked as paid
  - An invoice is reconciled with a payment (including partial payments)
  - Payment reconciliation occurs (handles partial reconciliations)
- **Accurate Partial Payments**: System correctly calculates the exact amount allocated to each invoice
- **Multiple Triggers**: Works on payment creation, payment posting, and reconciliation events

### Automatic Project Income Creation
- When a customer pays an invoice that is linked to a project, the system automatically creates a project income entry
- The payment amount, date, customer, and memo are copied to the project income record
- Works with full payments and partial payments
- Real-time processing ensures immediate synchronization

### Project Linking Methods
The system uses multiple methods to link invoices to projects:

1. **Sale Order Lines**: Checks if the invoice line is linked to a sale order line that has a project
2. **Sale Order**: Checks if the sale order itself has a project assigned
3. **Invoice Origin**: Uses the invoice origin field to find the related sale order
4. **Analytic Distribution**: Falls back to finding projects through analytic accounts

### Manual Control
- View payment records to see if project income was created automatically
- Use the "Create Project Income" button on payments to manually trigger the process
- Project income records show their source (manual or automatic)
- **Bulk Sync**: Use "Sync Payments to Income" menu to process all payments at once
- **Scheduled Sync**: Automatic hourly sync ensures no payments are missed

### Project Income Tracking
- All project income entries show their source type
- Payment and invoice references are stored for traceability
- Prevents duplicate income entries for the same payment
- **Real-time Updates**: Income entries are created immediately upon payment/reconciliation

## Usage

1. **Setup**: Install the module and ensure your invoices are properly linked to projects through sale orders
2. **Real-Time**: As soon as customers pay invoices, project income is automatically created in real-time
3. **Partial Payments**: System handles partial payments accurately, recording the exact amount paid
4. **Manual**: For any missed payments, use the "Create Project Income" button or bulk sync
5. **Monitor**: Check the project income list to see all entries and their sources

### Real-Time Processing
The system monitors:
- Payment creation and posting
- Invoice reconciliation events  
- Partial reconciliation processes
- Ensures immediate income recording without delays

## Configuration

Ensure that:
- Sale orders are linked to projects
- Invoices are created from sale orders
- Payments are properly reconciled with invoices

The system will handle the rest automatically!
