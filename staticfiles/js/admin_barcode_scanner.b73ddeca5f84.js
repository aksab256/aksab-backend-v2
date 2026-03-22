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
                    // 1. نبحث في المنسدلة عن خيار يحتوي على هذا الباركود
                    let found = false;
                    for (let i = 0; i < inputField.options.length; i++) {
                        // بنشيك لو النص بتاع المنتج فيه الباركود
                        if (inputField.options[i].text.includes(decodedText)) {
                            inputField.selectedIndex = i;
                            found = true;
                            break;
                        }
                    }

                    if (!found) {
                        alert("الباركود " + decodedText + " غير مسجل لأي منتج في القائمة!");
                    }

                    // 2. تنبيه السيستم بالتغيير
                    inputField.dispatchEvent(new Event('change', { bubbles: true }));

                    // 3. قفل الكاميرا
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
        }
    }

    function setupScanner(field) {
        if (field.dataset.hasScanner || field.parentElement.querySelector('.scan-btn')) return;
        field.dataset.hasScanner = "true";

        const scanBtn = document.createElement('button');
        scanBtn.innerHTML = '📷';
        scanBtn.type = 'button';
        scanBtn.className = 'scan-btn';
        scanBtn.style.cssText = "margin: 0 5px; padding: 4px 10px; background: #417690; color: white; border: none; border-radius: 4px; cursor: pointer;";
        
        const readerDiv = document.createElement('div');
        const rId = 'reader-' + Math.random().toString(36).substr(2, 9);
        readerDiv.id = rId;
        readerDiv.style.cssText = "width: 100%; max-width: 300px; margin-top: 10px; display: none; border: 2px solid #417690;";

        field.parentNode.insertBefore(scanBtn, field.nextSibling);
        field.parentNode.appendChild(readerDiv);

        scanBtn.onclick = () => startScanning(field, rId);
    }

    // استهداف الحقول (منسدلة الأصناف أو خانة الباركود)
    const selector = 'select[id*="product"], input[id*="barcode"]';
    document.querySelectorAll(selector).forEach(setupScanner);

    const observer = new MutationObserver(() => {
        document.querySelectorAll(selector).forEach(setupScanner);
    });
    observer.observe(document.body, { childList: true, subtree: true });
});

