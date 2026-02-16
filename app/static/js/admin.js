
(function(){
  const modal = document.getElementById('descModal');
  const body  = document.getElementById('modalBody');
  const title = document.getElementById('modalTitle');
  const close = document.getElementById('modalClose');
  function openModal(t, text){
    title.textContent = t || 'Description';
    body.textContent = text || '';
    modal.classList.add('open');
  }
  function closeModal(){
    modal.classList.remove('open');
  }
  document.addEventListener('click', (e) => {
    const el = e.target.closest('.desc-text');
    if(!el) return;
    openModal(el.dataset.title, el.dataset.desc);
  });
  close.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if(e.target === modal) closeModal();
  });
  document.addEventListener('keydown', (e) => {
    if(e.key === 'Escape') closeModal();
  });
})();



(function(){
  const modal = document.getElementById('editModal');

  const idEl = document.getElementById('editId');
  const titleEl = document.getElementById('editTitle');
  const sizeEl = document.getElementById('editSize');
  const priceEl = document.getElementById('editPrice');
  const discountEl = document.getElementById('editDiscount');
  const descEl = document.getElementById('editDescription');
  const previewEl = document.getElementById('editPreview');
  const imageInput = document.getElementById('editImageInput');

  const form = document.getElementById('editForm');
  const deleteBtn = document.getElementById('deleteBtn');

  document.querySelectorAll('.admin-product-img').forEach(img=>{
    img.addEventListener('click', ()=>{
      idEl.value = img.dataset.id;
      titleEl.value = img.dataset.title;
      sizeEl.value = img.dataset.size;
      priceEl.value = img.dataset.price;
      discountEl.value = img.dataset.discount;
      descEl.value = img.dataset.description;
      previewEl.src = "/static/uploads/" + img.dataset.image;
      imageInput.value = "";

      form.action = "/admin/update_product";

      imageInput.addEventListener("change", ()=>{
        const file = imageInput.files[0];
        if (!file) return;

        const reader = new FileReader();

        reader.onload = (e)=>{
          previewEl.src = e.target.result;
        };

        reader.readAsDataURL(file);
      });

      deleteBtn.onclick = () => {
        if(confirm("Rostdan o‘chirasizmi?")){
          const f = document.createElement("form");
          f.method = "post";
          f.action = "/admin/delete_product/" + img.dataset.id;
          document.body.appendChild(f);
          f.submit();
        }
      };

      modal.classList.add('open');
    });
  });

  document.getElementById('editClose').onclick =
    () => modal.classList.remove('open');

  modal.addEventListener('click', (e)=>{
    if(e.target === modal) modal.classList.remove('open');
  });

})();