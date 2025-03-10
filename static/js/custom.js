window.statusLogin = function (status_login) {
    switch (parseInt(status_login)) {
        case 1:
            return `<span class='badge fs-10 bg-danger-subtle text-danger-emphasis'>Không thể đăng nhập tự động</span>`;
        case 2:
            return `<span class='badge fs-10 bg-success-subtle text-success-emphasis'>Đang hoạt động</span>`;
        case 3:
            return `<span class='badge fs-10 bg-info-subtle text-info-emphasis'>Đang lấy dữ liệu...</span>`;
        case 4:
            return `<span class='badge fs-10 bg-primary-subtle text-primary-emphasis'>Đang đăng bài...</span>`;
        case 5:
            return `<span class='badge fs-10 bg-danger-subtle text-danger-emphasis'>Tài khoản bị khóa</span>`;
        case 6:
            return `<span class='badge fs-10 bg-warning-subtle text-warning-emphasis'>Không dùng được Proxy</span>`;
        default:
            return `<span class='badge fs-10 bg-secondary-subtle text-secondary-emphasis'>Trạng thái không xác định</span>`;
    }
};
