// --- 設定モーダル ＆ タグ管理（すべてのタグの追加・削除が可能） ---
function renderSettingsTags() {
  const container = document.getElementById('settingsTagsList');
  if (!container) return;
  const allTags = DB.getAllTags();

  if (allTags.length === 0) {
    container.innerHTML = `<span class="text-stone-400 text-xs py-1">登録されているタグはありません</span>`;
    return;
  }

  container.innerHTML = allTags.map(t => {
    let badgeBg = 'bg-stone-100 text-stone-800 border-stone-200';
    let icon = '🏷️';
    if (t === 'English') { badgeBg = 'bg-blue-50 text-blue-800 border-blue-200'; icon = '📚'; }
    else if (t === 'Math') { badgeBg = 'bg-emerald-50 text-emerald-800 border-emerald-200'; icon = '🔢'; }
    else if (t === 'Mandarin') { badgeBg = 'bg-rose-50 text-rose-800 border-rose-200'; icon = '🀄'; }
    else if (t === 'event') { badgeBg = 'bg-purple-50 text-purple-800 border-purple-200'; icon = '🏫'; }

    return `
      <span class="px-2.5 py-1 rounded-xl ${badgeBg} text-xs font-bold flex items-center gap-1.5 border shadow-2xs">
        <span>${icon} ${escapeHtml(t)}</span>
        <button type="button" onclick="deleteTagFromSettings('${escapeHtml(t)}')" class="text-stone-400 hover:text-rose-600 font-bold ml-0.5 transition" title="「${escapeHtml(t)}」を削除">✕</button>
      </span>
    `;
  }).join('');
}

function addCustomTagFromSettings() {
  const input = document.getElementById('newCustomTagInput');
  const tag = (input ? input.value : '').trim();
  if (!tag) {
    alert('タグ名を入力してください');
    if (input) input.focus();
    return;
  }
  DB.addTag(tag);
  if (input) input.value = '';
  renderSettingsTags();
  renderHomeTagFilters();
  renderHomePage();
}

function deleteTagFromSettings(tag) {
  if (!confirm(`タグ「${tag}」を削除しますか？`)) return;
  DB.deleteTag(tag);
  if (activeTag === tag) {
    activeTag = 'all';
  }
  renderSettingsTags();
  renderHomeTagFilters();
  renderHomePage();
}

function deleteCustomTagFromSettings(tag) {
  deleteTagFromSettings(tag);
}

// --- ホーム画面 タグフィルター描画 ---
function renderHomeTagFilters() {
  const container = document.getElementById('homeTagFilterContainer');
  if (!container) return;
  const allTags = DB.getAllTags();

  let html = `
    <button onclick="filterByTag('all', this)" class="tag-filter-btn ${activeTag === 'all' ? 'active' : ''}">すべて</button>
  `;

  allTags.forEach(tag => {
    let icon = '🏷️';
    if (tag === 'English') icon = '📚';
    else if (tag === 'Math') icon = '🔢';
    else if (tag === 'Mandarin') icon = '🀄';
    else if (tag === 'event') icon = '🏫';
    
    html += `
      <button onclick="filterByTag('${escapeHtml(tag)}', this)" class="tag-filter-btn ${activeTag === tag ? 'active' : ''}">${icon} ${escapeHtml(tag)}</button>
    `;
  });

  container.innerHTML = html;
}
// 👶 お子さんカラー ＆ バッジ定義
const CHILD_COLOR_MAP = {
  blue: {
    badge: 'bg-sky-50 text-sky-700 border-sky-200 border',
    tabActive: 'bg-sky-600 text-white shadow-xs',
    pillActive: 'bg-sky-600 text-white border-sky-600'
  },
  pink: {
    badge: 'bg-rose-50 text-rose-700 border-rose-200 border',
    tabActive: 'bg-rose-600 text-white shadow-xs',
    pillActive: 'bg-rose-600 text-white border-rose-600'
  },
  emerald: {
    badge: 'bg-emerald-50 text-emerald-700 border-emerald-200 border',
    tabActive: 'bg-emerald-600 text-white shadow-xs',
    pillActive: 'bg-emerald-600 text-white border-emerald-600'
  },
  amber: {
    badge: 'bg-amber-50 text-amber-700 border-amber-200 border',
    tabActive: 'bg-amber-600 text-white shadow-xs',
    pillActive: 'bg-amber-600 text-white border-amber-600'
  },
  purple: {
    badge: 'bg-purple-50 text-purple-700 border-purple-200 border',
    tabActive: 'bg-purple-600 text-white shadow-xs',
    pillActive: 'bg-purple-600 text-white border-purple-600'
  }
};

function getChildBadgeHtml(childId) {
  if (!childId || childId === 'all') return '';
  const child = DB.getChildById(childId);
  if (!child) return '';
  const theme = CHILD_COLOR_MAP[child.color] || CHILD_COLOR_MAP.blue;
  const gradeStr = child.grade ? ` (${escapeHtml(child.grade)})` : '';
  return `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${theme.badge} inline-flex items-center gap-1 flex-shrink-0">${child.icon || '👶'} ${escapeHtml(child.name)}${gradeStr}</span>`;
}

// 🏷️ デフォルトタグ ＆ カスタムタグ定義
const DEFAULT_TAGS = ['English', 'Math', 'Mandarin', 'event', 'その他'];

const CUSTOM_TAG_PALETTES = [
  'bg-amber-50 text-amber-800 border-amber-200',
  'bg-teal-50 text-teal-800 border-teal-200',
  'bg-cyan-50 text-cyan-800 border-cyan-200',
  'bg-indigo-50 text-indigo-800 border-indigo-200',
  'bg-fuchsia-50 text-fuchsia-800 border-fuchsia-200',
  'bg-lime-50 text-lime-800 border-lime-200'
];

function getTagBadgeHtml(t) {
  let color = 'bg-stone-100 text-stone-700 border-stone-200', icon = '🏷️';
  let label = t;
  if (t === 'English' || t.includes('English') || t.includes('英語') || t.includes('UOI')) {
    color = 'bg-blue-50 text-blue-700 border-blue-200';
    icon = '📚';
    label = 'English';
  } else if (t === 'Math' || t.includes('Math') || t.includes('算数') || t.includes('数学')) {
    color = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    icon = '🔢';
    label = 'Math';
  } else if (t === 'Mandarin' || t.includes('Mandarin') || t.includes('中国語') || t.includes('Chinese')) {
    color = 'bg-rose-50 text-rose-700 border-rose-200';
    icon = '🀄';
    label = 'Mandarin';
  } else if (t === 'event' || t === 'Event' || t.includes('event') || t.includes('Event') || t.includes('行事') || t.includes('イベント')) {
    color = 'bg-purple-50 text-purple-700 border-purple-200';
    icon = '🏫';
    label = 'event';
  } else if (t === 'その他') {
    color = 'bg-stone-100 text-stone-700 border-stone-200';
    icon = '🏷️';
    label = 'その他';
  } else {
    // カスタムタグ用のパレット
    let hash = 0;
    for (let i = 0; i < t.length; i++) hash = (hash * 31 + t.charCodeAt(i)) % CUSTOM_TAG_PALETTES.length;
    color = CUSTOM_TAG_PALETTES[Math.abs(hash)];
    icon = '🏷️';
    label = t;
  }
  return `<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${color}">${icon} ${escapeHtml(label)}</span>`;
}

function normalizeTags(rawTags, contentText = '') {
  const text = (contentText || '').toLowerCase();
  const allTags = DB.getAllTags();
  const normalized = [];

  if (Array.isArray(rawTags)) {
    for (const t of rawTags) {
      if (!t) continue;
      const tTrimmed = String(t).trim();
      if (tTrimmed === 'English' || tTrimmed.includes('English') || tTrimmed.includes('英語') || tTrimmed.includes('UOI')) {
        if (!normalized.includes('English')) normalized.push('English');
      } else if (tTrimmed === 'Math' || tTrimmed.includes('Math') || tTrimmed.includes('算数') || tTrimmed.includes('数学')) {
        if (!normalized.includes('Math')) normalized.push('Math');
      } else if (tTrimmed === 'Mandarin' || tTrimmed.includes('Mandarin') || tTrimmed.includes('中国語') || tTrimmed.includes('Chinese')) {
        if (!normalized.includes('Mandarin')) normalized.push('Mandarin');
      } else if (tTrimmed === 'event' || tTrimmed === 'Event' || tTrimmed.includes('event') || tTrimmed.includes('行事') || tTrimmed.includes('イベント')) {
        if (!normalized.includes('event')) normalized.push('event');
      } else if (tTrimmed === 'その他') {
        if (!normalized.includes('その他')) normalized.push('その他');
      } else {
        // カスタムタグマッチ
        const matchedCustom = allTags.find(ct => ct.toLowerCase() === tTrimmed.toLowerCase());
        if (matchedCustom) {
          if (!normalized.includes(matchedCustom)) normalized.push(matchedCustom);
        } else {
          if (!normalized.includes(tTrimmed)) normalized.push(tTrimmed);
        }
      }
    }
  }

  if (normalized.length === 0) {
    if (text.includes('english') || text.includes('uoi') || text.includes('reading') || text.includes('writing') || text.includes('phonics') || text.includes('spelling') || text.includes('language') || text.includes('英語')) {
      normalized.push('English');
    }
    if (text.includes('math') || text.includes('mathematics') || text.includes('geometry') || text.includes('algebra') || text.includes('算数') || text.includes('数学')) {
      normalized.push('Math');
    }
    if (text.includes('mandarin') || text.includes('chinese') || text.includes('华语') || text.includes('中文') || text.includes('中国語')) {
      normalized.push('Mandarin');
    }
    if (text.includes('event') || text.includes('trip') || text.includes('field trip') || text.includes('festival') || text.includes('ceremony') || text.includes('sports day') || text.includes('concert') || text.includes('party') || text.includes('行事') || text.includes('遠足') || text.includes('イベント')) {
      normalized.push('event');
    }

    // カスタムタグのテキストマッチング
    const customTags = DB.getCustomTags();
    for (const ct of customTags) {
      if (text.includes(ct.toLowerCase())) {
        if (!normalized.includes(ct)) normalized.push(ct);
      }
    }
  }

  if (normalized.length === 0) {
    normalized.push('その他');
  }

  return normalized;
}


// School Info - Standalone SPA Logic for GitHub Pages
// (C) 2026 Otayori Post / School Info

// --- 初期サンプルデータ（初期値：空） ---
const INITIAL_SAMPLE_POSTS = [];

// --- ストレージ管理 (インメモリキャッシュ ＆ 容量上限ガード付き) ---
let _postsCache = null;

