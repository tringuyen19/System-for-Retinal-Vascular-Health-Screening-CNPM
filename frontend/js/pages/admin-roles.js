/**
 * Admin Roles Management - FR-32
 * Handles role CRUD and permission matrix UI
 */

// ========== CONFIGURATION ==========

const RESOURCES = ['Account', 'Doctor', 'Clinic', 'AiModel', 'Payment', 'Report', 'Role', 'Image'];
const ACTIONS = ['create', 'read', 'update', 'delete'];
const API_BASE_URL = `${window.API_CONFIG?.baseURL || 'http://localhost:9999'}/api/admin`;

let currentPage = 1;
let rolesPerPage = 10;
let allRoles = [];
let currentRoleId = null;
let currentRolePermissions = {};

// ========== INITIALIZATION ==========

document.addEventListener('DOMContentLoaded', () => {
    console.log('[FR-32] Admin Roles page initialized');
    
    // Load initial data
    loadRoles();
    
    // Event listeners
    document.getElementById('createRoleBtn').addEventListener('click', resetRoleForm);
    document.getElementById('saveRoleBtn').addEventListener('click', saveRole);
    document.getElementById('prevBtn').addEventListener('click', () => goToPage(currentPage - 1));
    document.getElementById('nextBtn').addEventListener('click', () => goToPage(currentPage + 1));
    document.getElementById('searchInput').addEventListener('input', handleSearch);
    document.getElementById('resetPermissionsBtn').addEventListener('click', resetPermissionsForm);
    document.getElementById('savePermissionsBtn').addEventListener('click', savePermissions);
    
    // Permission matrix select all
    document.getElementById('selectAllCreate').addEventListener('change', (e) => selectAllByAction('create', e.target.checked));
    document.getElementById('selectAllRead').addEventListener('change', (e) => selectAllByAction('read', e.target.checked));
    document.getElementById('selectAllUpdate').addEventListener('change', (e) => selectAllByAction('update', e.target.checked));
    document.getElementById('selectAllDelete').addEventListener('change', (e) => selectAllByAction('delete', e.target.checked));
});

// ========== LOAD & DISPLAY ROLES ==========

