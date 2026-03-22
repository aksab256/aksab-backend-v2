document.addEventListener('DOMContentLoaded', function() {
    // وظيفة لإنشاء السكانر وإضافته لأي حقل
    function setupScanner(inputField) {
        if (inputField.parentElement.querySelector('.scan-btn')) return;

        const scanBtn = document.createElement('button');
        scanBtn.innerHTML = '📷';
        scanBtn.type = 'button';
        scanBtn.className = 'scan-btn';
        scanBtn.style.cssText = "margin: 0 5px; padding: 5px 10px; background: #417690; color: white; border: none; border-radius: 4px; cursor: pointer;";
        
        const readerDiv = document.createElement('div');
        readerDiv.id = 'reader-' + Math.random().toString(36).substr(2, 9);
        readerDiv.style.cssText = "width: 300px; margin-top: 10px; display: none; border: 1px solid #ccc;";

        inputField.parentNode.insertBefore(scanBtn, inputField.nextSibling);
        inputField.parentNode.appendChild(readerDiv);

        let html5QrCode;

        scanBtn.onclick = function() {
            if (readerDiv.style.display === 'none') {
                readerDiv.style.display = 'block';
                html5QrCode = new Html5QrCode(readerDiv.id);
                
                // تشغيل الكاميرا الخلفية مباشرة
                html5QrCode.start(
                    { facingMode: "environment" }, 
                    { fps: 10, qrbox: { width: 250, height: 150 } },
                    (decodedText) => {
                        inputField.value = decodedText;
                        // لو ده حقل اختيار صنف (Select) بنعمل trigger للتغيير
                        inputField.dispatchEvent(new Event('change')); 
                        html5QrCode.stop();
                        readerDiv.style.display = 'none';
                    }
                ).catch(err => console.error("Camera error:", err));
            } else {
                html5QrCode.stop();
                readerDiv.style.display = 'none';
            }
        };
    }

    // 1. تشغيل على الحقل الرئيسي (في صفحة المنتجات)
    const mainBarcode = document.querySelector('#id_barcode');
    if (mainBarcode) setupScanner(mainBarcode);

    // 2. تشغيل على كل حقول الأصناف في جداول المشتريات (Inlines)
    // بنراقب الصفحة لو اتضاف سطر جديد (Add another row)
    const observer = new MutationObserver(() => {
        const fields = document.querySelectorAll('input[id*="barcode"], select[id*="product"]');
        fields.forEach(field => setupScanner(field));
    });

    observer.observe(document.body, { childList: true, subtree: true });
    
    // تشغيل أولي للحقول الموجودة حالياً
    document.querySelectorAll('input[id*="barcode"], select[id*="product"]').forEach(setupScanner);
});

