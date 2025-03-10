function showToast(title, message, type = "info", duration = 4000) {
  const container = document.querySelector(".toast-container");

  // Tạo thông báo
  const toast = document.createElement("div");
  toast.classList.add("toast", type);
  toast.innerHTML = `
                <div class="toast-icon">
                    <i class="${getIcon(type)}"></i>
                </div>
                <div class="toast-content">
                 ${message}
                </div>
                <span class="close-btn">&times;</span>
            `;

  // Thêm vào container
  container.appendChild(toast);

  // Xóa khi click vào nút đóng
  toast
    .querySelector(".close-btn")
    .addEventListener("click", () => removeToast(toast));

  // Tự động ẩn sau thời gian nhất định
  setTimeout(() => removeToast(toast), duration);
}

function removeToast(toast) {
  toast.style.animation = "fadeOut 0.5s forwards";
  setTimeout(() => toast.remove(), 500);
}

function getIcon(type) {
  switch (type) {
    case "success":
      return "fa-solid fa-check";
    case "error":
      return "fas fa-times-circle";
    case "warning":
      return "fas fa-exclamation-triangle";
    case "info":
      return "fas fa-info-circle";
    default:
      return "fas fa-info-circle";
  }
}
