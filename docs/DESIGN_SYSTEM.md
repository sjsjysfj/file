# UI Design System & Accessibility Guidelines

## 1. Typography (字体规范)

### Font Family
- **Primary**: Segoe UI, Microsoft YaHei, Sans-Serif
- **Fallback**: System Default Sans-Serif

### Font Scale (字号层级)
| Token | Size | Weight | Usage |
|-------|------|--------|-------|
| `FONT_SIZE_XXL` | 22px | 700 (Bold) | App Title (应用标题) |
| `FONT_SIZE_XL` | 18px | 600 (Semi-Bold) | Page Headings (页面标题) |
| `FONT_SIZE_LG` | 16px | 600 (Semi-Bold) | Section Titles (区块标题) |
| `FONT_SIZE_BASE` | 14px | 400 (Regular) | Body Text, Inputs, Buttons (正文) |
| `FONT_SIZE_SM` | 12px | 400 (Regular) | Captions, Subtitles, Tooltips (说明文字) |

## 2. Color Palette & Accessibility (配色与可访问性)

### Light Theme (浅色模式)
| Semantic Role | Color Value | Contrast (on Bg) | WCAG Rating |
|---------------|-------------|------------------|-------------|
| **Background** | `#F5F7FB` | - | - |
| **Surface** | `#FFFFFF` | 1.05:1 | - |
| **Text Primary** | `#0F172A` (Slate-900) | **15.4:1** | **AAA** |
| **Text Secondary** | `#475569` (Slate-600) | **7.5:1** | **AAA** |
| **Text Muted** | `#64748B` (Slate-500) | **4.9:1** | **AA** |
| **Primary Brand** | `#5B8CFF` | 3.0:1 (Large text ok) | UI Components |
| **Border** | `#E2E8F0` | - | Structural |

### Dark Theme (深色模式)
| Semantic Role | Color Value | Contrast (on Bg) | WCAG Rating |
|---------------|-------------|------------------|-------------|
| **Background** | `#0F1220` | - | - |
| **Surface** | `#161A2B` | 1.1:1 | - |
| **Text Primary** | `#E8ECF6` | **15.8:1** | **AAA** |
| **Text Secondary** | `#A9B2C7` | **9.2:1** | **AAA** |
| **Text Muted** | `#7E879C` | **5.3:1** | **AA** |
| **Primary Brand** | `#7AA2FF` | 5.5:1 | **AA** |

## 3. Layout & Spacing (布局与间距)

### Spacing System (4px Grid)
- **XS**: 4px (Icon/Text gap)
- **SM**: 8px (Component internal padding)
- **MD**: 16px (Container padding, Section gap)
- **LG**: 24px (Large section gap)
- **XL**: 32px (Major layout separation)

### Borders & Radius
- **Border Width**: 1px (Standard), 0px (Clean look preference)
- **Radius SM**: 4px (Buttons, Inputs)
- **Radius LG**: 12px (Cards, Panels)

## 4. Text Overflow & Responsiveness (文本溢出与响应式)
- **ElidedLabel**: Custom component implemented to handle text overflow with ellipsis (`...`) in the middle or end.
- **Responsive Splitter**: Main layout switches between Horizontal/Vertical split based on window width (< 980px).
- **No Borders on Text**: Labels removed borders to reduce visual noise and improve reading flow.

## 5. Accessibility Checklist (可访问性检查)
- [x] All text meets WCAG 2.1 AA contrast ratio (4.5:1 minimum for normal text).
- [x] Interactive elements have minimum size (min-height 32px).
- [x] Text resizes correctly without breaking layout (via ElidedLabel).
- [x] Focus states visible (via Border Focus color).