async function loadRoles() {
    try {
        const params = new URLSearchParams({
            limit: rolesPerPage,
            offset: (currentPage - 1) * rolesPerPage
        });
        
        const response = await fetch(`${API_BASE_URL}/roles?${params}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load roles');
        
        const data = await response.json();
        const result = data.data;
        
        allRoles = result.roles || [];
        const total = result.total || 0;
        
        // Update statistics
        document.getElementById('totalRoles').textContent = total;
        
        // Render table
        renderRolesTable(allRoles);
        
        // Update pagination
        updatePaginationButtons(total);
    } catch (error) {
        console.error('[FR-32] Error loading roles:', error);
        showAlert(`Error loading roles: ${error.message}`, 'danger');
    }
}

function renderRolesTable(roles) {
    const tbody = document.getElementById('rolesTableBody');
    
    if (!roles || roles.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted py-4">
                    No roles found
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = roles.map(role => {
        const roleId = role.role_id || role.id;
        const roleName = role.role_name || role.name || 'Unknown';
        const createdAt = formatDate(role.created_at || new Date());
        
        return `
            <tr>
                <td>${roleId}</td>
                <td>
                    <span class="role-badge" style="background-color: #f0f0f0; color: #333;">
                        ${roleName}
                    </span>
                </td>
                <td>
                    <span class="role-count-badge" onclick="loadPermissions(${roleId})" style="cursor: pointer;">
                        <i class="fas fa-key"></i> Manage
                    </span>
                </td>
                <td><small class="text-muted">${createdAt}</small></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline-primary" onclick="editRole(${roleId})">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteRole(${roleId})">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function updatePaginationButtons(total) {
    const totalPages = Math.ceil(total / rolesPerPage);
    
    document.getElementById('currentPage').textContent = currentPage;
    document.getElementById('prevBtn').disabled = currentPage <= 1;
    document.getElementById('nextBtn').disabled = currentPage >= totalPages;
}

function goToPage(page) {
    currentPage = Math.max(1, page);
    loadRoles();
}

function handleSearch(e) {
    const query = e.target.value.toLowerCase();
    const filtered = allRoles.filter(role => {
        const name = (role.role_name || role.name || '').toLowerCase();
        return name.includes(query);
    });
    renderRolesTable(filtered);
}

// ========== ROLE CRUD ==========

function resetRoleForm() {
    currentRoleId = null;
    document.getElementById('roleModalTitle').textContent = 'Create New Role';
    document.getElementById('roleName').value = '';
    document.getElementById('roleDescription').value = '';
    document.getElementById('roleFormError').classList.add('d-none');
}

function editRole(roleId) {
    const role = allRoles.find(r => (r.role_id || r.id) === roleId);
    if (!role) return;
    
    currentRoleId = roleId;
    document.getElementById('roleModalTitle').textContent = `Edit Role: ${role.role_name || role.name}`;
    document.getElementById('roleName').value = role.role_name || role.name || '';
    document.getElementById('roleDescription').value = role.description || '';
    document.getElementById('roleFormError').classList.add('d-none');
    
    const modal = new bootstrap.Modal(document.getElementById('roleModal'));
    modal.show();
}

async function saveRole() {
    const roleName = document.getElementById('roleName').value.trim();
    
    if (!roleName) {
        showFormError('roleName', 'Role name is required');
        return;
    }
    
    try {
        const method = currentRoleId ? 'PUT' : 'POST';
        const url = currentRoleId 
            ? `${API_BASE_URL}/roles/${currentRoleId}`
            : `${API_BASE_URL}/roles`;
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ role_name: roleName })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to save role');
        }
        
        // Close modal and reload
        bootstrap.Modal.getInstance(document.getElementById('roleModal')).hide();
        showAlert(
            currentRoleId ? 'Role updated successfully' : 'Role created successfully',
            'success'
        );
        loadRoles();
    } catch (error) {
        console.error('[FR-32] Error saving role:', error);
        showFormError('roleForm', error.message);
    }
}

async function deleteRole(roleId) {
    if (!confirm('Are you sure you want to delete this role? All permissions will also be deleted.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/roles/${roleId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to delete role');
        
        showAlert('Role deleted successfully', 'success');
        loadRoles();
    } catch (error) {
        console.error('[FR-32] Error deleting role:', error);
        showAlert(`Error deleting role: ${error.message}`, 'danger');
    }
}

// ========== PERMISSION MANAGEMENT ==========

async function loadPermissions(roleId) {
    currentRoleId = roleId;
    
    try {
        // Get role name
        const role = allRoles.find(r => (r.role_id || r.id) === roleId);
        if (!role) {
            showAlert('Role not found', 'danger');
            return;
        }
        
        document.getElementById('permissionRoleName').textContent = role.role_name || role.name || 'Unknown';
        
        // Get existing permissions
        const response = await fetch(`${API_BASE_URL}/roles/${roleId}/permissions`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to load permissions');
        
        const data = await response.json();
        const permissions = data.data.permissions || [];
        
        // Build current permissions map
        currentRolePermissions = {};
        permissions.forEach(perm => {
            const key = `${perm.resource}-${perm.action}`;
            currentRolePermissions[key] = true;
        });
        
        // Render permission matrix
        renderPermissionMatrix();
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('permissionsModal'));
        modal.show();
    } catch (error) {
        console.error('[FR-32] Error loading permissions:', error);
        showAlert(`Error loading permissions: ${error.message}`, 'danger');
    }
}

