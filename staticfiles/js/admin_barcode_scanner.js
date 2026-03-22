document.addEventListener('DOMContentLoaded', function() {
    const barcodeInput = document.querySelector('#id_barcode');
    if (barcodeInput) {
        // إنشاء زرار الكاميرا
        const scanBtn = document.createElement('button');
        scanBtn.innerHTML = '📷 مسح باركود';
        scanBtn.type = 'button';
        scanBtn.className = 'button';
        scanBtn.style.margin = '0 10px';
        scanBtn.style.padding = '5px 15px';
        scanBtn.style.background = '#417690';
        scanBtn.style.color = 'white';
        scanBtn.style.border = 'none';
        scanBtn.style.borderRadius = '4px';
        scanBtn.style.cursor = 'pointer';

        // إنشاء مكان عرض الكاميرا
        const readerDiv = document.createElement('div');
        readerDiv.id = 'barcode-reader';
        readerDiv.style.width = '300px';
        readerDiv.style.marginTop = '10px';
        readerDiv.style.display = 'none';

        // وضع الزرار والـ div جنب الخانة
        barcodeInput.parentNode.insertBefore(scanBtn, barcodeInput.nextSibling);
        barcodeInput.parentNode.appendChild(readerDiv);

        let html5QrcodeScanner;

        scanBtn.onclick = function() {
            if (readerDiv.style.display === 'none') {
                readerDiv.style.display = 'block';
                html5QrcodeScanner = new Html5QrcodeScanner("barcode-reader", { fps: 10, qrbox: 250 });
                html5QrcodeScanner.render((decodedText) => {
                    barcodeInput.value = decodedText;
                    html5QrcodeScanner.clear();
                    readerDiv.style.display = 'none';
                });
            } else {
                html5QrcodeScanner.clear();
                readerDiv.style.display = 'none';
            }
        };
    }
});

