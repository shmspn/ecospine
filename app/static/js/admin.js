
// Modal helper: generic open/close/click-outside handling
const __createModalManager = (modalId, options = {}) => {
  const modal = document.getElementById(modalId);
  if (!modal) return null;

  const open = () => modal.classList.add("open");
  const close = () => modal.classList.remove("open");
  const toggle = () => modal.classList.toggle("open");

  // Click outside to close
  modal.addEventListener("click", (e) => {
    if (e.target === modal) close();
  });

  // Escape key to close
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("open")) close();
  });

  return { modal, open, close, toggle };
};

// Desc modal setup
(() => {
  const mgr = __createModalManager("descModal");
  if (!mgr) return;

  const body = document.getElementById("modalBody");
  const title = document.getElementById("modalTitle");
  const closeBtn = document.getElementById("modalClose");

  if (!body || !title || !closeBtn) return;

  const openModal = (t, text) => {
    title.textContent = t || "Description";
    body.textContent = text || "";
    mgr.open();
  };

  document.addEventListener("click", (e) => {
    const el = e.target.closest(".desc-text");
    if (!el) return;
    openModal(el.dataset.title, el.dataset.desc);
  });

  closeBtn.addEventListener("click", mgr.close);
})();


// Carousel index state
const __carouselIndex = new WeakMap();
const __carouselGo = (carousel, newIndex) => {
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
const __carouselGetIndex = (carousel) => __carouselIndex.get(carousel) ?? 0;
const __carouselReset = (carousel) => __carouselGo(carousel, 0);


// ---------------- Edit modal (admin update) ----------------
(() => {
  const modal = document.getElementById("editModal");
  const form = document.getElementById("editForm");
  const deleteBtn = document.getElementById("deleteBtn");
  const idEl = document.getElementById("editId");
  const titleEl = document.getElementById("editTitle");
  const sizeEl = document.getElementById("editSize");
  const priceEl = document.getElementById("editPrice");
  const discountEl = document.getElementById("editDiscount");
  const descEl = document.getElementById("editDescription");
  const imagesEl = document.getElementById("carousel-images");

  const imageInput = document.getElementById("editImageInput");

  const closeBtn = document.getElementById("editClose");

  const imgDeleteBtn = document.getElementById("imgDeleteBtn");
  const deleteImagesInput = document.getElementById("deleteImages");
  let deletedImages = [];

  const resetDeleteState = () => {
    deletedImages = [];
    if (deleteImagesInput) deleteImagesInput.value = "[]";
  };

  // Event delegation for card clicks
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
    resetDeleteState();

    // Images
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
        img.dataset.filename = fn;
        imagesEl.appendChild(img);
      });

      const editCarousel = modal.querySelector(".carousel");
      if (editCarousel) __carouselReset(editCarousel);
    }

    form.action = "/admin/update_product";

    deleteBtn.onclick = () => {
      if (!confirm("Rostdan o‘chirasizmi?")) return;
      const f = document.createElement("form");
      f.method = "post";
      f.action = "/admin/delete_product/" + (card.dataset.id || "");
      const csrfInput = document.createElement("input");
      csrfInput.type = "hidden";
      csrfInput.name = "csrf_token";
      csrfInput.value = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
      f.appendChild(csrfInput);
      document.body.appendChild(f);
      f.submit();
    };

    modal.classList.add("open");
  });

  if (closeBtn) closeBtn.addEventListener("click", () => {
    resetDeleteState();
    modal.classList.remove("open");
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      resetDeleteState();
      modal.classList.remove("open");
    }
  });

  // Delete current slide
  if (imgDeleteBtn) {
    imgDeleteBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      const editCarousel = modal.querySelector(".carousel");
      if (!editCarousel) return;

      const track = editCarousel.querySelector(".carousel-track");
      if (!track) return;

      const slides = Array.from(track.children);
      if (!slides.length) return;

      const idx = __carouselGetIndex(editCarousel);
      const current = slides[idx];
      if (!current) return;

      const filename = current.dataset.filename;
      if (filename) {
        deletedImages.push(filename);
        if (deleteImagesInput) {
          deleteImagesInput.value = JSON.stringify(deletedImages);
        }
      }

      current.remove();


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
document.querySelectorAll(".carousel").forEach((carousel) => {
  const track = carousel.querySelector(".carousel-track");
  if (!track) return;

  __carouselIndex.set(carousel, 0);

  carousel.querySelector(".next").onclick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const slides = track.children;
    if (!slides.length) return;

    const idx = __carouselGetIndex(carousel);
    __carouselGo(carousel, idx + 1);
  };

  carousel.querySelector(".prev").onclick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const slides = track.children;
    if (!slides.length) return;

    const idx = __carouselGetIndex(carousel);
    __carouselGo(carousel, idx - 1);
  };
});