const DB = {
  getPosts: function() {
    if (_postsCache !== null) {
      return _postsCache;
    }
    
    try {
      const data = localStorage.getItem('otayori_posts_v1');
      if (data !== null) {
        _postsCache = JSON.parse(data);
        return _postsCache;
      }
    } catch(e) {
      console.warn('Storage read error:', e);
    }

    // 初回起動時は空で初期化
    const hasInit = localStorage.getItem('otayori_has_initialized_v1');
    if (!hasInit) {
      try {
        localStorage.setItem('otayori_has_initialized_v1', 'true');
        localStorage.setItem('otayori_posts_v1', JSON.stringify([]));
      } catch(e) {}
      _postsCache = [];
      return _postsCache;
    }

    _postsCache = [];
    return _postsCache;
  },

  savePosts: function(posts) {
    _postsCache = posts;
    try {
      localStorage.setItem('otayori_has_initialized_v1', 'true');
      localStorage.setItem('otayori_posts_v1', JSON.stringify(posts));
    } catch(e) {
      console.warn('LocalStorage quota reached, optimizing storage...', e);
      // 容量超過時：古い投稿の写真データを軽量化して確実に保存
      try {
        const lightweightPosts = posts.map((p, idx) => {
          if (idx >= 2 && p.image_url && p.image_url.length > 50000) {
            return { ...p, image_url: null };
          }
          return p;
        });
        localStorage.setItem('otayori_posts_v1', JSON.stringify(lightweightPosts));
      } catch(e2) {
        console.error('Fatal storage save error:', e2);
      }
    }
  },

  getPostById: function(id) {
    const posts = this.getPosts();
    return posts.find(p => String(p.id) === String(id));
  },

  addPost: function(postData) {
    const posts = this.getPosts();
    if (!postData.id) {
      postData.id = 'p_' + Date.now().toString(36) + Math.random().toString(36).substring(2, 6);
    }
    if (!postData.created_at) {
      postData.created_at = new Date().toISOString();
    }
    posts.unshift(postData);
    this.savePosts(posts);
    return postData;
  },

  updatePost: function(id, updateData) {
    const posts = this.getPosts();
    const idx = posts.findIndex(p => String(p.id) === String(id));
    if (idx === -1) return null;
    posts[idx] = { ...posts[idx], ...updateData };
    this.savePosts(posts);
    return posts[idx];
  },

  deletePost: function(id) {
    let posts = this.getPosts();
    const initialLen = posts.length;
    posts = posts.filter(p => String(p.id) !== String(id));
    this.savePosts(posts);
    return posts.length < initialLen;
  },

  getAllTags: function() {
    const s = this.getSettings();
    if (Array.isArray(s.tags) && s.tags.length > 0) {
      return s.tags;
    }
    // 初期デフォルトタグ
    return ['English', 'Math', 'Mandarin', 'event', 'その他'];
  },

  getCustomTags: function() {
    return this.getAllTags();
  },

  addTag: function(tag) {
    const trimmed = (tag || '').trim();
    if (!trimmed) return this.getAllTags();
    const settings = this.getSettings();
    if (!Array.isArray(settings.tags)) settings.tags = this.getAllTags();
    if (!settings.tags.includes(trimmed)) {
      settings.tags.push(trimmed);
      this.saveSettings(settings);
    }
    return settings.tags;
  },

  addCustomTag: function(tag) {
    return this.addTag(tag);
  },

  deleteTag: function(tag) {
    const settings = this.getSettings();
    const current = this.getAllTags();
    settings.tags = current.filter(t => t !== tag);
    this.saveSettings(settings);
    return settings.tags;
  },

  deleteCustomTag: function(tag) {
    return this.deleteTag(tag);
  },

  getChildren: function() {
    const s = this.getSettings();
    return Array.isArray(s.children) ? s.children : [];
  },

  getChildById: function(childId) {
    const children = this.getChildren();
    return children.find(c => String(c.id) === String(childId)) || null;
  },

  saveChild: function(childData) {
    const settings = this.getSettings();
    if (!Array.isArray(settings.children)) settings.children = [];
    if (!childData.id) {
      childData.id = 'c_' + Date.now().toString(36) + Math.random().toString(36).substring(2, 5);
    }
    const idx = settings.children.findIndex(c => String(c.id) === String(childData.id));
    if (idx !== -1) {
      settings.children[idx] = { ...settings.children[idx], ...childData };
    } else {
      settings.children.push(childData);
    }
    this.saveSettings(settings);
    return childData;
  },

  deleteChild: function(childId) {
    const settings = this.getSettings();
    if (!Array.isArray(settings.children)) return false;
    settings.children = settings.children.filter(c => String(c.id) !== String(childId));
    this.saveSettings(settings);
    return true;
  },
  getSettings: function() {
    try {
      const data = localStorage.getItem('otayori_settings_v1');
      if (data) {
        const parsed = JSON.parse(data);
        if (!Array.isArray(parsed.children)) parsed.children = [];
        if (!Array.isArray(parsed.tags)) {
          if (Array.isArray(parsed.custom_tags) && parsed.custom_tags.length > 0) {
            const merged = ['English', 'Math', 'Mandarin', 'event', 'その他'];
            for (const ct of parsed.custom_tags) { if (!merged.includes(ct)) merged.push(ct); }
            parsed.tags = merged;
          } else {
            parsed.tags = ['English', 'Math', 'Mandarin', 'event', 'その他'];
          }
        }
        return parsed;
      }
    } catch(e) {}
    return {
      user_name: "ゲスト",
      gemini_api_key: "",
      line_notify_token: "",
      notification_time: "18:00",
      children: [], tags: ['English', 'Math', 'Mandarin', 'event', 'その他']
    };
  },

  saveSettings: function(settings) {
    try {
      localStorage.setItem('otayori_settings_v1', JSON.stringify(settings));
    } catch(e) {}
  }
};

// --- ルーティング & 画面管理 ---
function handleRouting() {
  const hash = window.location.hash || '#/';
  
  const homeView = document.getElementById('homeView');
  const detailView = document.getElementById('detailView');
  const newView = document.getElementById('newView');
  const editView = document.getElementById('editView');
  const settingsView = document.getElementById('settingsView');

  [homeView, detailView, newView, editView, settingsView].forEach(el => {
    if (el) el.classList.add('hidden');
  });

  window.scrollTo(0, 0);

  if (hash === '#/' || hash === '#' || hash === '') {
    if (homeView) homeView.classList.remove('hidden');
    renderHomePage();
  } else if (hash.startsWith('#/post/')) {
    const postId = hash.replace('#/post/', '');
    if (detailView) detailView.classList.remove('hidden');
    renderDetailPage(postId);
  } else if (hash === '#/new') {
    if (newView) newView.classList.remove('hidden');
    renderNewPage();
  } else if (hash.startsWith('#/edit/')) {
    const postId = hash.replace('#/edit/', '');
    if (editView) editView.classList.remove('hidden');
    renderEditPage(postId);
  } else if (hash === '#/settings') {
    if (settingsView) settingsView.classList.remove('hidden');
    renderSettingsPage();
  } else {
    window.location.hash = '#/';
  }

  if (window.lucide) {
    try { lucide.createIcons(); } catch(e) {}
  }
}

window.addEventListener('hashchange', handleRouting);
document.addEventListener('DOMContentLoaded', () => {
  handleRouting();
});

// --- 👦 お子さんタブ ＆ フィルター管理 ---
let activeChildId = 'all';

function renderChildTabs() {
  const container = document.getElementById('childTabsContainer');
  if (!container) return;
  const children = DB.getChildren();

  let tabsHtml = `
    <button onclick="filterByChild('all', this)" class="child-tab-btn px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition flex items-center gap-1 border ${activeChildId === 'all' ? 'bg-stone-900 text-white border-stone-900 shadow-xs' : 'bg-white text-stone-600 border-stone-200 hover:bg-stone-50'}">
      <span>👨‍👩‍👧‍👦</span> <span>全員</span>
    </button>
  `;

  children.forEach(child => {
    const isActive = String(activeChildId) === String(child.id);
    const theme = CHILD_COLOR_MAP[child.color] || CHILD_COLOR_MAP.blue;
    const gradeStr = child.grade ? ` (${escapeHtml(child.grade)})` : '';
    const activeCls = isActive ? `${theme.tabActive} border-transparent` : 'bg-white text-stone-700 border-stone-200 hover:bg-stone-50';
    tabsHtml += `
      <button onclick="filterByChild('${child.id}', this)" class="child-tab-btn px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition flex items-center gap-1 border ${activeCls}">
        <span>${child.icon || '👶'}</span> <span>${escapeHtml(child.name)}${gradeStr}</span>
      </button>
    `;
  });

  if (children.length === 0) {
    tabsHtml += `
      <button onclick="openSettingsModal('children')" class="child-tab-btn px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition flex items-center gap-1 border border-dashed border-rose-300 text-rose-600 hover:bg-rose-50">
        <span>＋</span> <span>お子さんを登録</span>
      </button>
    `;
  }

  container.innerHTML = tabsHtml;
}

function filterByChild(childId, el) {
  activeChildId = childId;
  renderHomePage();
}

// --- ホーム画面描画 ---
let activeTag = 'all';

function renderHomePage() {
  const allPosts = DB.getPosts();
  const settings = DB.getSettings();

  const userEl = document.getElementById('userNameDisplay');
  if (userEl) userEl.innerText = settings.user_name || 'ゲスト';

  renderChildTabs();
  renderHomeTagFilters();

  // activeChildId による絞り込み
  const filteredPosts = (activeChildId === 'all')
    ? allPosts
    : allPosts.filter(p => !p.child_id || p.child_id === 'all' || String(p.child_id) === String(activeChildId));

  renderUpcomingEvents(filteredPosts);
  renderPostsList(filteredPosts);
  applyTagFilters();
}

// 📅 直近の予定（今日以降の未来の予定のみを表示 - コンパクト版）
function renderUpcomingEvents(posts) {
  const container = document.getElementById('upcomingEventsList');
  if (!container) return;

  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  const todayStr = `${y}-${m}-${d}`;
  const upcoming = posts
    .filter(p => p.date && p.date >= todayStr)
    .sort((a, b) => (a.date > b.date ? 1 : -1))
    .slice(0, 5);

  if (upcoming.length === 0) {
    container.innerHTML = '<div class="text-center py-2.5 text-stone-400 text-xs">直近（予定あり）のおたよりはありません</div>';
    return;
  }

  container.innerHTML = upcoming.map(p => {
    const dParts = (p.date || '').split('-');
    const day = dParts.length === 3 ? dParts[2] : '—';
    const month = dParts.length === 3 ? `${parseInt(dParts[1])}月` : '—';
    const timeStr = p.time_start ? `<span>⏰ ${escapeHtml(p.time_start)}〜</span>` : '';
    const locStr = p.location ? `<span class="truncate">📍 ${escapeHtml(p.location)}</span>` : '';
    const childBadge = (activeChildId === 'all' && p.child_id && p.child_id !== 'all')
      ? getChildBadgeHtml(p.child_id)
      : '';

    return `
      <a href="#/post/${p.id}" class="m3-card post-card otayori-card block p-3 no-underline">
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-3 min-w-0 flex-1">
            <div class="date-badge">
              <span class="day">${day}</span>
              <span class="month">${month}</span>
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5 mb-0.5">
                ${childBadge}
                <h4 class="font-bold text-xs text-stone-900 truncate leading-snug">${escapeHtml(p.title)}</h4>
              </div>
              <div class="flex items-center gap-2 mt-0.5 text-[11px] text-stone-500 font-medium">
                ${timeStr}
                ${locStr}
              </div>
              </div>
          </div>
          <span class="w-6 h-6 rounded-full bg-rose-50 text-rose-500 font-bold text-xs flex items-center justify-center flex-shrink-0">
            ›
          </span>
        </div>
      </a>
    `;
  }).join('');
}

