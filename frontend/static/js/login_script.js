/**
 * LOGIN SCRIPT - University Management System
 * Handles user authentication and login functionality
 */

// Configuration
const BACKEND_URL = "http://localhost:5000/api";

// DOM Elements (loaded after page loads)
let loginForm, roleSelect, codeInput, passwordInput, loginBtn, btnText;
let errorMsg, successMsg, eyeOpen, eyeClosed;

/**
 * Initialize the page when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get all DOM elements
    loginForm = document.getElementById('loginForm');
    roleSelect = document.getElementById('role');
    codeInput = document.getElementById('code_apoge');
    passwordInput = document.getElementById('password');
    loginBtn = document.getElementById('loginBtn');
    btnText = document.getElementById('btnText');
    errorMsg = document.getElementById('error-message');
    successMsg = document.getElementById('success-message');
    eyeOpen = document.getElementById('eye-open');
    eyeClosed = document.getElementById('eye-closed');

    // Auto-focus on role select
    if (roleSelect) {
        roleSelect.focus();
    }

    // Add input event listeners to clear messages
    const inputs = [roleSelect, codeInput, passwordInput];
    inputs.forEach(input => {
        if (input) {
            input.addEventListener('input', hideMessages);
            input.addEventListener('change', hideMessages);
        }
    });

    // Add form submit listener
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Prevent multiple form submissions
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            if (loginBtn.classList.contains('loading')) {
                e.preventDefault();
            }
        });
    }
});

/**
 * Toggle password visibility
 */
function togglePassword() {
    if (!passwordInput || !eyeOpen || !eyeClosed) return;

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eyeOpen.style.display = 'none';
        eyeClosed.style.display = 'block';
    } else {
        passwordInput.type = 'password';
        eyeOpen.style.display = 'block';
        eyeClosed.style.display = 'none';
    }
}

/**
 * Handle login form submission
 */
async function handleLogin(event) {
    event.preventDefault();

    // Get form values
    const role = roleSelect.value.trim();
    const code = codeInput.value.trim();
    const password = passwordInput.value;

    // Clear previous messages
    hideMessages();

    // Client-side validation
    if (!role) {
        showError("Veuillez sélectionner un rôle.");
        roleSelect.focus();
        return;
    }

    if (!code) {
        showError("Veuillez entrer votre identifiant.");
        codeInput.focus();
        return;
    }

    if (!password) {
        showError("Veuillez entrer votre mot de passe.");
        passwordInput.focus();
        return;
    }

    if (password.length < 4) {
        showError("Le mot de passe doit contenir au moins 4 caractères.");
        passwordInput.focus();
        return;
    }

    // Show loading state
    setLoadingState(true);

    try {
        // Make API call
        const response = await fetch(`${BACKEND_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                role: role,
                code_apoge: code,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok && data) {
            // Success - Store user data
            localStorage.setItem('user_role', data.role);
            localStorage.setItem('user_code', data.code_apoge || '');
            localStorage.setItem('user_name', data.name || '');
            localStorage.setItem('login_time', new Date().toISOString());

            // Show success message
            showSuccess("Connexion réussie ! Redirection en cours...");

            // Redirect based on role
            setTimeout(() => {
                redirectToDashboard(role);
            }, 1200);

        } else {
            // Handle error response
            const errorMessage = data.error || data.message || "Identifiants incorrects. Veuillez réessayer.";
            showError(errorMessage);
            setLoadingState(false);
            
            // Clear password on error
            passwordInput.value = '';
            passwordInput.focus();
        }

    } catch (error) {
        console.error('Login error:', error);
        
        // Check if it's a network error
        if (error instanceof TypeError && error.message.includes('fetch')) {
            showError("Impossible de se connecter au serveur. Vérifiez votre connexion internet.");
        } else {
            showError("Une erreur s'est produite. Veuillez réessayer.");
        }
        
        setLoadingState(false);
    }
}

/**
 * Redirect to appropriate dashboard based on role
 */
function redirectToDashboard(role) {
    switch(role) {
        case 'ADMIN':
            window.location.href = "/admin";
            break;
        case 'TEACHER':
            // Check if teacher dashboard exists
            if (checkRouteExists('/teacher')) {
                window.location.href = "/teacher";
            } else {
                showError("Dashboard Professeur en cours de développement.");
                setLoadingState(false);
                console.log("Teacher dashboard not implemented yet");
            }
            break;
        case 'STUDENT':
            // Check if student dashboard exists
            if (checkRouteExists('/student')) {
                window.location.href = "/student";
            } else {
                showError("Dashboard Étudiant en cours de développement.");
                setLoadingState(false);
                console.log("Student dashboard not implemented yet");
            }
            break;
        default:
            showError("Rôle non reconnu.");
            setLoadingState(false);
    }
}

/**
 * Check if a route exists (simple check)
 */
function checkRouteExists(route) {
    // This is a simple placeholder - in production, you might want to make an actual check
    // For now, we'll just return true for /admin and false for others
    return route === '/admin';
}

/**
 * Set loading state for the login button
 */
function setLoadingState(isLoading) {
    if (!loginBtn || !btnText) return;

    if (isLoading) {
        loginBtn.classList.add('loading');
        loginBtn.disabled = true;
        btnText.textContent = 'Connexion en cours...';
    } else {
        loginBtn.classList.remove('loading');
        loginBtn.disabled = false;
        btnText.textContent = 'Se Connecter';
    }
}

/**
 * Show error message
 */
function showError(message) {
    if (!errorMsg) return;
    
    errorMsg.textContent = message;
    errorMsg.classList.add('show');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorMsg.classList.remove('show');
    }, 5000);
}

/**
 * Show success message
 */
function showSuccess(message) {
    if (!successMsg) return;
    
    successMsg.textContent = message;
    successMsg.classList.add('show');
}

/**
 * Hide all messages
 */
function hideMessages() {
    if (errorMsg) {
        errorMsg.classList.remove('show');
    }
    if (successMsg) {
        successMsg.classList.remove('show');
    }
}

/**
 * Check if user is already logged in
 */
function checkExistingLogin() {
    const userRole = localStorage.getItem('user_role');
    const loginTime = localStorage.getItem('login_time');
    
    if (userRole && loginTime) {
        // Check if login is still valid (e.g., within 24 hours)
        const loginDate = new Date(loginTime);
        const now = new Date();
        const hoursDiff = (now - loginDate) / (1000 * 60 * 60);
        
        if (hoursDiff < 24) {
            // Redirect to appropriate dashboard
            console.log('User already logged in, redirecting...');
            redirectToDashboard(userRole);
        } else {
            // Clear old login data
            localStorage.clear();
        }
    }
}

/**
 * Handle Enter key press for form submission
 */
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && loginForm && !loginBtn.classList.contains('loading')) {
        loginForm.dispatchEvent(new Event('submit'));
    }
});

/**
 * Prevent form submission when already loading
 */
window.addEventListener('beforeunload', function(e) {
    if (loginBtn && loginBtn.classList.contains('loading')) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Check for existing login on page load
checkExistingLogin();

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        handleLogin,
        togglePassword,
        showError,
        showSuccess,
        hideMessages,
        redirectToDashboard
    };
}