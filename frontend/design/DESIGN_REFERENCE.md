# 🎨 AURA Frontend Design Reference

## 📋 Tổng quan

File này mô tả **màu sắc, bố cục, và giao diện cơ bản** của hệ thống AURA để tham khảo khi xây dựng frontend.

**Lưu ý:** Các ảnh demo hiện có trong thư mục này (`Screenshot 2026-01-29 220339.png`, `Screenshot 2026-01-29 220351.png`, `Screenshot 2026-01-29 220358.png`, `trang chủ.png`) là các mẫu tham khảo về giao diện.

---

## 🎨 Color Palette (Bảng màu)

### Primary Colors (Màu chính)
- **Primary Blue:** `#1976D2` - Màu chủ đạo cho buttons, links, highlights
- **Primary Dark:** `#1565C0` - Hover state cho primary buttons
- **Primary Light:** `#BBDEFB` - Background nhẹ, subtle highlights

### Secondary Colors (Màu phụ)
- **Secondary Gray:** `#424242` - Text, borders
- **Secondary Light:** `#757575` - Secondary text, icons

### Status Colors (Màu trạng thái)
- **Success Green:** `#4CAF50` - Thành công, completed status
- **Warning Orange:** `#FF9800` - Cảnh báo, pending status
- **Error Red:** `#F44336` - Lỗi, failed status
- **Info Blue:** `#2196F3` - Thông tin, in-progress status

### Background Colors (Màu nền)
- **Background Light:** `#F5F5F5` - Nền chính của trang
- **Background White:** `#FFFFFF` - Nền của cards, containers
- **Background Dark:** `#212121` - Sidebar, header (nếu có)

### Text Colors (Màu chữ)
- **Text Primary:** `#212121` - Text chính, headings
- **Text Secondary:** `#757575` - Text phụ, descriptions
- **Text Disabled:** `#BDBDBD` - Text disabled
- **Text White:** `#FFFFFF` - Text trên nền tối

---

## 📐 Typography (Kiểu chữ)

### Font Family
- **Primary Font:** `'Roboto', sans-serif` (Google Fonts)
- **Fallback:** `Arial, Helvetica, sans-serif`

### Font Sizes
- **H1 (Page Title):** `32px` / `2rem` - Font-weight: `700` (Bold)
- **H2 (Section Title):** `24px` / `1.5rem` - Font-weight: `600` (SemiBold)
- **H3 (Subsection):** `20px` / `1.25rem` - Font-weight: `500` (Medium)
- **H4 (Card Title):** `18px` / `1.125rem` - Font-weight: `500` (Medium)
- **Body (Normal Text):** `16px` / `1rem` - Font-weight: `400` (Regular)
- **Small Text:** `14px` / `0.875rem` - Font-weight: `400` (Regular)
- **Caption:** `12px` / `0.75rem` - Font-weight: `400` (Regular)

### Line Heights
- **Headings:** `1.2` - Tight spacing
- **Body:** `1.5` - Comfortable reading
- **Small:** `1.4` - Compact but readable

---

## 📏 Spacing System (Hệ thống khoảng cách)

### Base Unit: `8px`

- **XS (Extra Small):** `4px` / `0.25rem` - Tight spacing
- **S (Small):** `8px` / `0.5rem` - Base unit
- **M (Medium):** `16px` / `1rem` - Standard spacing
- **L (Large):** `24px` / `1.5rem` - Section spacing
- **XL (Extra Large):** `32px` / `2rem` - Major section spacing
- **XXL (2X Large):** `48px` / `3rem` - Page-level spacing

### Usage Examples
- **Card Padding:** `16px` (M)
- **Button Padding:** `12px 24px` (vertical: M/2, horizontal: L)
- **Input Padding:** `12px 16px` (vertical: M/2, horizontal: M)
- **Section Margin:** `32px` (XL)
- **Element Gap:** `16px` (M)

---

## 🎯 Layout Structure (Cấu trúc bố cục)

### Desktop Layout (≥1200px)
```
┌─────────────────────────────────────────────────┐
│              Header (Fixed Top)                 │
│  Logo | Navigation | User Menu | Notifications │
├──────────┬──────────────────────────────────────┤
│          │                                      │
│ Sidebar  │         Main Content Area            │
│ (250px)  │         (Fluid Width)                │
│          │                                      │
│ - Menu   │  ┌──────────────────────────────┐   │
│ - Items  │  │   Content Cards/Components   │   │
│          │  └──────────────────────────────┘   │
│          │                                      │
└──────────┴──────────────────────────────────────┘
```

### Tablet Layout (768px - 1199px)
- Sidebar: Collapsed hoặc overlay
- Main content: Full width
- Cards: 2 columns

### Mobile Layout (<768px)
- Sidebar: Hidden (hamburger menu)
- Main content: Full width, single column
- Cards: Stack vertically

---

## 🧩 Component Styles (Kiểu component)

### Buttons

#### Primary Button
```css
- Background: #1976D2 (Primary Blue)
- Text Color: #FFFFFF
- Padding: 12px 24px
- Border Radius: 4px
- Font Size: 16px
- Font Weight: 500 (Medium)
- Hover: Background #1565C0, cursor pointer
- Active: Background #0D47A1
- Disabled: Background #E0E0E0, Text #9E9E9E
```

