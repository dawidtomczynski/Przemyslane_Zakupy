document.querySelectorAll('.list-group-item').forEach(function(button) {
    button.addEventListener('click', function() {
        if(this.parentElement.id === 'list1') {
            document.querySelector('#list2').appendChild(button);
        } else {
            document.querySelector('#list1').appendChild(button);
        }
    })
})