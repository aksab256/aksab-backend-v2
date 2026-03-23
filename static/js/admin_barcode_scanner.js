document.addEventListener('DOMContentLoaded', function() {
    let html5QrCode = null;

    async function startScanning(targetInput, readerId) {
        const readerDiv = document.getElementById(readerId);
        
        if (html5QrCode && html5QrCode.isScanning) {
            await html5QrCode.stop();
        }

        if (readerDiv.style.display === 'none') {
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
                { fps: 25, qrbox: { width: 250, height: 150 } },
                (decodedText) => {
                    // 1. ضع الكود في الخانة المستهدفة
                    targetInput.value = decodedText;
                    
                    // 2. ابحث عن المنسدلة (المنتج) في نفس السطر
                    const row = targetInput.closest('tr') || targetInput.closest('.inline-related');
                    const productSelect = row.querySelector('select[id*="product"]');
                    
                    if (productSelect) {
                        let found = false;
                        for (let i = 0; i < productSelect.options.length; i++) {
                            // بنشيك لو اسم المنتج في القائمة يحتوي على الباركود اللي لقطناه
                            if (productSelect.options[i].text.includes(decodedText)) {
                                productSelect.selectedIndex = i;
                                found = true;
                                break;
                            }
                        }
                        if (!found) {
                            alert("الباركود " + decodedText + " غير موجود في قائمة المنتجات!");
                        }
                        // تنبيه ديجانجو بالتغيير عشان يحسب الأسعار لو فيه سكربت تاني
                        productSelect.dispatchEvent(new Event('change', { bubbles: true }));
                    }

                    // 3. اقفل الكاميرا
                    html5QrCode.stop().then(() => {
                        readerDiv.style.display = 'none';
                    });
                }
            ).catch(err => {
                console.error("Camera Error:", err);
                readerDiv.style.display = 'none';
            });
        } else {
            readerDiv.style.display = 'none';
            if (html5QrCode) html5QrCode.stop();
        }
    }

    function setupScannerForRow(field) {
        // نطبق السكربت على حقل المنتج في الجدول
        if (field.dataset.hasScanner) return;
        field.dataset.hasScanner = "true";

        const container = field.parentNode;
        
        // إنشاء خانة إدخال مؤقتة للباركود (عشان الكاميرا تكتب فيها)
        const barcodeInput = document.createElement('input');
        barcodeInput.type = 'text';
        barcodeInput.placeholder = 'كود المنتج...';
        barcodeInput.style.cssText = "width: 100px; margin: 2px; padding: 4px; border: 1px solid #ccc; font-size: 12px;";

        const scanBtn = document.createElement('button');
        scanBtn.innerHTML = '📷';
        scanBtn.type = 'button';
        scanBtn.style.cssText = "padding: 4px 8px; background: #417690; color: white; border: none; border-radius: 4px; cursor: pointer;";

        const readerDiv = document.createElement('div');
        const rId = 'reader-' + Math.random().toString(36).substr(2, 9);
        readerDiv.id = rId;
        readerDiv.style.cssText = "width: 250px; display: none; border: 2px solid #417690; position: absolute; z-index: 1000; background: white;";

        container.appendChild(barcodeInput);
        container.appendChild(scanBtn);
        container.appendChild(readerDiv);

        scanBtn.onclick = (e) => {
            e.preventDefault();
            startScanning(barcodeInput, rId);
        };
    }

    // تشغيل المراقب للجداول
    const selector = 'select[id*="product"]';
    const observer = new MutationObserver(() => {
        document.querySelectorAll(selector).forEach(setupScannerForRow);
    });
    observer.observe(document.body, { childList: true, subtree: true });
    document.querySelectorAll(selector).forEach(setupScannerForRow);
});

