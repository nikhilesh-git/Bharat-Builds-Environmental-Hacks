# Kabadi Connect — 3-Minute Demo Video Script & Test Inputs

**Team Roles during Demo Recording:**
- **Teammate B (You):** Screen Driver (clicks, speaks, types, triggers Hindi/English toggle, demonstrates polling & live accept).
- **Teammate A:** Narrator (explains the problem, architecture, AWS Bedrock Strands agent, and impact).
- **Teammate C:** Screen Recorder & Timekeeper (OBS / ScreenStudio recording, checks video quality & audio sync).

---

## Part 1: Prepared Demo Test Inputs (10-Input Suite)

Use these exact inputs to showcase how the agent handles quantities, implied items, Hindi Devanagari, English, and mixed Hinglish:

| # | Test Input String | Language / Mode | Expected Items Detected | Assumed Flag Check |
|---|---|---|---|---|
| 1 | `10 किलो अखबार, 5 किलो गत्ता, एक पुरानी लोहे की कुर्सी` | Hindi | Newspaper (10kg), Cardboard (5kg), Iron (4kg) | Iron `assumed: true` (chair weight assumed) |
| 2 | `15 kg newspaper, 20 pet bottles, 4 kg scrap iron` | English | Newspaper (15kg), PET Bottles (20pcs/2kg), Iron (4kg) | Accurate rate ranges |
| 3 | `पुराना कूलर, लोहे की जाली, 8 बीयर की बोतलें` | Hindi | Iron / Cooler (15kg), Bottles (2kg) | Cooler `assumed: true` |
| 4 | `broken ceiling fan, 2 kg copper wire, 10 kg cardboard` | English | E-waste/Fan (8kg), Copper (2kg), Cardboard (10kg) | Copper high rate (₹450+/kg) |
| 5 | `25 kg raddi paper, 5 plastic chairs, broken mixer grinder` | Hinglish | Mixed paper (25kg), Hard plastic (6kg), E-waste (3kg) | High total range |
| 6 | `एक टूटी लोहे की अलमारी और 30 किलो अखबार` | Hindi | Iron (15kg), Newspaper (30kg) | Iron `assumed: true` |
| 7 | `12 kg books, old study notebooks, 4 empty paint buckets` | English | Books (12kg), Plastic (4kg) | Transparent breakdown |
| 8 | `तांबे के तार 1.5 kg, एल्युमिनियम के बर्तन 3 kg` | Hindi | Copper (1.5kg), Aluminium (3kg) | Premium scrap valuation |
| 9 | `only 5 plastic water bottles` | English | PET Bottles (1kg) | Small volume handled |
| 10 | `घर का पुराना कबाड़ और रद्दी` | Hindi | General scrap fallback (5kg) | Graceful fallback estimate |

---

## Part 2: Second-by-Second 3-Minute Demo Script

### 🕒 0:00 - 0:35 — The Hook & Problem Statement (Split Screen / Household View)
- **Screen:** Open `/household` on the left half of the screen, `/kabadi` on the right half (or mobile emulator side-by-side).
- **B Action:** Highlight the default Hindi interface: "कबाड़ी कनेक्ट — घर बैठे कबाड़ बेचें". Toggle the language switch (`English / हिंदी`) to show seamless instant localization. Keep it in Hindi.
- **Narrator (A):**
  > "Millions of Indian households accumulate recyclable scrap—newspapers, plastics, metals, and e-waste—but lack price transparency. Meanwhile, informal waste collectors (kabadiwalas) struggle with unpredictable collection routes.
  > Today, we present **Kabadi Connect**, built on AWS. It gives households an instant, fair price estimate powered by an intelligent agent, and connects them directly with local collectors in real-time."

---

### 🕒 0:35 - 1:15 — Intelligent Scrap Valuation (Household Side)
- **B Action:**
  1. Click the microphone button or type Input #1:
     `"10 किलो अखबार, 5 किलो गत्ता, एक पुरानी लोहे की कुर्सी"`
  2. Click the big green CTA: **"कीमत का अनुमान लगाएं (Get Price Estimate)"**.
  3. The estimate table appears with a smooth transition.
- **Narrator (A):**
  > "Notice what just happened. The household described their scrap naturally. Our AWS Bedrock Strands agent parsed the text, queried our real-time scrap rates tool, and noticed that while newspapers and cardboard had explicit weights, the 'iron chair' didn't.
  > The agent intelligently flagged the iron chair as **अनुमानित (Assumed)** with an estimated 4 kg weight, giving a total payout estimate of ₹230 to ₹280. No surprises at the doorstep."

---

### 🕒 1:15 - 1:55 — Doorstep Pickup Booking & Status Polling
- **B Action:**
  1. Enter name: `"सुनीता शर्मा (Sunita Sharma)"`.
  2. Locality: `"लाजपत नगर IV, दिल्ली"`.
  3. Select time slot: `"कल सुबह (10:00 AM - 12:00 PM)"`.
  4. Click **"कबाड़ीवाला बुलाएं (Book Pickup)"**.
  5. The screen transitions to the live **Status Card**.
  6. Point out the animated radar pulse: **"कबाड़ीवाले की प्रतीक्षा में... (Waiting for a kabadiwala...)"** polling `GET /requests/{id}` every 5 seconds.
- **Narrator (A):**
  > "With a single click, Sunita books a pickup. The request is persisted and published to our event bus, broadcasting to verified collectors in the area. The household's screen is now actively live-polling every 5 seconds."

---

### 🕒 1:55 - 2:35 — Kabadiwala Portal & Live Acceptance Loop
- **B Action:**
  1. Shift focus to the `/kabadi` tab.
  2. Show the pre-seeded sample data badge: **"नमूना डेटा (Sample Data)"** alongside Sunita's real incoming request at the top of the list!
  3. Collector name is set to: `"रमेश कुमार (Ramesh Kumar)"`.
  4. Click the large green **"स्वीकार करें (Accept Pickup)"** button on Sunita's card.
  5. The card instantly moves to **"मेरे स्वीकृत अनुरोध (Accepted Pickups)"**.
  6. Switch back to the `/household` tab. Within 5 seconds, watch the radar turn into:
     **"🎉 रमेश कुमार कल सुबह (10:00 AM - 12:00 PM) पर आपके पते पर आ रहे हैं!"**
- **Narrator (A):**
  > "Over on the Kabadiwala dashboard, Ramesh Kumar sees open requests in his locality with the scrap breakdown and estimated cash needed.
  > When Ramesh clicks 'Accept', the backend updates DynamoDB/SQLite and notifies the household. Sunita's screen immediately updates without a page reload: Ramesh is confirmed for tomorrow morning."

---

### 🕒 2:35 - 3:00 — Architecture, AWS Stack & Closing
- **B Action:** Show clean responsive UI (toggle English mode, open inspect mobile view 375px to prove 48px+ touch targets and mobile-first responsiveness).
- **Narrator (A):**
  > "Kabadi Connect uses:
  > - **Amazon Bedrock & Strands Agents SDK** with a rules-based fallback safety net.
  > - **FastAPI on AWS Lambda with Function URL** via Mangum for single-deploy zero-CORS architecture.
  > - **DynamoDB and Amazon SNS** for scalable storage and notifications.
  > Kabadi Connect digitizes circular waste management in India, giving fair value to families and empowering frontline recycling workers. Thank you!"
