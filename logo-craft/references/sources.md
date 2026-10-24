# Sources

Annotated bibliography behind this skill. Every fact in the other reference files traces to one of these; when a reference file says "verified October 2026" it means the primary page was read on 2026-10-24. Books are listed for their arguments, not quoted. Sections: 1 Philosophy and method · 2 Perception and colour science · 3 Typography and lettering · 4 Calligraphy · 5 Case studies (primary accounts) · 6 Platform specifications · 7 Standards (SVG, WCAG, fonts, trademarks) · 8 Trends and critique · 9 Tooling · 10 Prior art (other logo skills) · 11 Research documents in this repo.

## 1. Philosophy and method

- Paul Rand, *Logos, Flags, and Escutcheons* (1991) — https://www.paulrand.design/writing/articles/1991-logos-flags-and-escutcheons.html — the "a logo identifies, it does not explain" argument and the list of qualities a mark should have. Primary.
- Paul Rand, work pages for ABC and UPS — https://www.paulrand.design/work/ABC.html , https://www.paulrand.design/work/United-Parcel-Service.html — Primary (estate site).
- Sagi Haviv / Chermayeff & Geismar & Haviv, identity principles and the Chase, NBC projects — https://cghnyc.com/work/project/identity-chermayeff-geismar-haviv , https://cghnyc.com/work/project/chase-bank , https://cghnyc.com/work/project/nbc — appropriate / distinctive and memorable / simple; the doodle test. Primary.
- Massimo Vignelli, *The Vignelli Canon* (PDF) — https://designmanifestos.org/wp-content/uploads/2020/04/vignelli-canon.pdf — semantics, syntactics, pragmatics; discipline; timelessness. Primary.
- Michael Bierut, *How to...* (2nd ed.) — https://www.pentagram.com/news/michael-bierut-s-how-to-updated-with-second-edition — identity as a system; the mark is the seed, not the whole. Secondary (publisher page); arguments from the book.
- Alina Wheeler, *Designing Brand Identity* (5th/6th ed.) — https://www.wiley.com/en-us/designing-brand-identity-a-comprehensive-guide-to-the-world-of-brands-and-branding-6th-edition-p-9781119984825 — five-phase process (research, strategy, design, touchpoints, management). Secondary (publisher page).
- David Airey, *Logo Design Love* and the design-process pages — https://www.logodesignlove.com/book , https://www.davidairey.com/process , https://archive.davidairey.com/branding/the-ideal-design-process/ — practitioner process, mind-mapping, sketching in black first. Primary (author site).
- George Bokhua, *Principles of Logo Design* — https://www.quarto.com/books/9780760376515/principles-of-logo-design — geometric construction, grids as organisation, finishing by eye. Secondary (publisher page).
- Chris Do / The Futur, "The 3 rules of good logo design" — https://thefutur.com/content/the-3-rules-of-good-logo-design — Secondary; practitioner summary.
- Taschen, *Logo Modernism* — https://www.taschen.com/en/books/graphic-design/02879/logo-modernism/ — the modernist corpus the geometric vocabulary comes from. Secondary.
- Pentagram, brand identity overview — https://www.pentagram.com/brand-identity — Primary (studio).

## 2. Perception and colour science

- Wagemans et al., "A century of Gestalt psychology in visual perception" (2012) — https://pmc.ncbi.nlm.nih.gov/articles/PMC3482144/ — grouping principles as used in perception.md. Primary (peer-reviewed).
- Elliot & Maier, "Color psychology: effects of perceiving color on psychological functioning in humans", *Annual Review of Psychology* (2014) — https://www.annualreviews.org/content/journals/10.1146/annurev-psych-010213-115035/ — why "blue means trust" is folklore; context-dependence of colour effects. Primary.
- Björn Ottosson, "A perceptual color space for image processing" (OKLab) — https://bottosson.github.io/posts/oklab/ — the OKLab/OKLCH maths used by palette.py. Primary.
- MDN, `oklch()` — https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/color_value/oklch — Primary (browser support, syntax).
- Color.js gamut mapping and colour spaces — https://colorjs.io/docs/gamut-mapping.html , https://colorjs.io/docs/spaces.html — reference for clamping OKLCH into sRGB. Secondary.
- Machado, Oliveira & Fernandes (2009), CVD simulation model (as implemented in DaltonLens) — https://github.com/DaltonLens/DaltonLens-Python — the matrices behind `simulate_cvd`. Secondary (implementation of the paper).
- Josef Albers, *Interaction of Color* — https://yalebooks.yale.edu/book/9780300179354/interaction-of-color/ — simultaneous contrast; colours are relative. Secondary (publisher).
- Fast Company, "Debunking the myth of Apple's golden ratio" — https://www.fastcompany.com/1672682/debunking-the-myth-of-apple-s-golden-ratio — why retrofitted construction diagrams prove nothing. Secondary.

