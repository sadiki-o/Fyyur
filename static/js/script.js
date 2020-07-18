window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

const deleteVenue = (e, route) => {

  let id = e.target.classList.contains('delete-btn') ? e.target.dataset['id'] : e.target.parentNode.dataset['id']
  fetch(`/${route}/${id}`, {
    method: 'POST',
  })
  .then(() => {
    console.log("success");
  })
  .catch(() => {
    console.log("fail");
  })
}