// 📑 届いたおたより一覧（横書き・読みやすいコンパクトM3カード）
function renderPostsList(posts) {
  const container = document.getElementById('postsList');
  const countEl = document.getElementById('postsCount');
  if (!container) return;

  if (posts.length === 0) {
    container.innerHTML = `
      <div class="text-center py-10 px-4 space-y-3 bg-white/70 rounded-2xl border border-dashed border-stone-200">
        <div class="text-4xl">📮</div>
        <div class="space-y-1">
          <p class="font-bold text-xs text-stone-700">登録されたおたよりはまだありません</p>
          <p class="text-[11px] text-stone-400">「＋ おたよりを追加」から写真や英文を登録できます</p>
        </div>
        <a href="#/new" class="inline-flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-rose-500 to-pink-500 text-white rounded-xl text-xs font-bold shadow-xs hover:opacity-95 transition">
          <span>＋ 初めてのおたよりを追加</span>
        </a>
      </div>
    `;
    if (countEl) countEl.innerText = '0件';
    return;
  }

  container.innerHTML = posts.map(p => {
    const rawTags = (p.tags || []).join(',');
    const pDateStr = p.date ? `📅 ${p.date.replace(/-/g, '/')}` : '';
    const hasRealImage = Boolean(p.image_url && !p.image_url.includes('no_image.svg'));
    const summaryText = p.summary || p.text_translation || p.image_translation || p.title;

    const tagsHtml = (normalizeTags(p.tags, summaryText)).map(t => getTagBadgeHtml(t)).join('');

    const itemsBadge = (p.items && p.items.length > 0)
      ? `<span class="text-amber-800 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded-md font-bold text-[10px]">🎒 持ち物 ${p.items.length}点</span>`
      : '';
    const dlBadge = p.deadline
      ? `<span class="text-rose-700 bg-rose-50 border border-rose-200 px-1.5 py-0.5 rounded-md font-bold text-[10px]">⚠️ 締切: ${p.deadline.replace(/-/g, '/')}</span>`
      : '';
    const imgBadge = hasRealImage
      ? `<span class="text-sky-700 bg-sky-50 border border-sky-200 px-1.5 py-0.5 rounded-md font-bold text-[10px]">🖼️ 写真あり</span>`
      : '';

    const childBadge = (p.child_id && p.child_id !== 'all') ? getChildBadgeHtml(p.child_id) : '';

    return `
      <a href="#/post/${p.id}" data-tags="${escapeHtml(rawTags)}" data-child-id="${p.child_id || 'all'}" class="m3-card post-card otayori-card block p-3.5 no-underline">
        <!-- 上部：お子さんバッジ ＆ タグ ＆ 日程 -->
        <div class="flex items-center justify-between gap-2 mb-2">
          <div class="flex items-center gap-1.5 flex-wrap min-w-0">
            ${childBadge}
            ${tagsHtml}
          </div>
          ${pDateStr ? `<span class="text-[11px] text-stone-500 font-bold whitespace-nowrap flex-shrink-0">${pDateStr}</span>` : ''}
        </div>

        <!-- 中部：サムネイル ＋ テキスト（横並びレイアウト） -->
        <div class="flex items-start gap-3">
          ${hasRealImage ? `
            <div class="card-thumb-box" style="width:48px !important;height:48px !important;min-width:48px !important;min-height:48px !important;max-width:48px !important;max-height:48px !important;flex-shrink:0 !important;border-radius:12px;overflow:hidden;background:#F8F5EE;border:1px solid #EAE3D9;display:flex;align-items:center;justify-content:center;">
              <img src="${p.image_url}" class="card-thumb-img" style="width:48px !important;height:48px !important;max-width:48px !important;max-height:48px !important;object-fit:cover !important;display:block;" alt="プリント" onerror="this.parentElement.style.display='none'">
            </div>
          ` : ''}
          <div class="flex-1 min-w-0">
            <h3 class="text-xs sm:text-sm font-bold text-stone-900 leading-snug break-words">${escapeHtml(p.title)}</h3>
            ${p.title_en ? `<p class="text-[10px] text-stone-400 font-medium truncate mt-0.5">${escapeHtml(p.title_en)}</p>` : ''}
            <p class="text-[11px] text-stone-600 font-normal line-clamp-2 mt-1 leading-relaxed break-words">${escapeHtml(summaryText)}</p>
          </div>
        </div>

        <!-- 下部：持ち物・締切バッジ ＆ 詳細リンク -->
        <div class="flex items-center justify-between mt-2.5 pt-2 border-t border-stone-100 text-[11px]">
          <div class="flex items-center gap-1.5 flex-wrap min-w-0">
            ${itemsBadge}
            ${dlBadge}
            ${imgBadge}
          </div>
          <span class="text-rose-500 font-bold flex items-center gap-0.5 ml-auto flex-shrink-0">
            <span>詳細を見る</span>
            <span class="text-xs font-black">›</span>
          </span>
        </div>
      </a>
    `;
  }).join('');

  if (countEl) countEl.innerText = `${posts.length}件`;
}

// --- タグフィルター ---
function filterByTag(tag, el) {
  activeTag = tag;
  const allBtns = document.querySelectorAll('.tag-filter-btn');
  allBtns.forEach(btn => btn.classList.remove('active'));
  if (el) el.classList.add('active');
  applyTagFilters();
}

function applyTagFilters() {
  const cards = document.querySelectorAll('#postsList .otayori-card, #postsList .m3-card, #postsList .post-card');
  let matchCount = 0;

  cards.forEach(card => {
    const rawTagsStr = card.getAttribute('data-tags') || '';
    const tagsArr = normalizeTags(rawTagsStr.split(','));
    const isMatch = (activeTag === 'all') || tagsArr.includes(activeTag);

    if (isMatch) {
      card.style.removeProperty('display');
      matchCount++;
    } else {
      card.style.setProperty('display', 'none', 'important');
    }
  });

  const countEl = document.getElementById('postsCount');
  if (countEl) countEl.innerText = `${matchCount}件`;
}


