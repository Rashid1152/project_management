// Global variables
let currentUser = null;
let currentProject = null;
let csrfToken = null;

// DOM elements
const userInfoElement = document.getElementById('user-info');
const loginBtn = document.getElementById('login-btn');
const registerBtn = document.getElementById('register-btn');
const logoutBtn = document.getElementById('logout-btn');
const projectsContainer = document.getElementById('projects-container');
const welcomeMessage = document.getElementById('welcome-message');
const projectsList = document.getElementById('projects-list');

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Get CSRF token
    csrfToken = getCookie('csrftoken');
    console.log('CSRF Token:', csrfToken);
    
    // Check if user is logged in
    checkAuth();

    // Auth forms
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    logoutBtn.addEventListener('click', handleLogout);

    // Project forms
    document.getElementById('project-form').addEventListener('submit', handleProjectSubmit);
    document.getElementById('add-comment-form').addEventListener('submit', handleCommentSubmit);
    document.getElementById('add-user-form').addEventListener('submit', handleAddUser);

    // Project actions
    document.getElementById('edit-project-btn').addEventListener('click', handleEditProject);
    document.getElementById('delete-project-btn').addEventListener('click', handleDeleteProject);
    
    // New project button
    document.getElementById('new-project-btn').addEventListener('click', () => {
        // Reset form when opening the modal
        document.getElementById('project-form').reset();
        document.getElementById('project-id').value = '';
        document.getElementById('projectModalLabel').textContent = 'New Project';
        document.getElementById('project-error').classList.add('d-none');
    });
});

// Authentication functions
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/me/', {
            credentials: 'same-origin'
        });
        if (response.ok) {
            const userData = await response.json();
            setCurrentUser(userData);
            fetchProjects();
        } else {
            setCurrentUser(null);
        }
    } catch (error) {
        console.error('Error checking authentication:', error);
        setCurrentUser(null);
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const errorElement = document.getElementById('login-error');

    try {
        const response = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ username, password }),
            credentials: 'same-origin'
        });

        if (response.ok) {
            const userData = await response.json();
            setCurrentUser(userData);
            fetchProjects();
            const modalElement = document.getElementById('loginModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            } else {
                // Fallback if the modal instance isn't available
                $(modalElement).modal('hide');
            }
            document.getElementById('login-form').reset();
            errorElement.classList.add('d-none');
        } else {
            const errorData = await response.json();
            errorElement.textContent = errorData.error || 'Login failed. Please try again.';
            errorElement.classList.remove('d-none');
        }
    } catch (error) {
        console.error('Error during login:', error);
        errorElement.textContent = 'An error occurred. Please try again.';
        errorElement.classList.remove('d-none');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const firstName = document.getElementById('register-first-name').value;
    const lastName = document.getElementById('register-last-name').value;
    const password = document.getElementById('register-password').value;
    const password2 = document.getElementById('register-password2').value;
    const errorElement = document.getElementById('register-error');

    if (password !== password2) {
        errorElement.textContent = 'Passwords do not match.';
        errorElement.classList.remove('d-none');
        return;
    }

    try {
        const response = await fetch('/api/auth/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                username,
                email,
                first_name: firstName,
                last_name: lastName,
                password,
                password2
            }),
            credentials: 'same-origin'
        });

        if (response.ok) {
            // Auto-login after registration
            const loginResponse = await fetch('/api/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ username, password }),
                credentials: 'same-origin'
            });

            if (loginResponse.ok) {
                const userData = await loginResponse.json();
                setCurrentUser(userData);
                fetchProjects();
                const modalElement = document.getElementById('registerModal');
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                } else {
                    // Fallback if the modal instance isn't available
                    $(modalElement).modal('hide');
                }
                document.getElementById('register-form').reset();
                errorElement.classList.add('d-none');
            }
        } else {
            const errorData = await response.json();
            let errorMessage = 'Registration failed. Please try again.';
            if (errorData.username) errorMessage = `Username: ${errorData.username}`;
            else if (errorData.email) errorMessage = `Email: ${errorData.email}`;
            else if (errorData.password) errorMessage = `Password: ${errorData.password}`;
            
            errorElement.textContent = errorMessage;
            errorElement.classList.remove('d-none');
        }
    } catch (error) {
        console.error('Error during registration:', error);
        errorElement.textContent = 'An error occurred. Please try again.';
        errorElement.classList.remove('d-none');
    }
}

