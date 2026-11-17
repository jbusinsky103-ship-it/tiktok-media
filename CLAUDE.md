# tiktok-media — daily content pipeline for TikTok @manipulation.edu

Media host for scheduled TikTok posts. Files here are public; Metricool fetches them via
`https://raw.githubusercontent.com/jbusinsky103-ship-it/tiktok-media/main/<path>`.

## Brand
- Niche: dark psychology (manipulation, attraction, power, relationships, body language, toxic people). English text.
- Product: ebook "Principles of Dark Psychology" — free version + full book, link in bio (linktr.ee/jbusinsky103).
- Style: black background, dark red radial glow, red accent #e02a00, white serif headlines, gray sans body, thin red corner marks.
- Best-performing format: "How to …" / "Signs …" lists, e.g. "How to make anyone love you", "How to win every argument".

## Formats
- **Cards (TikTok photo carousel):** 6 slides, 1080x1350. Slide 1 hook + teaser ("#2 hurts the most"),
  slides 2–5 one point each, slide 6 takeaway + "FREE EBOOK — LINK IN BIO".
  Copy `templates/cards_example.html` (keep its CSS), replace the text, render:
  `python3 templates/render_cards.py <dir_with_cards.html> <prefix>` → writes PNGs to /mnt/user-data/outputs/<prefix>_N.png
  (edit the output path in the script if that dir doesn't exist). Move them to `posts/YYYY-MM-DD/<slug>/`.
- **Video:** 1080x1920 silent MP4, ~20–25 s. Write a scenes JSON (see docstring) and run
  `python3 templates/make_video.py scenes.json posts/YYYY-MM-DD/<slug>.mp4`. Ends with book-cover CTA.

## Daily run
1. Read `topics_used.md`; pick 5 NEW topics (never repeat). Mix: 3 card posts + 2 videos.
2. Render each; look at every output image/frame before committing (check text fits, nothing cut off).
3. Commit to `posts/YYYY-MM-DD/`, push to main, verify each raw URL returns 200.
4. Schedule each in Metricool (blogId 7006725, network tiktok, timezone Europe/Warsaw) for the NEXT day at
   10:00, 12:00, 14:00, 16:00, 18:00. tiktokData: title (required), privacyOption PUBLIC_TO_EVERYONE,
   autoAddMusic true, isAigc false for cards. autoPublish true, draft false.
   Caption: 1 hook line + engagement question ("Which one hit hardest? Comment the number 👇") + "Free ebook in bio 🧠" + 4–6 hashtags incl. #darkpsychology #fyp.
5. Append the 5 topics with date to `topics_used.md`, commit and push.
6. If anything fails (push refused, Metricool error, network not connected), stop and report — don't retry endlessly.
