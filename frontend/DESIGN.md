---
name: Pancham Rural Development System
colors:
  surface: '#fbf9f4'
  surface-dim: '#dbdad5'
  surface-bright: '#fbf9f4'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3ee'
  surface-container: '#f0eee9'
  surface-container-high: '#eae8e3'
  surface-container-highest: '#e4e2dd'
  on-surface: '#1b1c19'
  on-surface-variant: '#414844'
  inverse-surface: '#30312e'
  inverse-on-surface: '#f2f1ec'
  outline: '#717973'
  outline-variant: '#c1c8c2'
  surface-tint: '#3f6653'
  primary: '#012d1d'
  on-primary: '#ffffff'
  primary-container: '#1b4332'
  on-primary-container: '#86af99'
  inverse-primary: '#a5d0b9'
  secondary: '#a7373b'
  on-secondary: '#ffffff'
  secondary-container: '#ff7a7a'
  on-secondary-container: '#74101a'
  tertiary: '#162c0a'
  on-tertiary: '#ffffff'
  tertiary-container: '#2b421e'
  on-tertiary-container: '#93af81'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c1ecd4'
  primary-fixed-dim: '#a5d0b9'
  on-primary-fixed: '#002114'
  on-primary-fixed-variant: '#274e3d'
  secondary-fixed: '#ffdad8'
  secondary-fixed-dim: '#ffb3b0'
  on-secondary-fixed: '#410007'
  on-secondary-fixed-variant: '#861f25'
  tertiary-fixed: '#cfebb9'
  tertiary-fixed-dim: '#b3cf9f'
  on-tertiary-fixed: '#0b2003'
  on-tertiary-fixed-variant: '#364d28'
  background: '#fbf9f4'
  on-background: '#1b1c19'
  surface-variant: '#e4e2dd'
typography:
  display-lg:
    fontFamily: Source Serif 4
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 60px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Source Serif 4
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Source Serif 4
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Source Serif 4
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-xs:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  container-margin: 20px
  gutter: 16px
---

## Brand & Style

The design system is anchored in the values of stewardship, growth, and community resilience. It is tailored for a rural development platform that must bridge the gap between institutional authority and grassroots accessibility. The visual language avoids the cold, clinical feel of standard enterprise software in favor of a "Human-Centric Institutional" style—professional enough for government stakeholders, yet warm and legible for field workers and rural citizens.

The aesthetic blends **Modern Corporate** reliability with **Tactile/Organic** warmth. It prioritizes clarity and high contrast to ensure usability in varied lighting conditions (such as outdoor field use) and on diverse mobile hardware. The emotional goal is to evoke a sense of grounded progress and trusted partnership.

## Colors

The palette is derived from the natural landscape of rural development. 

