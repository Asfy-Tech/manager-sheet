function loadGoogleFont(font) {
    let linkId = "google-font-" + font.replace(/\s+/g, "-");
    if (!document.getElementById(linkId)) {
        let link = document.createElement("link");
        link.id = linkId;
        link.rel = "stylesheet";
        link.href = `https://fonts.googleapis.com/css2?family=${font.replace(/\s+/g, '+')}:wght@400;700&display=swap`;
        document.head.appendChild(link);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    let fontSelector = document.getElementById("fontSelector");
    let fontList = [
        "Arial", "Verdana", "Tahoma", "Times New Roman", "Georgia", "Courier New", "Comic Sans MS", "Trebuchet MS",
        "Roboto", "Open Sans", "Lato", "Montserrat", "Poppins", "Raleway", "Nunito", "Inter", "Dancing Script",
        "Merriweather", "Playfair Display", "Oswald", "Source Sans Pro", "Lora", "Ubuntu", "PT Sans", "Fira Sans",
        "Bitter", "Crimson Text", "Libre Baskerville", "Arvo", "Josefin Sans", "Pacifico", "Caveat", "Indie Flower",
        "Shadows Into Light", "Amatic SC", "Lobster", "Bebas Neue", "Righteous", "Anton", "Exo 2", "Rajdhani"
    ];

    // Thêm từng font vào select
    fontList.forEach((font) => {
        let option = document.createElement("option");
        option.value = font;
        option.textContent = font;
        fontSelector.appendChild(option);
    });

    const choiceFontSelector = new Choices(fontSelector);

    // Tạo thẻ <style> để thay đổi font toàn bộ website
    let fontStyleTag = document.createElement("style");
    fontStyleTag.id = "global-font-style";
    document.head.appendChild(fontStyleTag);

    // 🌟 Load font đã lưu trong localStorage nếu có
    let savedFont = localStorage.getItem("selectedFont");
    if (savedFont) {
        applyFont(savedFont);
        fontSelector.value = savedFont; // Chọn đúng font trong dropdown
        choiceFontSelector.setChoiceByValue(savedFont);
    }

    fontSelector.addEventListener("change", function () {
        let selectedFont = this.value;
        console.log("Chọn font:", selectedFont);

        // Lưu vào localStorage
        localStorage.setItem("selectedFont", selectedFont);

        applyFont(selectedFont);
    });

    function applyFont(font) {
        // Nếu font không phải hệ thống, tải từ Google Fonts
        if (!["Arial", "Verdana", "Tahoma", "Times New Roman", "Georgia", "Courier New", "Comic Sans MS", "Trebuchet MS"].includes(font)) {
            loadGoogleFont(font);
        }

        // Cập nhật font trong thẻ <style>
        fontStyleTag.innerHTML = `
                * {
                    font-family: '${font}', sans-serif !important;
                }
            `;
    }
});