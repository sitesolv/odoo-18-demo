/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

export class ProjectDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
    }

    async refreshDashboard() {
        // Reload the current view
        await this.env.services.action.doAction({
            type: 'ir.actions.client',
            tag: 'reload',
        });
    }

    async openIncomeAnalysis() {
        return this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Income Analysis',
            res_model: 'project.income',
            view_mode: 'graph,pivot,tree',
            target: 'current',
        });
    }

    async openExpenseAnalysis() {
        return this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Expense Analysis',
            res_model: 'project.expense',
            view_mode: 'graph,pivot,tree',
            target: 'current',
        });
    }
}

ProjectDashboard.template = "project_dashboard.Dashboard";

registry.category("actions").add("project_dashboard", ProjectDashboard);