async function handleLogout() {
    try {
        await fetch('/api/auth/logout/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin'
        });
        setCurrentUser(null);
    } catch (error) {
        console.error('Error during logout:', error);
    }
}

function setCurrentUser(user) {
    currentUser = user;
    
    if (user) {
        userInfoElement.innerHTML = `<span>Welcome, ${user.first_name} ${user.last_name} (${user.username})</span>`;
        loginBtn.classList.add('d-none');
        registerBtn.classList.add('d-none');
        logoutBtn.classList.remove('d-none');
        projectsContainer.classList.remove('d-none');
        welcomeMessage.classList.add('d-none');
    } else {
        userInfoElement.innerHTML = '';
        loginBtn.classList.remove('d-none');
        registerBtn.classList.remove('d-none');
        logoutBtn.classList.add('d-none');
        projectsContainer.classList.add('d-none');
        welcomeMessage.classList.remove('d-none');
    }
}

// Project functions
async function fetchProjects() {
    try {
        const response = await fetch('/api/projects/', {
            credentials: 'same-origin'
        });
        if (response.ok) {
            const projects = await response.json();
            renderProjects(projects);
        } else {
            console.error('Failed to fetch projects:', response.status);
        }
    } catch (error) {
        console.error('Error fetching projects:', error);
    }
}

function renderProjects(projects) {
    projectsList.innerHTML = '';
    
    if (projects.length === 0) {
        projectsList.innerHTML = '<div class="col-12"><p>No projects found. Create a new project to get started.</p></div>';
        return;
    }
    
    projects.forEach(project => {
        const projectCard = document.createElement('div');
        projectCard.className = 'col-md-4 project-card';
        projectCard.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">${project.title}</h5>
                    <p class="card-text">${project.description.substring(0, 100)}${project.description.length > 100 ? '...' : ''}</p>
                    <button class="btn btn-primary view-project" data-project-id="${project.id}">View Details</button>
                </div>
            </div>
        `;
        
        projectsList.appendChild(projectCard);
        
        // Add event listener to view project button
        projectCard.querySelector('.view-project').addEventListener('click', () => {
            fetchProjectDetails(project.id);
        });
    });
}

async function fetchProjectDetails(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}/`, {
            credentials: 'same-origin'
        });
        if (response.ok) {
            const project = await response.json();
            currentProject = project;
            
            // Fetch project users
            const usersResponse = await fetch(`/api/projects/${projectId}/users/`, {
                credentials: 'same-origin'
            });
            const projectUsers = await usersResponse.json();
            
            // Fetch comments
            const commentsResponse = await fetch(`/api/projects/${projectId}/comments/`, {
                credentials: 'same-origin'
            });
            const comments = await commentsResponse.json();
            
            renderProjectDetails(project, projectUsers, comments);
            
            // Show the modal
            const projectDetailModal = new bootstrap.Modal(document.getElementById('projectDetailModal'));
            projectDetailModal.show();
        }
    } catch (error) {
        console.error('Error fetching project details:', error);
    }
}

