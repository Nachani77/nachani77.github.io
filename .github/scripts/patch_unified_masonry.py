from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_css = ".archive{padding:3vw;columns:4 260px;column-gap:10px}\n.archive.is-loading{min-height:40vh}\n.archive-tail{padding:0 3vw 3vw}\n.archive-tail-batch{columns:4 260px;column-gap:10px}\n.archive-tail-batch+.archive-tail-batch{margin-top:10px}\n.archive-tail-batch .photo{margin-bottom:10px}\n"
new_css = ".archive{padding:3vw;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;align-items:start}\n.archive.is-loading{min-height:40vh}\n.archive-column{display:flex;flex-direction:column;gap:10px;min-width:0}\n"
if old_css not in s:
    raise SystemExit('desktop gallery CSS anchor not found')
s = s.replace(old_css, new_css, 1)

old_photo = ".photo{display:block;width:100%;margin:0 0 10px;"
if old_photo not in s:
    raise SystemExit('photo CSS anchor not found')
s = s.replace(old_photo, ".photo{display:block;width:100%;margin:0;", 1)

old_mobile = ".archive{padding:16px;columns:2 140px;column-gap:6px}.archive-tail{padding:0 16px 16px}.archive-tail-batch{columns:2 140px;column-gap:6px}.archive-tail-batch+.archive-tail-batch{margin-top:6px}.archive-tail-batch .photo{margin-bottom:6px}.photo{margin-bottom:6px}"
new_mobile = ".archive{padding:16px;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}.archive-column{gap:6px}.photo{margin:0}"
if old_mobile not in s:
    raise SystemExit('mobile gallery CSS anchor not found')
s = s.replace(old_mobile, new_mobile, 1)

pattern = re.compile(r"function renderPhoto\(photo,index,parent=archive\).*?\nrenderInitialArchive\(\);", re.S)
replacement = """const renderedEntries=[];
let galleryColumns=[],galleryColumnCount=0,resizeTimer=null;
function wantedColumnCount(){return window.matchMedia('(max-width:650px)').matches?2:4}
function shortestGalleryColumn(){let best=galleryColumns[0];for(let i=1;i<galleryColumns.length;i++){if(galleryColumns[i].scrollHeight<best.scrollHeight)best=galleryColumns[i]}return best}
function placeEntry(entry){shortestGalleryColumn().appendChild(entry.item)}
function setupGalleryColumns(){galleryColumnCount=wantedColumnCount();archive.replaceChildren();galleryColumns=Array.from({length:galleryColumnCount},()=>{const col=document.createElement('div');col.className='archive-column';archive.appendChild(col);return col});renderedEntries.forEach(placeEntry)}
function renderPhoto(photo,index){const item=document.createElement('div');item.className='photo';const img=document.createElement('img');img.width=photo.w;img.height=photo.h;img.alt='';img.decoding='async';if(index<6){img.loading='eager';img.fetchPriority=index<2?'high':'auto'}else img.loading='lazy';retryImage(img,photos[index],()=>img.classList.add('loaded'));item.appendChild(img);item.addEventListener('click',()=>openLightbox(index));const entry={photo,index,item};renderedEntries.push(entry);placeEntry(entry)}
function renderInitialArchive(){setupGalleryColumns();let tailStart=0;while(tailStart<photoData.length&&photoData[tailStart].w&&photoData[tailStart].h){renderPhoto(photoData[tailStart],tailStart);tailStart++}archive.classList.remove('is-loading');if(tailStart>=photoData.length){archive.setAttribute('aria-busy','false');return}const startTail=()=>hydrateUnknownTail(tailStart).finally(()=>archive.setAttribute('aria-busy','false'));window.addEventListener('load',()=>setTimeout(()=>{'requestIdleCallback'in window?requestIdleCallback(startTail,{timeout:1200}):startTail()},150),{once:true})}
async function hydrateUnknownTail(start){const batchSize=8;for(let i=start;i<photoData.length;i+=batchSize){const batch=[];for(let j=i;j<Math.min(i+batchSize,photoData.length);j++)batch.push({photo:photoData[j],index:j});await Promise.all(batch.map(({photo})=>probeDimensions(photo)));batch.forEach(({photo,index})=>renderPhoto(photo,index));await new Promise(resolve=>requestAnimationFrame(resolve))}}
renderInitialArchive();
window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(wantedColumnCount()!==galleryColumnCount)setupGalleryColumns()},120)},{passive:true});"""
s2, n = pattern.subn(replacement, s, count=1)
if n != 1:
    raise SystemExit(f'gallery JS anchor count: {n}')

p.write_text(s2, encoding='utf-8')
