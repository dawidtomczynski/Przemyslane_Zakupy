const chosenPlanType = document.querySelector('#chosenPlanType');

chosenPlanType.addEventListener('change', function() {
    console.log(chosenPlanType.value)
    document.querySelectorAll('#plan').forEach(function (plan) {
        if (plan.attributes.type_id.value === chosenPlanType.value) {
            plan.style.display = ''
            console.log(plan.attributes.type_id.value)
        } else {
            plan.style.display = 'none'
        }
    })
})