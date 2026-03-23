document.addEventListener('DOMContentLoaded', function() {
    let html5QrCode = null;

    async function startScanning(inputField, readerId) {
        const readerDiv = document.getElementById(readerId);
        
        // لو الكاميرا مفتوحة في مكان تاني، اقفلها الأول
        if (html5QrCode && html5QrCode.isScanning) {
            await html5QrCode.stop();
        }

        if (readerDiv.style.display === 'none') {
            // إخفاء أي كاميرا تانية مفتوحة في الصفحة
            document.querySelectorAll('[id^="reader-"]').forEach(el => el.style.display = 'none');
            
            readerDiv.style.display = 'block';
            html5QrCode = new Html5Qrcode(readerId, { 
                formatsToSupport: [ 
                    Html5QrcodeSupportedFormats.EAN_13, 
                    Html5QrcodeSupportedFormats.CODE_128, 
                    Html5QrcodeSupportedFormats.UPC_A 
                ] 
            });

            html5QrCode.start(
                { facingMode: "environment" }, 
                { fps: 20, qrbox: { width: 250, height: 150 } },
                (decodedText) => {
                    // التعامل مع حقول الجداول (Inlines) أو الحقول العادية
                    if (inputField.tagName === 'SELECT') {
                        let found = false;
                        for (let i = 0; i < inputField.options.length; i++) {
                            if (inputField.options[i].text.includes(decodedText)) {
                                inputField.selectedIndex = i;
                                found = true;
                                break;
                            }
                        }
                        if (!found) alert("الباركود " + decodedText + " غير مسجل!");
                    } else {
                        inputField.value = decodedText;
                    }

                    inputField.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    html5QrCode.stop().then(() => {
                        readerDiv.style.display = 'none';
                    });
                }
            ).catch(err => {
                console.error(err);
                readerDiv.style.display = 'none';
            });
        } else {
            readerDiv.style.display = 'none';
            if (html5QrCode) html5QrCode.stop();
        }
    }

    function setupScanner(field) {
        if (field.dataset.hasScanner) return;
        field.dataset.hasScanner = "true";

        const container = field.parentNode;
        const scanBtn = document.createElement('button');
        scanBtn.innerHTML = '📷 مسح';
        scanBtn.type = 'button';
        scanBtn.style.cssText = "margin: 2px; padding: 4px 8px; background: #417690; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;";

        const readerDiv = document.createElement('div');
        const rId = 'reader-' + Math.random().toString(36).substr(2, 9);
        readerDiv.id = rId;
        readerDiv.style.cssText = "width: 100%; max-width: 300px; display: none; border: 2px solid #417690; margin-top: 5px; position: relative; z-index: 999;";

        container.appendChild(scanBtn);
        container.appendChild(readerDiv);

        scanBtn.onclick = (e) => {
            e.preventDefault();
            startScanning(field, rId);
        };
    }

    // مراقبة الصفحة لإضافة الزرار حتى للأسطر الجديدة في الفاتورة
    const selector = 'select[id*="product"], input[id*="barcode"]';
    const scanObserver = new MutationObserver(() => {
        document.querySelectorAll(selector).forEach(setupScanner);
    });
    scanObserver.observe(document.body, { childList: true, subtree: true });
    document.querySelectorAll(selector).forEach(setupScanner);
});

