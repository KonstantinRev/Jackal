document.addEventListener('DOMContentLoaded', function() {
    // Look for typing
    let input1 = document.querySelector('.input1');
    input1.addEventListener('keyup', function() {
        let html = '';
        if (input1.value) {
            for (us of USERS) {
                if (us.startsWith(input1.value)) {
                    html += `<option>${us}</option>`;
                }
            }
        }
        if (html == '') {
            document.querySelector('#pirat1').innerHTML = `<option>` + current_user + `</option>`;
        } else {
            document.querySelector('#pirat1').innerHTML = html;
        }
    });
    let input2 = document.querySelector('.input2');
    input2.addEventListener('keyup', function() {
        let html = '';
        if (input2.value) {
            for (us of USERS) {
                if (us.startsWith(input2.value)) {
                    html += `<option>${us}</option>`;
                }
            }
        }
        if (html == '') {
            document.querySelector('#pirat2').innerHTML = `<option>` + current_user + `</option>`;
        } else {
            document.querySelector('#pirat2').innerHTML = html;
        }
    });
    let input3 = document.querySelector('.input3');
    input3.addEventListener('keyup', function() {
        let html = '';
        if (input3.value) {
            for (us of USERS) {
                if (us.startsWith(input3.value)) {
                    html += `<option>${us}</option>`;
                }
            }
        }
        if (html == '') {
            document.querySelector('#pirat3').innerHTML = `<option>` + current_user + `</option>`;
        } else {
            document.querySelector('#pirat3').innerHTML = html;
        }
    });
    let input4 = document.querySelector('.input4');
    input4.addEventListener('keyup', function() {
        let html = '';
        if (input4.value) {
            for (us of USERS) {
                if (us.startsWith(input4.value)) {
                    html += `<option>${us}</option>`;
                }
            }
        }
        if (html == '') {
            document.querySelector('#pirat4').innerHTML = `<option>` + current_user + `</option>`;
        } else {
            document.querySelector('#pirat4').innerHTML = html;
        }
    });
    // Fill chosen field
    let chosen1 = document.querySelector('#pirat1_chosen');
    let select1 = document.querySelector('#pirat1');
    select1.addEventListener('click', function() {
        chosen_user = select1.value
        chosen1.innerHTML = chosen_user
        chosen1.value = chosen_user
    });
    select1.addEventListener('change', function() {
        chosen_user = select1.value
        chosen1.innerHTML = chosen_user
        chosen1.value = chosen_user
    });
    let chosen2 = document.querySelector('#pirat2_chosen');
    let select2 = document.querySelector('#pirat2');
    select2.addEventListener('click', function() {
        chosen_user = select2.value
        chosen2.innerHTML = chosen_user
        chosen2.value = chosen_user
    });
    select2.addEventListener('change', function() {
        chosen_user = select2.value
        chosen2.innerHTML = chosen_user
        chosen2.value = chosen_user
    });
    let chosen3 = document.querySelector('#pirat3_chosen');
    let select3 = document.querySelector('#pirat3');
    select3.addEventListener('click', function() {
        chosen_user = select3.value
        chosen3.innerHTML = chosen_user
        chosen3.value = chosen_user
    });
    select3.addEventListener('change', function() {
        chosen_user = select3.value
        chosen3.innerHTML = chosen_user
        chosen3.value = chosen_user
    });
    let chosen4 = document.querySelector('#pirat4_chosen');
    let select4 = document.querySelector('#pirat4');
    select4.addEventListener('click', function() {
        chosen_user = select4.value
        chosen4.innerHTML = chosen_user
        chosen4.value = chosen_user
    });
    select4.addEventListener('change', function() {
        chosen_user = select4.value
        chosen4.innerHTML = chosen_user
        chosen4.value = chosen_user
    });
});