/**
 * Kabadi Connect - Frontend Logic (app.js)
 * Teammate B: Plain vanilla ES6, zero build step, relative API URLs
 */

// 1. Comprehensive Multilingual Dictionary (Hindi Default)
const i18n = {
  hi: {
    brand_title: "कबाड़ी कनेक्ट",
    brand_tagline: "घर बैठे कबाड़ बेचें • सही दाम और तुरंत पिकअप",
    nav_household: "घर के लिए (Household)",
    nav_kabadi: "कबाड़ीवाला पोर्टल (Collector)",
    toggle_lang: "English में देखें",

    // Household Page
    hero_title: "घर का कबाड़ बेचें, तुरंत सही दाम जानें",
    hero_subtitle: "अखबार, गत्ता, लोहा, प्लास्टिक या ई-कचरा — कुछ भी लिखिए या बोलिए। AI तुरंत अनुमानित कीमत बताएगा।",
    step1_heading: "1. कबाड़ का विवरण दें",
    input_placeholder: "उदाहरण: 10 किलो अखबार, 5 किलो गत्ता, एक पुरानी लोहे की कुर्सी, 10 पानी की बोतलें...",
    mic_btn_title: "बोलकर दर्ज करें (Speak in Hindi)",
    mic_listening: "🎙️ सुन रहे हैं... बोलिए",
    mic_unsupported: "माइक्रोफ़ोन इस ब्राउज़र में समर्थित नहीं है",
    chips_title: "त्वरित उदाहरण (क्लिक करें):",
    chip1: "10 किलो अखबार, 5 किलो गत्ता",
    chip2: "पुराना कूलर, लोहे की जाली, 8 बीयर की बोतलें",
    chip3: "15 प्लास्टिक की बोतलें, टूटा पंखा, तांबे का तार",
    btn_estimate: "कीमत का अनुमान लगाएं",
    btn_estimating: "अनुमान लगाया जा रहा है...",

    // Estimate Table
    estimate_heading: "अनुमानित दर और कुल मूल्य",
    table_material: "सामग्री (Item)",
    table_qty: "मात्रा (Quantity)",
    table_rate: "अनुमानित दर (Rate)",
    table_price: "अनुमानित मूल्य (Value)",
    badge_assumed: "अनुमानित",
    assumed_tooltip: "इस आइटम की मात्रा/वजन का AI द्वारा अंदाज़ा लगाया गया है",
    total_estimated_label: "कुल अनुमानित भुगतान:",
    approx_note: "* सभी दरें अनुमानित हैं। वास्तविक वजन कबाड़ीवाले के आने पर कांटा (digital scale) से तय होगा।",

    // Step 2 Booking
    step2_heading: "2. पिकअप का समय और पता चुनें",
    label_name: "आपका नाम",
    name_placeholder: "उदा. सुनीता शर्मा",
    label_locality: "इलाका / पता",
    locality_placeholder: "उदा. लाजपत नगर IV, मालवीय नगर, रोहिणी सेक्टर 7...",
    label_slot: "पिकअप का समय (Time Slot)",
    slot_today_afternoon: "आज दोपहर (2:00 PM - 4:00 PM)",
    slot_today_evening: "आज शाम (4:00 PM - 6:00 PM)",
    slot_tomorrow_morning: "कल सुबह (10:00 AM - 12:00 PM)",
    slot_tomorrow_afternoon: "कल दोपहर (2:00 PM - 4:00 PM)",
    btn_book_pickup: "कबाड़ीवाला बुलाएं (Book Pickup)",
    btn_booking: "अनुरोध दर्ज हो रहा है...",

    // Status Card
    status_card_heading: "अनुरोध की स्थिति (Live Status)",
    status_waiting_title: "कबाड़ीवाले की प्रतीक्षा में...",
    status_waiting_desc: "आपका अनुरोध पास के कबाड़ीवालों को भेज दिया गया है। जैसे ही कोई स्वीकार करेगा, आपको यहाँ दिखेगा।",
    status_accepted_title: "कबाड़ीवाला आ रहा है!",
    status_accepted_msg: "{collector} {slot} पर आपके पते पर आ रहे हैं।",
    status_req_id: "अनुरोध संख्या (ID):",
    status_customer: "ग्राहक का नाम:",
    status_locality: "स्थान:",
    status_slot: "समय स्लॉट:",
    status_scrap_summary: "कबाड़ का ब्योरा:",
    status_total: "अनुमानित मूल्य:",
    btn_new_request: "नया अनुरोध बनाएं",

    // Kabadiwala Page
    kabadi_hero_title: "कबाड़ीवाला साथी पोर्टल",
    kabadi_hero_subtitle: "अपने इलाके में घरों से सीधे कबाड़ पिकअप स्वीकार करें।",
    label_collector_name: "आपका नाम दर्ज करें (Collector Name):",
    collector_name_placeholder: "उदा. रमेश कुमार / सुरेश कबाड़ी",
    tab_open_requests: "उपलब्ध अनुरोध (Open Requests)",
    tab_accepted_requests: "मेरे स्वीकृत अनुरोध (Accepted)",
    badge_sample: "नमूना डेटा (Sample)",
    btn_accept: "पिकअप स्वीकार करें",
    btn_accepting: "स्वीकार किया जा रहा है...",
    btn_accepted_badge: "स्वीकृत (Accepted)",
    no_open_requests: "वर्तमान में कोई नया खुला अनुरोध उपलब्ध नहीं है। 5 सेकंड में ऑटो-रिफ्रेश हो रहा है...",
    no_accepted_requests: "आपने अभी तक कोई अनुरोध स्वीकार नहीं किया है।",
    collector_name_required: "कृपया पहले ऊपर अपना नाम दर्ज करें!",

    // Common Alerts & Errors
    err_title: "त्रुटि (Error)",
    err_network: "सर्वर से संपर्क नहीं हो पाया। कृपया पुनः प्रयास करें।",
    btn_retry: "पुनः प्रयास करें",
    toast_accepted_success: "पिकअप सफलतापूर्वक स्वीकार कर लिया गया!",
    auto_refresh_badge: "🔴 लाइव अपडेट (हर 5 सेकंड)"
  },
  en: {
    brand_title: "Kabadi Connect",
    brand_tagline: "Doorstep Scrap Selling • Fair Rates & Fast Pickup",
    nav_household: "Household",
    nav_kabadi: "Collector Portal",
    toggle_lang: "हिंदी में देखें",

    // Household Page
    hero_title: "Sell Household Scrap at Fair Market Rates",
    hero_subtitle: "Newspaper, cardboard, iron, plastics or e-waste — type or speak. AI estimates prices instantly.",
    step1_heading: "1. Describe Your Scrap",
    input_placeholder: "e.g., 10 kg newspaper, 5 kg cardboard, old iron chair, 10 plastic bottles...",
    mic_btn_title: "Voice Input (Speech to Text)",
    mic_listening: "🎙️ Listening... Speak now",
    mic_unsupported: "Speech recognition not supported in this browser",
    chips_title: "Quick Examples (click to fill):",
    chip1: "10 kg newspaper, 5 kg cardboard",
    chip2: "Broken cooler, iron grill, 8 glass beer bottles",
    chip3: "15 plastic bottles, broken ceiling fan, copper wire",
    btn_estimate: "Get Price Estimate",
    btn_estimating: "Estimating Scrap Value...",

    // Estimate Table
    estimate_heading: "Estimated Rates & Value",
    table_material: "Material / Item",
    table_qty: "Quantity",
    table_rate: "Est. Rate",
    table_price: "Est. Value",
    badge_assumed: "Assumed",
    assumed_tooltip: "Weight/quantity was approximated by the AI agent",
    total_estimated_label: "Total Estimated Payout:",
    approx_note: "* All rates are approximate. Final weight will be verified on digital scale upon doorstep pickup.",

    // Step 2 Booking
    step2_heading: "2. Select Pickup Slot & Address",
    label_name: "Your Name",
    name_placeholder: "e.g., Sunita Sharma",
    label_locality: "Locality / Address",
    locality_placeholder: "e.g., Lajpat Nagar IV, Malviya Nagar, Rohini...",
    label_slot: "Preferred Time Slot",
    slot_today_afternoon: "Today Afternoon (2:00 PM - 4:00 PM)",
    slot_today_evening: "Today Evening (4:00 PM - 6:00 PM)",
    slot_tomorrow_morning: "Tomorrow Morning (10:00 AM - 12:00 PM)",
    slot_tomorrow_afternoon: "Tomorrow Afternoon (2:00 PM - 4:00 PM)",
    btn_book_pickup: "Book Pickup Request",
    btn_booking: "Submitting Request...",

    // Status Card
    status_card_heading: "Pickup Request Live Status",
    status_waiting_title: "Waiting for a kabadiwala...",
    status_waiting_desc: "Your request is broadcast to nearby verified collectors. Once accepted, updates appear here.",
    status_accepted_title: "Kabadiwala Confirmed!",
    status_accepted_msg: "{collector} is coming at {slot}.",
    status_req_id: "Request ID:",
    status_customer: "Customer Name:",
    status_locality: "Locality:",
    status_slot: "Time Slot:",
    status_scrap_summary: "Items Summary:",
    status_total: "Estimated Payout:",
    btn_new_request: "Create Another Request",

    // Kabadiwala Page
    kabadi_hero_title: "Kabadiwala Partner Dashboard",
    kabadi_hero_subtitle: "Accept verified doorstep scrap pickup requests in your locality.",
    label_collector_name: "Your Name (Collector Name):",
    collector_name_placeholder: "e.g., Ramesh Kumar / Suresh Kabadi",
    tab_open_requests: "Open Requests",
    tab_accepted_requests: "My Accepted Pickups",
    badge_sample: "Sample Data",
    btn_accept: "Accept Pickup",
    btn_accepting: "Accepting...",
    btn_accepted_badge: "Accepted",
    no_open_requests: "No open requests available right now. Auto-refreshing every 5s...",
    no_accepted_requests: "You have not accepted any requests yet.",
    collector_name_required: "Please enter your collector name above first!",

    // Common Alerts & Errors
    err_title: "Error",
    err_network: "Could not connect to server. Please try again.",
    btn_retry: "Retry",
    toast_accepted_success: "Pickup accepted successfully!",
    auto_refresh_badge: "🔴 Live Sync (every 5s)"
  }
};