function renderProjectDetails(project, projectUsers, comments) {
    const detailContent = document.getElementById('project-detail-content');
    const commentsList = document.getElementById('comments-list');
    const addCommentForm = document.getElementById('add-comment-form-container');
    const editBtn = document.getElementById('edit-project-btn');
    const deleteBtn = document.getElementById('delete-project-btn');
    
    // Set modal title
    document.getElementById('projectDetailModalLabel').textContent = project.title;
    
    // Render project details
    detailContent.innerHTML = `
        <h4>${project.title}</h4>
        <p>${project.description}</p>
        <div class="d-flex justify-content-between">
            <small>Created: ${new Date(project.created_at).toLocaleString()}</small>
            <small>Updated: ${new Date(project.updated_at).toLocaleString()}</small>
        </div>
        <div class="mt-3">
            <button id="manage-users-btn" class="btn btn-outline-primary btn-sm">Manage Users</button>
        </div>
    `;
    
    // Render comments
    commentsList.innerHTML = '';
    if (comments.length === 0) {
        commentsList.innerHTML = '<p>No comments yet.</p>';
    } else {
        comments.forEach(comment => {
            const commentElement = document.createElement('div');
            commentElement.className = 'card mb-2';
            commentElement.innerHTML = `
                <div class="card-body">
                    <p class="card-text">${comment.text}</p>
                    <div class="d-flex justify-content-between">
                        <small>By: ${comment.user.username}</small>
                        <small>${new Date(comment.created_at).toLocaleString()}</small>
                    </div>
                </div>
            `;
            commentsList.appendChild(commentElement);
        });
    }
    
    // Check user role for permissions
    const currentUserRole = getUserRoleInProject(projectUsers);
    
    // Set button visibility based on role
    if (currentUserRole === 'owner') {
        editBtn.classList.remove('d-none');
        deleteBtn.classList.remove('d-none');
        addCommentForm.classList.remove('d-none');
    } else if (currentUserRole === 'editor') {
        editBtn.classList.remove('d-none');
        deleteBtn.classList.add('d-none');
        addCommentForm.classList.remove('d-none');
    } else {
        editBtn.classList.add('d-none');
        deleteBtn.classList.add('d-none');
        addCommentForm.classList.add('d-none');
    }
    
    // Add event listener to manage users button
    document.getElementById('manage-users-btn').addEventListener('click', () => {
        if (currentUserRole === 'owner') {
            renderUserManagement(projectUsers);
            const userManagementModal = new bootstrap.Modal(document.getElementById('userManagementModal'));
            userManagementModal.show();
        } else {
            alert('Only project owners can manage users.');
        }
    });
}

function getUserRoleInProject(projectUsers) {
    if (!currentUser) return null;
    
    const userEntry = projectUsers.find(pu => pu.user === currentUser.id);
    return userEntry ? userEntry.role : null;
}

function renderUserManagement(projectUsers) {
    const usersList = document.getElementById('project-users-list');
    usersList.innerHTML = '';
    
    projectUsers.forEach(pu => {
        const userElement = document.createElement('div');
        userElement.className = 'd-flex justify-content-between align-items-center mb-2';
        
        // Don't allow removing or changing the owner
        if (pu.role === 'owner') {
            userElement.innerHTML = `
                <div>
                    <strong>${pu.user_details.username}</strong> (Owner)
                </div>
                <div>
                    <button class="btn btn-sm btn-outline-secondary" disabled>Cannot modify</button>
                </div>
            `;
        } else {
            userElement.innerHTML = `
                <div>
                    <strong>${pu.user_details.username}</strong> (${pu.role.charAt(0).toUpperCase() + pu.role.slice(1)})
                </div>
                <div>
                    <select class="form-select form-select-sm role-select me-2" data-user-id="${pu.user}" style="width: auto; display: inline-block;">
                        <option value="editor" ${pu.role === 'editor' ? 'selected' : ''}>Editor</option>
                        <option value="reader" ${pu.role === 'reader' ? 'selected' : ''}>Reader</option>
                    </select>
                    <button class="btn btn-sm btn-danger remove-user" data-user-id="${pu.user}">Remove</button>
                </div>
            `;
        }
        
        usersList.appendChild(userElement);
    });
    
    // Add event listeners for role changes and user removal
    document.querySelectorAll('.role-select').forEach(select => {
        select.addEventListener('change', async (event) => {
            const userId = event.target.dataset.userId;
            const newRole = event.target.value;
            
            try {
                await fetch(`/api/projects/${currentProject.id}/update-role/${userId}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ role: newRole }),
                    credentials: 'same-origin'
                });
                
                // Refresh project details
                fetchProjectDetails(currentProject.id);
            } catch (error) {
                console.error('Error updating user role:', error);
            }
        });
    });
    
    document.querySelectorAll('.remove-user').forEach(button => {
        button.addEventListener('click', async () => {
            const userId = button.dataset.userId;
            
            if (confirm('Are you sure you want to remove this user from the project?')) {
                try {
                    await fetch(`/api/projects/${currentProject.id}/remove-user/${userId}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': csrfToken
                        },
                        credentials: 'same-origin'
                    });
                    
                    // Refresh project details
                    fetchProjectDetails(currentProject.id);
                } catch (error) {
                    console.error('Error removing user:', error);
                }
            }
        });
    });
}

