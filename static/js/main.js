/* ═══════════════════════════════════
   Apple Leaf Disease Detection — JS
   ═══════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

    // ── MOBILE NAV TOGGLE ──
    const navToggle = document.getElementById('navToggle');
    const navMobile = document.getElementById('navMobile');
    if (navToggle && navMobile) {
        navToggle.addEventListener('click', () => {
            navMobile.classList.toggle('open');
        });
    }

    // ── DRAG & DROP UPLOAD ──
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const dropIdle = document.getElementById('dropIdle');
    const dropPreview = document.getElementById('dropPreview');
    const previewImg = document.getElementById('previewImg');
    const previewName = document.getElementById('previewName');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = analyzeBtn?.querySelector('.btn-text');
    const uploadForm = document.getElementById('uploadForm');
    const btnLoader = document.getElementById('btnLoader');

    if (!dropZone) return;

    // Click to browse
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag events
    ['dragenter', 'dragover'].forEach(evt => {
        dropZone.addEventListener(evt, e => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'dragend'].forEach(evt => {
        dropZone.addEventListener(evt, () => {
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && isValidImage(file)) {
            setFile(file);
        } else {
            showToast('Please upload a valid image (JPG, PNG, WEBP)', 'error');
        }
    });

    // File input change
    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file && isValidImage(file)) {
            setFile(file);
        }
    });

    function isValidImage(file) {
        return ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'].includes(file.type);
    }

    function setFile(file) {
        const reader = new FileReader();
        reader.onload = e => {
            previewImg.src = e.target.result;
            previewName.textContent = file.name;
            dropIdle.style.display = 'none';
            dropPreview.style.display = 'block';

            // Enable button
            analyzeBtn.classList.add('ready');
            analyzeBtn.disabled = false;
            btnText.textContent = 'Analyze Leaf Disease';
        };
        reader.readAsDataURL(file);
    }

    // Form submit — show loader
    if (uploadForm) {
        uploadForm.addEventListener('submit', e => {
            if (!fileInput.files[0]) {
                e.preventDefault();
                showToast('Please select an image first', 'error');
                return;
            }
            // Show loading state
            const btnTextEl = analyzeBtn.querySelector('.btn-text');
            const btnIconEl = analyzeBtn.querySelector('.btn-icon');
            if (btnTextEl) btnTextEl.style.display = 'none';
            if (btnIconEl) btnIconEl.style.display = 'none';
            if (btnLoader) btnLoader.style.display = 'flex';
            analyzeBtn.disabled = true;
            analyzeBtn.style.cursor = 'not-allowed';
        });
    }

    // ── ANIMATE BARS ON PAGE LOAD ──
    setTimeout(() => {
        document.querySelectorAll('.dc-bar').forEach(bar => {
            const w = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.transition = 'width 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)';
                bar.style.width = w;
            }, 100);
        });

        document.querySelectorAll('.hc-conf-bar').forEach(bar => {
            const w = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.transition = 'width 0.9s ease';
                bar.style.width = w;
            }, 200);
        });

        document.querySelectorAll('.hpm-bar').forEach(bar => {
            const w = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.transition = 'width 0.7s ease';
                bar.style.width = w;
            }, 300);
        });

        document.querySelectorAll('.bc-bar').forEach(bar => {
            const w = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.transition = 'width 1s ease';
                bar.style.width = w;
            }, 200);
        });
    }, 100);

    // ── TOAST NOTIFICATIONS ──
    function showToast(message, type = 'info') {
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        Object.assign(toast.style, {
            position: 'fixed',
            bottom: '24px', right: '24px',
            padding: '12px 20px',
            background: type === 'error' ? '#1F0F0F' : '#0F1F10',
            border: `1px solid ${type === 'error' ? '#EF444440' : '#22C55E40'}`,
            color: type === 'error' ? '#EF4444' : '#22C55E',
            borderRadius: '10px',
            fontFamily: 'Crimson Pro, serif',
            fontSize: '15px',
            zIndex: '9999',
            boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
            transform: 'translateY(20px)',
            opacity: '0',
            transition: 'all 0.3s ease'
        });

        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.transform = 'translateY(0)';
            toast.style.opacity = '1';
        }, 10);

        setTimeout(() => {
            toast.style.transform = 'translateY(20px)';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // ── ENTRANCE ANIMATIONS ──
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.disease-card, .step-item, .kpi-card, .breakdown-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    // ── HISTORY CARD STAGGER ──
    document.querySelectorAll('.history-card').forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(16px)';
        card.style.transition = `opacity 0.4s ease ${i * 0.05}s, transform 0.4s ease ${i * 0.05}s`;
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, i * 50 + 100);
    });

});
