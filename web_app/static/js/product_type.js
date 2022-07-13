const chosenProductType = document.querySelector('#chosenProductType');

chosenProductType.addEventListener('change', function() {
  document.querySelectorAll('#product').forEach(function (product) {
      if (product.attributes.type_id.value === chosenProductType.value) {
        product.style.display = ''
        console.log(product.attributes.type_id.value)
      } else {
        product.style.display = 'none'
      }
  })
})