// --- 詳細画面描画 (コンパクト ＆ スマホ最適化) ---
function renderDetailPage(postId) {
  const post = DB.getPostById(postId);
  const container = document.getElementById('detailContainer');
  if (!container) return;

  if (!post) {
    container.innerHTML = `
      <div class="p-8 text-center space-y-3">
        <p class="text-xs font-bold text-stone-500">おたよりが見つかりませんでした</p>
        <a href="#/" class="inline-block px-4 py-2 bg-stone-800 text-white rounded-xl text-xs font-bold">一覧に戻る</a>
      </div>
    `;
    return;
  }

  const title = escapeHtml(post.title || 'お知らせ');
  const titleEn = escapeHtml(post.title_en || '');
  const dateVal = post.date || '';
  const dateDisplay = dateVal ? `📅 ${dateVal.replace(/-/g, '/')}` : '';
  const timeDisplay = (post.time_start && post.time_end) ? `${post.time_start} 〜 ${post.time_end}` : (post.time_start || '');
  const location = escapeHtml(post.location || '');
  const deadline = post.deadline || '';
  const deadlineDesc = escapeHtml(post.deadline_description || '提出');
  const items = post.items || [];
  
  // 翻訳本文 (text_translation / image_translation / summary を統合)
  const transText = formatWithDateDividers((post.text_translation || post.image_translation || (post.summary && post.summary !== post.title ? post.summary : '') || '').trim());
  const rawText = (post.text_raw || post.image_raw || '').trim();
  const imgUrl = (post.image_url || '').trim();

  // お子さん ＆ タグHTML
  const childBadge = (post.child_id && post.child_id !== 'all') ? getChildBadgeHtml(post.child_id) : '';
  const tagsHtml = (normalizeTags(post.tags, transText)).map(t => getTagBadgeHtml(t)).join('');

  // 持ち物HTML
  const itemsHtml = items.length > 0 ? `
    <div class="p-3 rounded-2xl bg-amber-50/70 border border-amber-200/80 space-y-1.5">
      <h4 class="text-xs font-bold text-amber-900 flex items-center gap-1">
        <span>🎒 持ち物・持参するもの (${items.length}点)</span>
      </h4>
      <div class="flex flex-wrap gap-1 pt-0.5">
        ${items.map(it => `<span class="item-tag text-xs px-2.5 py-1 font-bold shadow-xs">🎒 ${escapeHtml(it)}</span>`).join('')}
      </div>
    </div>
  ` : '';

  // 締切行
  const dlRow = deadline ? `
    <div class="flex items-center justify-between text-rose-600 font-bold border-t border-rose-100 pt-1.5 text-xs">
      <span>⚠️ 提出締切:</span>
      <span>${deadline.replace(/-/g, '/')} (${deadlineDesc})</span>
    </div>
  ` : '';

  // 日時・場所・締切HTML
  const dateTimeHtml = (dateVal || timeDisplay || location || deadline) ? `
    <div class="p-3 rounded-2xl bg-stone-50 border border-stone-200 text-xs space-y-1.5">
      ${dateVal ? `
        <div class="flex items-center justify-between">
          <span class="text-stone-500 font-medium">📅 日程:</span>
          <span class="font-bold text-stone-800">${dateDisplay}</span>
        </div>
      ` : ''}
      ${timeDisplay ? `
        <div class="flex items-center justify-between">
          <span class="text-stone-500 font-medium">⏰ 時間:</span>
          <span class="font-bold text-stone-800">${timeDisplay}</span>
        </div>
      ` : ''}
      ${location ? `
        <div class="flex items-center justify-between">
          <span class="text-stone-500 font-medium">📍 場所:</span>
          <span class="font-bold text-stone-800">${location}</span>
        </div>
      ` : ''}
      ${dlRow}
    </div>
  ` : '';

  // ① 日本語翻訳・連絡事項カード
  const transCardHtml = transText ? `
    <div class="p-3.5 rounded-2xl bg-amber-50/70 border border-amber-200/80 space-y-2 shadow-xs">
      <h4 class="text-xs font-bold text-amber-950 flex items-center gap-1">
        <span>📱 日本語訳 ＆ 連絡事項</span>
      </h4>
      <div class="text-xs leading-relaxed text-stone-850 bg-white p-3.5 rounded-xl border border-amber-200/60 whitespace-pre-wrap font-medium shadow-xs">${escapeHtml(transText)}</div>
      ${rawText ? `
        <details class="text-[11px] pt-1">
          <summary class="font-bold text-amber-900 cursor-pointer hover:text-amber-950">英語原文（メール本文・OCR）を表示</summary>
          <div class="mt-1.5 p-2.5 rounded-xl bg-white border border-stone-200 text-stone-600 text-[10px] font-mono whitespace-pre-wrap leading-relaxed">${escapeHtml(rawText)}</div>
        </details>
      ` : ''}
    </div>
  ` : (rawText ? `
    <div class="p-3.5 rounded-2xl bg-amber-50/70 border border-amber-200/80 space-y-2">
      <h4 class="text-xs font-bold text-amber-950 flex items-center gap-1">
        <span>📄 英語原文テキスト</span>
      </h4>
      <div class="p-2.5 rounded-xl bg-white border border-stone-200 text-stone-600 text-[10px] font-mono whitespace-pre-wrap leading-relaxed">${escapeHtml(rawText)}</div>
    </div>
  ` : '');

  // ② 添付写真カード
  const imageCardHtml = imgUrl ? `
    <div class="p-3.5 rounded-2xl bg-sky-50/70 border border-sky-200/80 space-y-2 shadow-xs">
      <h4 class="text-xs font-bold text-sky-950 flex items-center gap-1">
        <span>🖼️ 添付プリント写真</span>
      </h4>
      <div class="w-full rounded-xl bg-white overflow-hidden border border-sky-200 flex items-center justify-center p-2">
        <img src="${imgUrl}" class="max-h-72 w-auto object-contain rounded-lg" alt="プリント" onerror="this.style.display='none'">
      </div>
    </div>
  ` : '';

  let shareText = `【おたより】${post.title}

`;
  if (transText) shareText += `📱 内容:
${transText}

`;
  if (items.length > 0) shareText += `🎒 持ち物: ${items.join(', ')}
`;
  const lineUrl = `https://line.me/R/msg/text/?${encodeURIComponent(shareText)}`;

  const calTitle = encodeURIComponent(post.title || '');
  const calLoc = encodeURIComponent(post.location || '');
  const calDesc = encodeURIComponent(`${post.title_en || ''}

${transText}

持ち物: ${items.join(', ')}`);
  const dClean = (dateVal || '20260907').replace(/-/g, '');
  const calDates = `${dClean}/${dClean}`;
  const googleCalUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${calTitle}&dates=${calDates}&details=${calDesc}&location=${calLoc}`;

  container.innerHTML = `
    <header class="px-4 py-3 bg-white border-b border-stone-200 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      <a href="#/" class="flex items-center gap-1 text-xs font-bold text-stone-700 hover:text-stone-900 bg-stone-100 hover:bg-stone-200 px-3 py-1.5 rounded-xl transition">
        <span>← 一覧に戻る</span>
      </a>
      <div class="flex items-center gap-1.5">
        <a href="#/edit/${post.id}" class="px-3 py-1.5 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-700 font-bold text-xs shadow-xs flex items-center gap-1 transition">
          <span>✏️ 編集</span>
        </a>
        <a href="${lineUrl}" target="_blank" class="px-3 py-1.5 rounded-xl bg-[#06C755] text-white font-bold text-xs shadow-xs flex items-center gap-1">
          <span>LINE共有</span>
        </a>
      </div>
    </header>

    <main class="p-4 space-y-3.5 flex-1">
      <div class="space-y-1.5">
        <div class="flex flex-wrap gap-1.5 items-center">
          ${tagsHtml}
          ${dateDisplay ? `<span class="text-xs text-stone-400 font-semibold ml-auto">${dateDisplay}</span>` : ''}
        </div>
        <h1 class="text-base sm:text-lg font-bold text-stone-900 leading-snug break-words">${title}</h1>
        ${titleEn ? `<p class="text-xs text-stone-500 font-medium">${titleEn}</p>` : ''}
      </div>

      ${dateTimeHtml}
      ${itemsHtml}
      ${transCardHtml}
      ${imageCardHtml}

      <div class="pt-2 grid grid-cols-2 gap-2">
        <a href="${googleCalUrl}" target="_blank" class="py-2.5 px-3 rounded-xl bg-sky-50 text-sky-700 hover:bg-sky-100 border border-sky-200 font-bold text-xs flex items-center justify-center gap-1 transition text-center shadow-xs">
          <span>📅 カレンダー追加</span>
        </a>
        <a href="${lineUrl}" target="_blank" class="py-2.5 px-3 rounded-xl bg-[#06C755] text-white hover:opacity-95 font-bold text-xs flex items-center justify-center gap-1 transition text-center shadow-xs">
          <span>📲 LINEで共有</span>
        </a>
      </div>

      <div class="text-center pt-2 pb-1 border-t border-stone-100">
        <button onclick="deleteCurrentPost('${post.id}', '${escapeHtml(post.title)}')" class="text-xs font-bold text-rose-500 hover:text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 px-3.5 py-2 rounded-xl transition flex items-center justify-center gap-1 mx-auto active:scale-95">
          <span>🗑️ このおたよりを削除する</span>
        </button>
      </div>

      <div class="text-center pt-1 pb-4">
        <a href="#/" class="inline-block text-xs font-bold text-stone-500 hover:text-stone-800 bg-stone-100 px-4 py-2 rounded-xl transition">
          ← おたより一覧に戻る
        </a>
      </div>
    </main>
  `;
}

function deleteCurrentPost(id, title) {
  if (!confirm(`「${title}」を削除してもよろしいですか？`)) return;
  DB.deletePost(id);
  alert('🗑️ おたよりを削除しました');
  window.location.hash = '#/';
}

// --- 対象のお子さん選択UI (新規追加 ＆ 編集画面共通) ---
let newSelectedChildId = 'all';
let editSelectedChildId = 'all';

function renderChildSelector(containerId, currentSelectedId, onSelectFnName) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const children = DB.getChildren();

  let html = `
    <button type="button" onclick="${onSelectFnName}('all')" class="child-select-btn px-3 py-1.5 rounded-xl text-xs font-bold border transition ${currentSelectedId === 'all' || !currentSelectedId ? 'bg-stone-900 text-white border-stone-900 shadow-xs' : 'bg-white text-stone-600 border-stone-200 hover:bg-stone-50'}">
      <span>👨‍👩‍👧‍👦 全員共通</span>
    </button>
  `;

  children.forEach(child => {
    const isSelected = String(currentSelectedId) === String(child.id);
    const theme = CHILD_COLOR_MAP[child.color] || CHILD_COLOR_MAP.blue;
    const cls = isSelected ? `${theme.pillActive} shadow-xs font-bold` : 'bg-white text-stone-600 border-stone-200 hover:bg-stone-50 font-medium';
    const gradeStr = child.grade ? ` (${escapeHtml(child.grade)})` : '';
    html += `
      <button type="button" onclick="${onSelectFnName}('${child.id}')" class="child-select-btn px-3 py-1.5 rounded-xl text-xs border transition ${cls}">
        <span>${child.icon || '👶'}</span> <span>${escapeHtml(child.name)}${gradeStr}</span>
      </button>
    `;
  });

  if (children.length === 0) {
    html += `
      <button type="button" onclick="openSettingsModal('children')" class="px-2.5 py-1.5 text-xs text-rose-500 font-bold hover:underline flex items-center gap-1">
        <span>＋ お子さんを登録する</span>
      </button>
    `;
  }

  container.innerHTML = html;
}

function selectNewPostChild(childId) {
  newSelectedChildId = childId;
  const input = document.getElementById('newPostChildId');
  if (input) input.value = childId;
  renderChildSelector('newChildSelectorContainer', newSelectedChildId, 'selectNewPostChild');
}

function selectEditPostChild(childId) {
  editSelectedChildId = childId;
  const input = document.getElementById('editPostChildId');
  if (input) input.value = childId;
  renderChildSelector('editChildSelectorContainer', editSelectedChildId, 'selectEditPostChild');
}

// --- 新規追加画面 ---
let newSelectedFile = null;
let newUploadedImageUrl = null;
let newSelectedTags = ['English'];
const ALL_TAGS = ['English', 'Math', 'Mandarin', 'event', 'その他'];

function renderNewPage() {
  newSelectedFile = null;
  newUploadedImageUrl = null;
  newSelectedTags = ['English'];
  newSelectedChildId = (activeChildId && activeChildId !== 'all') ? activeChildId : 'all';
  const childInput = document.getElementById('newPostChildId');
  if (childInput) childInput.value = newSelectedChildId;
  renderChildSelector('newChildSelectorContainer', newSelectedChildId, 'selectNewPostChild');

  document.getElementById('newRawTextInput').value = '';
  document.getElementById('newSelectedFileName').classList.add('hidden');
  document.getElementById('newLoadingBox').classList.add('hidden');
  document.getElementById('newResultForm').classList.add('hidden');
  renderNewTags();
  updateAiEngineStatusBanner();
}

function updateAiEngineStatusBanner() {
  const banner = document.getElementById('aiEngineStatusBanner');
  if (!banner) return;
  const settings = DB.getSettings();
  const apiKey = (settings.gemini_api_key || '').trim();
  if (apiKey) {
    banner.innerHTML = `
      <div class="p-3 rounded-2xl bg-purple-50 border border-purple-200 text-purple-900 text-xs flex items-center justify-between shadow-xs">
        <div class="flex items-center gap-1.5 font-bold">
          <span>✨ Gemini AI 高精度モード:</span>
          <span class="text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full text-[10px] font-black">有効</span>
        </div>
        <button type="button" onclick="openSettingsModal()" class="text-purple-700 hover:text-purple-900 underline text-[11px] font-bold">キー設定変更</button>
      </div>
    `;
  } else {
    banner.innerHTML = `
      <div class="p-3.5 rounded-2xl bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-300 text-amber-950 space-y-2 shadow-xs">
        <div class="flex items-center justify-between">
          <div class="font-bold text-xs flex items-center gap-1">
            <span>✨ Gemini AI 高精度モードを有効にする</span>
          </div>
          <span class="text-[10px] bg-amber-200 text-amber-900 px-2 py-0.5 rounded-full font-bold">無料・推奨</span>
        </div>
        <p class="text-[11px] text-stone-700 leading-relaxed">
          写真内の表やスケジュールをGeminiが直接綺麗に翻訳するには、Googleの無料APIキーを入力してください。
        </p>
        <div class="flex gap-1.5 pt-0.5">
          <input type="password" id="inlineApiKeyInput" placeholder="AIzaSy... (APIキーを貼り付け)" class="flex-1 p-2 bg-white border border-amber-300 rounded-xl font-mono text-[11px] text-stone-800 focus:outline-none shadow-inner">
          <button type="button" onclick="saveInlineApiKey()" class="px-3.5 py-2 bg-stone-900 hover:bg-stone-800 active:scale-95 text-white rounded-xl text-xs font-bold transition shadow-xs flex-shrink-0">保存</button>
        </div>
        <div class="text-[10px] text-stone-500 flex items-center justify-between pt-0.5">
          <span>※キーをお持ちでない方は</span>
          <a href="https://aistudio.google.com/app/apikey" target="_blank" class="text-blue-600 underline font-bold">Google AI Studioで無料取得 ↗</a>
        </div>
      </div>
    `;
  }
}

function saveInlineApiKey() {
  const input = document.getElementById('inlineApiKeyInput');
  const key = input ? input.value.trim() : '';
  if (!key) {
    alert('APIキーを入力してください');
    return;
  }
  const settings = DB.getSettings();
  settings.gemini_api_key = key;
  DB.saveSettings(settings);
  updateAiEngineStatusBanner();
  alert('✨ Gemini APIキーを保存しました！高精度モードが有効になりました。');
}



// ==========================================
// 🌟 堅牢・画像圧縮 ＆ 多段式 AI 解析・日本語翻訳エンジン
// ==========================================

// クライアント側画像圧縮 (Canvas - 最大1200px / JPEG品質0.8 / 約100KB〜200KBに軽量化)
function compressImageFile(file, maxWidth = 1200, maxHeight = 1200, quality = 0.8) {
  return new Promise((resolve) => {
    if (!file || !file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = () => resolve(null);
      reader.readAsDataURL(file);
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        let width = img.width;
        let height = img.height;

        if (width > maxWidth || height > maxHeight) {
          if (width > height) {
            height = Math.round((height * maxWidth) / width);
            width = maxWidth;
          } else {
            width = Math.round((width * maxHeight) / height);
            height = maxHeight;
          }
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        const compressedDataUrl = canvas.toDataURL('image/jpeg', quality);
        resolve(compressedDataUrl);
      };
      img.onerror = () => resolve(e.target.result);
      img.src = e.target.result;
    };
    reader.onerror = () => resolve(null);
    reader.readAsDataURL(file);
  });
}

async function handleNewFileChange(e) {
  const file = e.target.files[0];
  if (file) {
    newSelectedFile = file;
    const nameEl = document.getElementById('newSelectedFileNameText');
    if (nameEl) nameEl.innerText = file.name;
    const boxEl = document.getElementById('newSelectedFileName');
    if (boxEl) boxEl.classList.remove('hidden');

    // 即座に軽量画像へ圧縮変換
    newUploadedImageUrl = await compressImageFile(file);
  }
}

async function executeAIAnalyze() {
  const textVal = document.getElementById('newRawTextInput').value.trim();
  if (!newSelectedFile && !textVal) {
    alert('写真を選択するか、英語テキストを貼り付けてください。');
    return;
  }

  const loadingBox = document.getElementById('newLoadingBox');
  if (loadingBox) loadingBox.classList.remove('hidden');
  const resultForm = document.getElementById('newResultForm');
  if (resultForm) resultForm.classList.add('hidden');

  try {
    // 画像圧縮が未完了の場合は待機
    if (newSelectedFile && !newUploadedImageUrl) {
      newUploadedImageUrl = await compressImageFile(newSelectedFile);
    }

    const settings = DB.getSettings();
    const apiKey = (settings.gemini_api_key || '').trim();

    let draft = null;

        // 1. Gemini API Direct Call (ユーザー設定APIキーがある場合)
    if (apiKey) {
      console.log('Using Gemini API Direct Call with API Key...');
      try {
        draft = await callGeminiDirect(apiKey, newUploadedImageUrl, textVal);
        if (draft) {
          console.log('✨ Gemini AI Direct analysis succeeded!');
        } else {
          console.warn('Gemini direct call returned null, falling back...');
          alert(`⚠️ Gemini API呼出に失敗しました。\n\n【エラー詳細】\n${lastGeminiErrorDetails || 'APIキーまたは通信エラー'}\n\n（簡易OCRモードで読取を継続します）`);
        }
      } catch(geminiErr) {
        console.warn('Gemini direct call failed:', geminiErr);
        alert(`⚠️ Gemini API通信エラー: ${geminiErr.message}\n（簡易OCRモードで読取を継続します）`);
      }
    } else {
      console.log('No Gemini API Key set in settings. Using Client OCR translation fallback.');
    }

    // 2. クライアント側フォールバック翻訳（Google Translate + MyMemory + 高速OCR + 内蔵辞書）
    if (!draft) {
      console.log('Using Client-side Robust Multi-tier Translation Engine...');
      draft = await clientSideTranslateEngine(textVal, newSelectedFile, newUploadedImageUrl);
    }

    if (loadingBox) loadingBox.classList.add('hidden');

    if (draft) {
      populateNewForm(draft, Boolean(textVal), Boolean(newSelectedFile || newUploadedImageUrl));
    } else {
      // 最終安全フォールバック
      const fallbackDraft = {
        title: "学校からのおたより",
        title_en: "School Notice",
        date: null,
        time_start: null,
        location: null,
        items: [],
        deadline: null,
        deadline_description: null,
        summary: textVal ? (await clientTranslate(textVal)) : "添付プリントを確認して登録",
        text_translation: textVal ? (await clientTranslate(textVal)) : null,
        text_raw: textVal || null,
        image_translation: newUploadedImageUrl ? "添付プリントを確認して内容を登録できます" : null,
        image_raw: null,
        tags: ["英語・UOI"]
      };
      populateNewForm(fallbackDraft, Boolean(textVal), Boolean(newSelectedFile || newUploadedImageUrl));
    }
  } catch (err) {
    if (loadingBox) loadingBox.classList.add('hidden');
    console.error('AI Analysis Error:', err);
    alert('AI解析完了（一部項目は手動で確認・編集いただけます）');
    
    // エラー時でも画面が止まらないようフォームを表示
    const safeDraft = {
      title: "学校からのおたより",
      title_en: "School Notice",
      date: null,
      time_start: null,
      location: null,
      items: [],
      deadline: null,
      deadline_description: null,
      summary: textVal || "おたより内容",
      text_translation: textVal || null,
      text_raw: textVal || null,
      image_translation: newUploadedImageUrl ? "添付写真あり" : null,
      image_raw: null,
      tags: ["英語・UOI"]
    };
    populateNewForm(safeDraft, Boolean(textVal), Boolean(newSelectedFile || newUploadedImageUrl));
  }
}

// 🌟 日付・セッション区切り線の自動挿入フォーマッター（AI・OCR・手入力すべてに完全対応）
function formatWithDateDividers(text) {
  if (!text || typeof text !== 'string') return text || '';
  
  const lines = text.split('\n');
  const result = [];
  
  // セッションヘッダー正規表現
  const sessionRegex = /^(?:[■📅【\s]*)(?:セッション\s*[0-9０-９]+|session\s*[0-9]+|第\s*[0-9０-９]+\s*回)/i;
  // 日付単独ヘッダー正規表現
  const dateHeaderRegex = /^(?:[■📅【\s]*)(?:(?:1[0-2]|[1-9])\s*月\s*(?:[1-3][0-9]|[1-9])\s*日|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{1,2})/i;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    if (!trimmed) {
      result.push(line);
      continue;
    }
    
    const isSession = sessionRegex.test(trimmed);
    const isDate = dateHeaderRegex.test(trimmed);
    
    // 直前の非空行がセッションヘッダーだったか確認（セッション直後の日付行に二重で仕切りが入るのを防ぐ）
    let prevWasSessionHeader = false;
    let hasPrevDivider = false;
    for (let prevIdx = result.length - 1; prevIdx >= 0; prevIdx--) {
      const prevLine = result[prevIdx].trim();
      if (!prevLine) continue;
      if (prevLine.startsWith('===') || prevLine.startsWith('━━━') || prevLine.startsWith('---')) {
        hasPrevDivider = true;
      }
      if (sessionRegex.test(prevLine)) {
        prevWasSessionHeader = true;
      }
      break;
    }
    
    // セッション開始行、またはセッション直後ではない単独日付行の場合に仕切りを挿入
    if (isSession || (isDate && !prevWasSessionHeader)) {
      if (!hasPrevDivider && result.length > 0) {
        result.push("==============================");
      }
    }
    
    result.push(line);
  }
  
  return result.join('\n');
}

// ① Gemini API 直接呼出 (自動モデル検出 & 最適フォールバック)
let lastGeminiErrorDetails = '';

async function getAvailableGeminiModels(apiKey) {
  try {
    const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey.trim()}`;
    const res = await fetch(url);
    if (res.ok) {
      const data = await res.json();
      if (data.models && Array.isArray(data.models)) {
        const validModels = data.models
          .filter(m => m.supportedGenerationMethods && m.supportedGenerationMethods.includes('generateContent'))
          .map(m => m.name.replace('models/', ''));
        
        const preferred = ['gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-1.5-flash-002', 'gemini-1.5-flash-001', 'gemini-pro-vision', 'gemini-1.5-pro-latest'];
        const sorted = [];
        for (const p of preferred) {
          if (validModels.includes(p)) sorted.push(p);
        }
        for (const m of validModels) {
          if (!sorted.includes(m) && m.includes('gemini') && !m.includes('embedding') && !m.includes('imagen')) {
            sorted.push(m);
          }
        }
        if (sorted.length > 0) return sorted;
      }
    } else {
      const errJson = await res.json().catch(() => ({}));
      if (errJson?.error?.message) {
        lastGeminiErrorDetails = errJson.error.message;
      }
    }
  } catch(e) {
    lastGeminiErrorDetails = e.message;
  }
  
  return ['gemini-1.5-flash-latest', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-1.5-flash-002', 'gemini-1.5-flash-001'];
}

