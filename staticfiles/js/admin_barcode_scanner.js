document.addEventListener('DOMContentLoaded', function() {
    
    function startScanning(inputField, readerId) {
        const readerDiv = document.getElementById(readerId);
        
        if (readerDiv.style.display === 'none') {
            readerDiv.style.display = 'block';
            const html5QrCode = new Html5Qrcode(readerId);
            
            html5QrCode.start(
                { facingMode: "environment" }, 
                { fps: 10, qrbox: { width: 250, height: 150 } },
                (decodedText) => {
                    // 1. حط الكود المقروء في الخانة
                    inputField.value = decodedText;

                    // 2. 🚀 الجزء السحري: التعامل مع المنسدلة (Select2)
                    if (window.jQuery && jQuery(inputField).hasClass('admin-autocomplete')) {
                        // ديجانجو بيستخدم Select2 للأصناف
                        var $select = jQuery(inputField);
                        
                        // بنحاول نلاقي الخيار اللي الباركود بتاعه مطابق (لو موجود في القائمة)
                        // أو بنبعت استعلام للبحث عن المنتج بالباركود
                        var option = new Option(decodedText, decodedText, true, true);
                        $select.append(option).trigger('change');
                        
                        // تنبيه السيستم إن فيه صنف تم اختياره
                        $select.trigger({
                            type: 'select2:select',
                            params: { data: { id: decodedText, text: decodedText } }
                        });
                    }

                    // 3. تنبيه عام للتغيير
                    inputField.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    // 4. قفل الكاميرا
                    html5QrCode.stop().then(() => {
                        readerDiv.style.display = 'none';
                    });
                }
            ).catch(err => {
                console.error("Camera Error:", err);
                readerDiv.style.display = 'none';
            });
            window.activeScanner = html5QrCode; 
        } else {
            if (window.activeScanner) {
                window.activeScanner.stop().then(() => {
                    readerDiv.style.display = 'none';
                });
            }
        }
    }

    function setupScanner(field) {
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
        readerDiv.style.cssText = "width: 100%; max-width: 300px; margin-top: 10px; display: none; border: 2px solid #417690;";

        field.parentNode.insertBefore(scanBtn, field.nextSibling);
        field.parentNode.appendChild(readerDiv);

        scanBtn.onclick = () => startScanning(field, rId);
    }

    // استهداف حقول الباركود والأصناف
    const targetSelectors = 'input[id*="barcode"], select[id*="product"], .admin-autocomplete';

    document.querySelectorAll(targetSelectors).forEach(setupScanner);

    const observer = new MutationObserver(() => {
        document.querySelectorAll(targetSelectors).forEach(setupScanner);
    });
    observer.observe(document.body, { childList: true, subtree: true });
});

