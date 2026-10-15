const React = window.React;
const useState = React.useState;
const tabs = [['home', '首页', '⌂'], ['library', '世界图书馆', '▤'], ['search', '搜索', '⌕'], ['profile', '我的', '○']];
const books = [['古典名著选编', 'CLASSICAL TEXTS', 'linear-gradient(145deg,#b9a46a,#5a4520 56%,#1b201b)'], ['世界文学经典', 'WORLD LITERATURE', 'linear-gradient(145deg,#5a8970,#214f3b 58%,#17221a)'], ['基础语法入门', 'BASIC GRAMMAR', 'linear-gradient(145deg,#7990a0,#354657 58%,#192128)'], ['阿拉伯故事集', 'FOLKTALES', 'linear-gradient(145deg,#a06c43,#5a3521 58%,#231b15)']];
function Nav({
  active,
  onChange
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "absolute bottom-3 left-3 right-3 z-20 grid grid-cols-4 rounded-2xl border border-white/10 bg-[#191c1c]/90 px-1 py-2 shadow-2xl backdrop-blur-xl"
  }, tabs.map(([id, label, icon]) => /*#__PURE__*/React.createElement("button", {
    key: id,
    onClick: () => onChange(id),
    className: `flex flex-col items-center gap-1 rounded-xl py-1 text-[9px] transition ${active === id ? 'text-[#ead99f]' : 'text-white/45'}`
  }, /*#__PURE__*/React.createElement("span", {
    className: "text-lg leading-5"
  }, icon), /*#__PURE__*/React.createElement("span", null, label))));
}
function Phone({
  initial
}) {
  const [page, setPage] = useState(initial);
  return /*#__PURE__*/React.createElement("div", {
    className: "relative mx-auto h-[520px] w-[244px] overflow-hidden rounded-[34px] border-[5px] border-[#292c2b] bg-[#0f1111] shadow-[0_28px_70px_rgba(0,0,0,.34)] ring-1 ring-white/30"
  }, /*#__PURE__*/React.createElement("div", {
    className: "absolute left-1/2 top-2 z-30 h-5 w-[74px] -translate-x-1/2 rounded-full bg-black"
  }), /*#__PURE__*/React.createElement("div", {
    className: "absolute left-4 right-4 top-3 z-30 flex justify-between text-[8px] text-white/75"
  }, /*#__PURE__*/React.createElement("span", null, "9:41"), /*#__PURE__*/React.createElement("span", null, "\u25AE\u25AE  Wi-Fi  \u25B0")), /*#__PURE__*/React.createElement("div", {
    className: "h-full overflow-y-auto px-3 pb-20 pt-10"
  }, page === 'home' && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("header", {
    className: "text-center"
  }, /*#__PURE__*/React.createElement("div", {
    className: "text-[18px] font-semibold tracking-wide text-[#ead99f]"
  }, "\u0623\u0647\u0644\u0627\u064B \u0628\u0643 \u0641\u064A \u0631\u0627\u0646\u062F\u0646\u062C"), /*#__PURE__*/React.createElement("div", {
    className: "mt-1 text-[10px] text-white/50"
  }, "\u71C3\u706F\u540C\u5B66 \xB7 Nour")), /*#__PURE__*/React.createElement("button", {
    onClick: () => setPage('profile'),
    className: "mx-auto mt-10 flex h-40 w-40 flex-col items-center justify-center rounded-full border border-[#e7d18c]/50 bg-[radial-gradient(circle_at_32%_25%,#fff0bd,#b59247_25%,#136b54_60%,#0d1713_82%)] text-[#fff0bd] shadow-[0_0_44px_rgba(213,182,97,.26)]"
  }, /*#__PURE__*/React.createElement("span", {
    className: "font-serif text-6xl"
  }, "\u0646\u0648\u0631"), /*#__PURE__*/React.createElement("span", {
    className: "mt-1 text-[9px] tracking-[.3em]"
  }, "NOUR AI")), /*#__PURE__*/React.createElement("section", {
    className: "mt-8 rounded-2xl border border-white/10 bg-white/[.055] p-4 text-center"
  }, /*#__PURE__*/React.createElement("div", {
    className: "text-[9px] uppercase tracking-[.28em] text-[#baaa77]"
  }, "\u6BCF\u65E5\u4E00\u53E5"), /*#__PURE__*/React.createElement("div", {
    dir: "rtl",
    className: "mt-3 font-serif text-[23px] leading-relaxed text-[#ead99f]"
  }, "\u0627\u0644\u0639\u0650\u0644\u0652\u0645\u064F \u0643\u064E\u0646\u0652\u0632\u064C \u0644\u064E\u0627 \u064A\u064E\u0641\u0652\u0646\u064E\u0649\u0670"), /*#__PURE__*/React.createElement("p", {
    className: "mt-2 text-[11px] text-white/75"
  }, "\u77E5\u8BC6\u662F\u6C38\u4E0D\u6D88\u901D\u7684\u5B9D\u85CF")), /*#__PURE__*/React.createElement("section", {
    className: "mt-3 rounded-2xl border border-white/10 bg-white/[.04] p-3"
  }, /*#__PURE__*/React.createElement("div", {
    className: "flex justify-between text-[10px] text-white/70"
  }, /*#__PURE__*/React.createElement("span", null, "\u5B66\u4E60\u8FDB\u5EA6"), /*#__PURE__*/React.createElement("b", {
    className: "text-[#ead99f]"
  }, "\u4ECA\u65E5")), /*#__PURE__*/React.createElement("div", {
    className: "mt-3 h-1 rounded bg-white/10"
  }, /*#__PURE__*/React.createElement("i", {
    className: "block h-full w-2/5 rounded bg-gradient-to-r from-emerald-700 to-[#e4c878]"
  })))), page === 'library' && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("header", {
    className: "flex items-center justify-between"
  }, /*#__PURE__*/React.createElement("h2", {
    className: "text-[17px] font-semibold"
  }, "\u4E16\u754C\u56FE\u4E66\u9986"), /*#__PURE__*/React.createElement("span", {
    className: "text-[#e4c878]"
  }, "\u25CE")), /*#__PURE__*/React.createElement("div", {
    className: "mt-4 flex gap-2 overflow-hidden"
  }, ['思想', '历史', '文学', '语言'].map(x => /*#__PURE__*/React.createElement("button", {
    key: x,
    className: "rounded-full border border-white/10 px-3 py-1 text-[9px] text-white/65"
  }, x))), /*#__PURE__*/React.createElement("div", {
    className: "mt-4 grid grid-cols-2 gap-3"
  }, books.map(([title, sub, bg]) => /*#__PURE__*/React.createElement("button", {
    key: title,
    onClick: () => setPage('search'),
    className: "rounded-xl border border-white/[.07] bg-white/[.035] p-2 text-left"
  }, /*#__PURE__*/React.createElement("div", {
    className: "flex h-32 items-center justify-center rounded-lg border border-[#e5cf86]/40 p-2 shadow-lg",
    style: {
      background: bg
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "flex h-full w-full flex-col items-center justify-center border border-[#f1dfad]/40 text-center"
  }, /*#__PURE__*/React.createElement("span", {
    className: "font-serif text-[12px] leading-5 text-[#f2dfaa]"
  }, title), /*#__PURE__*/React.createElement("span", {
    className: "mt-2 text-[6px] tracking-wider text-[#f2dfaa]/65"
  }, sub))), /*#__PURE__*/React.createElement("span", {
    className: "mt-2 block text-[9px] text-white/75"
  }, title))))), page === 'search' && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("h2", {
    className: "text-[17px] font-semibold"
  }, "\u67E5\u5355\u8BCD & \u53E5\u5B50\u67E5\u8BE2"), /*#__PURE__*/React.createElement("input", {
    className: "mt-5 w-full rounded-xl border border-white/10 bg-white/[.05] px-3 py-3 text-right text-[11px] outline-none placeholder:text-white/30",
    placeholder: "\u0627\u0628\u062D\u062B \u0639\u0646 \u0643\u0644\u0645\u0629 \u0623\u0648 \u0639\u0628\u0627\u0631\u0629\u2026"
  }), /*#__PURE__*/React.createElement("div", {
    className: "mt-3 grid grid-cols-3 gap-2"
  }, ['查单词', '句子分析', '全文翻译'].map(x => /*#__PURE__*/React.createElement("button", {
    key: x,
    className: "rounded-xl border border-white/10 bg-white/[.045] px-1 py-3 text-[9px] text-[#ead99f]"
  }, x))), /*#__PURE__*/React.createElement("div", {
    className: "mt-6 text-[10px] text-white/55"
  }, "\u6700\u8FD1\u67E5\u8BE2"), ['كِتَابٌ', 'نور', 'العِلْمُ'].map((x, i) => /*#__PURE__*/React.createElement("div", {
    key: x,
    className: "border-b border-white/[.07] py-4"
  }, /*#__PURE__*/React.createElement("div", {
    dir: "rtl",
    className: "font-serif text-xl text-[#ead99f]"
  }, x), /*#__PURE__*/React.createElement("div", {
    className: "mt-1 text-[9px] text-white/55"
  }, ['书；著作', '光；灯', '知识；学问'][i])))), page === 'profile' && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("h2", {
    className: "text-[17px] font-semibold"
  }, "\u6211\u7684\u71C3\u706F"), /*#__PURE__*/React.createElement("section", {
    className: "mt-5 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[.05] p-4"
  }, /*#__PURE__*/React.createElement("div", {
    className: "grid h-12 w-12 place-items-center rounded-full bg-gradient-to-br from-[#ead99f] to-emerald-900 font-serif text-2xl"
  }, "\u0646"), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "text-[12px]"
  }, "\u4F60\u597D\uFF0C\u5B66\u4E60\u8005"), /*#__PURE__*/React.createElement("div", {
    className: "mt-1 text-[9px] text-white/50"
  }, "Level 5 \xB7 Arabic learner"))), /*#__PURE__*/React.createElement("section", {
    className: "mt-4 rounded-2xl border border-white/10 bg-white/[.04] p-4"
  }, /*#__PURE__*/React.createElement("h3", {
    className: "text-[12px]"
  }, "\u6D4F\u89C8\u8DB3\u8FF9"), ['《世说新语》', '基础语法入门', 'كِتَابٌ · 书'].map(x => /*#__PURE__*/React.createElement("div", {
    key: x,
    className: "border-b border-white/[.06] py-3 text-[10px] text-white/65"
  }, "\u25C9\u3000", x))), ['学业成就', '外观设置', '帮助与支持'].map(x => /*#__PURE__*/React.createElement("button", {
    key: x,
    className: "mt-2 flex w-full justify-between rounded-xl border border-white/[.08] bg-white/[.035] p-3 text-[10px] text-white/75"
  }, /*#__PURE__*/React.createElement("span", null, x), /*#__PURE__*/React.createElement("span", {
    className: "text-[#ead99f]"
  }, "\u203A"))))), /*#__PURE__*/React.createElement(Nav, {
    active: page,
    onChange: setPage
  }), /*#__PURE__*/React.createElement("div", {
    className: "absolute bottom-[4px] left-1/2 z-30 h-1 w-20 -translate-x-1/2 rounded-full bg-white/80"
  }));
}
function App() {
  return /*#__PURE__*/React.createElement("main", {
    className: "min-h-screen bg-[#f2f1ed] px-8 py-10 text-[#171817]"
  }, /*#__PURE__*/React.createElement("header", {
    className: "mx-auto mb-8 flex max-w-5xl items-end justify-between"
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("p", {
    className: "text-[10px] uppercase tracking-[.32em] text-[#7b776c]"
  }, "NOUR \xB7 ARABIC LEARNING"), /*#__PURE__*/React.createElement("h1", {
    className: "mt-2 text-2xl font-semibold tracking-tight"
  }, "\u71C3\u706F\u540C\u5B66 \xB7 \u56DB\u5C4F\u754C\u9762")), /*#__PURE__*/React.createElement("span", {
    className: "text-xs text-[#77736a]"
  }, "\u5168\u5C4F\u5BFC\u822A \xB7 \u8BBE\u8BA1\u9884\u89C8")), /*#__PURE__*/React.createElement("section", {
    className: "mx-auto grid max-w-5xl grid-cols-2 gap-x-12 gap-y-10 rounded-[28px] bg-white p-10 shadow-[0_20px_70px_rgba(32,30,24,.09)] max-[650px]:grid-cols-1 max-[650px]:p-5"
  }, /*#__PURE__*/React.createElement(Phone, {
    initial: "home"
  }), /*#__PURE__*/React.createElement(Phone, {
    initial: "library"
  }), /*#__PURE__*/React.createElement(Phone, {
    initial: "search"
  }), /*#__PURE__*/React.createElement(Phone, {
    initial: "profile"
  })));
}
ReactDOM.createRoot(document.getElementById("root")).render(React.createElement(App));
