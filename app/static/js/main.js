
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

  // ------- Price Apply -------
  const minPrice = document.getElementById('minPrice');
  const maxPrice = document.getElementById('maxPrice');
  const minPriceInput = document.getElementById('minPriceInput');
  const maxPriceInput = document.getElementById('maxPriceInput');

  document.getElementById('applyPrice').addEventListener('click', ()=>{
    const minEl = document.getElementById('minPrice');
    const maxEl = document.getElementById('maxPrice');

    const minHidden = document.getElementById('minPriceInput');
    const maxHidden = document.getElementById('maxPriceInput');

    const minVal = (minEl.value || '').trim();
    const maxVal = (maxEl.value || '').trim();

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