// 2. Language Management
function getCurrentLang() {
  return localStorage.getItem("kabadi_lang") || "hi";
}

function setLang(lang) {
  localStorage.setItem("kabadi_lang", lang);
  updateStaticTranslations();
  // Trigger custom event for page-specific rerenders
  window.dispatchEvent(new CustomEvent("langchange", { detail: { lang } }));
}

function toggleLang() {
  const current = getCurrentLang();
  const next = current === "hi" ? "en" : "hi";
  setLang(next);
}

function t(key, replacements = {}) {
  const lang = getCurrentLang();
  let str = (i18n[lang] && i18n[lang][key]) || (i18n["hi"] && i18n["hi"][key]) || key;
  for (const [k, v] of Object.entries(replacements)) {
    str = str.replace(`{${k}}`, v);
  }
  return str;
}

function updateStaticTranslations() {
  const lang = getCurrentLang();
  document.documentElement.lang = lang;
  
  // Update all elements with data-i18n
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (i18n[lang] && i18n[lang][key]) {
      el.textContent = i18n[lang][key];
    }
  });

  // Update placeholders with data-i18n-placeholder
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (i18n[lang] && i18n[lang][key]) {
      el.placeholder = i18n[lang][key];
    }
  });

  // Update language toggle button text
  const toggleBtn = document.getElementById("lang-toggle-btn");
  if (toggleBtn) {
    toggleBtn.innerHTML = `🌐 <span class="font-bold">${i18n[lang].toggle_lang}</span>`;
  }
}

