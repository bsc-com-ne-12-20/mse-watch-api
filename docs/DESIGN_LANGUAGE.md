# MSE Watch Design Language Documentation

## Overview
MSE Watch uses a professional, developer-focused design language that combines modern fintech aesthetics with African market identity. The design emphasizes clarity, trust, and technical sophistication while remaining accessible across all devices.

## Color Palette

### Primary Colors
```css
:root {
    --primary-color: #1a365d;     /* Deep Navy Blue - Primary brand color */
    --secondary-color: #2c5282;   /* Medium Blue - Supporting elements */
    --accent-color: #d69e2e;      /* Warm Gold - Call-to-action accents */
    --dark-color: #0a0e13;        /* Deep Charcoal - Dark backgrounds */
    --light-gray: #f8fafc;        /* Light Gray - Page backgrounds */
    --navy-blue: #1e3a8a;         /* Navy Blue - Badges and highlights */
    --charcoal: #374151;          /* Charcoal - Text and code blocks */
    --gold: #fbbf24;              /* Bright Gold - Interactive elements */
    --platinum: #e5e7eb;          /* Platinum - Subtle borders */
    --slate: #64748b;             /* Slate - Muted text */
}
```

### Color Usage Guidelines

#### Primary Navy (#1a365d)
- **Usage**: Main brand color, hero backgrounds, primary buttons
- **Meaning**: Trust, stability, financial security
- **Applications**: Navigation, hero gradients, primary CTAs

#### Accent Gold (#d69e2e, #fbbf24)
- **Usage**: Highlights, interactive elements, success states
- **Meaning**: Premium quality, value, prosperity
- **Applications**: Icons, hover states, gradient text

#### Charcoal (#374151, #0a0e13)
- **Usage**: Text, code blocks, dark sections
- **Meaning**: Professionalism, technical expertise
- **Applications**: Body text, code syntax, API demos

#### Light Grays (#f8fafc, #e5e7eb)
- **Usage**: Backgrounds, subtle borders, disabled states
- **Meaning**: Clean, minimal, spacious
- **Applications**: Section backgrounds, card borders

## Typography

### Font Stack
```css
font-family: 'system-ui', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Hierarchy & Scaling

#### Headlines
- **H1**: `text-3xl sm:text-4xl md:text-5xl lg:text-6xl` (Mobile-first responsive)
- **H2**: `text-3xl sm:text-4xl` 
- **H3**: `text-xl md:text-2xl`
- **Font Weight**: `font-bold` (700)

#### Body Text
- **Base Size**: `text-base` (16px)
- **Large**: `text-lg sm:text-xl` (18px-20px)
- **Small**: `text-sm md:text-base` (14px-16px)
- **Font Weight**: Regular (400) to `font-medium` (500)

#### Code Typography
```css
font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
```
- **Usage**: API endpoints, code examples, technical content
- **Styling**: Dark backgrounds with syntax highlighting

## Branding Elements

### Logo & Brand Mark
- **Primary**: "MSE Watch" wordmark
- **Icon**: Dual-icon system combining:
  - `fas fa-chart-line` (Financial growth)
  - `fas fa-clock` (Real-time data)
- **Colors**: Gold chart icon, gray clock overlay
- **Positioning**: Relative positioning for layered effect

### NumNet Badge
```css
.numnet-badge {
    background: linear-gradient(45deg, var(--navy-blue) 0%, var(--primary-color) 100%);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 50px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.875rem;
    box-shadow: 0 4px 14px 0 rgba(26, 54, 93, 0.39);
}
```

### Flag Integration
- **Malawi Flag**: `w-8 h-6` with rounded corners and shadow
- **Usage**: Country identification and local market emphasis
- **Placement**: Hero section, maintains cultural connection

## Layout System

### Grid Structure
- **Base**: CSS Grid with responsive breakpoints
- **Mobile-first**: Single column layout scaling to multi-column
- **Breakpoints**: 
  - Mobile: `grid-cols-1`
  - Tablet: `md:grid-cols-2`
  - Desktop: `lg:grid-cols-3` or `lg:grid-cols-4`

### Spacing Scale
- **Micro**: `space-x-2` (8px), `space-y-2` (8px)
- **Small**: `gap-4` (16px), `p-4` (16px)
- **Medium**: `gap-6 md:gap-8` (24px-32px)
- **Large**: `py-12 sm:py-16 md:py-20` (48px-80px)

### Container System
```css
max-width: 7xl; /* 1280px */
margin: auto;
padding: px-4 sm:px-6 lg:px-8;
```

## Component Design Patterns

### Cards
```css
.card-hover {
    transition: all 0.3s ease;
    background: white;
    border-radius: 0.75rem; /* rounded-xl */
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
}