#### Secondary Button
```css
- Background: Transparent
- Border: 1px solid #1976D2
- Text Color: #1976D2
- Padding: 12px 24px
- Border Radius: 4px
- Hover: Background #E3F2FD
```

#### Danger Button
```css
- Background: #F44336 (Error Red)
- Text Color: #FFFFFF
- Hover: Background #D32F2F
```

### Input Fields

#### Text Input
```css
- Width: 100%
- Height: 48px
- Padding: 12px 16px
- Border: 1px solid #E0E0E0
- Border Radius: 4px
- Font Size: 16px
- Focus: Border #1976D2, Outline none
- Placeholder: Color #9E9E9E
```

#### Textarea
```css
- Same as Text Input
- Min Height: 120px
- Resize: vertical
```

### Cards

#### Standard Card
```css
- Background: #FFFFFF
- Border Radius: 8px
- Padding: 24px
- Box Shadow: 0 2px 4px rgba(0,0,0,0.1)
- Hover: Box Shadow 0 4px 8px rgba(0,0,0,0.15)
```

#### Stats Card
```css
- Background: #FFFFFF
- Border Radius: 8px
- Padding: 20px
- Border Left: 4px solid #1976D2
- Box Shadow: 0 2px 4px rgba(0,0,0,0.1)
```

### Tables

#### Table Header
```css
- Background: #F5F5F5
- Font Weight: 600 (SemiBold)
- Padding: 12px 16px
- Border Bottom: 2px solid #E0E0E0
```

#### Table Row
```css
- Padding: 12px 16px
- Border Bottom: 1px solid #E0E0E0
- Hover: Background #F5F5F5
```

### Badges/Labels

#### Status Badge
```css
- Padding: 4px 12px
- Border Radius: 12px
- Font Size: 12px
- Font Weight: 500

- Success: Background #E8F5E9, Color #2E7D32
- Warning: Background #FFF3E0, Color #E65100
- Error: Background #FFEBEE, Color #C62828
- Info: Background #E3F2FD, Color #1565C0
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First Approach */
- Mobile: < 768px
- Tablet: 768px - 1199px
- Desktop: ≥ 1200px
```

### Media Queries
```css
/* Tablet */
@media (min-width: 768px) { ... }

/* Desktop */
@media (min-width: 1200px) { ... }
```

---

## 🎭 UI Patterns (Mẫu giao diện)

### Navigation
- **Sidebar Navigation:** Dark background (#212121), white text
- **Active Item:** Highlighted với primary color
- **Hover:** Light background (#424242)

### Forms
- **Form Container:** White card với padding
- **Form Groups:** Margin bottom 24px
- **Labels:** Font weight 500, margin bottom 8px
- **Error Messages:** Red text (#F44336), font size 14px, margin top 4px

### Modals/Dialogs
- **Overlay:** Background rgba(0,0,0,0.5)
- **Modal:** Centered, max-width 600px, white background, border radius 8px
- **Header:** Padding 20px, border bottom
- **Body:** Padding 20px
- **Footer:** Padding 20px, border top, button group

### Loading States
- **Spinner:** Primary color (#1976D2)
- **Skeleton Loader:** Light gray background (#F5F5F5)
- **Progress Bar:** Primary color background

---

## 🖼️ Image Guidelines

### Image Sizes
- **Logo:** 120x120px (square) hoặc 200x60px (horizontal)
- **Avatar:** 40x40px (small), 80x80px (medium), 120x120px (large)
- **Thumbnail:** 150x150px
- **Retinal Image Preview:** 300x300px hoặc responsive

### Image Formats
- **Icons:** SVG (preferred) hoặc PNG
- **Photos:** JPG (optimized)
- **Logos:** SVG hoặc PNG với transparent background

---

## 📝 Design Principles

1. **Consistency:** Sử dụng cùng spacing, colors, typography trong toàn bộ ứng dụng
2. **Clarity:** UI rõ ràng, dễ hiểu, không gây nhầm lẫn
3. **Accessibility:** Contrast ratio đủ cao, font size đọc được
4. **Responsive:** Hoạt động tốt trên mọi kích thước màn hình
5. **Performance:** Tối ưu images, CSS, JavaScript

---

## 🎨 Reference Images

Các ảnh demo trong thư mục này (`Screenshot 2026-01-29 220339.png`, `Screenshot 2026-01-29 220351.png`, `Screenshot 2026-01-29 220358.png`, `trang chủ.png`) thể hiện:

- **Màu sắc:** Primary blue, clean white backgrounds
- **Bố cục:** Card-based layout, sidebar navigation
- **Typography:** Clear, readable fonts
- **Components:** Buttons, inputs, cards, tables

**Lưu ý:** Khi implement, tham khảo các ảnh này để đảm bảo giao diện nhất quán.

---

## 📚 Resources

- **Google Fonts:** https://fonts.google.com/specimen/Roboto
- **Material Design Colors:** https://material.io/design/color/the-color-system.html
- **Bootstrap Icons:** https://icons.getbootstrap.com/
- **Font Awesome:** https://fontawesome.com/

---

**Cập nhật:** File này sẽ được cập nhật khi có thay đổi về design system.
