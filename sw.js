const C="eng2-v1";const F=["./","./index.html","./manifest.json"];
self.addEventListener("install",e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(F)))});
self.addEventListener("fetch",e=>e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request))));
self.addEventListener("periodicsync",e=>{if(e.tag==="daily")e.waitUntil((async()=>{const c=await caches.open("eng-cfg");const r=await c.match("cfg");if(!r)return;const g=await r.json();if(!g.on)return;const d=new Date(),hm=String(d.getHours()).padStart(2,"0")+":"+String(d.getMinutes()).padStart(2,"0");if(hm>=g.time)await self.registration.showNotification("🔔 وقت إنجليزي",{body:g.text,tag:"daily"})})())});
self.addEventListener("notificationclick",e=>{e.notification.close();e.waitUntil(clients.openWindow("./index.html"))});
