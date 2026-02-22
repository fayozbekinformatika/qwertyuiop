# GitHub'ga Yuklash Qo'llanmasi

## 1. Git Bash ni oching
- Windows'da "Git Bash" ni qidiring va oching

## 2. Loyiha papkasiga kiring
```bash
cd /e/merenhub_project
```

## 3. Git ni ishga tushiring
```
bash
git init
```

## 4. Barcha fayllarni qo'shing
```
bash
git add .
```

## 5. Commit yozing
```
bash
git commit -m "Learning section - Backend/Frontend categories"
```

## 6. GitHub'da yangi repository yarating
- github.com saytida tizimga kiring
- "+" tugmasini bosing -> "New repository"
- Repository nomi: `merenhub`
- "Create repository" bosing

## 7. Remote qo'shing va push qiling
```
bash
git branch -M main
git remote add origin https://github.com/USERNAME/merenhub.git
git push -u origin main
```

**Eslatma**: `USERNAME` o'rniga o'z GitHub username'ingizni yozing.

---

## Agar xatolik bo'lsa:
```
bash
git remote remove origin
git remote add origin https://github.com/USERNAME/merenhub.git
git push -u origin main
