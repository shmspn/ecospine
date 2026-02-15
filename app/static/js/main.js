

(function(){
  const form = document.getElementById('filtersForm');

  // ------- Modal open/close -------
  const openBtns = document.querySelectorAll('[data-open]');
  const closeBtns = document.querySelectorAll('[data-close]');

  function openModal(sel){
    const m = document.querySelector(sel);
    if(m) m.classList.add('open');
  }
  function closeModal(modal){
    modal.classList.remove('open');
  }

  openBtns.forEach(btn=>{
    btn.addEventListener('click', ()=> openModal(btn.getAttribute('data-open')));
  });

  closeBtns.forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const modal = btn.closest('.modal');
      if(modal) closeModal(modal);
    });
  });

  document.querySelectorAll('.modal').forEach(modal=>{
    modal.addEventListener('click', (e)=>{
      if(e.target === modal) closeModal(modal);
    });
  });

  document.addEventListener('keydown', (e)=>{
    if(e.key === 'Escape'){
      document.querySelectorAll('.modal.open').forEach(m => m.classList.remove('open'));
    }
  });

  // ------- Sort: select change -> apply immediately -------
  const sortSelect = document.getElementById('sortSelect');
  const sortInput  = document.getElementById('sortInput');
  sortSelect.addEventListener('change', ()=>{
    sortInput.value = sortSelect.value;
    form.submit();
  });



function formatUZS(value){
  const digits = value.replace(/\D/g, ""); // faqat sonlar
  return digits.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function cleanNumber(value){
  return value.replace(/\s/g, ""); // probellarni olib tashlash
}

function attachMoneyFormatter(el){
  el.addEventListener("input", ()=>{
    const start = el.selectionStart;
    const before = el.value;

    el.value = formatUZS(el.value);

    const diff = el.value.length - before.length;
    el.setSelectionRange(start + diff, start + diff);
  });
}

  // ------- Price Apply -------
  const minPrice = document.getElementById('minPrice');
  const maxPrice = document.getElementById('maxPrice');

  attachMoneyFormatter(minPrice);
  attachMoneyFormatter(maxPrice);

  const minPriceInput = document.getElementById('minPriceInput');
  const maxPriceInput = document.getElementById('maxPriceInput');

  document.getElementById('applyPrice').addEventListener('click', ()=>{
    const minEl = document.getElementById('minPrice');
    const maxEl = document.getElementById('maxPrice');

    const minHidden = document.getElementById('minPriceInput');
    const maxHidden = document.getElementById('maxPriceInput');

    // FORMATNI TOZALAYMIZ (<<< muhim qism)
    const minVal = cleanNumber(minEl.value || '');
    const maxVal = cleanNumber(maxEl.value || '');

    // min
    if (minVal) {
        minHidden.disabled = false;
        minHidden.value = minVal;
    } else {
        minHidden.value = '';
        minHidden.disabled = true; // <<< muhim
    }

    // max
    if (maxVal) {
        maxHidden.disabled = false;
        maxHidden.value = maxVal;
    } else {
        maxHidden.value = '';
        maxHidden.disabled = true; // <<< muhim
    }

    document.getElementById('priceModal').classList.remove('open');
    document.getElementById('filtersForm').submit();
  });

  (function initPriceHidden(){
    const minHidden = document.getElementById('minPriceInput');
    const maxHidden = document.getElementById('maxPriceInput');

    if (!minHidden.value) minHidden.disabled = true;
    if (!maxHidden.value) maxHidden.disabled = true;
  })();



  // ------- Sizes Apply (multi) -------
  const sizesHidden = document.getElementById('sizesHiddenContainer');

  function rebuildSizesHidden(){
    sizesHidden.innerHTML = '';
    document.querySelectorAll('.sizeCheck:checked').forEach(ch=>{
      const inp = document.createElement('input');
      inp.type = 'hidden';
      inp.name = 'sizes';
      inp.value = ch.value;
      sizesHidden.appendChild(inp);
    });
  }

  document.getElementById('applySizes').addEventListener('click', ()=>{
    rebuildSizesHidden();
    document.getElementById('sizeModal').classList.remove('open');
    form.submit();
  });

  document.getElementById('clearSizes').addEventListener('click', ()=>{
    document.querySelectorAll('.sizeCheck').forEach(ch=> ch.checked = false);
    rebuildSizesHidden();
    // apply qilmasdan faqat tozalab qo‘yamiz; apply bosilsa ketadi
  });

  // Page reload bo‘lganda ham hidden sizes to‘g‘ri turishi uchun:
  rebuildSizesHidden();
})();




(function(){
  const modal = document.getElementById('quickViewModal');

  const titleEl = document.getElementById('qvTitle');
  const sizeEl  = document.getElementById('qvSize');
  const imgEl   = document.getElementById('qvImage');
  const descEl    = document.getElementById('description')

  const oldPriceEl = document.getElementById('qvOldPrice');
  const newPriceEl = document.getElementById('qvNewPrice');

  document.querySelectorAll('.product-card').forEach(card=>{
    card.addEventListener('click', (e)=>{
      e.preventDefault();

      const title = card.dataset.title;
      const size  = card.dataset.size;
      const price = card.dataset.price;
      const final = card.dataset.final;
      const desc  = card.dataset.description;
      const discount = parseInt(card.dataset.discount || "0");

      titleEl.textContent = title;
      sizeEl.textContent  = size;
      descEl.textContent  = desc;
      imgEl.src = card.dataset.image;

      if(discount > 0){
        oldPriceEl.textContent = price + " so‘m";
        oldPriceEl.style.display = "block";
      } else {
        oldPriceEl.style.display = "none";
      }

      newPriceEl.textContent = final + " so‘m";

      modal.classList.add('open');
    });
  });

  document.getElementById('qvClose').onclick = () => modal.classList.remove('open');

  modal.addEventListener('click', (e)=>{
    if(e.target === modal) modal.classList.remove('open');
  });

})();


