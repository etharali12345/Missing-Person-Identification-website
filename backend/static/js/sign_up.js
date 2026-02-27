const signUpForm = document.getElementById('signUpForm');
const password_floating = document.getElementById('passwordFloating');
const passwordInput = document.getElementById('password');

const passwordImage = document.getElementById('passwordImg');
const passwordImgBox = document.getElementById('passwordImg-box');

const error_message = document.getElementById("errorMessage");

signUpForm.addEventListener('submit', async function(event) {
    event.preventDefault();

    if (!signUpForm.checkValidity()) {
        if(!passwordInput.checkValidity()) {
            password_floating.classList.add('is-invalid');
        }
        event.stopPropagation();
        signUpForm.classList.add('was-validated');
    } else {
        signUpForm.classList.remove('was-validated');
        const formData = new FormData(signUpForm);
        const response = await fetch('/sign_up', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.valid) {
            window.location.href = data.redirect;
        } else {
            error_message.hidden = false;
            error_message.innerText = data.message;
        }
    }
});

passwordInput.addEventListener('input', function() {
    if (passwordInput.checkValidity()) {
        password_floating.classList.remove('is-invalid');
    }
});

passwordImgBox.addEventListener('click', function() {
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        passwordImage.src = '/static/images/eye.png';
    } else {
        passwordInput.type = 'password';
        passwordImage.src = '/static/images/hidden.png';
    }
});