function renderPermissionMatrix() {
    const tbody = document.getElementById('permissionMatrixBody');
    
    tbody.innerHTML = RESOURCES.map(resource => {
        const cells = ACTIONS.map(action => {
            const key = `${resource}-${action}`;
            const isChecked = currentRolePermissions[key] ? 'checked' : '';
            
            return `
                <td>
                    <input type="checkbox" 
                           class="permission-checkbox" 
                           data-resource="${resource}" 
                           data-action="${action}"
                           ${isChecked}>
                </td>
            `;
        }).join('');
        
        return `
            <tr>
                <td>${resource}</td>
                ${cells}
            </tr>
        `;
    }).join('');
    
    // Add change listeners
    document.querySelectorAll('.permission-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectAllButtons);
    });
}

function updateSelectAllButtons() {
    ACTIONS.forEach(action => {
        const checkboxes = document.querySelectorAll(`.permission-checkbox[data-action="${action}"]`);
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        const someChecked = Array.from(checkboxes).some(cb => cb.checked);
        
        const selectAllBtn = document.getElementById(`selectAll${action.charAt(0).toUpperCase() + action.slice(1)}`);
        selectAllBtn.checked = allChecked;
        selectAllBtn.indeterminate = someChecked && !allChecked;
    });
}

function selectAllByAction(action, checked) {
    document.querySelectorAll(`.permission-checkbox[data-action="${action}"]`).forEach(checkbox => {
        checkbox.checked = checked;
    });
    updateSelectAllButtons();
}

function resetPermissionsForm() {
    document.querySelectorAll('.permission-checkbox').forEach(checkbox => {
        const key = `${checkbox.dataset.resource}-${checkbox.dataset.action}`;
        checkbox.checked = !!currentRolePermissions[key];
    });
    updateSelectAllButtons();
}

async function savePermissions() {
    if (!currentRoleId) return;
    
    try {
        // Collect selected permissions
        const selectedPermissions = [];
        document.querySelectorAll('.permission-checkbox:checked').forEach(checkbox => {
            selectedPermissions.push({
                resource: checkbox.dataset.resource,
                action: checkbox.dataset.action
            });
        });
        
        // Get current permissions
        const currentPerms = Object.keys(currentRolePermissions).map(key => {
            const [resource, action] = key.split('-');
            return { resource, action };
        });
        
        // Find permissions to add
        const toAdd = selectedPermissions.filter(perm => 
            !currentPerms.some(p => p.resource === perm.resource && p.action === perm.action)
        );
        
        // Find permissions to remove
        const toRemove = currentPerms.filter(perm =>
            !selectedPermissions.some(p => p.resource === perm.resource && p.action === perm.action)
        );
        
        // Add new permissions
        for (const perm of toAdd) {
            const response = await fetch(`${API_BASE_URL}/roles/${currentRoleId}/permissions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    resource: perm.resource,
                    action: perm.action
                })
            });
            
            if (!response.ok) throw new Error(`Failed to add permission: ${perm.resource}.${perm.action}`);
        }
        
        // Remove permissions
        for (const perm of toRemove) {
            const response = await fetch(
                `${API_BASE_URL}/roles/${currentRoleId}/permissions/${perm.resource}/${perm.action}`,
                {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                }
            );
            
            if (!response.ok) throw new Error(`Failed to remove permission: ${perm.resource}.${perm.action}`);
        }
        
        // Close modal and reload
        bootstrap.Modal.getInstance(document.getElementById('permissionsModal')).hide();
        showAlert('Permissions updated successfully', 'success');
        loadPermissions(currentRoleId);
    } catch (error) {
        console.error('[FR-32] Error saving permissions:', error);
        document.getElementById('permissionsFormError').textContent = error.message;
        document.getElementById('permissionsFormError').classList.remove('d-none');
    }
}

// ========== UTILITY FUNCTIONS ==========

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    const alertId = `alert-${Date.now()}`;
    
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        const element = document.getElementById(alertId);
        if (element) element.remove();
    }, 5000);
}

function showFormError(fieldName, message) {
    const errorDiv = document.getElementById(`${fieldName}Error`) || 
                     document.getElementById('roleFormError');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('d-none');
    }
}

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (e) {
        return 'Invalid Date';
    }
}

console.log('[FR-32] Admin Roles JavaScript loaded');