// 3. Audio & Speech Recognition (webkitSpeechRecognition)
let recognition = null;
let isListening = false;

function initSpeechRecognition(textareaId, micBtnId, statusMsgId) {
  const textarea = document.getElementById(textareaId);
  const micBtn = document.getElementById(micBtnId);
  const statusMsg = document.getElementById(statusMsgId);

  if (!micBtn) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    // Hide microphone button if not supported in the browser
    micBtn.style.display = "none";
    return;
  }

  try {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onstart = () => {
      isListening = true;
      micBtn.classList.add("mic-active");
      if (statusMsg) {
        statusMsg.classList.remove("hidden");
        statusMsg.textContent = t("mic_listening");
      }
    };

    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      if (textarea) {
        textarea.value = transcript;
      }
    };

    recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      stopListening();
    };

    recognition.onend = () => {
      stopListening();
    };

    micBtn.addEventListener("click", () => {
      if (isListening) {
        stopListening();
      } else {
        startListening();
      }
    });

  } catch (err) {
    console.warn("Speech recognition initialization error:", err);
    micBtn.style.display = "none";
  }

  function startListening() {
    if (!recognition) return;
    const lang = getCurrentLang();
    recognition.lang = lang === "hi" ? "hi-IN" : "en-IN";
    try {
      recognition.start();
    } catch (e) {
      console.error(e);
    }
  }

  function stopListening() {
    isListening = false;
    if (micBtn) micBtn.classList.remove("mic-active");
    if (statusMsg) statusMsg.classList.add("hidden");
    if (recognition) {
      try { recognition.stop(); } catch (e) {}
    }
  }
}

// 4. API Client with Relative URLs and Standard Error Format
async function apiPost(endpoint, body) {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const lang = getCurrentLang();
    const errMsg = (data && (lang === "hi" ? data.message_hi : data.message_en)) || 
                   (data && data.error) || 
                   t("err_network");
    throw new Error(errMsg);
  }

  return data;
}

async function apiGet(endpoint) {
  const response = await fetch(endpoint, {
    headers: { "Accept": "application/json" }
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const lang = getCurrentLang();
    const errMsg = (data && (lang === "hi" ? data.message_hi : data.message_en)) || 
                   (data && data.error) || 
                   t("err_network");
    throw new Error(errMsg);
  }

  return data;
}

// Global Export for household.html and kabadi.html
window.KabadiApp = {
  i18n,
  t,
  getCurrentLang,
  setLang,
  toggleLang,
  updateStaticTranslations,
  initSpeechRecognition,
  apiPost,
  apiGet
};
