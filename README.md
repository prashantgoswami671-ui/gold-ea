# For Her — a birthday gift

A little hand-built website: an envelope that opens, a scrapbook of memories,
a jar of wishes, a tiny melody game, a letter, and a fireworks finale.

Everything is plain HTML/CSS/JS — no build step, no install, works offline.

---

## 1. Put her name in

Open **`config.js`** — it is the only file you need to edit. At the top:

```js
herName: "Ananya",       // her name, shown big
nickname: "Anu",         // what you call her, used in the letter
fromName: "Yours, always",
birthdayDate: "20 November",
```

Everything else in that file is your words: the opening lines, the photo captions,
the nine jar notes, the letter, and the final question.

---

## 2. Add your photos

**The easy way:** drop six photos into **`photos/`** and name them
`01.jpg`, `02.jpg`, `03.jpg`, `04.jpg`, `05.jpg`, `06.jpg`.

They automatically replace the six placeholders — you don't have to edit
anything. (`.jpeg`, `.png` and `.webp` work too, as long as the name is
`01`, `02`, and so on. If a real photo exists, it wins over the placeholder.)

**The flexible way:** put your photos anywhere in the folder and point
`config.js` → `memories` at each one:

```js
{
  photo: "photos/us-at-the-beach.jpg",
  caption: "The first time you laughed at something I said…",
  date: "last summer"
}
```

- Keep the images roughly portrait (4:5) for the nicest polaroid look.
- You can add more than six — just add another `{ ... }` block.
- The six `01.svg … 06.svg` files are the pretty placeholders. You can leave
  them there; they only show up when there's no real photo with that number.

---

## 3. Add the song

Put an **mp3** in **`music/`** and name it exactly **`song.mp3`**.

That's it — it starts when she opens the envelope. There's a music button in the
bottom-right corner if she wants to pause it.

> If the file is missing, the page quietly plays a soft generated piano melody
> instead, so it never feels broken.

---

## 4. Try it

Just double-click **`index.html`**.

For the best result on her phone, put the whole folder online (free options):

- **Netlify Drop** — drag the folder onto <https://app.netlify.com/drop>, get a link.
- **GitHub Pages** — push the folder to a repo, enable Pages.
- **Vercel** — same idea.

Then send her the link. Or copy the folder to her phone and open `index.html`.

---

## What's inside

| File | What it does |
|---|---|
| `index.html` | the page |
| `styles.css` | all the visuals, animations, responsive layout |
| `config.js` | **your words** — edit this |
| `js/core.js` | stars, petals, music, scroll effects |
| `js/gift.js` | envelope, scrapbook, wish jar, letter |
| `js/play.js` | the melody game, fireworks, the final question |
| `photos/` | her photos (placeholders included) |
| `music/` | `song.mp3` goes here |

---

## Small notes

- Everything respects `prefers-reduced-motion` for people who get motion sickness.
- It works on phones, tablets and desktop. In the melody game she can tap the
  stars or press **1–5**.
- The melody game is forgiving on purpose: a wrong note only replays the melody,
  it never loses her progress. Change the number of rounds with
  `melodyRounds` in `config.js` (5 is the default).
- The "no" button runs away. That's on purpose. 🙂
- To start over, just refresh the page.

Made to be given away.
