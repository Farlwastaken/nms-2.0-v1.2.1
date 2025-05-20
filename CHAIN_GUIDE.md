# How to Continue This Project (GitHub Chain Guide)

This project is passed from one person to the next. Each person builds on the last version by creating a new GitHub branch such as `v1`, `v2`, `v3`, etc.

You do **not** need to know Git deeply — just follow the steps below.

---

## Step-by-Step Instructions

### 1. **Create a GitHub account** (if you don’t have one)

Go to [https://github.com](https://github.com) and sign up.

---

### 2. **Fork this project**

- Visit the original project repository:  
  https://github.com/Farlwastaken/nms2.0

- Click the **"Fork"** button on the top-right of the page.

This creates your own copy of the project under your GitHub account.

---

### 3. **Install Git (if you don’t have it)**

- Windows: [https://git-scm.com/download/win](https://git-scm.com/download/win)  
- macOS: [https://git-scm.com/download/mac](https://git-scm.com/download/mac)  
- Linux: Install via your package manager

---

### 4. **Clone your fork to your computer**

> Replace `yourusername` with your actual GitHub username

Open a terminal (Command Prompt or Terminal), and run:

```bash
git clone https://github.com/yourusername/project-name.git
cd project-name
```

---

### 5. **Create your own branch**

First, see what the latest version is (e.g., `v2` is the last one).  
Then create a new branch (e.g., `v3`) based on it:

```bash
git checkout -b v3 origin/v2
```

> Replace `v2` with the current latest version  
> Replace `v3` with your new version name

---

### 6. **Work on the project**

- Make your code changes
- Test your work

---

### 7. **Save your changes**

```bash
git add .
git commit -m "Summary of what you added and/or changed"
```

---

### 8. **Push your work to GitHub**

```bash
git push origin v3
```

---

### 9. **Submit your work to the original repository**

1. Go to your fork on GitHub (e.g., `https://github.com/yourusername/project-name`)
2. GitHub should show a **“Compare & pull request”** button. Click it.
3. Set these options:
   - **Base repository:** `yourname/project-name`
   - **Base branch:** `v3`
   - **Head repository:** your fork
   - **Head branch:** `v3`
4. Give the pull request a title like:  
   `"v3: YourName - Added new feature X"`
5. Click **“Create Pull Request”**

---

## That’s All

Once approved, you should have successfully added your work as the next version in the chain.

This keeps all versions in one place and gives each contributor credit.

---

## Example Chain

```text
main → v1 → v2 → v3 → v4 → ...
```

Each person adds the next link in the chain. Do not delete or overwrite older branches.