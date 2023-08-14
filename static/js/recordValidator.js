export const nothingWritten = (e) => {
    e.style.borderColor = '#86b7fe';
    e.style.boxShadow = 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(20, 71, 208, 0.6)';
    return false;
}

export const validWritten = (e) => {
    e.style.borderColor = '#00FF00';
    e.style.boxShadow = 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(0, 255, 0, 0.6)';
}

export const invalidWritten = (e) => {
    e.style.borderColor = '#FF0000';
    e.style.boxShadow = 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(255, 0, 0, 0.6)';
}

export const inputValid = (e, isValid) => {
    if (isValid) {
        validWritten(e);
    } else {
        invalidWritten(e);
    }
    return isValid;
}

export const onlyNumber = (val) => {
    const patt = /(^$)|(^(\d|[1-9]\d{1,8})$)/;
    return patt.test(val);
}

export const submitButtonChecker = (messagesID, submitButtonID, forms) => {
    let ul = document.getElementById(messagesID);
    $(submitButtonID).on('click', function (e) {
        e.preventDefault();
        forms.map((value, index) => {
            const inputEl = document.getElementById(forms[index]);
            let isValid = inputValid(inputEl, onlyNumber(inputEl.value));
            if (!isValid) {
                e.preventDefault(); //prevent the default action
                let warning = `<li class="alert alert-danger">"${inputEl.value}" is invalid.</li>`;
                if (ul.innerHTML.indexOf(warning) === -1) {
                    ul.innerHTML += warning;
                }
            }
        });
    });
}