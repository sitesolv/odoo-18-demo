/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class ProjectReportingDashboard extends Component {
    static template = "project_reporting.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        
        this.state = useState({
            dashboardData: {},
            kpis: {},
            loading: true,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            console.log("Loading dashboard data...");
            const [dashboardData, kpis] = await Promise.all([
                this.orm.call("project.reporting.dashboard", "get_dashboard_data", []),
                this.orm.call("project.reporting.dashboard", "get_project_kpis", []),
            ]);

            console.log("Dashboard data received:", dashboardData);
            console.log("KPIs received:", kpis);
            
            this.state.dashboardData = dashboardData;
            this.state.kpis = kpis;
            this.state.loading = false;
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.loading = false;
        }
    }

    async openProjectAnalysis() {
        try {
            // For now, redirect to regular project list until project.dashboard model is working
            return this.actionService.doAction({
                type: "ir.actions.act_window",
                name: "Projects",
                res_model: "project.project",
                view_mode: "kanban,list",
                views: [
                    [false, "kanban"],
                    [false, "list"],
                ],
                target: "current",
            });
        } catch (error) {
            console.error("Error opening project analysis:", error);
        }
    }

    async openIncomeAnalysis() {
        try {
            return this.actionService.doAction({
                type: "ir.actions.act_window",
                name: "Income Analysis",
                res_model: "project.income",
                view_mode: "graph,list",
                views: [
                    [false, "graph"],
                    [false, "list"],
                ],
                target: "current",
            });
        } catch (error) {
            console.error("Error opening income analysis:", error);
        }
    }

    async openExpenseAnalysis() {
        try {
            return this.actionService.doAction({
                type: "ir.actions.act_window",
                name: "Expense Analysis",
                res_model: "project.expense",
                view_mode: "graph,list",
                views: [
                    [false, "graph"],
                    [false, "list"],
                ],
                target: "current",
            });
        } catch (error) {
            console.error("Error opening expense analysis:", error);
        }
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(value || 0);
    }

    formatPercentage(value) {
        return `${(value || 0).toFixed(1)}%`;
    }
}

registry.category("actions").add("project_reporting_dashboard", ProjectReportingDashboard);