async function handleProjectSubmit(event) {
    event.preventDefault();
    const projectId = document.getElementById('project-id').value;
    const title = document.getElementById('project-title').value;
    const description = document.getElementById('project-description').value;
    const errorElement = document.getElementById('project-error');
    
    // Refresh CSRF token
    csrfToken = getCookie('csrftoken');
    console.log('Submitting project with CSRF token:', csrfToken);
    
    try {
        let url = '/api/projects/';
        let method = 'POST';
        
        if (projectId) {
            url = `/api/projects/${projectId}/`;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ title, description }),
            credentials: 'same-origin'
        });
        
        if (response.ok) {
            const modalElement = document.getElementById('projectModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            } else {
                // Fallback if the modal instance isn't available
                $(modalElement).modal('hide');
            }
            document.getElementById('project-form').reset();
            document.getElementById('project-id').value = '';
            errorElement.classList.add('d-none');
            fetchProjects();
        } else {
            console.error('Failed to save project:', response.status);
            try {
                const errorData = await response.json();
                let errorMessage = 'Failed to save project. Please try again.';
                if (errorData.title) errorMessage = `Title: ${errorData.title}`;
                else if (errorData.description) errorMessage = `Description: ${errorData.description}`;
                else if (errorData.detail) errorMessage = errorData.detail;
                
                errorElement.textContent = errorMessage;
            } catch (e) {
                errorElement.textContent = `Failed to save project. Status: ${response.status}`;
            }
            errorElement.classList.remove('d-none');
        }
    } catch (error) {
        console.error('Error saving project:', error);
        errorElement.textContent = 'An error occurred. Please try again.';
        errorElement.classList.remove('d-none');
    }
}

function handleEditProject() {
    document.getElementById('project-id').value = currentProject.id;
    document.getElementById('project-title').value = currentProject.title;
    document.getElementById('project-description').value = currentProject.description;
    document.getElementById('projectModalLabel').textContent = 'Edit Project';
    
    const modalElement = document.getElementById('projectDetailModal');
    const modal = bootstrap.Modal.getInstance(modalElement);
    if (modal) {
        modal.hide();
    } else {
        // Fallback if the modal instance isn't available
        $(modalElement).modal('hide');
    }
    
    const projectModal = new bootstrap.Modal(document.getElementById('projectModal'));
    projectModal.show();
}

async function handleDeleteProject() {
    if (confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
        try {
            const response = await fetch(`/api/projects/${currentProject.id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const modalElement = document.getElementById('projectDetailModal');
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                } else {
                    // Fallback if the modal instance isn't available
                    $(modalElement).modal('hide');
                }
                fetchProjects();
            } else {
                alert('Failed to delete project. Please try again.');
            }
        } catch (error) {
            console.error('Error deleting project:', error);
            alert('An error occurred. Please try again.');
        }
    }
}

async function handleCommentSubmit(event) {
    event.preventDefault();
    const text = document.getElementById('comment-text').value;
    
    try {
        const response = await fetch(`/api/projects/${currentProject.id}/add_comment/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ text }),
            credentials: 'same-origin'
        });
        
        if (response.ok) {
            document.getElementById('comment-text').value = '';
            fetchProjectDetails(currentProject.id);
        } else {
            alert('Failed to add comment. Please try again.');
        }
    } catch (error) {
        console.error('Error adding comment:', error);
        alert('An error occurred. Please try again.');
    }
}

async function handleAddUser(event) {
    event.preventDefault();
    const username = document.getElementById('user-username').value;
    const role = document.getElementById('user-role').value;
    const errorElement = document.getElementById('add-user-error');
    
    try {
        // Skip the user lookup since the endpoint doesn't exist
        // Instead, directly add the user by username
        const response = await fetch(`/api/projects/${currentProject.id}/add_user/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ username: username, role: role }),
            credentials: 'same-origin'
        });
        
        if (response.ok) {
            document.getElementById('add-user-form').reset();
            errorElement.classList.add('d-none');
            fetchProjectDetails(currentProject.id);
        } else {
            const errorData = await response.json();
            errorElement.textContent = errorData.detail || 'Failed to add user. Please try again.';
            errorElement.classList.remove('d-none');
        }
    } catch (error) {
        console.error('Error adding user:', error);
        errorElement.textContent = 'An error occurred. Please try again.';
        errorElement.classList.remove('d-none');
    }
}

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 