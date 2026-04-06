# 🖼️ open-word-images

Open-source library of AI-generated word images. Consistent style, versioned, free to use.

## 🎨 Usage

### Stable version (won't change)
```html
<img src="https://raw.githubusercontent.com/krivich/open-word-images/main/styles/flat/cat_v1.png">
```

### Always latest
```html
<img src="https://raw.githubusercontent.com/krivich/open-word-images/main/styles/flat/cat_latest.png">
```

## 📚 Dictionary

Autocomplete and suggestions use [wordfreq-en-25000](https://github.com/aparrish/wordfreq-en-25000).
- **Author:** Allison Parrish
- **License:** CC-BY-SA 4.0
- **Words:** 25,000 most common English words with frequency scores

## 🤝 Contribute

1. Open [index.html](https://krivich.github.io/open-word-images/)
2. Search a word → if missing, click **🎨 Generate**
3. Insert your OpenAI API key → get image
4. Click **💾 Download & Contribute** → upload to repo via PR/Issue

## 📁 Structure
```
styles/
└── flat/
    ├── STYLE_PROMPT.md  # Fixed prompt for this style
    ├── cat_v1.png
    ├── cat_v2.png
    └── cat_latest.png
```

## 📜 License
- **Images & Code:** CC0-1.0 (Public Domain)
- **Dictionary:** CC-BY-SA 4.0 (Attribution required)
