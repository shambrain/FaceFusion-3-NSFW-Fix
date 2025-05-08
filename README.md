# FaceFusion 3.2 NSFW-Fix 🛡️

![Preview](https://github.com/user-attachments/assets/1f859424-0509-488d-84a2-bb7da15b4694)

> ⚠️ **IMPORTANT:** Always back up your original `content_analyser.py` before replacing it with any version here!

---
🙏 Specical thanks to [Digioso](https://github.com/Digioso) for input & feedback!
---
## 📂 Available Versions

### 🔹 `NSFW-Fix Only`
- Removes all NSFW filtering logic.
- Leaves everything else untouched.
- Recommended for users who want **full content control** without altering video handling.

### 🔹 `NSFW-Fix + Frame Skip`
- Also removes NSFW filtering logic.
- Adds safe handling for corrupted, unreadable, or empty frames.
- Recommended for users processing **large/batch video sets** or encountering OpenCV crashes.

---

## 🔧 What’s Fixed in Both Versions
- ✅ **NSFW model completely removed** — no loading, evaluation, or scoring.
- ✅ **Safe API compliance** — all expected hooks (`clear_inference_pool`, etc.) kept intact.
- ✅ **Compatible with FaceFusion 3.2** — including lip sync and face swap.
- ✅ **No fragile bypasses** — clean integration, no hacks or breakage.

---

## 🚫 What Was Causing Errors?
- `clear_inference_pool()` in FaceFusion 3.2 now expects a `model_names` list — fixed in both versions.
- Frame errors like:
  ```
  OpenCV(4.x): error: (-215:Assertion failed) !ssize.empty() in function 'resize'
  ```
  are resolved in the **Frame Skip** version.

---

## 🌟 Why Apply These Fixes?
- **Total Privacy** – All processing stays on your machine.
- **Creative Freedom** – Process your own content without restrictions.
- **No Online Checks** – NSFW filters are gone, nothing is uploaded or verified.
- **Stability Boost** – Frame skip version guards against crash-prone frames.

---

## ⚙️ How to Apply the NSFW Fix for FaceFusion 3.2

### 🧩 Option 1: 🖥️ Pinokio Version

1️⃣ **Download** the fixed `content_analyser.py` file (✅ NSFW-Fix or ✅ NSFW-Fix with Frame Skip).

2️⃣ **Open the folder** in File Explorer:  
📂  
```
C:\pinokio\api\facefusion-pinokio.git\facefusion\facefusion\
```

3️⃣ **Replace** the old file with the new one:
- ✂️ Delete the old `content_analyser.py`  
- 📥 Paste the new `content_analyser.py` into the folder

4️⃣ *(Optional)* 🔒 **Lock the file** to prevent overwrites:
- 🖱️ Right-click → 🛠️ Properties → ☑️ Check “Read-only” → ✅ Apply

---

### 🧩 Option 2: 💾 Locally Installed FaceFusion

1️⃣ **Locate** your FaceFusion folder. Typical paths:

🪟 Windows:  
📂  
```
C:\Users\<YourUsername>\facefusion\
```
or  
📂  
```
C:\facefusion-master\
```

🐧 macOS/Linux:  
📂  
```
~/facefusion/
```

2️⃣ **Navigate to** the internal facefusion directory:  
📁  
```
<your_installation_path>/facefusion/
```

3️⃣ **Replace** `content_analyser.py`:
- 📥 Drop in the fixed version to overwrite the old one

4️⃣ *(Optional)* 🔐 **Make it read-only**:

🪟 Windows:  
- 🖱️ Right-click → Properties → ☑️ Read-only

🐧 macOS/Linux:  
```bash
chmod 444 content_analyser.py
```

---

### ✅ Final Step: 🧪 Test It!

---

## 🧠 Developer Notes

### Frame Skip Logic (only in frame skip version):
```python
if vision_frame is None or vision_frame.size == 0:
    return None  # Prevent OpenCV resize crashes
```

### NSFW Filtering Removed:
- No `yolo_nsfw` model.
- No NSFW detection or scoring.
- `forward()` returns `0.0` by default.
- `inference_pool` and `model_set` are stubbed safely.

---

## ✅ About
These patches give you total control over your workflow. Whether you want a clean NSFW-free version or added robustness with frame skipping — the power is back in your hands.

---

## 💬 Final Thoughts
No filters. No crashes. No interruptions. Just smooth, unrestricted processing under your full control. 💪

---

📌 Choose your version in the repository and drop in your preferred `content_analyser.py`.