## 3. Typography and lettering

- Tobias Frere-Jones, *Typeface Mechanics 001* and *002* — https://frerejones.com/blog/typeface-mechanics-001 , https://frerejones.com/blog/typeface-mechanics-002 — overshoot, optical centre, horizontals thinner than verticals, apparent size of round vs flat shapes. Primary (practitioner).
- Monotype, "Lack of overshoots" — https://foundrysupport.monotype.com/hc/en-us/articles/360029597112-Lack-of-Overshoots — Primary (foundry).
- Design With FontForge, "Trusting your eyes" — https://designwithfontforge.com/en-US/Trusting_Your_Eyes.html — optical illusions in letterforms. Primary (open book).
- Gunnlaugur Briem via FontLab, "Illusion" — https://help.fontlab.com/fontlab/8/tutorials/briem/2-0-basics/briem-2-06-illusion/ — Primary (practitioner).
- Ellen Lupton, *Thinking With Type* — https://www.chroniclebooks.com/products/thinking-with-type-1 — classification, spacing, hierarchy. Secondary (publisher).
- Karen Cheng, *Designing Type* — https://yalebooks.yale.edu/book/9780300249927/designing-type/ — construction of letters, proportion. Secondary (publisher).
- Ken Barber / House Industries, *Lettering Manual* — https://www.penguinrandomhouse.com/books/536312/house-industries-lettering-manual-by-ken-barber/ — lettering as drawing; the skeleton-then-weight method. Secondary (publisher).
- Jessica Hische, *In Progress* — https://www.chroniclebooks.com/products/in-progress-revised-edition — lettering process, spacing checks. Secondary (publisher).
- Monotype, typography terms and definitions — https://www.monotype.com/resources/expertise/typography-terms-and-definitions — vocabulary. Primary.
- Grilli Type, information on licensing — https://cdn.grillitype.com/information — example of a commercial foundry's logo-use licence. Primary (foundry).
- Fonts In Use — https://fontsinuse.com/ — what faces real identities use; competitor shelf research. Secondary (archive).
- Letterform Archive — https://letterformarchive.org/about/ — Secondary (archive).
- Doyald Young — https://www.doyaldyoung.com/about/ — logotype lettering, script logos. Secondary.
- Adobe, "Design a typographic logo" — https://www.adobe.com/learn/illustrator/web/design-typographic-logo — Secondary (tutorial; used only for workflow vocabulary).

## 4. Calligraphy

- Gerrit Noordzij, *The Stroke* (theory summarised at TypeMedia) — https://typemedia.org/noordzij — translation / expansion / rotation model of contrast. Primary (school page summarising the book).
- Paul Shaw, "Calligraphy: the basics of italic" — https://www.paulshawletterdesign.com/2011/10/tutorial-no-5%E2%80%94calligraphy-the-basics-of-italic-2/ — italic pen angle, slant, nib-widths. Primary (practitioner).
- Calligraphy Skills, Gothic / Textura — https://www.calligraphy-skills.com/gothic-writing.html — Secondary (tutorial).
- Calligrascape, blackletter — https://calligrascape.com/learn-blackletter-calligraphy/ — Secondary.
- Faber-Castell, calligraphy alphabet types — https://www.faber-castell.com/tutorials/Artists/calligraphy-alphabet-types — Secondary (overview of hands).
- Calligraphy Museum, Copperplate vs Spencerian — https://www.calligraphy-museum.com/en/news/news/discovering-the-secret-of-differences-between-the-copperplate-and-spenserian-scripts — slant angles, shade placement. Secondary.
- John Neal Books, pointed-pen guideline sheets — https://www.johnnealbooks.com/product/pointed-pen-guidline-sheets — the 55° Copperplate / 52° Spencerian guideline convention. Secondary (supplier).
- Jim Bennett, *Calligraphy for Dummies* (PDF mirror) — https://library.ucaphil.online/assets/files/Calligraphy-ForDummies.pdf — nib-width tables for Foundational, Uncial, Italic. Secondary; the figures agree with Shaw and Faber-Castell.

