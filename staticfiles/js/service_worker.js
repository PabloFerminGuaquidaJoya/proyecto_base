// static/js/sw.js - Service Worker
const CACHE_NAME = 'sena-maquinaria-v1.0.0';
const urlsToCache = [
    '/',
    '/static/css/bootstrap.min.css',
    '/static/js/bootstrap.bundle.min.js',
    '/static/js/app.js',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    '/offline/',
    '/manifest.json'
];

// Install event
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Cache opened');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Return cached version or fetch from network
                if (response) {
                    return response;
                }
                
                return fetch(event.request)
                    .then(function(response) {
                        // Check if valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone the response
                        var responseToCache = response.clone();
                        
                        caches.open(CACHE_NAME)
                            .then(function(cache) {
                                cache.put(event.request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch(function() {
                        // Return offline page for navigation requests
                        if (event.request.mode === 'navigate') {
                            return caches.match('/offline/');
                        }
                        
                        // Return default offline asset
                        if (event.request.destination === 'image') {
                            return caches.match('/static/images/offline-image.svg');
                        }
                    });
            })
    );
});

// Activate event
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Background sync for offline actions
self.addEventListener('sync', function(event) {
    if (event.tag === 'background-sync') {
        event.waitUntil(syncOfflineActions());
    }
});

function syncOfflineActions() {
    return new Promise(function(resolve, reject) {
        // Get offline actions from IndexedDB
        const request = indexedDB.open('sena-offline-actions', 1);
        
        request.onsuccess = function(event) {
            const db = event.target.result;
            const transaction = db.transaction(['actions'], 'readwrite');
            const store = transaction.objectStore('actions');
            
            store.getAll().onsuccess = function(event) {
                const actions = event.target.result;
                
                // Process each offline action
                actions.forEach(function(action) {
                    fetch(action.url, {
                        method: action.method,
                        headers: action.headers,
                        body: action.body
                    })
                    .then(function(response) {
                        if (response.ok) {
                            // Remove successful action from store
                            store.delete(action.id);
                        }
                    })
                    .catch(function(error) {
                        console.error('Sync failed for action:', action, error);
                    });
                });
                
                resolve();
            };
        };
        
        request.onerror = function() {
            reject(new Error('Failed to open IndexedDB'));
        };
    });
}

