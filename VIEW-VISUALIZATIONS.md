# 📊 Quick Guide: Viewing Project Visualizations

## 🚀 Fastest Way: Built-in HTML Preview (No Extension Needed!)

### Quick Preview in Cursor:
1. **Open `index.html`** in Cursor
2. **Press `Ctrl+K V`** (Windows/Linux) or **`Cmd+K V`** (Mac)
3. Preview opens **side-by-side** with auto-refresh! ✨

### Alternative: Live Server Extension

### 1️⃣ Install Live Server Extension
- Open Extensions (Ctrl+Shift+X)
- Search: **"Live Server"** by Ritwick Dey
- Click **Install**

### 2️⃣ Start Live Server
**Option A:** Right-click `index.html` → **"Open with Live Server"**  
**Option B:** Click **"Go Live"** button in status bar (bottom-right)  
**Option C:** Press `Ctrl+Shift+P` → Type "Live Server: Open with Live Server"

### 3️⃣ View Visualizations
Your browser opens automatically! Navigate using the homepage or direct links:

- 🏠 **Homepage:** http://127.0.0.1:5500/index.html
- 🏗️ **Architecture:** http://127.0.0.1:5500/system-architecture-viewer.html
- 📊 **Dashboard:** http://127.0.0.1:5500/ai_bridge_dashboard.html
- ⚡ **Live Dashboard:** http://127.0.0.1:5500/dashboard-live-system.html
- 🔍 **Claim Viewer:** http://127.0.0.1:5500/claim-analysis-viewer.html
- 🔒 **Security:** http://127.0.0.1:5500/security-compliance.html
- 💰 **Cost Analysis:** http://127.0.0.1:5500/cost-savings.html

---

## 🖥️ Alternative Methods

### Double-Click Method
Just double-click any `.html` file in your file explorer!

### Python HTTP Server
```bash
python -m http.server 8000
# Then visit http://localhost:8000/index.html
```

### Node.js http-server
```bash
npx http-server -p 8000
# Then visit http://localhost:8000/index.html
```

---

## 🎯 Method 3: Simple Browser (In Cursor)

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P`)
2. Type: **"Simple Browser: Show"**
3. Enter: `file:///d:/aUp/Devan/Projects/insurance-ai-bridge/index.html`

Opens HTML in a browser tab **inside Cursor**!

> 💡 **See detailed guide:** [.vscode/HTML-PREVIEW-GUIDE.md](.vscode/HTML-PREVIEW-GUIDE.md)

---

## 📁 All Available Visualizations

1. **index.html** - Project homepage with navigation to all visualizations
2. **system-architecture-viewer.html** - Complete technical architecture
3. **ai_bridge_dashboard.html** - Interactive claim processing dashboard
4. **dashboard-live-system.html** - Live system with data streaming
5. **claim-analysis-viewer.html** - Step-by-step AI claim analysis
6. **security-compliance.html** - HIPAA compliance and security features
7. **cost-savings.html** - ROI and cost savings visualization

---

**💡 Tip:** Start with `index.html` - it's the central hub with links to everything!

For detailed Live Server instructions, see [.vscode/README-LIVE-SERVER.md](.vscode/README-LIVE-SERVER.md)