.card-hover:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
```

### Buttons

#### Primary Button
```css
background: linear-gradient(to right, #d69e2e, #b7791f);
color: white;
padding: 0.75rem 2rem;
border-radius: 0.5rem;
font-weight: 700;
transition: all 0.3s;
box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
```

#### Secondary Button
```css
border: 2px solid #d1d5db;
color: white;
background: transparent;
hover:background: white;
hover:color: #1f2937;
```

### API Demo Block
```css
.api-demo {
    background: var(--charcoal);
    border-radius: 8px;
    color: #e2e8f0;
    font-family: monospace;
    border: 1px solid var(--slate);
    padding: 1.5rem;
}
```

#### Syntax Highlighting
- **Keys**: `color: var(--gold)` (#fbbf24)
- **Strings**: `color: #f6ad55` (Orange)
- **Numbers**: `color: #63b3ed` (Blue)

## Animation & Interactions

### Pulse Animation
```css
.pulse-animation {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

### Hover Transitions
- **Standard**: `transition: all 0.3s ease`
- **Cards**: `transform: translateY(-5px)` with enhanced shadow
- **Buttons**: Color transitions and scale effects

### Gradient Effects

#### Hero Background
```css
.hero-gradient {
    background: linear-gradient(135deg, 
        var(--dark-color) 0%, 
        var(--primary-color) 50%, 
        var(--charcoal) 100%);
}
```

#### Gradient Text
```css
.gradient-text {
    background: linear-gradient(135deg, var(--gold), var(--accent-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
```

## Mobile Responsiveness

### Breakpoint Strategy
- **Mobile-first**: Base styles for mobile devices
- **Tablet**: `sm:` (640px+) and `md:` (768px+)
- **Desktop**: `lg:` (1024px+) and `xl:` (1280px+)

### Mobile Optimizations
- **Typography**: Scaled down for smaller screens
- **Spacing**: Reduced padding and margins
- **Navigation**: Collapsible hamburger menu
- **Grid**: Single-column layouts on mobile

### Mobile CSS Classes
```css
.mobile-text-responsive { font-size: 1.25rem !important; }
.mobile-hero-title { font-size: 2.5rem !important; }
.mobile-nav-title { font-size: 1.5rem !important; }
```

## Accessibility & UX

### Focus States
- **Visible**: Ring-based focus indicators
- **Color**: `focus:ring-yellow-600` for brand consistency
- **Size**: `focus:ring-2` for sufficient visibility

### Color Contrast
- **Text on Background**: High contrast ratios (4.5:1 minimum)
- **Interactive Elements**: Clear visual feedback
- **Status Indicators**: Color + icon combinations

### Icon Usage
- **Font Awesome**: Consistent icon library
- **Semantic**: Icons support text content
- **Interactive**: Clear hover and active states

## Brand Voice & Personality

### Visual Characteristics
- **Professional**: Clean, structured layouts
- **Technical**: Code-focused design elements
- **Trustworthy**: Financial industry color palette
- **Modern**: Contemporary UI patterns and animations
- **African**: Cultural elements through flag integration

### Design Principles
1. **Clarity**: Information hierarchy and clear CTAs
2. **Consistency**: Unified spacing and component patterns
3. **Accessibility**: Mobile-first and inclusive design
4. **Performance**: Optimized animations and transitions
5. **Trust**: Professional aesthetics suitable for financial data

## Implementation Guidelines

### CSS Architecture
- **Utility-first**: Tailwind CSS framework
- **Custom Properties**: CSS variables for brand colors
- **Component Classes**: Reusable patterns for common elements
- **Responsive**: Mobile-first media queries

### File Organization
```
styles/
├── base/           # Reset and base styles
├── components/     # Card, button, form components
├── utilities/      # Helper classes
└── responsive/     # Breakpoint-specific styles
```

This design language creates a cohesive, professional appearance that positions MSE Watch as a reliable, modern financial data platform while maintaining cultural relevance to the Malawi market.
