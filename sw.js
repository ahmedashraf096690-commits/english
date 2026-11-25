const C="eng2-v3";const F=["./","./index.html","./manifest.json"];
self.addEventListener("install",e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(F)))});
self.addEventListener("activate",e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x.startsWith("eng2-")&&x!==C).map(x=>caches.delete(x)))).then(()=>clients.claim())));
self.addEventListener("fetch",e=>{if(e.request.method!=="GET")return;e.respondWith(caches.open(C).then(c=>c.match(e.request).then(r=>{const f=fetch(e.request).then(n=>{if(n&&n.ok&&e.request.url.startsWith(self.location.origin))c.put(e.request,n.clone());return n}).catch(()=>r);return r||f})))});
self.addEventListener("periodicsync",e=>{if(e.tag==="daily")e.waitUntil((async()=>{const c=await caches.open("eng-cfg");const r=await c.match("cfg");if(!r)return;const g=await r.json();if(!g.on)return;const d=new Date(),hm=String(d.getHours()).padStart(2,"0")+":"+String(d.getMinutes()).padStart(2,"0");if(hm>=g.time)await self.registration.showNotification("🔔 وقت إنجليزي",{body:g.text,tag:"daily"})})())});
self.addEventListener("notificationclick",e=>{e.notification.close();e.waitUntil(clients.openWindow("./index.html"))});
