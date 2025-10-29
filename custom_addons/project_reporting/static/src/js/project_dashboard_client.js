/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

console.log("Project Dashboard Client JS loaded");

class ProjectDashboard extends Component {
    setup() {
        console.log("ProjectDashboard setup() called");
        this.orm = useService("orm");
        this.http = useService("http");
        this.state = useState({
            projects: [],
            company_summary: {},
            currency_symbol: '$',
            loading: true,
            dashboardData: {},
            kpis: {}
        });
        
        onWillStart(async () => {
            console.log("ProjectDashboard onWillStart called");
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;
            console.log("Loading project list data...");
            
            // Load projects using ORM for project list view
            const projects = await this.orm.searchRead(
                'project.project',
                [],
                [
                    'name', 
                    'partner_id', 
                    'user_id',
                    'date_start',
                    'date',
                    'stage_id',
                    'active',
                    'privacy_visibility',
                    'task_count',
                    'task_count_with_subtasks'
                ]
            );
            
            console.log("Projects loaded:", projects);
            
            // Update state with project list data
            this.state.projects = projects.map(project => ({
                id: project.id,
                name: project.name,
                partner_id: project.partner_id ? project.partner_id[1] : 'No Customer',
                user_id: project.user_id ? project.user_id[1] : 'No Manager',
                date_start: project.date_start,
                date: project.date,
                stage_id: project.stage_id ? project.stage_id[1] : 'No Stage',
                active: project.active,
                privacy_visibility: project.privacy_visibility,
                task_count: project.task_count || 0,
                task_count_with_subtasks: project.task_count_with_subtasks || 0
            }));
            
            // Set dashboard data for summary
            this.state.dashboardData = {
                total_projects: this.state.projects.length,
                active_projects: this.state.projects.filter(p => p.active).length,
                inactive_projects: this.state.projects.filter(p => !p.active).length,
                projects_with_tasks: this.state.projects.filter(p => p.task_count > 0).length
            };
            
            console.log("Final dashboard state:", this.state);
            
        } catch (error) {
            console.error("Error loading project data:", error);
            
            // Set default empty state
            this.state.projects = [];
            this.state.dashboardData = {
                total_projects: 0,
                active_projects: 0,
                inactive_projects: 0,
                projects_with_tasks: 0
            };
        } finally {
            this.state.loading = false;
        }
    }

    async refreshDashboard() {
        await this.loadDashboardData();
    }

    formatCurrency(amount) {
        return `${this.state.currency_symbol}${amount.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`;
    }

    getStatusClass(status) {
        if (status === 'Profitable') return 'badge-success';
        if (status === 'Loss') return 'badge-danger';
        return 'badge-warning';
    }

    getProfitClass(profit) {
        return profit >= 0 ? 'text-success' : 'text-danger';
    }

    async openProject(projectId) {
        try {
            const action = {
                type: 'ir.actions.act_window',
                name: 'Project',
                res_model: 'project.project',
                res_id: projectId,
                view_mode: 'form',
                target: 'current'
            };
            await this.env.services.action.doAction(action);
        } catch (error) {
            console.error("Error opening project:", error);
        }
    }

    async openProjectTasks(projectId) {
        try {
            const action = {
                type: 'ir.actions.act_window',
                name: 'Project Tasks',
                res_model: 'project.task',
                view_mode: 'list,form',
                domain: [['project_id', '=', projectId]],
                context: { default_project_id: projectId },
                target: 'current'
            };
            await this.env.services.action.doAction(action);
        } catch (error) {
            console.error("Error opening project tasks:", error);
        }
    }

    async viewIncome(projectId) {
        try {
            const action = {
                type: 'ir.actions.act_window',
                name: 'Project Income',
                res_model: 'project.income',
                view_mode: 'list,form',
                domain: [['project_id', '=', projectId]],
                context: { default_project_id: projectId },
                target: 'current'
            };
            await this.env.services.action.doAction(action);
        } catch (error) {
            console.error("Error opening income view:", error);
        }
    }

    async viewExpenses(projectId) {
        try {
            const action = {
                type: 'ir.actions.act_window',
                name: 'Project Expenses',
                res_model: 'project.expense',
                view_mode: 'list,form',
                domain: [['project_id', '=', projectId]],
                context: { default_project_id: projectId },
                target: 'current'
            };
            await this.env.services.action.doAction(action);
        } catch (error) {
            console.error("Error opening expense view:", error);
        }
    }

    async openIncomeAnalysis() {
        try {
            const action = {
                type: 'ir.actions.act_window',
                name: 'Income Analysis',
                res_model: 'project.income',
                view_mode: 'list,form',
                target: 'current'
            };
            await this.env.services.action.doAction(action);
        } catch (error) {
            console.error("Error opening income analysis:", error);
        }
    }

    async openExpenseAnalysis() {
        try {
            const action = {
                type: 'ir.actions.act_window',
                name: 'Expense Analysis',
                res_model: 'project.expense',
                view_mode: 'list,form',
                target: 'current'
            };
            await this.env.services.action.doAction(action);
        } catch (error) {
            console.error("Error opening expense analysis:", error);
        }
    }

    async openProjectAnalysis() {
        try {
            const action = {
                type: 'ir.actions.act_window',
                name: 'Project Analysis',
                res_model: 'project.project',
                view_mode: 'list,form',
                target: 'current'
            };
            await this.env.services.action.doAction(action);
        } catch (error) {
            console.error("Error opening project analysis:", error);
        }
    }
}

ProjectDashboard.template = "project_reporting.ProjectDashboardTemplate";

registry.category("actions").add("project_reporting.dashboard_action", ProjectDashboard);
