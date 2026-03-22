document.addEventListener('DOMContentLoaded', function() {
    
    // وظيفة شاملة لفتح الكاميرا ووضع القيمة في الحقل
    function startScanning(inputField, readerId) {
        const readerDiv = document.getElementById(readerId);
        
        if (readerDiv.style.display === 'none') {
            readerDiv.style.display = 'block';
            
            // تعريف السكانر
            const html5QrCode = new Html5Qrcode(readerId);
            
            html5QrCode.start(
                { facingMode: "environment" }, // إجبار الكاميرا الخلفية
                { fps: 10, qrbox: { width: 250, height: 150 } },
                (decodedText) => {
                    // 1. وضع القيمة في الحقل
                    inputField.value = decodedText;

                    // 2. دعم خاص لـ Select2 (المستخدم في المشتريات والـ Autocomplete)
                    if (window.jQuery && jQuery(inputField).data('select2')) {
                        // إجبار المنسدلة تختار القيمة الجديدة وتحدث نفسها
                        let newOption = new Option(decodedText, decodedText, true, true);
                        jQuery(inputField).append(newOption).trigger('change');
                    }

                    // 3. تنبيه السيستم بحدوث تغيير
                    inputField.dispatchEvent(new Event('change', { bubbles: true }));
                    inputField.dispatchEvent(new Event('input', { bubbles: true }));

                    // 4. إغلاق الكاميرا وتخبيئة الـ Div
                    html5QrCode.stop().then(() => {
                        readerDiv.style.display = 'none';
                    }).catch(err => console.error("Stop error", err));
                }
            ).catch(err => {
                alert("تعذر فتح الكاميرا. تأكد من استخدام HTTPS ومنح صلاحية الكاميرا للمتصفح.");
                readerDiv.style.display = 'none';
            });
            
            // تخزين الكائن في الـ Div عشان نقدر نقفله لو المستخدم داس "إغلاق"
            readerDiv.dataset.scannerActive = "true";
            window.activeScanner = html5QrCode; 
        } else {
            if (window.activeScanner) {
                window.activeScanner.stop().then(() => {
                    readerDiv.style.display = 'none';
                });
            } else {
                readerDiv.style.display = 'none';
            }
        }
    }

    function setupScanner(field) {
        // منع التكرار لو الزرار موجود فعلاً
        if (field.dataset.hasScanner || field.parentElement.querySelector('.scan-btn')) return;
        field.dataset.hasScanner = "true";

        const scanBtn = document.createElement('button');
        scanBtn.innerHTML = '📷';
        scanBtn.type = 'button';
        scanBtn.className = 'scan-btn';
        scanBtn.style.cssText = "margin: 0 5px; padding: 4px 10px; background: #417690; color: white; border: none; border-radius: 4px; cursor: pointer; vertical-align: middle;";
        
        const readerDiv = document.createElement('div');
        const rId = 'reader-' + Math.random().toString(36).substr(2, 9);
        readerDiv.id = rId;
        readerDiv.style.cssText = "width: 100%; max-width: 300px; margin-top: 10px; display: none; border: 2px solid #417690; overflow: hidden;";

        field.parentNode.insertBefore(scanBtn, field.nextSibling);
        field.parentNode.appendChild(readerDiv);

        scanBtn.onclick = () => startScanning(field, rId);
    }

    // تشغيل على كل حقول الباركود والأصناف (رئيسي أو جداول)
    const targetSelectors = 'input[id*="barcode"], select[id*="product"], input[name*="barcode"]';

    // 1. تشغيل أولي
    document.querySelectorAll(targetSelectors).forEach(setupScanner);

    // 2. مراقبة إضافة أسطر جديدة (Inlines) في المشتريات
    const observer = new MutationObserver(() => {
        document.querySelectorAll(targetSelectors).forEach(setupScanner);
    });
    observer.observe(document.body, { childList: true, subtree: true });
});

