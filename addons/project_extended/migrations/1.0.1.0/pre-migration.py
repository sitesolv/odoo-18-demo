from odoo import tools

def migrate(env, version):
    """
    Add bought_date field to project.hosting model if it doesn't exist
    """
    cr = env.cr
    
    # Check if the column exists
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='project_hosting' AND column_name='bought_date'
    """)
    
    result = cr.fetchone()
    
    # If the column doesn't exist, add it
    if not result:
        tools.sql.add_column(cr, 'project_hosting', 'bought_date', 'date')
        cr.commit()