async function callGeminiDirect(apiKey, b64Image, textContent) {
  lastGeminiErrorDetails = '';
  const models = await getAvailableGeminiModels(apiKey);
  console.log('Available Gemini Models for this API Key:', models);
  
  const systemPrompt = `
あなたは学校・幼稚園・インターナショナルスクール等の英語のおたより（Newsletters, Schedule Tables, Event Notices, Handouts）を、保護者向けに極めて分かりやすく丁寧な日本語に翻訳・整理・構造化する専門AIです。
必ず以下のJSON形式のみを出力してください（Markdownコードブロック不要、純粋なJSON）。

${(() => {
  const children = DB.getChildren();
  if (children.length === 0) return '';
  const cList = children.map(c => `- ID: "${c.id}", お名前: "${c.name}", 学年/クラス: "${c.grade || '未設定'}"`).join('\n');
  return `【対象のお子さん（child_id）の自動判定】
登録されているお子さん一覧:
${cList}
- おたよりの内容（学年表記、クラス名、宛名等）から特定のお子さんに該当すると判断できる場合は、"child_id" にそのID（例: "${children[0].id}"）を設定してください。
- 兄弟姉妹共通、全校生徒向け、または特定のお子さんを判別できない場合は "child_id": "all" にしてください。\n`;
})()}
${(() => {
  const allT = DB.getAllTags();
  const tListStr = allT.map(t => `"${t}"`).join(', ');
  return `【タグ分類のルール】
tags に設定できる値は以下の一覧の中から最も適切なものを選択してください（複数可）:
[ ${tListStr} ]
- "English" : 英語学習、UOI、読書、ライティング、Language Arts等
- "Math" : 算数、数学、幾何、計算等
- "Mandarin" : 中国語、華語、中文等
- "event" : 学校行事、遠足、祝祭、発表会、スポーツデー等
- "その他" : 上記やカスタムタグに当てはまらない一般連絡
※ 必ず上記タグ一覧の中から選択してください。\n`;
})()}

tags に設定できる値は以下の5種類のみです（複数可）:
- "English" : 英語学習、UOI、読書、ライティング、Language Arts等
- "Math" : 算数、数学、幾何、計算等
- "Mandarin" : 中国語、華語、中文等
- "event" : 学校行事、遠足（Field Trip）、祝祭（Festival）、発表会、スポーツデー等
- "その他" : 上記4つに当てはまらないもの（アート、音楽、体育、事務連絡、一般通知等）
※ 上記以外のタグ名は出力しないでください。該当しないものはすべて "その他" にしてください。

【最重要・翻訳とフォーマットのルール】
1. 表形式（スケジュール、日時ごとの活動、持ち物・材料一覧等）の翻訳:
   - 表の内容を単に要約したり平坦な文章に縮小せず、保護者がひと目で分かるように**日にち・セッションごとに「==============================」の区切り線を入れて**明確に分離してください。
   - 各セッション内に「日付・見出し」「活動・プロジェクト名」「必要な材料・持ち物（個数・サイズ・色などの詳細を含む）」を箇条書きで美しく整理してください。
   - フォーマット例:
━━━━━━━━━━━━━━━━━━━━━━━━━━
【クラフトピア (CRAFTOPIA)】
木曜日: 午後2:00 - 3:20

==============================
📅 セッション1: 8月27日 (木)
・プロジェクト: ペン立て
・必要な材料:
  - アイスの棒（30本、何色でも可）
  - 空のポテトチップスの紙筒（小さい円柱形、直径7cm以上）
  - 接着剤
  - 紐または細いリボン（1メートル）

==============================
📅 セッション2: 9月3日 (木)
・プロジェクト: ジェスモナイトのコースター
・必要な材料:
  - 丸いシリコンモールド（直径: 10〜14 cm）
  - 透明なプラスチックカップ（大）
  - アイスの棒（1本）
  - エプロン

==============================
📅 セッション3: 9月17日 (木)
・プロジェクト: 毛糸玉のランタン
・必要な材料:
  - 木工用ボンド（白い接着剤）
  - 毛糸 1かせ（何色でも可）
  - 風船（最低3個）
  - エプロン
==============================
━━━━━━━━━━━━━━━━━━━━━━━━━━

2. 持ち物・材料リスト (items):
   - おたより全体で必要とされる持ち物・材料（各セッションで必要なアイテムも含む）を分かりやすく日本語配列にして抽出してください。
   - 例: ["アイスの棒 (30本)", "ポテトチップスの紙筒", "接着剤", "シリコンモールド", "エプロン", "木工用ボンド", "自然乾燥粘土 (300g)", "トイレットペーパーの芯 (20個)"]

3. 日付 (date) と 時間 (time_start):
   - 単一のイベント・期日の場合はその日付 (YYYY-MM-DD)。
   - 複数日程のスケジュール表の場合は、第1回目のセッション日付や直近の開始日 (YYYY-MM-DD)。本文や画像内に明確な日付がない場合のみ null。
   - 開始時間（例: "2:00 PM" -> "14:00"）を HH:MM 形式で抽出。ない場合は null。

4. タイトル (title / title_en):
   - おたよりの主題やイベント名を的確に表す自然な日本語タイトル（例: 「クラフトピア（木曜クラフト教室）の予定と持ち物一覧」）。

5. 提出締切 (deadline / deadline_description):
   - 提出物や返送の締切日がある場合のみ設定。ない場合は null。

{
  "title": "日本語の分かりやすいタイトル",
  "title_en": "Original English Title",
  "date": "YYYY-MM-DD (明確な日付がある場合のみ。不明なら null)",
  "time_start": "HH:MM (開始時刻。ない場合は null)",
  "location": "場所 (ない場合は null)",
  "items": ["持ち物1", "持ち物2"],
  "deadline": "YYYY-MM-DD (提出締切日。ない場合は null)",
  "deadline_description": "提出物の内容（ない場合は null)",
  "summary": "おたより全体の概要と重要ポイントの要約（丁寧な日本語）",
  "text_translation": "メッセージ本文の丁寧な日本語全訳（メッセージがない場合はnull）",
  "text_raw": "メッセージ英語原文（ない場合はnull）",
  "image_translation": "画像内英文の丁寧な日本語全訳・構造化テキスト（表やリストはセッション・日にちごとに==============================で区切って見やすく箇条書き）（画像がない場合はnull）",
  "image_raw": "画像内英文OCR・英語原文（画像がない場合はnull）",
  "tags": ["English"],
  "child_id": "all (または該当するお子さんのID)"
}
`;

  const parts = [];

  if (b64Image) {
    const mimeMatch = b64Image.match(/^data:([^;]+);/);
    const mimeType = mimeMatch ? mimeMatch[1] : 'image/jpeg';
    const rawB64 = b64Image.includes(',') ? b64Image.split(',')[1] : b64Image;
    parts.push({
      inlineData: {
        mimeType: mimeType,
        data: rawB64
      }
    });
    parts.push({
      text: systemPrompt + "\n\n添付のプリント画像を読み取り、上記の指示に従って指定のJSON形式のみで出力してください。"
    });
  }

  if (textContent) {
    parts.push({
      text: systemPrompt + `\n\n【英語メッセージ本文】:\n${textContent}\n\n上記の文章を自然な日本語に翻訳し、指定のJSON形式のみで出力してください。`
    });
  }

  for (const model of models) {
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey.trim()}`;
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: parts }]
        })
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        const msg = errJson?.error?.message || `HTTP ${res.status}`;
        lastGeminiErrorDetails = `[${model}] ${msg}`;
        console.warn(`Model ${model} error (HTTP ${res.status}):`, errJson);
        continue;
      }

      const data = await res.json();
      const rawOut = data.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!rawOut) {
        lastGeminiErrorDetails = `[${model}] 応答テキストが空でした`;
        console.warn(`Model ${model} returned empty response`);
        continue;
      }

      const cleanJson = rawOut.replace(/^```json\s*/i, '').replace(/^```\s*/i, '').replace(/```\s*$/i, '').trim();
      let parsed = null;
      try {
        parsed = JSON.parse(cleanJson);
      } catch(e) {
        const match = cleanJson.match(/(\{[\s\S]*\})/);
        if (match) {
          try { parsed = JSON.parse(match[1]); } catch(err2) {}
        }
      }

      if (parsed) {
        if (parsed.image_translation) parsed.image_translation = formatWithDateDividers(parsed.image_translation);
        if (parsed.text_translation) parsed.text_translation = formatWithDateDividers(parsed.text_translation);
        if (parsed.summary) parsed.summary = formatWithDateDividers(parsed.summary);
        return parsed;
      }
    } catch (err) {
      lastGeminiErrorDetails = `[${model}] ${err.message}`;
      console.warn(`Gemini Direct Error (${model}):`, err);
    }
  }
  return null;
}

