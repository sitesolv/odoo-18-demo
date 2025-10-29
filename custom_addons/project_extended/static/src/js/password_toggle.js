/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

// Password toggle functionality
function initPasswordToggle() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('o_toggle_password')) {
            const passwordDiv = e.target.parentElement;
            const passwordField = passwordDiv.querySelector('.o_password_field input');
            
            if (passwordField) {
                if (passwordField.type === 'password') {
                    passwordField.type = 'text';
                    e.target.textContent = '🙈';
                } else {
                    passwordField.type = 'password';
                    e.target.textContent = '👁️';
                }
            }
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPasswordToggle);
} else {
    initPasswordToggle();
}

// Also initialize on form load
registry.category("web_tour.tours").add("password_toggle", {
    test: true,
    steps: () => [],
});

// Simple initialization for forms
const passwordToggleService = {
    start() {
        // Re-initialize on any form change
        const observer = new MutationObserver(() => {
            initPasswordToggle();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        return initPasswordToggle();
    },
};

registry.category("services").add("password_toggle", passwordToggleService);
