

// ---------------- Desc modal ----------------
(() => {
  const modal = document.getElementById("descModal");
  const body = document.getElementById("modalBody");
  const title = document.getElementById("modalTitle");
  const closeBtn = document.getElementById("modalClose");

  if (!modal || !body || !title || !closeBtn) return;

  const openModal = (t, text) => {
    title.textContent = t || "Description";
    body.textContent = text || "";
    modal.classList.add("open");
  };

  const closeModal = () => modal.classList.remove("open");

  document.addEventListener("click", (e) => {
    const el = e.target.closest(".desc-text");
    if (!el) return;
    openModal(el.dataset.title, el.dataset.desc);
  });

  closeBtn.addEventListener("click", closeModal);

  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
})();


// ✅ NEW: Carousel index state (har carousel uchun alohida index saqlaymiz)
const __carouselIndex = new WeakMap(); // ✅ NEW
const __carouselGo = (carousel, newIndex) => { // ✅ NEW
  const track = carousel.querySelector(".carousel-track");
  if (!track) return;
  const slides = track.children;
  if (!slides.length) return;

  const len = slides.length;
  let idx = newIndex % len;
  if (idx < 0) idx += len;

  __carouselIndex.set(carousel, idx);
  track.style.transform = `translateX(-${idx * 100}%)`;
};
const __carouselGetIndex = (carousel) => __carouselIndex.get(carousel) ?? 0; // ✅ NEW
const __carouselReset = (carousel) => __carouselGo(carousel, 0); // ✅ NEW


// ---------------- Edit modal (admin update) ----------------
(() => {
  const modal = document.getElementById("editModal");
  const form = document.getElementById("editForm");
  const deleteBtn = document.getElementById("deleteBtn"); // siz comment qilgansiz
  const idEl = document.getElementById("editId");
  const titleEl = document.getElementById("editTitle");
  const sizeEl = document.getElementById("editSize");
  const priceEl = document.getElementById("editPrice");
  const discountEl = document.getElementById("editDiscount");
  const descEl = document.getElementById("editDescription");
  const imagesEl = document.getElementById("carousel-images");

  const imageInput = document.getElementById("editImageInput");

  const closeBtn = document.getElementById("editClose");

    // ✅ NEW: delete tugma + hidden input
  const imgDeleteBtn = document.getElementById("imgDeleteBtn"); // ✅ NEW (HTML’da qo‘ying)
  const deleteImagesInput = document.getElementById("deleteImages"); // ✅ NEW (hidden input)
  let deletedImages = []; // ✅ NEW (state)

  const open = () => modal.classList.add("open");
  const close = () => modal.classList.remove("open");

    const resetDeleteState = () => { // ✅ NEW
    deletedImages = [];
    if (deleteImagesInput) deleteImagesInput.value = "[]";
  };

  // ✅ event delegation: bitta click listener
  document.addEventListener("click", (e) => {
    const card = e.target.closest(".card");
    if (!card) return;

    e.preventDefault();

    idEl.value = card.dataset.id || "";
    titleEl.value = card.dataset.title || "";
    sizeEl.value = card.dataset.size || "";
    priceEl.value = card.dataset.price || "";
    discountEl.value = card.dataset.discount || "";
    descEl.value = card.dataset.description || "";

    if (imageInput) imageInput.value = "";

     // ✅ NEW: modal ochilganda delete state reset
    resetDeleteState(); // ✅ NEW

    // rasmlar
    if (imagesEl) {
      let images = [];
      try {
        images = card.dataset.images ? JSON.parse(card.dataset.images) : [];
      } catch {
        images = [];
      }

      imagesEl.innerHTML = "";
      images.forEach((fn) => {
        const img = document.createElement("img");
        img.src = `/static/uploads/${fn}`;
        img.alt = "";
        img.dataset.filename = fn; // ✅ NEW (delete uchun kerak)
        imagesEl.appendChild(img);
      });

      // ✅ NEW: modal ochilganda carousel index 0 ga qaytsin
      const editCarousel = modal.querySelector(".carousel"); // ✅ NEW
      if (editCarousel) __carouselReset(editCarousel); // ✅ NEW
    }

    form.action = "/admin/update_product";

    deleteBtn.onclick = () => {
      if (!confirm("Rostdan o‘chirasizmi?")) return;
      const f = document.createElement("form");
      f.method = "post";
      f.action = "/admin/delete_product/" + (card.dataset.id || "");
      document.body.appendChild(f);
      f.submit();
    };

    open();
  });

   if (closeBtn) closeBtn.addEventListener("click", () => { // ✅ NEW (reset ham qilsin)
    resetDeleteState(); // ✅ NEW
    close();
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      resetDeleteState(); // ✅ NEW
      close();
    };
  });

  // ✅ NEW: "current slide"ni delete qilish
  if (imgDeleteBtn) {
    imgDeleteBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      const editCarousel = modal.querySelector(".carousel"); // modal ichidagi carousel
      if (!editCarousel) return;

      const track = editCarousel.querySelector(".carousel-track");
      if (!track) return;

      const slides = Array.from(track.children);
      if (!slides.length) return;

      const idx = __carouselGetIndex(editCarousel); // hozirgi index
      const current = slides[idx];
      if (!current) return;

      const filename = current.dataset.filename; // ✅ NEW
      if (filename) {
        deletedImages.push(filename);
        if (deleteImagesInput) {
          deleteImagesInput.value = JSON.stringify(deletedImages);
        }
      }

      current.remove();

      // o‘chirgandan keyin indexni to‘g‘rilaymiz
      const afterLen = track.children.length;
      if (!afterLen) {
        __carouselReset(editCarousel);
        return;
      }

      const newIndex = idx >= afterLen ? afterLen - 1 : idx;
      __carouselGo(editCarousel, newIndex);
    });
  }

})();