## 5. Case studies (primary accounts)

- Nike, "The Swoosh logo history" — https://about.nike.com/en/magazine/nike-swoosh-logo-history
- Rob Janoff on the Apple logo — https://www.robjanoff.com/aboutrob , https://9to5mac.com/2018/03/26/interview-apple-logo-designer-rob-janoff/
- IBM Design Language, 8-bar logo — https://www.ibm.com/design/language/ibm-logos/8-bar/
- Pentagram, Mastercard (2016/2019) — https://www.pentagram.com/work/mastercard/story
- Pentagram, Slack (2019) — https://www.pentagram.com/work/slack
- Pentagram, MIT Media Lab — https://www.pentagram.com/news/mit-media-lab
- DesignStudio, Airbnb — https://www.design.studio/work/air-bnb
- Lindon Leader on the FedEx logo (interview) — https://thesneeze.com/the-man-behind-the-fedex-logo/
- Amazon 2000 logo press release — https://press.aboutamazon.com/2000/1/amazon-com-introduces-new-logo-new-design-communicates-customer-satisfaction-and-a-to-z-selection
- Google, "Evolving the Google identity" (2015) — https://design.google/library/evolving-google-identity
- Instagram 2016 (Meta newsroom) and Mackey Saturday on the 2013 script — https://about.fb.com/ja/news/2016/05/instagram_newlook/ , https://c9dd.com/mackey-saturday-designs-instagrams-new-logo/
- Gap 2010 reversal — https://www.gapinc.com/en-gb/articles/2010/10/gap-listens-to-customers-and-will-keep-classic-blu
- Tropicana 2009 (academic case study) — https://ageconsearch.umn.edu/record/104330/files/RP%202009-2.pdf
- Kia 2021 ("KN" misreading) — https://www.motortrend.com/features/kia-logo
- Jaguar 2024 — https://media.jlr.com/archive-jaguar/en-us/news/2024/11/fearless-exuberant-compelling-jaguar-reimagined-0
- London 2012 (Wolff Olins) — https://wolffolins.com/news/the-making-of-the-london-2012-olympic-games-logo-by-wolff-olins
- UPS 2003 media kit — https://www.underconsideration.com/speakup_v2/ups_media_kit.pdf
- Pepsi 2023 — https://www.pepsico.com/newsroom/press-releases/2023/pepsi-unveils-a-new-logo-and-visual-identity-marking-the-iconic-brands-next-era
- Burberry 2023 — https://www.burberryplc.com/news/brand/2023/introducing-the-first-creative-expression-of-burberry-under-dani
- Nokia 2023 (Form 20-F describes the brand refresh) — https://www.nokia.com/system/files/2025-04/nokia-form-20-f-2024_0.pdf
- OpenAI brand guidelines (2025) — https://openai.com/brand/ ; coverage: https://www.wallpaper.com/tech/openai-has-undergone-its-first-ever-rebrand-giving-fresh-life-to-chatgpt-interactions
- Coca-Cola red and script — https://www.coca-colacompany.com/about-us/history/coca-cola-red-our-second-secret-formula
- Ford script history — https://www.me.ford.com/en/lbn/history-and-heritage/
- Kellogg's history — https://www.kelloggs.com/en-tr/who-we-are/our-history.html
- Disney signature — https://d23.com/walt-disney-signature1/
- Cadbury 2020 — https://pentawards.com/live/en/node/newsitem-cadbury-celebrates-new-global-brand-identity
- Toblerone (Mondelez) — https://www.mondelezinternational.com/our-brands/toblerone/
- Baskin-Robbins 2022 — https://news.baskinrobbins.com/news/baskin-robbins-aims-to-inspire-everyone-to-seize-the-yay-through-rebrand-and-new-campaign
- Michelin Man — https://guide.michelin.com/en/article/features/8-surprising-facts-about-the-michelin-man