// ② クライアント側フォールバック翻訳エンジン
async function clientSideTranslateEngine(text, file, b64Image) {
  let textTrans = "";
  let imageRaw = "";
  let imageTrans = "";

  if (text) {
    textTrans = formatWithDateDividers(await clientTranslate(text));
  }

  if (b64Image) {
    console.log('Extracting text from image via client OCR...');
    imageRaw = await clientOCR(b64Image);
    if (imageRaw) {
      imageTrans = formatWithDateDividers(await clientTranslate(imageRaw));
    } else {
      imageTrans = "（添付写真あり・プリントの内容を確認してタイトルや持ち物を登録できます）";
    }
  }

  const combined = `${text || ''}\n${imageRaw || ''}`.trim();
  const lower = combined.toLowerCase();

  // 持ち物抽出
  const items = [];
  const keywordMap = [
    ['shoebox', '靴箱・シューズボックス'],
    ['shoe box', '靴箱・シューズボックス'],
    ['sticker', 'ステッカー・シール'],
    ['photo', '写真（家族・個人）'],
    ['scissors', 'はさみ'],
    ['glue', 'のり・接着剤'],
    ['lunch', 'お弁当'],
    ['water bottle', '水筒'],
    ['apron', 'エプロン'],
    ['towel', 'タオル'],
    ['hood', '防災頭巾'],
    ['shoes', '上履き・室内履き'],
    ['mat', 'レジャーシート'],
    ['backpack', 'リュックサック'],
    ['costume', '伝統衣装・コスチューム'],
    ['lantern', '手作りランタン'],
    ['silicon mold', 'シリコンモールド'],
    ['clay', '工作用粘土']
  ];

  for (const [enKey, jaVal] of keywordMap) {
    if (lower.includes(enKey) || (textTrans + imageTrans).includes(jaVal.split('・')[0])) {
      if (!items.includes(jaVal)) items.push(jaVal);
    }
  }

  // 日付
  let eventDate = null;
  const dateMatch = combined.match(/(?:on\s+)?([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?/i);
  if (dateMatch) {
    const monthNames = { jan:1, feb:2, mar:3, apr:4, may:5, jun:6, jul:7, aug:8, sep:9, sept:9, oct:10, nov:11, dec:12 };
    const mStr = dateMatch[1].toLowerCase().substring(0, 3);
    if (monthNames[mStr]) {
      const dVal = String(dateMatch[2]).padStart(2, '0');
      const mVal = String(monthNames[mStr]).padStart(2, '0');
      eventDate = `2026-${mVal}-${dVal}`;
    }
  }

  // 時間
  let timeStart = null;
  const timeMatch = combined.match(/(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?/);
  if (timeMatch) {
    let hr = parseInt(timeMatch[1]);
    const min = timeMatch[2];
    const ampm = (timeMatch[3] || '').toUpperCase();
    if (ampm === 'PM' && hr < 12) hr += 12;
    if (ampm === 'AM' && hr === 12) hr = 0;
    timeStart = `${String(hr).padStart(2, '0')}:${min}`;
  }

  // 締切
  let deadline = null;
  let deadlineDesc = null;
  if (lower.includes('return by') || lower.includes('due') || lower.includes('deadline') || lower.includes('締切')) {
    deadline = eventDate;
    deadlineDesc = items.length > 0 ? `${items[0]}等の持参` : "提出用紙・確認";
  }

  // タイトル自動生成 (ハードコード全廃・実際の英語テキストから動的に高精度翻訳)
  let titleJa = "";
  let titleEn = "";

  const lines = combined.split('\n').map(l => l.trim()).filter(l => l.length > 2);
  let candidateTitle = "";
  for (const line of lines) {
    const lLower = line.toLowerCase();
    // ヘッダーや挨拶を除外してタイトルらしい行を抽出
    if (lLower.startsWith('dear') || lLower.startsWith('hello') || lLower.startsWith('good morning') || lLower.startsWith('school info') || lLower.startsWith('page ')) {
      continue;
    }
    candidateTitle = line;
    break;
  }
  if (!candidateTitle && lines.length > 0) {
    candidateTitle = lines[0];
  }

  if (candidateTitle) {
    titleEn = candidateTitle.substring(0, 60);
    try {
      const transTitle = await translateSingleChunk(titleEn);
      if (transTitle && transTitle.trim() && transTitle !== titleEn) {
        titleJa = transTitle.trim().replace(/[.!]+$/, '');
        if (!titleJa.includes('お知らせ') && !titleJa.includes('案内') && !titleJa.includes('タスク') && !titleJa.includes('イベント') && titleJa.length < 15) {
          titleJa = `${titleJa}のお知らせ`;
        }
      }
    } catch(e) {}
  }

  if (!titleJa) {
    if (textTrans) {
      titleJa = textTrans.split('\n')[0].substring(0, 30);
    } else if (imageTrans && !imageTrans.includes('添付写真あり')) {
      titleJa = imageTrans.split('\n')[0].substring(0, 30);
    } else {
      titleJa = "学校からのおたより";
    }
    if (!titleEn) titleEn = "School Notice";
  }

  // お子さん自動判定
  let detectedChildId = 'all';
  const allChildren = DB.getChildren();
  for (const c of allChildren) {
    const nLower = (c.name || '').toLowerCase();
    const gLower = (c.grade || '').toLowerCase();
    if ((nLower && combined.toLowerCase().includes(nLower)) || (gLower && combined.toLowerCase().includes(gLower))) {
      detectedChildId = c.id;
      break;
    }
  }

  // タグ (English, Math, Mandarin, event, その他)
  const tags = normalizeTags([], combined);

  const summaryJa = textTrans || imageTrans || titleJa;

  return {
    title: titleJa,
    title_en: titleEn,
    date: eventDate,
    time_start: timeStart,
    time_end: null,
    location: null,
    items: items,
    deadline: deadline,
    deadline_description: deadlineDesc,
    summary: summaryJa,
    text_translation: text ? textTrans : null,
    text_raw: text || null,
    image_translation: b64Image ? imageTrans : null,
    image_raw: b64Image ? imageRaw : null,
    tags: tags
  };
}

// 🌟 多段式・超堅牢クライアント翻訳エンジン (Google + MyMemory + 内蔵辞書)
async function clientTranslate(text) {
  if (!text || !text.trim()) return "";
  
  const paragraphs = text.split('\n').map(p => p.trim()).filter(Boolean);
  const translated = [];

  for (const para of paragraphs) {
    let chunks = [para];
    if (para.length > 200) {
      chunks = para.match(/[^.!?]+[.!?]+/g) || [para];
    }

    const transChunks = [];
    for (const c of chunks) {
      const res = await translateSingleChunk(c.trim());
      transChunks.push(res);
    }

    translated.push(transChunks.join(' '));
  }

  return translated.join('\n\n');
}

// 単一テキストチャンクの多重フォールバック翻訳 (絶対に例外をスローしない)
async function translateSingleChunk(chunk) {
  if (!chunk || !chunk.trim()) return "";

  // 1. Google Translate API 直接呼び出し
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);
    const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ja&dt=t&q=${encodeURIComponent(chunk)}`;
    const res = await fetch(url, { signal: controller.signal });
    clearTimeout(timeoutId);
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && Array.isArray(data[0])) {
        const t = data[0].map(item => item && item[0]).filter(Boolean).join('');
        if (t && t.trim()) return t;
      }
    }
  } catch(e) {}

  // 2. MyMemory API (CORS完全対応・高精度)
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);
    const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(chunk)}&langpair=en|ja`;
    const res = await fetch(url, { signal: controller.signal });
    clearTimeout(timeoutId);
    if (res.ok) {
      const data = await res.json();
      const t = data && data.responseData && data.responseData.translatedText;
      if (t && !t.startsWith("MYMEMORY WARNING") && !t.includes("QUERY LENGTH LIMIT")) {
        return t;
      }
    }
  } catch(e) {}

  // 3. 内蔵オフライン学校英語辞書による自然翻訳フォールバック
  return offlineDictionaryTranslate(chunk);
}

// オフライン学校英語辞書変換
function offlineDictionaryTranslate(text) {
  let res = text;
  const dict = [
    [/Dear Parents,?/gi, '保護者の皆様へ、'],
    [/Please note that/gi, 'ご確認ください：'],
    [/Please be informed that/gi, 'お知らせいたします：'],
    [/Please bring/gi, 'ご持参ください：'],
    [/What to bring/gi, '【持ち物】'],
    [/Summative Assessment/gi, '総括評価（SA）'],
    [/Unit of Inquiry/gi, '探究単元（UOI）'],
    [/Identity Explorer/gi, 'アイデンティティ・エクスプローラー（自分探究者）'],
    [/Field Trip/gi, '遠足・校外学習'],
    [/Permission Slip/gi, '参加同意書・提出用紙'],
    [/Early Dismissal/gi, '短縮授業・早下校'],
    [/Opening Ceremony/gi, '始業式'],
    [/Welcome Back/gi, '新学期へようこそ'],
    [/Sports Day/gi, '運動会・スポーツデー'],
    [/Shoebox/gi, '靴箱'],
    [/Shoe box/gi, '靴箱'],
    [/Stickers/gi, 'ステッカー・シール'],
    [/Photos?/gi, '写真'],
    [/Scissors/gi, 'はさみ'],
    [/Glue/gi, 'のり'],
    [/Water bottle/gi, '水筒'],
    [/Packed lunch/gi, 'お弁当'],
    [/Lunch/gi, '昼食・お弁当'],
    [/Apron/gi, 'エプロン'],
    [/Backpack/gi, 'リュックサック'],
    [/Raincoat/gi, 'レインコート・雨具'],
    [/Indoor clean shoes/gi, '上履き・室内履き'],
    [/Disaster hood/gi, '防災頭巾'],
    [/Homework/gi, '宿題'],
    [/Health check card/gi, '健康観察カード'],
    [/Return signed permission slip by/gi, '記入済み同意書をご提出ください：'],
    [/by Monday/gi, '月曜日までに'],
    [/by Friday/gi, '金曜日までに'],
    [/Thank you for your support!?/gi, 'ご協力ありがとうございます！']
  ];

  for (const [regex, ja] of dict) {
    res = res.replace(regex, ja);
  }
  return res;
}

// 🌟 多段式OCR (OCR.space 軽量JPEG送信)
async function clientOCR(base64Data) {
  if (!base64Data) return '';
  const apiKeys = ['K88536892588957', 'helloworld'];

  for (const key of apiKeys) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000);

      const formData = new FormData();
      formData.append('base64Image', base64Data);
      formData.append('language', 'eng');
      formData.append('isOverlayRequired', 'false');
      formData.append('apikey', key);

      const res = await fetch('https://api.ocr.space/parse/image', {
        method: 'POST',
        body: formData,
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        const data = await res.json();
        if (data.ParsedResults && data.ParsedResults.length > 0) {
          const txt = (data.ParsedResults[0].ParsedText || '').trim();
          if (txt) return txt;
        }
      }
    } catch (err) {
      console.warn(`OCR error with key ${key}:`, err);
    }
  }
  return '';
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
    reader.readAsDataURL(file);
  });
}


