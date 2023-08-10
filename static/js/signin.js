function nothingWritten(e) {
    e.style.borderColor = '#86b7fe';
    e.style.boxShadow = 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(20, 71, 208, 0.6)';
    return false;
}

function validWritten(e) {
    e.style.borderColor = '#00FF00';
    e.style.boxShadow = 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(0, 255, 0, 0.6)';
}

function invalidWritten(e) {
    e.style.borderColor = '#FF0000';
    e.style.boxShadow = 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(255, 0, 0, 0.6)';
}

function usernameRegex(uname) {
    const regex = /^[\w.@+-]{1,149}$/;
    var isValid = regex.test(uname);
    return isValid;
}

function passwordRegex(pwd) {
    const notNumericPasswordRegex = /^.*\D.*$/;
    // var username = document.getElementById('usernameInput').value.toLowerCase();
    // console.log(username);
    var isValid = (pwd.length >= 8) && (notNumericPasswordRegex.test(pwd)); // && (username && (pwd.indexOf(username) === -1));
    /* console.log("pwd: ", pwd, "| >= 8:", (pwd.length >= 8), 
                "| all not numbers:", (~notNumericPasswordRegex.test(pwd)), 
                "| username:", username, 
                "| username not in password:", (pwd.indexOf(username) === -1), 
                "| result:",isValid); */
    return isValid;
}

function inputValid(e, isValid) {
    if (e.value.length === 0) {
        return nothingWritten(e);
    }
    if (isValid) {
        validWritten(e);
    } else {
        invalidWritten(e);
    }
    return isValid;
}

$('#usernameInput').on("input focus keyup click change", function () {
    var isValid = usernameRegex(this.value);
    // console.log(isValid);
    return inputValid(this, isValid);
});

$('#passwordInput').on("input click change focus keyup", function () {
    var passwordIsValid = passwordRegex(this.value);
    // console.log(passwordIsValid, password2IsValid)
    return inputValid(this, passwordIsValid);
});

$('#submitButton').on('click', function (e) {
    var ul = document.getElementById("allAlerts");
    var uname = document.getElementById('usernameInput');
    var pwd = document.getElementById('passwordInput');
    var isValid = inputValid(uname, usernameRegex(uname.value)) && inputValid(pwd, passwordRegex(pwd.value));
    if (!isValid) {
        e.preventDefault(); //prevent the default action
        var warning = '<li class="alert alert-danger">Enter proper credentials.</li>';
        if (ul.innerHTML.indexOf(warning) === -1) {
            ul.innerHTML += warning;
        }
    }
});