## 6. Platform specifications (verified 2026-10-24)

- Apple HIG, App icons — https://developer.apple.com/design/human-interface-guidelines/app-icons — layered icons, Default/Dark/Clear/Tinted, no baked effects, watchOS sizes.
- Apple, Icon Composer — https://developer.apple.com/icon-composer/ , https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer
- Apple, Configuring your app icon (Xcode) — https://developer.apple.com/documentation/xcode/configuring-your-app-icon
- Apple design resources (templates) — https://developer.apple.com/design/resources/
- WWDC25 session 361 and WWDC26 session 8012 (icon design) — https://developer.apple.com/videos/play/wwdc2025/361/ , https://developer.apple.com/videos/play/wwdc2026/8012/
- Apple, Configuring web applications (apple-touch-icon) — https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/ConfiguringWebApplications/ConfiguringWebApplications.html
- Android adaptive icons — https://developer.android.com/develop/ui/compose/system/icon_design_adaptive — 108 dp canvas, 72 dp visible, 66 dp safe zone, monochrome layer.
- Google Play icon specification — https://developer.android.com/distribute/google-play/resources/icon-design-specifications — 512 × 512 PNG, ≤1024 KB, no transparency.
- web.dev, Web app manifest — https://web.dev/learn/pwa/web-app-manifest — 192/512, `purpose: maskable`.
- web.dev, Adaptive favicon — https://web.dev/articles/building/an-adaptive-favicon — SVG favicon with `prefers-color-scheme`.
- WHATWG HTML, `rel=icon` — https://html.spec.whatwg.org/multipage/links.html#rel-icon
- Open Graph protocol — https://ogp.me/ ; Facebook thumbnail sizing — https://wordpress.com/support/facebook-image-thumbnail/
- GitHub profile reference (avatar) — https://docs.github.com/en/enterprise-server%403.20/account-and-profile/reference/profile-reference
- Slack workspace icon — https://slack.com/help/articles/204379773-Upload-a-Slack-icon
- Discord server profile — https://support.discord.com/hc/en-us/articles/30715364399511-Server-Profile
- Pantone coated vs uncoated — https://support.pantone.com/en/what-does-the-terms-coated-and-uncoated-mean-in-the-pantone-graphics-system

## 7. Standards

- SVG 2: paths, painting (fill, fill-rule, stroke, color) — https://www.w3.org/TR/SVG2/paths.html , https://www.w3.org/TR/SVG2/painting.html#FillRuleProperty , https://www.w3.org/TR/SVG2/painting.html#StrokeProperties , https://www.w3.org/TR/SVG2/painting.html#ColorProperty
- MDN SVG: viewBox, title, symbol — https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/viewBox , https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/title
- WCAG 2.2 contrast minimum and non-text contrast (logo exemption; 3:1 for UI components) — https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum , https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast
- SIL Open Font License, FAQ and Reserved Font Names — https://openfontlicense.org/ , https://openfontlicense.org/ofl-faq/ , https://openfontlicense.org/ofl-reserved-font-names/
- Google Fonts FAQ (logo use allowed) and CSS2 API / technical considerations — https://fonts.google.com/faq , https://developers.google.com/fonts/docs/css2 , https://developers.google.com/fonts/docs/technical_considerations , https://github.com/google/fonts
- Adobe Fonts licensing (logo use allowed under subscription) — https://helpx.adobe.com/fonts/web/font-licensing/font-licensing.html
- Trademark search: USPTO federal search and design search codes — https://www.uspto.gov/trademarks/search/federal-trademark-searching , https://www.uspto.gov/trademarks/search/design-search-codes ; EUIPO — https://www.euipo.europa.eu/en/search-ip ; WIPO Global Brand Database and Nice classification — https://www.wipo.int/documents/d/global-brand-database/docs-en-user-guide.pdf?download=true , https://www.wipo.int/classifications/nice
- OpenType GPOS (kerning) — https://learn.microsoft.com/en-us/typography/opentype/spec/gpos ; HarfBuzz clusters — https://harfbuzz.github.io/working-with-harfbuzz-clusters.html

