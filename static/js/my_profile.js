
if(document.getElementById("deleteBlogButton")) {

  const deleteButtons = document.querySelectorAll('.delete-button');
  const deleteConfirmations = document.querySelectorAll('.delete-confirmation');
  const cancelButtons = document.querySelectorAll('.cancel-button');

  deleteButtons.forEach(function(deleteButton, index) {
      deleteButton.addEventListener('click', function() {
          deleteConfirmations[index].classList.remove('d-none');
      });
  });

  cancelButtons.forEach(function(cancelButton, index) {
      cancelButton.addEventListener('click', function() {
          deleteConfirmations[index].classList.add('d-none');
      });
  });

}

  document.getElementById("deleteProfileButton").addEventListener("click", function() {
    document.getElementById("deleteConfirmationProfile").classList.toggle("d-none");
  });

  let cancelButtonProfile = document.getElementById("cancelButtonProfile");
  let deleteConfirmationProfile = document.getElementById("deleteConfirmationProfile");
  cancelButtonProfile.addEventListener("click", function(){
    deleteConfirmationProfile.classList.add("d-none");
  });

if(document.getElementById("deleteBlogButton")) {

  const deleteButtons = document.querySelectorAll('.delete-button');
  const deleteConfirmations = document.querySelectorAll('.delete-confirmation');
  const cancelButtons = document.querySelectorAll('.cancel-button');

  deleteButtons.forEach(function(deleteButton, index) {
      deleteButton.addEventListener('click', function() {
          deleteConfirmations[index].classList.remove('d-none');
      });
  });

  cancelButtons.forEach(function(cancelButton, index) {
      cancelButton.addEventListener('click', function() {
          deleteConfirmations[index].classList.add('d-none');
      });
  });

}