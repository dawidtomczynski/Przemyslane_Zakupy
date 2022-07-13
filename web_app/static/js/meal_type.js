const chosenMealType = document.querySelector('#chosenMealType');

chosenMealType.addEventListener('change', function() {
    document.querySelectorAll('#meal').forEach(function (meal) {
        if (meal.attributes.type_id.value === chosenMealType.value) {
            meal.style.display = ''
        } else {
            meal.style.display = 'none'
        }
    })
})