## 8. Trends and critique

- LogoLounge 2026 and 2025 trend reports — https://www.logolounge.com/trend/2026-logo-trend-report , https://www.logolounge.com/trend/2025-logo-trend-report — Primary (annual survey of submitted work).
- Brand New (UnderConsideration) — https://www.underconsideration.com/brandnew/ — redesign critique archive; Secondary (opinion, but documents what shipped).
- Logobook — https://logobook.com/about-us/ — historical corpus for look-alike checks. Secondary.
- Adobe, generative vectors in Illustrator; Recraft AI vector generator — https://helpx.adobe.com/illustrator/desktop/use-generative-ai/generate-scenes-subjects-and-icons.html , https://www.recraft.ai/ai-vector-generator — what AI vector tools output (noted as the source of the "AI aesthetic"). Secondary.

## 9. Tooling

- fontTools (TTFont, SVGPathPen, BoundsPen, varLib.instancer) — https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html , https://fonttools.readthedocs.io/en/latest/pens/svgPathPen.html , https://fonttools.readthedocs.io/en/latest/pens/boundsPen.html , https://fonttools.readthedocs.io/en/latest/varLib/instancer.html
- uharfbuzz — https://github.com/harfbuzz/uharfbuzz
- skia-pathops (boolean union of outlines) — https://github.com/fonttools/skia-pathops
- librsvg / rsvg-convert — https://gnome.pages.gitlab.gnome.org/librsvg/devel-docs/man-rsvg-convert.html , https://gnome.pages.gitlab.gnome.org/librsvg/devel-docs/features.html
- resvg — https://github.com/linebender/resvg
- CairoSVG support table — https://cairosvg.org/svg_support/
- ImageMagick formats — https://imagemagick.com/formats/ ; macOS `sips` — https://keith.github.io/xcode-man-pages/sips.1.html
- Pillow ICO and getcolors — https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#ico , https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.getcolors
- SVGO convertPathData — https://svgo.dev/docs/plugins/convertPathData/
- Inkscape command line — https://wiki.inkscape.org/wiki/Using_the_Command_Line
- Chrome headless — https://developer.chrome.com/docs/automation-and-testing/headless-cli
- Clipper2 (polygon offsetting theory used by pen_sweep) — https://www.angusj.com/clipper2/Docs/Overview.htm ; Paper.js PathItem (boolean ops reference) — https://paperjs.org/reference/pathitem/
- Agent Skills format — https://agentskills.io/home ; skill-creator — https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md

## 10. Prior art

- op7418, logo-generator-skill — https://github.com/op7418/logo-generator-skill/blob/bf4e9ac4d4428bda261afcfe981871ceb92d94e6/SKILL.md — a prompt-only skill that generates SVG logos from a short brief with a style list. Studied for what it lacks: no project reading, no typography engine, no small-size testing, no deliverables.
- kaankiziltug, logo-design-skill — https://github.com/kaankiziltug/logo-design-skill , SKILL.md and testing-checklist.md , TRADEMARKS.md — ships a library of famous marks as reference (and a trademark notice); its testing checklist informed critique.md. This skill bundles no third-party marks.

## 11. Research documents in this repo

- `research/chatgpt-research.md` — the user's ChatGPT deep-research export (professional logo design research), 2026-10.
- `research/codex-design-research.md` and `research/codex-tech-research.md` — Codex CLI (gpt-5 class, high reasoning, web search) research runs, prompts in `research/codex-prompt-*.md`, 2026-10-24.
- `research/fable-research.md` — Claude Fable 5.1 research notes and the synthesis decisions (what was adopted, what was rejected and why).
