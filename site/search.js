(function () {
  var idx = window.SEARCH_INDEX || [];
  for (var n = 0; n < idx.length; n++) idx[n].x = idx[n].raw.toLowerCase();
  var q = document.getElementById('q');
  var box = document.getElementById('results');
  var base = (document.querySelector('link[rel=stylesheet]').getAttribute('href') || '')
               .replace('style.css', '');
  var sel = -1, current = [];

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function score(page, terms) {
    var t = page.t.toLowerCase(), g = (page.g || '').toLowerCase(), x = page.x;
    var total = 0;
    for (var i = 0; i < terms.length; i++) {
      var term = terms[i], s = 0;
      if (t === term) s = 1000;
      else if (t.indexOf(term) === 0) s = 400;
      else if (t.indexOf(term) > -1) s = 200;
      if (g.indexOf(term) > -1) s += 60;
      var at = x.indexOf(term);
      if (at > -1) s += 30;
      if (s === 0) return 0;          // jeder Begriff muss vorkommen
      total += s;
    }
    return total;
  }

  function excerpt(page, term) {
    var at = page.x.indexOf(term);
    if (at < 0) return page.s || '';
    var from = Math.max(0, at - 40);
    return (from > 0 ? '…' : '') + page.raw.substr(from, 120) + '…';
  }

  function render(list, terms) {
    if (!list.length) {
      box.innerHTML = '<div class="empty">Keine Treffer</div>';
      box.hidden = false;
      return;
    }
    box.innerHTML = list.map(function (p, i) {
      return '<a href="' + base + p.u + '" data-i="' + i + '">' +
             '<span class="rt">' + esc(p.t) + '</span>' +
             '<span class="rc">' + esc(p.c) + '</span>' +
             '<span class="rx">' + esc(excerpt(p, terms[0])) + '</span></a>';
    }).join('');
    box.hidden = false;
  }

  function run() {
    var value = q.value.trim().toLowerCase();
    sel = -1;
    if (value.length < 2) { box.hidden = true; return; }
    var terms = value.split(/\s+/);
    var scored = [];
    for (var i = 0; i < idx.length; i++) {
      var s = score(idx[i], terms);
      if (s > 0) scored.push([s, idx[i]]);
    }
    scored.sort(function (a, b) { return b[0] - a[0]; });
    current = scored.slice(0, 25).map(function (p) { return p[1]; });
    render(current, terms);
  }

  function move(delta) {
    var links = box.querySelectorAll('a');
    if (!links.length) return;
    if (sel > -1) links[sel].classList.remove('sel');
    sel = (sel + delta + links.length) % links.length;
    links[sel].classList.add('sel');
    links[sel].scrollIntoView({ block: 'nearest' });
  }

  if (q) {
    q.addEventListener('input', run);
    q.addEventListener('focus', run);
    q.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Enter') {
        var links = box.querySelectorAll('a');
        if (links.length) { e.preventDefault(); (links[sel > -1 ? sel : 0]).click(); }
      } else if (e.key === 'Escape') { box.hidden = true; q.blur(); }
    });
  }

  document.addEventListener('click', function (e) {
    if (box && !box.contains(e.target) && e.target !== q) box.hidden = true;
  });

  document.addEventListener('keydown', function (e) {
    if ((e.key === '/' || (e.key === 'k' && (e.ctrlKey || e.metaKey))) &&
        document.activeElement !== q) {
      e.preventDefault(); q.focus(); q.select();
    }
  });

  var toggle = document.querySelector('.menu-toggle');
  if (toggle) toggle.addEventListener('click', function () {
    document.body.classList.toggle('nav-open');
  });

  var rnd = document.getElementById('random');
  if (rnd) rnd.addEventListener('click', function (e) {
    e.preventDefault();
    if (idx.length) location.href = base + idx[Math.floor(Math.random() * idx.length)].u;
  });
})();
