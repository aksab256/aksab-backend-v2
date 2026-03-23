document.addEventListener('DOMContentLoaded', function() {
    let html5QrCode = null;

    async function startScanning(targetInput, readerId) {
        const readerDiv = document.getElementById(readerId);
        if (html5QrCode && html5QrCode.isScanning) { await html5QrCode.stop(); }

        if (readerDiv.style.display === 'none') {
            document.querySelectorAll('[id^="reader-"]').forEach(el => el.style.display = 'none');
            readerDiv.style.display = 'block';
            html5QrCode = new Html5Qrcode(readerId);
            html5QrCode.start(
                { facingMode: "environment" },
                { fps: 25, qrbox: { width: 250, height: 150 } },
                (decodedText) => {
                    targetInput.value = decodedText;
                    // لو إحنا في جدول (زي المشتريات)، نحدث المنسدلة
                    const row = targetInput.closest('tr') || targetInput.closest('.inline-related');
                    if (row) {
                        const productSelect = row.querySelector('select[id*="product"]');
                        if (productSelect) {
                            for (let i = 0; i < productSelect.options.length; i++) {
                                if (productSelect.options[i].text.includes(decodedText)) {
                                    productSelect.selectedIndex = i;
                                    productSelect.dispatchEvent(new Event('change', { bubbles: true }));
                                    break;
                                }
                            }
                        }
                    }
                    html5QrCode.stop().then(() => { readerDiv.style.display = 'none'; });
                }
            ).catch(err => { readerDiv.style.display = 'none'; });
        } else {
            readerDiv.style.display = 'none';
            if (html5QrCode) html5QrCode.stop();
        }
    }

    function addScanner(targetField) {
        if (targetField.dataset.hasScanner) return;
        targetField.dataset.hasScanner = "true";
        const container = targetField.parentNode;
        
        const scanBtn = document.createElement('button');
        scanBtn.innerHTML = '📷 مسح باركود';
        scanBtn.type = 'button';
        scanBtn.style.cssText = "padding: 4px 8px; background: #417690; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px;";

        const readerDiv = document.createElement('div');
        const rId = 'reader-' + Math.random().toString(36).substr(2, 9);
        readerDiv.id = rId;
        readerDiv.style.cssText = "width: 250px; display: none; border: 2px solid #417690; position: absolute; z-index: 1000; background: white;";

        container.appendChild(scanBtn);
        container.appendChild(readerDiv);

        scanBtn.onclick = (e) => { e.preventDefault(); startScanning(targetField, rId); };
    }

    // تشغيل السكريبت على: 
    // 1. منسدلة المنتج (في الجداول) 2. خانة الباركود (في صفحة الصنف)
    const selectors = 'select[id*="product"], input[id*="barcode"]';
    const observer = new MutationObserver(() => {
        document.querySelectorAll(selectors).forEach(addScanner);
    });
    observer.observe(document.body, { childList: true, subtree: true });
    document.querySelectorAll(selectors).forEach(addScanner);
});