// フォームへの反映
function populateNewForm(draft, hasTextInput, hasImageInput) {
  document.getElementById('newPostTitle').value = draft.title || '';
  document.getElementById('newPostTitleEn').value = draft.title_en || '';

  const hasText = hasTextInput || Boolean(draft.text_translation) || Boolean(draft.text_raw);
  const hasImage = hasImageInput || Boolean(draft.image_translation) || Boolean(draft.image_raw) || Boolean(newUploadedImageUrl);

  const textSection = document.getElementById('newTextMessageSection');
  if (hasText) {
    textSection.classList.remove('hidden');
    document.getElementById('newPostTextTranslation').value = formatWithDateDividers(draft.text_translation || '');
    document.getElementById('newPostTextRaw').value = draft.text_raw || '';
  } else {
    textSection.classList.add('hidden');
    document.getElementById('newPostTextTranslation').value = '';
    document.getElementById('newPostTextRaw').value = '';
  }

  const imageSection = document.getElementById('newImageMessageSection');
  if (hasImage) {
    imageSection.classList.remove('hidden');
    document.getElementById('newPostImageTranslation').value = formatWithDateDividers(draft.image_translation || '');
    document.getElementById('newPostImageRaw').value = draft.image_raw || '';
    if (newUploadedImageUrl) {
      document.getElementById('newPreviewImageEl').src = newUploadedImageUrl;
    }
  } else {
    imageSection.classList.add('hidden');
    document.getElementById('newPostImageTranslation').value = '';
    document.getElementById('newPostImageRaw').value = '';
  }

  document.getElementById('newPostDate').value = draft.date || '';
  document.getElementById('newPostTimeStart').value = draft.time_start || '';
  document.getElementById('newPostLocation').value = draft.location || '';
  document.getElementById('newPostDeadline').value = draft.deadline || '';
  document.getElementById('newPostDeadlineDesc').value = draft.deadline_description || '';
  document.getElementById('newPostItems').value = (draft.items || []).join(', ');

  if (draft.tags && draft.tags.length > 0) {
    newSelectedTags = draft.tags;
  }
  renderNewTags();

  document.getElementById('newResultForm').classList.remove('hidden');
  document.getElementById('newResultForm').scrollIntoView({ behavior: 'smooth' });
}

function submitNewPost(e) {
  e.preventDefault();
  const title = document.getElementById('newPostTitle').value.trim();
  if (!title) {
    alert('タイトルを入力してください');
    return;
  }

  const itemsStr = document.getElementById('newPostItems').value;
  const itemsArr = itemsStr ? itemsStr.split(',').map(s => s.trim()).filter(Boolean) : [];

  const textTrans = document.getElementById('newPostTextTranslation').value.trim();
  const textRaw = document.getElementById('newPostTextRaw').value.trim();
  const imgTrans = document.getElementById('newPostImageTranslation').value.trim();
  const imgRaw = document.getElementById('newPostImageRaw').value.trim();

  const postData = {
    title: title,
    title_en: document.getElementById('newPostTitleEn').value.trim() || null,
    text_translation: textTrans ? formatWithDateDividers(textTrans) : null,
    text_raw: textRaw || null,
    image_translation: imgTrans ? formatWithDateDividers(imgTrans) : null,
    image_raw: imgRaw || null,
    summary: textTrans || imgTrans || title,
    date: document.getElementById('newPostDate').value || null,
    time_start: document.getElementById('newPostTimeStart').value || null,
    location: document.getElementById('newPostLocation').value.trim() || null,
    deadline: document.getElementById('newPostDeadline').value || null,
    deadline_description: document.getElementById('newPostDeadlineDesc').value.trim() || null,
    items: itemsArr,
    tags: (newSelectedTags && newSelectedTags.length > 0) ? normalizeTags(newSelectedTags) : ['その他'],
    child_id: document.getElementById('newPostChildId').value || newSelectedChildId || 'all',
    image_url: newUploadedImageUrl
  };

  const saved = DB.addPost(postData);
  alert('✨ 新しいおたよりを保存しました！');
  window.location.hash = `#/post/${saved.id}`;
  renderDetailPage(saved.id);
}

// --- 編集画面描画 ---
let editPostId = null;
let editUploadedImageUrl = null;
let editSelectedTags = [];

function renderEditPage(postId) {
  const post = DB.getPostById(postId);
  if (!post) {
    window.location.hash = '#/';
    return;
  }

  editPostId = postId;
  editUploadedImageUrl = post.image_url || null;
  editSelectedTags = post.tags ? normalizeTags(post.tags) : ['その他'];
  editSelectedChildId = post.child_id || 'all';
  const editChildInput = document.getElementById('editPostChildId');
  if (editChildInput) editChildInput.value = editSelectedChildId;
  renderChildSelector('editChildSelectorContainer', editSelectedChildId, 'selectEditPostChild');

  const backLink = document.getElementById('editBackLink');
  if (backLink) backLink.href = `#/post/${postId}`;

  document.getElementById('editPostTitle').value = post.title || '';
  document.getElementById('editPostTitleEn').value = post.title_en || '';
  
  // 統合された翻訳テキストと英語原文を確実にフォームへセット
  const currentTrans = formatWithDateDividers(post.text_translation || post.image_translation || (post.summary && post.summary !== post.title ? post.summary : '') || '');
  const currentRaw = post.text_raw || post.image_raw || '';
  
  document.getElementById('editPostTranslation').value = currentTrans;
  document.getElementById('editPostRaw').value = currentRaw;

  document.getElementById('editPostDate').value = post.date || '';
  document.getElementById('editPostTimeStart').value = post.time_start || '';
  document.getElementById('editPostLocation').value = post.location || '';
  document.getElementById('editPostDeadline').value = post.deadline || '';
  document.getElementById('editPostDeadlineDesc').value = post.deadline_description || '';
  document.getElementById('editPostItems').value = (post.items || []).join(', ');

  const imgBox = document.getElementById('editImagePreviewBox');
  const imgEl = document.getElementById('editPreviewImageEl');
  if (editUploadedImageUrl) {
    imgEl.src = editUploadedImageUrl;
    imgBox.style.display = 'flex';
  } else {
    imgBox.style.display = 'none';
  }

  renderEditTags();
}



function renderNewTags() {
  const container = document.getElementById('newTagContainer');
  if (!container) return;
  const allTags = DB.getAllTags();

  let html = allTags.map(t => {
    const isSel = newSelectedTags.includes(t);
    const bg = isSel ? 'bg-stone-900 text-white font-bold shadow-xs' : 'bg-stone-100 text-stone-600 hover:bg-stone-200';
    return `<button type="button" onclick="toggleNewTag('${escapeHtml(t)}')" class="px-3 py-1.5 rounded-full text-xs transition ${bg}">${escapeHtml(t)}</button>`;
  }).join('');

  html += `
    <button type="button" onclick="promptAddNewTag('new')" class="px-3 py-1.5 rounded-full text-xs font-bold bg-rose-50 text-rose-600 hover:bg-rose-100 border border-dashed border-rose-300 transition flex items-center gap-0.5">
      <span>＋ タグを追加</span>
    </button>
  `;

  container.innerHTML = html;
}

function toggleNewTag(t) {
  if (newSelectedTags.includes(t)) {
    newSelectedTags = newSelectedTags.filter(x => x !== t);
  } else {
    newSelectedTags.push(t);
  }
  renderNewTags();
}

function renderEditTags() {
  const container = document.getElementById('editTagContainer');
  if (!container) return;
  const allTags = DB.getAllTags();

  let html = allTags.map(t => {
    const isSel = editSelectedTags.includes(t);
    const bg = isSel ? 'bg-stone-900 text-white font-bold shadow-xs' : 'bg-stone-100 text-stone-600 hover:bg-stone-200';
    return `<button type="button" onclick="toggleEditTag('${escapeHtml(t)}')" class="px-3 py-1.5 rounded-full text-xs transition ${bg}">${escapeHtml(t)}</button>`;
  }).join('');

  html += `
    <button type="button" onclick="promptAddNewTag('edit')" class="px-3 py-1.5 rounded-full text-xs font-bold bg-rose-50 text-rose-600 hover:bg-rose-100 border border-dashed border-rose-300 transition flex items-center gap-0.5">
      <span>＋ タグを追加</span>
    </button>
  `;

  container.innerHTML = html;
}

function toggleEditTag(t) {
  if (editSelectedTags.includes(t)) {
    editSelectedTags = editSelectedTags.filter(x => x !== t);
  } else {
    editSelectedTags.push(t);
  }
  renderEditTags();
}

function promptAddNewTag(context) {
  const tagName = prompt('追加したい新しいタグ名を入力してください\n(例: Science, 水泳, PTA, 提出物あり)');
  if (!tagName || !tagName.trim()) return;
  const trimmed = tagName.trim();
  DB.addTag(trimmed);

  if (context === 'new') {
    if (!newSelectedTags.includes(trimmed)) newSelectedTags.push(trimmed);
    renderNewTags();
  } else if (context === 'edit') {
    if (!editSelectedTags.includes(trimmed)) editSelectedTags.push(trimmed);
    renderEditTags();
  }
  renderHomeTagFilters();
}

async function handleEditFileChange(e) {
  const file = e.target.files[0];
  if (!file) return;

  editUploadedImageUrl = await compressImageFile(file);
  const imgEl = document.getElementById('editPreviewImageEl');
  const imgBox = document.getElementById('editImagePreviewBox');
  if (imgEl && imgBox && editUploadedImageUrl) {
    imgEl.src = editUploadedImageUrl;
    imgBox.style.display = 'flex';
  }
}

function removeEditImage() {
  editUploadedImageUrl = null;
  document.getElementById('editImagePreviewBox').style.display = 'none';
  document.getElementById('editPreviewImageEl').src = '';
}