// Push notifications
self.addEventListener('push', function(event) {
    if (event.data) {
        const data = event.data.json();
        
        const options = {
            body: data.message,
            icon: '/static/icons/icon-192x192.png',
            badge: '/static/icons/badge-72x72.png',
            vibrate: [100, 50, 100],
            data: data,
            actions: [
                {
                    action: 'open',
                    title: 'Abrir',
                    icon: '/static/icons/open.png'
                },
                {
                    action: 'close',
                    title: 'Cerrar',
                    icon: '/static/icons/close.png'
                }
            ]
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

// Notification click
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    if (event.action === 'open') {
        event.waitUntil(
            clients.openWindow(event.notification.data.url || '/')
        );
    }
});

// manifest.json - Web App Manifest
const manifest = {
    "name": "SENA - Sistema de Maquinaria Especializada",
    "short_name": "SENA Maquinaria",
    "description": "Sistema tecnológico integral para monitorización, control y mantenimiento predictivo de maquinaria especializada mediante IA",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#667eea",
    "orientation": "portrait-primary",
    "scope": "/",
    "lang": "es-CO",
    "dir": "ltr",
    "categories": ["productivity", "education", "utilities"],
    "screenshots": [
        {
            "src": "/static/screenshots/desktop-1.png",
            "sizes": "1280x720",
            "type": "image/png",
            "form_factor": "wide",
            "label": "Dashboard Principal"
        },
        {
            "src": "/static/screenshots/mobile-1.png",
            "sizes": "390x844",
            "type": "image/png",
            "form_factor": "narrow",
            "label": "Vista Móvil"
        }
    ],
    "icons": [
        {
            "src": "/static/icons/icon-72x72.png",
            "sizes": "72x72",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-96x96.png",
            "sizes": "96x96",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-128x128.png",
            "sizes": "128x128",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-144x144.png",
            "sizes": "144x144",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-152x152.png",
            "sizes": "152x152",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-192x192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable"
        },
        {
            "src": "/static/icons/icon-384x384.png",
            "sizes": "384x384",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable"
        }
    ],
    "shortcuts": [
        {
            "name": "Nueva Máquina",
            "short_name": "Nueva",
            "description": "Registrar una nueva máquina",
            "url": "/maquinaria/crear/",
            "icons": [
                {
                    "src": "/static/icons/shortcut-add.png",
                    "sizes": "96x96"
                }
            ]
        },
        {
            "name": "Mantenimiento",
            "short_name": "Mantenimiento",
            "description": "Centro de mantenimiento",
            "url": "/mantenimiento/",
            "icons": [
                {
                    "src": "/static/icons/shortcut-maintenance.png",
                    "sizes": "96x96"
                }
            ]
        },
        {
            "name": "Asistente IA",
            "short_name": "IA",
            "description": "Consultar con el asistente de IA",
            "url": "/ia/",
            "icons": [
                {
                    "src": "/static/icons/shortcut-ai.png",
                    "sizes": "96x96"
                }
            ]
        }
    ],
    "related_applications": [],
    "prefer_related_applications": false
};

// static/js/app.js - Main Application JavaScript
class SENAApp {
    constructor() {
        this.isOnline = navigator.onLine;
        this.offlineActions = [];
        this.init();
    }
    
    init() {
        this.registerServiceWorker();
        this.setupOfflineSupport();
        this.setupPushNotifications();
        this.setupAppShortcuts();
        this.setupPerformanceOptimizations();
        this.setupAccessibility();
    }
    
    registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js')
                    .then((registration) => {
                        console.log('SW registered: ', registration);
                        
                        // Check for updates
                        registration.addEventListener('updatefound', () => {
                            const newWorker = registration.installing;
                            newWorker.addEventListener('statechange', () => {
                                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                                    this.showUpdateAvailable();
                                }
                            });
                        });
                    })
                    .catch((registrationError) => {
                        console.log('SW registration failed: ', registrationError);
                    });
            });
        }
    }
    
    setupOfflineSupport() {
        // Listen for online/offline events
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.syncOfflineActions();
            this.hideOfflineIndicator();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showOfflineIndicator();
        });
        
        // Intercept form submissions when offline
        document.addEventListener('submit', (e) => {
            if (!this.isOnline) {
                e.preventDefault();
                this.handleOfflineSubmission(e.target);
            }
        });
        
        // Initialize IndexedDB for offline storage
        this.initOfflineDB();
    }
    
    initOfflineDB() {
        const request = indexedDB.open('sena-offline-actions', 1);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            const store = db.createObjectStore('actions', { keyPath: 'id', autoIncrement: true });
            store.createIndex('timestamp', 'timestamp', { unique: false });
        };
        
        request.onsuccess = (event) => {
            this.offlineDB = event.target.result;
        };
    }
    
    handleOfflineSubmission(form) {
        const formData = new FormData(form);
        const action = {
            id: Date.now(),
            url: form.action,
            method: form.method || 'POST',
            data: Object.fromEntries(formData),
            timestamp: new Date().toISOString()
        };
        
        // Store in IndexedDB
        if (this.offlineDB) {
            const transaction = this.offlineDB.transaction(['actions'], 'readwrite');
            const store = transaction.objectStore('actions');
            store.add(action);
        }
        
        // Show user feedback
        if (typeof showInfo !== 'undefined') {
            showInfo(
                'Acción Guardada',
                'Tu acción se enviará cuando tengas conexión a internet',
                { duration: 5000 }
            );
        }
    }
    
    syncOfflineActions() {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            navigator.serviceWorker.ready.then((registration) => {
                return registration.sync.register('background-sync');
            });
        }
    }
    
    setupPushNotifications() {
        if ('Notification' in window && 'serviceWorker' in navigator && 'PushManager' in window) {
            // Request permission
            Notification.requestPermission().then((permission) => {
                if (permission === 'granted') {
                    this.subscribeForPushNotifications();
                }
            });
        }
    }
    
    subscribeForPushNotifications() {
        navigator.serviceWorker.ready.then((registration) => {
            const applicationServerKey = 'YOUR_VAPID_PUBLIC_KEY'; // Replace with actual VAPID key
            
            registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(applicationServerKey)
            }).then((subscription) => {
                // Send subscription to server
                fetch('/api/push-subscription/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(subscription)
                });
            });
        });
    }
    
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }
    
    setupAppShortcuts() {
        // Handle app shortcuts
        if ('getInstalledRelatedApps' in navigator) {
            navigator.getInstalledRelatedApps().then((relatedApps) => {
                if (relatedApps.length === 0) {
                    this.showInstallPrompt();
                }
            });
        }
        
        // Handle keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'k':
                        e.preventDefault();
                        this.openGlobalSearch();
                        break;
                    case 'n':
                        e.preventDefault();
                        this.openNewMachineForm();
                        break;
                    case 'h':
                        e.preventDefault();
                        this.showKeyboardShortcuts();
                        break;
                }
            }
        });
    }
    
    setupPerformanceOptimizations() {
        // Lazy loading for images
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
        
        // Preload critical resources
        this.preloadCriticalResources();
        
        // Setup performance monitoring
        this.setupPerformanceMonitoring();
    }
    
    preloadCriticalResources() {
        const criticalResources = [
            '/static/css/app.css',
            '/static/js/notifications.js',
            '/api/user/preferences/'
        ];
        
        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = resource;
            document.head.appendChild(link);
        });
    }
    
    setupPerformanceMonitoring() {
        if ('PerformanceObserver' in window) {
            // Monitor First Contentful Paint
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    if (entry.name === 'first-contentful-paint') {
                        console.log('FCP:', entry.startTime);
                        // Send to analytics
                        this.trackPerformance('fcp', entry.startTime);
                    }
                });
            });
            
            observer.observe({ entryTypes: ['paint'] });
        }
        
        // Monitor Long Tasks
        if ('PerformanceObserver' in window) {
            const longTaskObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    console.warn('Long task detected:', entry.duration);
                    this.trackPerformance('long-task', entry.duration);
                });
            });
            
            try {
                longTaskObserver.observe({ entryTypes: ['longtask'] });
            } catch (e) {
                console.log('Long task monitoring not supported');
            }
        }
    }
    
    setupAccessibility() {
        // High contrast mode detection
        if (window.matchMedia) {
            const prefersHighContrast = window.matchMedia('(prefers-contrast: high)');
            if (prefersHighContrast.matches) {
                document.body.classList.add('high-contrast');
            }
            
            prefersHighContrast.addEventListener('change', (e) => {
                if (e.matches) {
                    document.body.classList.add('high-contrast');
                } else {
                    document.body.classList.remove('high-contrast');
                }
            });
        }
        
        // Reduced motion preference
        if (window.matchMedia) {
            const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
            if (prefersReducedMotion.matches) {
                document.body.classList.add('reduced-motion');
            }
            
            prefersReducedMotion.addEventListener('change', (e) => {
                if (e.matches) {
                    document.body.classList.add('reduced-motion');
                } else {
                    document.body.classList.remove('reduced-motion');
                }
            });
        }
        
        // Focus management
        this.setupFocusManagement();
    }
    
    setupFocusManagement() {
        // Skip links for screen readers
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Saltar al contenido principal';
        skipLink.className = 'skip-link';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: #000;
            color: #fff;
            padding: 8px;
            text-decoration: none;
            z-index: 9999;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // Announce page changes to screen readers
        this.setupPageChangeAnnouncements();
    }
    
    setupPageChangeAnnouncements() {
        // Create live region for announcements
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'live-region';
        document.body.appendChild(liveRegion);
        
        // Announce navigation changes
        window.addEventListener('popstate', () => {
            this.announcePageChange();
        });
    }
    
    announcePageChange() {
        const liveRegion = document.getElementById('live-region');
        const pageTitle = document.title;
        if (liveRegion) {
            liveRegion.textContent = `Navegado a ${pageTitle}`;
        }
    }
    
    // Utility methods
    showUpdateAvailable() {
        if (typeof showInfo !== 'undefined') {
            showInfo(
                'Actualización Disponible',
                'Una nueva versión está disponible. Recarga la página para actualizar.',
                {
                    persistent: true,
                    actions: [
                        {
                            text: 'Recargar',
                            type: 'primary',
                            action: 'reload'
                        }
                    ],
                    onAction: (action) => {
                        if (action === 'reload') {
                            window.location.reload();
                        }
                    }
                }
            );
        }
    }
    
    showOfflineIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'offline-indicator';
        indicator.className = 'alert alert-warning fixed-top text-center';
        indicator.style.zIndex = '1070';
        indicator.innerHTML = `
            <i class="bi bi-wifi-off me-2"></i>
            Sin conexión - Trabajando en modo offline
        `;
        document.body.appendChild(indicator);
    }
    
    hideOfflineIndicator() {
        const indicator = document.getElementById('offline-indicator');
        if (indicator) {
            indicator.remove();
        }
        
        if (typeof showSuccess !== 'undefined') {
            showSuccess('Conexión Restaurada', 'Ya tienes acceso a internet');
        }
    }
    
    showInstallPrompt() {
        // This would be called when the beforeinstallprompt event is fired
        if (typeof showInfo !== 'undefined') {
            showInfo(
                '📱 Instalar App',
                'Instala SENA Maquinaria en tu dispositivo para un acceso más rápido',
                {
                    actions: [
                        {
                            text: 'Instalar',
                            type: 'primary',
                            action: 'install'
                        }
                    ]
                }
            );
        }
    }
    
    openGlobalSearch() {
        const searchModal = document.getElementById('globalSearchModal');
        if (searchModal) {
            new bootstrap.Modal(searchModal).show();
        } else {
            // Create search modal if it doesn't exist
            this.createGlobalSearchModal();
        }
    }
    
    createGlobalSearchModal() {
        const modal = document.createElement('div');
        modal.id = 'globalSearchModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">🔍 Búsqueda Global</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <input type="text" class="form-control mb-3" placeholder="Buscar máquinas, órdenes, documentos..." id="globalSearchInput">
                        <div id="searchResults">
                            <div class="text-center text-muted">
                                <i class="bi bi-search fs-3"></i>
                                <p>Escribe para buscar en todo el sistema</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Setup search functionality
        const searchInput = document.getElementById('globalSearchInput');
        let searchTimeout;
        
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.performGlobalSearch(searchInput.value);
            }, 300);
        });
        
        new bootstrap.Modal(modal).show();
    }
    
    performGlobalSearch(query) {
        if (!query.trim()) return;
        
        const resultsContainer = document.getElementById('searchResults');
        resultsContainer.innerHTML = '<div class="text-center"><i class="bi bi-hourglass-split"></i> Buscando...</div>';
        
        fetch(`/api/search/?q=${encodeURIComponent(query)}`, {
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            this.displaySearchResults(data);
        })
        .catch(error => {
            resultsContainer.innerHTML = '<div class="alert alert-danger">Error en la búsqueda</div>';
        });
    }
    
    displaySearchResults(results) {
        const resultsContainer = document.getElementById('searchResults');
        
        if (!results.machines && !results.orders && !results.documents) {
            resultsContainer.innerHTML = '<div class="text-center text-muted">No se encontraron resultados</div>';
            return;
        }
        
        let html = '';
        
        if (results.machines && results.machines.length > 0) {
            html += '<h6>Máquinas</h6>';
            results.machines.forEach(machine => {
                html += `
                    <div class="list-group-item list-group-item-action">
                        <div class="d-flex align-items-center">
                            <i class="bi bi-gear me-3 text-primary"></i>
                            <div>
                                <strong>${machine.codigo_inventario}</strong> - ${machine.nombre}
                                <br><small class="text-muted">${machine.ubicacion}</small>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
        
        resultsContainer.innerHTML = html;
    }
    
    openNewMachineForm() {
        window.location.href = '/maquinaria/crear/';
    }
    
    showKeyboardShortcuts() {
        const shortcuts = [
            { key: 'Ctrl/Cmd + K', action: 'Búsqueda global' },
            { key: 'Ctrl/Cmd + N', action: 'Nueva máquina' },
            { key: 'Ctrl/Cmd + H', action: 'Mostrar atajos' },
            { key: 'Esc', action: 'Cerrar modales' }
        ];
        
        let shortcutsHtml = '<h6>⌨️ Atajos de Teclado</h6><div class="list-group">';
        shortcuts.forEach(shortcut => {
            shortcutsHtml += `
                <div class="list-group-item d-flex justify-content-between">
                    <span>${shortcut.action}</span>
                    <kbd>${shortcut.key}</kbd>
                </div>
            `;
        });
        shortcutsHtml += '</div>';
        
        if (typeof showInfo !== 'undefined') {
            showInfo('Atajos de Teclado', shortcutsHtml, { duration: 8000 });
        }
    }
    
    trackPerformance(metric, value) {
        // Send performance metrics to analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', 'performance', {
                metric_name: metric,
                metric_value: value
            });
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.senaApp = new SENAApp();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SENAApp;
}