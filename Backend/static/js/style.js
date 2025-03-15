const checkbox = document.querySelector('.navigation__checkbox');

checkbox.addEventListener('change', () => {
  if (checkbox.checked) {
    document.body.classList.add('no-scroll');
  } else {
    document.body.classList.remove('no-scroll');
  }
});
