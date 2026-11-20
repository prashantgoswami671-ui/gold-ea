/* ============================================================
   💛  EDIT THIS FILE  —  everything personal lives here.
   You do not need to touch any other file.
   ============================================================ */

window.GIFT = {

  /* ----------------------------------------------------------
     1. HER
     ---------------------------------------------------------- */
  herName: "Khushi",               // ← her real name (shown big on the opening screen)
  nickname: "Khushu",               // ← what you actually call her (used in the letter)
  fromName: "Yours, always",      // ← how the letter is signed
  birthdayDate: "21st November",   // ← shown on the letter

  /* ----------------------------------------------------------
     2. THE SONG
     Put an mp3 in the  music/  folder and keep the name "song.mp3".
     If the file is missing, a soft piano melody plays instead.
     ---------------------------------------------------------- */
  song: "music/song.mp3",

  /* ----------------------------------------------------------
     3. OPENING LINES
     These fade in one after another on the first screen.
     ---------------------------------------------------------- */
  heroLines: [
    "I couldn't wrap a whole year of you, so I made this instead.",
    "Every little thing in here is something I noticed, and kept.",
    "Take your time. It's all yours."
  ],

  /* ----------------------------------------------------------
     4. THE SCRAPBOOK
     Easiest: put six photos in the  photos/  folder named
     01.jpg … 06.jpg — they replace the placeholders automatically.
     Or point each "photo" below at any file you like.
     ---------------------------------------------------------- */
  memories: [
    {
      photo: "photos/her3.jpeg",
      caption: "Happy birthday, Khushi! 🎂✨ Keep your sparkle up, and thank you for coming into my life so unexpectedly 💛 I know it was unexpected, but kuch galtiyan bahut achi hoti hain 😌🌟",
      date: "unexpected, but perfect"
    },
    {
      photo: "photos/her_1.jpeg",
      caption: "well jada to kuch nahi bus is image ka liya kuch lines yad aa gaya “chand sa roshan chehra baalo ka rang sunhara 😌 ” one more appeal from you pleaase kuch bina face hide karka bhi photo bheja kar 😌🌅",
      date: "golden hour"
    },
    {
      photo: "photos/fan.png",
      caption: "This was the image I saved, and I found it so funny 😂 Your images and snaps make my day, yar. They're so funny to watch, and I love the way you look at things 💛 Never lose that humour, Khushi 🌀",
      date: "the funniest one"
    },
    {
      photo: "photos/curls.png",
      caption: "The best feature of you is your curly hair 💛 It's messy, but it looks so cool on you, and it makes you a solid 11/10 ✨🌀",
      date: "11 out of 10"
    }
  ],

  /* ----------------------------------------------------------
     5. THE WISH JAR
     Little notes she can open one by one.
     x / y are positions inside the jar (percent). Leave them
     as they are if you're not sure — they look good already.
     ---------------------------------------------------------- */
  wishNotes: [
    { x: 24, y: 58, title: "You are the calm", text: "Some people walk into a room and make it louder. You walk in and everything in me goes quiet, in the good way." },
    { x: 50, y: 42, title: "A confession", text: "I have replayed our conversations in my head more times than I will ever admit to you. This is me admitting it. Slightly." },
    { x: 72, y: 62, title: "Your laugh", text: "I would genuinely do embarrassing things just to hear it. I have done embarrassing things. Worth it every time." },
    { x: 34, y: 32, title: "The thing you do", text: "You tuck your hair behind your ear when you're concentrating. I noticed in week one. I never stopped noticing." },
    { x: 63, y: 24, title: "For the bad days", text: "On the days you feel like you're not enough — you are. Not because I say so. Because it's simply true." },
    { x: 19, y: 72, title: "A small promise", text: "I promise to remember the small things. Your coffee order. The songs you skip. The stories you tell twice." },
    { x: 81, y: 74, title: "If you're sad", text: "You don't have to be okay around me. You can just be. I'm not going anywhere because the weather changed." },
    { x: 46, y: 66, title: "The truth", text: "I like you on the ordinary days more than the extraordinary ones. That's how I know it's real." },
    { x: 58, y: 48, title: "One wish", text: "That this year is gentle with you. That you get everything you've been quietly hoping for. That I get to watch." }
  ],

  /* ----------------------------------------------------------
     6. THE GAME  ("Sing it back")
     She listens to a short melody on the stars, then taps it
     back. Each round adds one more note.
     melodyRounds: how many rounds (3 is easy, 5 is the default,
                   7 if you want her to work for it).
     ---------------------------------------------------------- */
  melodyRounds: 5,
  gameSecret: "You held the whole melody in your head. I've been holding onto you for a lot longer than five rounds — and I'm not planning on forgetting a single note.",

  /* ----------------------------------------------------------
     7. THE LETTER
     Each string is its own paragraph. Write as many as you want.
     ---------------------------------------------------------- */
  letter: [
    "Happy birthday, Khushi! 🎂 Thank you for coming into my life. I remember it was 1st April when you first messaged me. I know you were looking for someone else, but galti se koi aur ladka mil gaya, bhagwan ne thoda sa mazak kar diya. But ok, kuch galtiyan bahut achi hoti hain 😄",
    "And believe me, whatever you say, I find comfort in you. That's why I share everything with you, even things I don't share with my close friends. You are a kind soul with very good emotional intelligence. You tried to understand me, and you can even tell from my tone whether I'm sad or not. Not many people notice that, and you do it without making a big deal out of it.",
    "Yeah, many times I have hurt you, and it made me feel very bad. I know you got hurt by me many times and never came to tell me, because you are not that expressive. But I know you don't deserve that. You deserve someone who notices before you have to say it, and I am trying to be that person.",
    "In the end, for this legendary girl on her birthday, I pray that you always remain what you are and always stay happy. I will always try not to hurt you, and I will keep entertaining you. You are cool, and I don't want to lose you because of my behaviour. If I ever hurt you, come to me and scold me, but please don't leave.",
    "So happy birthday, {nickname}. I hope this year is as kind to you as you are to everyone around you 💛"
  ],

  /* ----------------------------------------------------------
     8. THE FINALE
     ---------------------------------------------------------- */
  finalQuestion: "One last thing. If I'm allowed to ask for something this year — will you let me be the one who gets to celebrate you, every year after this?",
  finalYes: "I was really hoping you'd say yes. Happy birthday, {nickname}. Here's to all the ordinary days we haven't had yet.",
  finalNoLabels: [
    "no",
    "wait, really?",
    "the button is shy",
    "try again?",
    "it keeps running",
    "just say yes",
    "okay it's rigged"
  ],
  finalFooter: "made by hand, with a ridiculous amount of love"
};
