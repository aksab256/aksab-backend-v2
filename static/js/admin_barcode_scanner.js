document.addEventListener('DOMContentLoaded', function() {
    function startScanning(inputField, readerId) {
        const readerDiv = document.getElementById(readerId);
        if (readerDiv.style.display === 'none') {
            readerDiv.style.display = 'block';
            
            // إضافة إعدادات دعم كل أنواع الباركود
            const html5QrCode = new Html5Qrcode(readerId, { 
                formatsToSupport: [ 
                    Html5QrcodeSupportedFormats.EAN_13, 
                    Html5QrcodeSupportedFormats.EAN_8, 
                    Html5QrcodeSupportedFormats.CODE_128, 
                    Html5QrcodeSupportedFormats.UPC_A, 
                    Html5QrcodeSupportedFormats.QR_CODE 
                ] 
            });

            html5QrCode.start(
                { facingMode: "environment" }, 
                { 
                    fps: 20, // سرعة أعلى للقط أسرع
                    qrbox: { width: 280, height: 160 }, // تكبير مربع التركيز شوية
                    aspectRatio: 1.777778 // نسبة عرض الشاشة لتحسين الفوكس
                },
                (decodedText) => {
                    let found = false;
                    
                    // لو الحقل عبارة عن Input (خانة نصية) مش Select
                    if (inputField.tagName === 'INPUT') {
                        inputField.value = decodedText;
                        found = true;
                    } else {
                        // لو الحقل منسدلة (Select)
                        for (let i = 0; i < inputField.options.length; i++) {
                            if (inputField.options[i].text.includes(decodedText)) {
                                inputField.selectedIndex = i;
                                found = true;
                                break;
                            }
                        }
                    }

                    if (!found) {
                        alert("الباركود [" + decodedText + "] غير مسجل!");
                    }

                    inputField.dispatchEvent(new Event('change', { bubbles: true }));

                    // قفل الكاميرا بعد اللقط بنجاح
                    html5QrCode.stop().then(() => {
                        readerDiv.style.display = 'none';
                    }).catch(err => console.error("Error stopping scan:", err));
                }
            ).catch(err => {
                console.error("Camera Error:", err);
                alert("تعذر فتح الكاميرا، تأكد من إعطاء التصريح.");
                readerDiv.style.display = 'none';
            });
        } else {
            // لو الزرار اتداس والكاميرا مفتوحة، اقفلها
            readerDiv.style.display = 'none';
        }
    }

    function setupScanner(field) {
        if (field.dataset.hasScanner || field.parentElement.querySelector('.scan-btn')) return;
        field.dataset.hasScanner = "true";

        const scanBtn = document.createElement('button');
        scanBtn.innerHTML = '📷 مسح';
        scanBtn.type = 'button';
        scanBtn.className = 'scan-btn';
        scanBtn.style.cssText = "margin: 0 5px; padding: 6px 12px; background: #417690; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;";

        const readerDiv = document.createElement('div');
        const rId = 'reader-' + Math.random().toString(36).substr(2, 9);
        readerDiv.id = rId;
        readerDiv.style.cssText = "width: 100%; max-width: 350px; margin: 15px auto; display: none; border: 3px solid #417690; border-radius: 8px; overflow: hidden;";

        field.parentNode.insertBefore(scanBtn, field.nextSibling);
        field.parentNode.appendChild(readerDiv);

        scanBtn.onclick = (e) => {
            e.preventDefault();
            startScanning(field, rId);
        };
    }

    const selector = 'select[id*="product"], input[id*="barcode"]';
    document.querySelectorAll(selector).forEach(setupScanner);

    const observer = new MutationObserver(() => {
        document.querySelectorAll(selector).forEach(setupScanner);
    });
    observer.observe(document.body, { childList: true, subtree: true });
});