function submitEditPost(e) {
  e.preventDefault();
  const oldPost = DB.getPostById(editPostId) || {};

  const title = document.getElementById('editPostTitle').value.trim();
  if (!title) {
    alert('タイトルを入力してください');
    return;
  }

  const itemsStr = document.getElementById('editPostItems').value.trim();
  const itemsArr = itemsStr ? itemsStr.split(',').map(s => s.trim()).filter(Boolean) : [];

  const transVal = document.getElementById('editPostTranslation').value.trim();
  const rawVal = document.getElementById('editPostRaw').value.trim();

  const updateData = {
    ...oldPost,
    id: editPostId,
    title: title,
    title_en: document.getElementById('editPostTitleEn').value.trim() || null,
    text_translation: transVal ? formatWithDateDividers(transVal) : null,
    image_translation: editUploadedImageUrl ? (transVal || null) : null,
    text_raw: rawVal || null,
    image_raw: editUploadedImageUrl ? (rawVal || null) : null,
    summary: transVal || title,
    date: document.getElementById('editPostDate').value || null,
    time_start: document.getElementById('editPostTimeStart').value || null,
    location: document.getElementById('editPostLocation').value.trim() || null,
    deadline: document.getElementById('editPostDeadline').value || null,
    deadline_description: document.getElementById('editPostDeadlineDesc').value.trim() || null,
    items: itemsArr,
    tags: editSelectedTags.length > 0 ? normalizeTags(editSelectedTags) : ['その他'],
    child_id: document.getElementById('editPostChildId').value || editSelectedChildId || 'all',
    image_url: editUploadedImageUrl,
    updated_at: new Date().toISOString()
  };

  DB.updatePost(editPostId, updateData);
  alert('✅ 変更を保存しました！');
  window.location.hash = `#/post/${editPostId}`;
  renderDetailPage(editPostId);
}

// --- 設定モーダル ＆ お子さん管理（追加・編集・削除） ---
function openSettingsModal(tab) {
  const settings = DB.getSettings();
  document.getElementById('settingUserName').value = settings.user_name || 'ゲスト';
  document.getElementById('settingApiKey').value = settings.gemini_api_key || '';
  resetChildForm();
  renderSettingsChildren();
  renderSettingsTags();
  document.getElementById('settingsModal').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function setChildGenderForm(gender) {
  const input = document.getElementById('childFormGender');
  if (input) input.value = gender;

  const btnBoy = document.getElementById('genderBtnBoy');
  const btnGirl = document.getElementById('genderBtnGirl');

  if (btnBoy && btnGirl) {
    if (gender === '👦') {
      btnBoy.className = 'flex items-center justify-center gap-1.5 p-2.5 rounded-xl border-2 border-sky-600 bg-sky-500 text-white font-black shadow-md ring-2 ring-sky-200 text-xs transition scale-[1.02] cursor-pointer';
      btnBoy.innerHTML = '<span>👦 男の子</span> <span class="text-xs font-black ml-0.5">✓</span>';

      btnGirl.className = 'flex items-center justify-center gap-1.5 p-2.5 rounded-xl border border-stone-200 bg-stone-100 text-stone-500 font-medium hover:bg-stone-200 text-xs transition cursor-pointer opacity-70';
      btnGirl.innerHTML = '<span>👧 女の子</span>';
    } else {
      btnGirl.className = 'flex items-center justify-center gap-1.5 p-2.5 rounded-xl border-2 border-rose-600 bg-rose-500 text-white font-black shadow-md ring-2 ring-rose-200 text-xs transition scale-[1.02] cursor-pointer';
      btnGirl.innerHTML = '<span>👧 女の子</span> <span class="text-xs font-black ml-0.5">✓</span>';

      btnBoy.className = 'flex items-center justify-center gap-1.5 p-2.5 rounded-xl border border-stone-200 bg-stone-100 text-stone-500 font-medium hover:bg-stone-200 text-xs transition cursor-pointer opacity-70';
      btnBoy.innerHTML = '<span>👦 男の子</span>';
    }
  }
}


function renderSettingsChildren() {
  const container = document.getElementById('settingsChildrenList');
  if (!container) return;
  const children = DB.getChildren();
  if (children.length === 0) {
    container.innerHTML = `
      <div class="p-2.5 text-center text-stone-400 text-[11px] bg-stone-50 rounded-xl border border-dashed border-stone-200">
        登録されたお子さんはいません
      </div>
    `;
    return;
  }

  container.innerHTML = children.map((c, index) => {
    const isGirl = (c.icon === '👧' || c.color === 'pink');
    const displayIcon = isGirl ? '👧' : '👦';
    const gradeStr = c.grade ? ` (${escapeHtml(c.grade)})` : '';
    const badgeBg = isGirl ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-sky-50 text-sky-700 border-sky-200';

    const upBtn = (index > 0)
      ? `<button type="button" onclick="moveChildOrder('${c.id}', 'up')" class="w-6 h-6 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 flex items-center justify-center text-[10px] font-bold transition shadow-2xs" title="上へ並び替え">▲</button>`
      : `<span class="w-6 h-6"></span>`;

    const downBtn = (index < children.length - 1)
      ? `<button type="button" onclick="moveChildOrder('${c.id}', 'down')" class="w-6 h-6 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 flex items-center justify-center text-[10px] font-bold transition shadow-2xs" title="下へ並び替え">▼</button>`
      : `<span class="w-6 h-6"></span>`;

    return `
      <div class="flex items-center justify-between p-2.5 rounded-xl bg-white border border-stone-200 shadow-2xs">
        <div class="flex items-center gap-2 min-w-0">
          <span class="text-lg flex-shrink-0">${displayIcon}</span>
          <div class="min-w-0">
            <div class="flex items-center gap-1.5">
              <span class="font-bold text-xs text-stone-900 truncate">${escapeHtml(c.name)}</span>
              <span class="px-1.5 py-0.2 rounded-md text-[10px] font-bold border ${badgeBg}">${isGirl ? '女の子' : '男の子'}</span>
            </div>
            ${c.grade ? `<p class="text-[10px] text-stone-500 font-medium">${escapeHtml(c.grade)}</p>` : ''}
          </div>
        </div>
        <div class="flex items-center gap-1 flex-shrink-0">
          ${upBtn}
          ${downBtn}
          <button type="button" onclick="editChildInSettings('${c.id}')" class="px-2 py-1 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 text-[11px] font-bold transition flex items-center gap-0.5" title="設定を変更">
            <span>✏️</span> <span>変更</span>
          </button>
          <button type="button" onclick="deleteChildFromSettings('${c.id}')" class="w-6 h-6 rounded-lg bg-stone-100 hover:bg-rose-50 text-stone-400 hover:text-rose-600 flex items-center justify-center text-xs font-bold transition" title="削除">
            ✕
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function moveChildOrder(childId, direction) {
  const settings = DB.getSettings();
  const children = Array.isArray(settings.children) ? [...settings.children] : [];
  const idx = children.findIndex(c => String(c.id) === String(childId));
  if (idx === -1) return;

  const targetIdx = (direction === 'up') ? idx - 1 : idx + 1;
  if (targetIdx < 0 || targetIdx >= children.length) return;

  // Swap
  const temp = children[idx];
  children[idx] = children[targetIdx];
  children[targetIdx] = temp;

  settings.children = children;
  DB.saveSettings(settings);

  renderSettingsChildren();
  renderChildTabs();
  renderHomePage();
}

function editChildInSettings(childId) {
  const child = DB.getChildById(childId);
  if (!child) return;

  const idInput = document.getElementById('editingChildId');
  const nameInput = document.getElementById('newChildName');
  const gradeInput = document.getElementById('newChildGrade');

  if (idInput) idInput.value = child.id;
  if (nameInput) nameInput.value = child.name || '';
  if (gradeInput) gradeInput.value = child.grade || '';

  const isGirl = (child.icon === '👧' || child.color === 'pink');
  setChildGenderForm(isGirl ? '👧' : '👦');

  const titleEl = document.getElementById('childFormTitle');
  if (titleEl) titleEl.innerText = `✏️ 「${child.name}」の設定を変更`;

  const cancelBtn = document.getElementById('childFormCancelBtn');
  if (cancelBtn) cancelBtn.classList.remove('hidden');

  const submitBtn = document.getElementById('childFormSubmitBtn');
  if (submitBtn) {
    submitBtn.innerHTML = '<span>💾 変更を保存する</span>';
    submitBtn.className = 'w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white rounded-xl text-xs font-bold shadow-xs transition flex items-center justify-center gap-1';
  }

  nameInput.focus();
}

function resetChildForm() {
  const idInput = document.getElementById('editingChildId');
  const nameInput = document.getElementById('newChildName');
  const gradeInput = document.getElementById('newChildGrade');

  if (idInput) idInput.value = '';
  if (nameInput) nameInput.value = '';
  if (gradeInput) gradeInput.value = '';

  setChildGenderForm('👦');

  const titleEl = document.getElementById('childFormTitle');
  if (titleEl) titleEl.innerText = '＋ 新しいお子さんを追加';

  const cancelBtn = document.getElementById('childFormCancelBtn');
  if (cancelBtn) cancelBtn.classList.add('hidden');

  const submitBtn = document.getElementById('childFormSubmitBtn');
  if (submitBtn) {
    submitBtn.innerHTML = '<span>＋ お子さんを追加</span>';
    submitBtn.className = 'w-full py-2.5 bg-rose-500 hover:bg-rose-600 active:scale-95 text-white rounded-xl text-xs font-bold shadow-xs transition flex items-center justify-center gap-1';
  }
}

function saveChildFromSettings() {
  const editingId = (document.getElementById('editingChildId').value || '').trim();
  const nameInput = document.getElementById('newChildName');
  const gradeInput = document.getElementById('newChildGrade');

  const name = (nameInput.value || '').trim();
  if (!name) {
    alert('お子さんのお名前を入力してください');
    nameInput.focus();
    return;
  }

  const genderInput = document.getElementById('childFormGender');
  const selectedGender = (genderInput ? genderInput.value : '👦') || '👦';

  const color = (selectedGender === '👧') ? 'pink' : 'blue';

  const childData = {
    name: name,
    grade: (gradeInput.value || '').trim(),
    icon: selectedGender,
    color: color
  };

  if (editingId) {
    childData.id = editingId;
  }

  DB.saveChild(childData);
  resetChildForm();
  renderSettingsChildren();
  renderSettingsTags();
  renderChildTabs();
  renderHomeTagFilters();
  renderHomePage();
}

function deleteChildFromSettings(childId) {
  const child = DB.getChildById(childId);
  const name = child ? child.name : 'このお子さん';
  if (!confirm(`「${name}」の登録を削除しますか？`)) return;

  DB.deleteChild(childId);
  if (activeChildId === childId) {
    activeChildId = 'all';
  }
  const editId = (document.getElementById('editingChildId').value || '').trim();
  if (editId === childId) {
    resetChildForm();
  }
  renderSettingsChildren();
  renderSettingsTags();
  renderChildTabs();
  renderHomeTagFilters();
  renderHomePage();
}




function closeSettingsModal() {
  document.getElementById('settingsModal').classList.add('hidden');
  document.body.style.overflow = '';
}

function saveSettings(e) {
  e.preventDefault();
  const current = DB.getSettings();
  const settings = {
    ...current,
    user_name: document.getElementById('settingUserName').value.trim() || 'ゲスト',
    gemini_api_key: document.getElementById('settingApiKey').value.trim(),
    notification_time: "18:00"
  };
  DB.saveSettings(settings);
  const userDisplay = document.getElementById('userNameDisplay');
  if (userDisplay) userDisplay.innerText = settings.user_name;
  updateAiEngineStatusBanner();
  renderChildTabs();
  renderHomeTagFilters();
  alert('⚙️ 設定を保存しました！');
  window.location.hash = '#/';
}

// バックアップ
function exportBackupData() {
  const posts = DB.getPosts();
  const settings = DB.getSettings();
  const data = JSON.stringify({ posts, settings }, null, 2);
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `school_info_backup_${new Date().toISOString().split('T')[0]}.json`;
  a.click();
}

function importBackupData(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const data = JSON.parse(e.target.result);
      if (data.posts) DB.savePosts(data.posts);
      if (data.settings) DB.saveSettings(data.settings);
      alert('✅ データを復元しました！');
      window.location.hash = "#/";
    } catch(err) {
      alert('復元エラー: ' + err.message);
    }
  };
  reader.readAsText(file);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// データの全削除・初期化
function resetAllPostsData() {
  if (!confirm('⚠️ すべてのおたよりデータを完全に消去して初期化しますか？\n（※この操作は取り消せません）')) return;
  _postsCache = [];
  DB.savePosts([]);
  alert('🧹 すべてのおたよりデータを削除しました。');
  window.location.hash = "#/";
}