- **Primary (Forest Green):** Used for primary actions, navigation headers, and brand-level elements to signal stability and growth.
- **Secondary (Terracotta):** Reserved for meaningful accents, call-to-outs, and specific interactive elements that require distinction without being aggressive.
- **Backgrounds:** A tiered system using soft cream (#F9F7F2) for page backgrounds to reduce eye strain, and pure white (#FFFFFF) for cards and interactive surfaces to create a clear "layer" effect.
- **Semantic Colors:** Success states utilize subtle sage greens rather than harsh neon greens, maintaining the calm, professional tone of the interface.

## Typography

This design system employs a dual-font strategy to balance tradition with modern utility.

- **Headlines (Source Serif 4):** A professional serif that feels authoritative and established. It is used for page titles and section headers to provide a "documentary" feel that respects the gravity of rural development work.
- **Body & UI (Plus Jakarta Sans):** A friendly, highly legible sans-serif chosen for its generous x-height and open counters. This ensures that data-heavy tables and forms remain readable on small screens.

**Bilingual Support:** 
For English and Marathi pairings, the Marathi text should typically be set 10-15% larger than the English equivalent to maintain visual weight parity. Always ensure the Marathi typeface used in production supports the same weight variants as the English fonts.

## Layout & Spacing

The layout philosophy follows a **Fixed Grid** on desktop (12 columns, 1200px max-width) and a **Fluid Content** model on mobile. 

- **Vertical Rhythm:** An 8px baseline grid ensures consistent vertical pacing.
- **Whitespace:** Generous padding is applied within cards and containers to avoid a "cluttered" feeling, which is essential for users who may be less tech-literate.
- **Mobile First:** Given the context of rural development, the primary layout target is a mobile device. Touch targets for all interactive elements must be a minimum of 44x44px.
- **Sidebars:** Desktop views utilize a fixed left-hand navigation sidebar to provide a persistent "home base" for the user.

## Elevation & Depth

This design system uses a **Tonal Layering** approach combined with **Ambient Shadows**. 

Instead of heavy borders or deep shadows, hierarchy is established by placing white cards (#FFFFFF) on a cream background (#F9F7F2). Depth is enhanced by a single "Elevated" state:
- **Shadow Profile:** A very soft, diffused shadow (Y: 4px, Blur: 12px, Opacity: 6%) using a hint of the primary green color in the shadow tint to keep it organic.
- **Interaction:** On hover or active state, elements may slightly increase their shadow spread to provide tactile feedback without looking "game-like."

## Shapes

The shape language is "Soft-Modern." Elements use a consistent radius of 12px for standard components (buttons, input fields) and 16px for larger containers (cards, modals). This level of roundedness (Level 2) conveys friendliness and approachability, breaking away from the rigid, sharp corners of traditional government or enterprise software. 

Circular shapes are reserved exclusively for status indicators (avatars, notification dots) and select icon backgrounds to maintain clear functional distinction.

## Components

- **Cards:** The primary container. Always white background, 16px corner radius, and 24px internal padding. Use a subtle 1px border (#E5E5E0) instead of a shadow for low-elevation cards.
- **Buttons:** 
  - *Primary:* Solid Forest Green with white text.
  - *Secondary:* Outlined Terracotta for destructive or alternative actions.
  - *Tertiary:* Ghost style for low-priority navigation.
- **Bilingual Labels:** When displaying English and Marathi together, use a vertical stack with the primary language in **Label-SM (Bold)** and the secondary language in **Label-XS (Medium)** with 50% opacity.
- **Input Fields:** 12px corner radius, 1.5px border. On focus, the border transitions to Forest Green with a 2px outer glow in Sage Green.
- **Status Badges:** Use the "Pill" shape (Level 3 roundedness). Backgrounds should be highly desaturated (tinted with the status color) and text should be high-contrast for maximum legibility.
- **Progress Indicators:** Use thick, 8px rounded tracks to convey a sense of "filling up" that is visible even in direct sunlight.

## Stitch Reference Screens

Store exported PNGs in `frontend/public/design/` and link them here.

### 1) Village Dashboard

Desktop PNG:
![Village Dashboard Desktop](./public/design/village-dashboard-desktop.png)

Mobile PNG:
![Village Dashboard Mobile](./public/design/village-dashboard-mobile.png)

Match notes:
- Topbar color, hierarchy, and spacing
- Card radius, border/shadow, and padding rhythm
- Tab sizing and active/inactive treatment

### 2) Proposal Form

Desktop PNG:
![Proposal Form Desktop](./public/design/proposal-form-desktop.png)

Mobile PNG:
![Proposal Form Mobile](./public/design/proposal-form-mobile.png)

Match notes:
- Field spacing and label/input visual hierarchy
- Input focus states and button styles
- Marathi + English label readability

### 3) Plan / Milestones

Desktop PNG:
![Plan Milestones Desktop](./public/design/plan-milestones-desktop.png)

Mobile PNG:
![Plan Milestones Mobile](./public/design/plan-milestones-mobile.png)

Match notes:
- Milestone card grouping and grid behavior
- Status chips and emphasis colors
- Section heading scale and whitespace cadence

### 4) Status / Updates

Desktop PNG:
![Status Updates Desktop](./public/design/status-updates-desktop.png)

Mobile PNG:
![Status Updates Mobile](./public/design/status-updates-mobile.png)

Match notes:
- Thread item spacing and readability
- Media preview sizes and alignment
- Primary vs secondary action contrast

### 5) Anubhav (Community Posts)

Desktop PNG:
![Anubhav Desktop](./public/design/anubhav-desktop.png)

Mobile PNG:
![Anubhav Mobile](./public/design/anubhav-mobile.png)

Match notes:
- Post card hierarchy (title, author, timestamp, body)
- Create/edit/delete action visibility and spacing
- Marathi readability and line-height for long text
- Empty state and list spacing rhythm

### Naming Convention

Use lowercase kebab-case filenames:
- `screen-name-desktop.png`
- `screen-name-mobile.png`

When replacing a screenshot, keep the same filename so links remain stable.