// ---------------- Size filter modal ----------------
(() => {
  const form = document.getElementById("get-form");
  const hiddenBox = document.getElementById("sizeHiddenBox");
  const applyBtn = document.getElementById("applySizes");
  const clearBtn = document.getElementById("clearSizes");
  const sizeModal = document.getElementById("sizeModal");

  if (!form || !hiddenBox || !applyBtn || !clearBtn) return;

  const rebuildHiddenSizes = () => {
    hiddenBox.innerHTML = "";
    document.querySelectorAll(".sizeCheck:checked").forEach((ch) => {
      const inp = document.createElement("input");
      inp.type = "hidden";
      inp.name = "size";
      inp.value = ch.value;
      hiddenBox.appendChild(inp);
    });
  };

  // generic open/close (faqat shu blokka kerak bo‘lsa)
  document.addEventListener("click", (e) => {
    const openBtn = e.target.closest("[data-open]");
    if (openBtn) {
      const m = document.querySelector(openBtn.getAttribute("data-open"));
      if (m) m.classList.add("open");
      return;
    }

    const closeBtn = e.target.closest("[data-close]");
    if (closeBtn) {
      closeBtn.closest(".modal")?.classList.remove("open");
    }
  });

  document.querySelectorAll(".modal").forEach((m) => {
    m.addEventListener("click", (e) => {
      if (e.target === m) m.classList.remove("open");
    });
  });

  applyBtn.addEventListener("click", () => {
    rebuildHiddenSizes();
    if (sizeModal) sizeModal.classList.remove("open");
    form.submit();
  });

  clearBtn.addEventListener("click", () => {
    document.querySelectorAll(".sizeCheck").forEach((ch) => (ch.checked = false));
    rebuildHiddenSizes();
  });

  rebuildHiddenSizes();
})();


 // ----------- Carousel ----------------------

// ----------- Carousel ----------------------
document.querySelectorAll(".carousel").forEach((carousel) => {
  const track = carousel.querySelector(".carousel-track");
  if (!track) return;

  // ✅ NEW: har carousel uchun index init
  __carouselIndex.set(carousel, 0); // ✅ NEW

  carousel.querySelector(".next").onclick = (e) => { // ✅ NEW: e qo‘shdik
    e.preventDefault();         // ✅ NEW
    e.stopPropagation();        // ✅ NEW (modal yopilib ketmasin)
    const slides = track.children;
    if (!slides.length) return;

    const idx = __carouselGetIndex(carousel);
    __carouselGo(carousel, idx + 1); // ✅ NEW (index state bilan)
  };

  carousel.querySelector(".prev").onclick = (e) => { // ✅ NEW: e qo‘shdik
    e.preventDefault();         // ✅ NEW
    e.stopPropagation();        // ✅ NEW
    const slides = track.children;
    if (!slides.length) return;

    const idx = __carouselGetIndex(carousel);
    __carouselGo(carousel, idx - 1); // ✅ NEW
  };
});