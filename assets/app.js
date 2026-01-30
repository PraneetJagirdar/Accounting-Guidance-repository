
async function loadUpdates(){
  try{
    const res = await fetch('data/amendments.json?_=' + Date.now());
    const data = await res.json();
    const list = document.getElementById('updates-list');
    list.innerHTML = '';
    (data.items||[]).slice(0,30).forEach(item=>{
      const div = document.createElement('div');
      div.className = 'update';
      div.innerHTML = `
        <h4><a target="_blank" href="${item.link}">${item.title}</a></h4>
        <div class="meta">${item.source} • ${item.date}</div>
        ${item.summary ? `<p>${item.summary}</p>`:''}
      `;
      list.appendChild(div);
    });
  }catch(e){
    console.error(e);
    document.getElementById('updates-list').innerHTML = '<p class="note">Could not load updates. Ensure <code>data/amendments.json</code> exists or your server allows static JSON.</p>'
  }
}

document.getElementById('refresh').addEventListener('click', loadUpdates);
window.addEventListener('DOMContentLoaded', loadUpdates);
