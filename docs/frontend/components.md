# Frontend Component Inventory

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Frontend Team  

## Overview

This document provides a comprehensive inventory of all frontend components in SarvanOM v2, following the Cosmic Pro design system with accessibility and consistency requirements. Components are organized by category and include usage guidelines.

## Component Categories

### 1. Layout Components

#### 1.1 Page Layout
- **`AppLayout`** - Main application layout
  - **Purpose**: Provides consistent layout structure
  - **Props**: `children`, `sidebar`, `header`, `footer`
  - **Accessibility**: ARIA landmarks, focus management
  - **Usage**: Wrap all page content

- **`DashboardLayout`** - Dashboard-specific layout
  - **Purpose**: Dashboard page layout with sidebar
  - **Props**: `children`, `activeTab`, `user`
  - **Accessibility**: Navigation landmarks, keyboard shortcuts
  - **Usage**: Dashboard pages only

- **`AuthLayout`** - Authentication page layout
  - **Purpose**: Clean layout for auth pages
  - **Props**: `children`, `title`, `subtitle`
  - **Accessibility**: Form landmarks, error handling
  - **Usage**: Login, register, forgot password pages

#### 1.2 Navigation Components
- **`Navigation`** - Main navigation bar
  - **Purpose**: Primary site navigation
  - **Props**: `items`, `user`, `onLogout`
  - **Accessibility**: Keyboard navigation, ARIA labels
  - **Usage**: All authenticated pages

- **`Sidebar`** - Sidebar navigation
  - **Purpose**: Secondary navigation and tools
  - **Props**: `items`, `collapsed`, `onToggle`
  - **Accessibility**: Collapsible navigation, focus management
  - **Usage**: Dashboard and main app pages

- **`Breadcrumbs`** - Breadcrumb navigation
  - **Purpose**: Show current page location
  - **Props**: `items`, `separator`
  - **Accessibility**: Navigation landmarks, current page indication
  - **Usage**: All pages with hierarchical structure

- **`Footer`** - Site footer
  - **Purpose**: Footer links and information
  - **Props**: `links`, `copyright`, `social`
  - **Accessibility**: Link groups, contact information
  - **Usage**: All public pages

### 2. Form Components

#### 2.1 Input Components
- **`Input`** - Text input field
  - **Purpose**: Single-line text input
  - **Props**: `type`, `placeholder`, `value`, `onChange`, `error`
  - **Accessibility**: Label association, error announcements
  - **Usage**: All forms requiring text input

- **`Textarea`** - Multi-line text input
  - **Purpose**: Multi-line text input
  - **Props**: `rows`, `placeholder`, `value`, `onChange`, `error`
  - **Accessibility**: Label association, resize control
  - **Usage**: Long text input, comments, descriptions

- **`Select`** - Dropdown selection
  - **Purpose**: Single selection from options
  - **Props**: `options`, `value`, `onChange`, `placeholder`
  - **Accessibility**: Keyboard navigation, option announcements
  - **Usage**: Category selection, settings, filters

- **`Checkbox`** - Checkbox input
  - **Purpose**: Boolean selection
  - **Props**: `checked`, `onChange`, `label`, `indeterminate`
  - **Accessibility**: Label association, state announcements
  - **Usage**: Multiple selections, preferences, agreements

- **`Radio`** - Radio button input
  - **Purpose**: Single selection from group
  - **Props**: `name`, `value`, `checked`, `onChange`, `label`
  - **Accessibility**: Group association, selection announcements
  - **Usage**: Single choice selections, settings

#### 2.2 Form Layout Components
- **`Form`** - Form container
  - **Purpose**: Form structure and validation
  - **Props**: `onSubmit`, `validation`, `children`
  - **Accessibility**: Form landmarks, error handling
  - **Usage**: All forms

- **`FormGroup`** - Form field group
  - **Purpose**: Group related form fields
  - **Props**: `label`, `error`, `required`, `children`
  - **Accessibility**: Fieldset grouping, error association
  - **Usage**: Related form fields

- **`FormRow`** - Form field row
  - **Purpose**: Horizontal form field layout
  - **Props**: `children`, `gap`
  - **Accessibility**: Logical grouping, tab order
  - **Usage**: Side-by-side form fields

### 3. Data Display Components

#### 3.1 Table Components
- **`Table`** - Data table
  - **Purpose**: Display tabular data
  - **Props**: `data`, `columns`, `sortable`, `filterable`
  - **Accessibility**: Table headers, sorting, filtering
  - **Usage**: Query results, analytics data, user lists

- **`TableRow`** - Table row
  - **Purpose**: Individual table row
  - **Props**: `data`, `onClick`, `selectable`
  - **Accessibility**: Row selection, keyboard navigation
  - **Usage**: Within Table component

- **`TableCell`** - Table cell
  - **Purpose**: Individual table cell
  - **Props**: `value`, `type`, `align`
  - **Accessibility**: Cell content, data type indication
  - **Usage**: Within TableRow component

#### 3.2 List Components
- **`List`** - Generic list
  - **Purpose**: Display list of items
  - **Props**: `items`, `renderItem`, `emptyState`
  - **Accessibility**: List landmarks, empty state
  - **Usage**: Query history, document lists, notifications

- **`ListItem`** - List item
  - **Purpose**: Individual list item
  - **Props**: `item`, `onClick`, `actions`
  - **Accessibility**: Item selection, action buttons
  - **Usage**: Within List component

- **`Card`** - Content card
  - **Purpose**: Display content in card format
  - **Props**: `title`, `content`, `actions`, `image`
  - **Accessibility**: Card structure, action buttons
  - **Usage**: Feature cards, result cards, content blocks

#### 3.3 Chart Components
- **`Chart`** - Generic chart component
  - **Purpose**: Display data visualizations
  - **Props**: `data`, `type`, `options`, `height`
  - **Accessibility**: Chart descriptions, data tables
  - **Usage**: Analytics dashboards, performance metrics

- **`LineChart`** - Line chart
  - **Purpose**: Display time series data
  - **Props**: `data`, `xAxis`, `yAxis`, `colors`
  - **Accessibility**: Data table, trend descriptions
  - **Usage**: Performance trends, usage analytics

- **`BarChart`** - Bar chart
  - **Purpose**: Display categorical data
  - **Props**: `data`, `categories`, `values`, `colors`
  - **Accessibility**: Data table, category descriptions
  - **Usage**: Usage statistics, comparison data

- **`PieChart`** - Pie chart
  - **Purpose**: Display proportional data
  - **Props**: `data`, `colors`, `showLegend`
  - **Accessibility**: Data table, segment descriptions
  - **Usage**: Distribution data, category breakdowns

### 4. Interactive Components

#### 4.1 Button Components
- **`Button`** - Primary button
  - **Purpose**: Primary action button
  - **Props**: `variant`, `size`, `disabled`, `loading`, `onClick`
  - **Accessibility**: Button role, loading state, keyboard activation
  - **Usage**: Primary actions, form submissions

- **`IconButton`** - Icon-only button
  - **Purpose**: Icon-based action button
  - **Props**: `icon`, `size`, `disabled`, `onClick`, `ariaLabel`
  - **Accessibility**: Icon description, keyboard activation
  - **Usage**: Toolbar actions, close buttons, menu triggers

- **`ButtonGroup`** - Button group
  - **Purpose**: Group related buttons
  - **Props**: `children`, `orientation`, `size`
  - **Accessibility**: Group association, keyboard navigation
  - **Usage**: Related actions, toolbar buttons

#### 4.2 Modal Components

- **`GuidedPromptModal`** - Guided prompt confirmation modal
  - **Purpose**: Display query refinement suggestions and collect user confirmation
  - **Props**: 
    - `isOpen: boolean` - Modal visibility state
    - `originalQuery: string` - User's original query
    - `refinements: RefinementSuggestion[]` - Array of refinement suggestions
    - `onAccept: (refinement: RefinementSuggestion) => void` - Accept refinement callback
    - `onEdit: (editedQuery: string) => void` - Edit query callback
    - `onSkip: () => void` - Skip refinement callback
    - `onClose: () => void` - Close modal callback
    - `constraints: ConstraintChip[]` - Available constraint chips
    - `onConstraintSelect: (constraint: ConstraintChip) => void` - Constraint selection callback
  - **States**: 
    - `hidden` - Modal not visible
    - `loading` - Refinement suggestions being generated
    - `suggestions_ready` - Refinements displayed for user selection
    - `confirmed` - User has made a selection
    - `error` - Error state with fallback options
  - **Accessibility**: 
    - Keyboard navigation (Tab, Enter, Escape)
    - ARIA roles and labels for screen readers
    - Focus management and trap
    - High contrast mode support
  - **Usage**: Triggered between query input and execution
  - **Mobile**: Full-screen sheet on mobile devices
  - **Constraints**: 
    - Maximum 3 refinement suggestions
    - 500ms latency budget for suggestions
    - Auto-skip if budget exceeded

- **`RefinementSuggestion`** - Individual refinement suggestion
  - **Purpose**: Display a single refinement option
  - **Props**:
    - `id: string` - Unique suggestion identifier
    - `title: string` - Suggestion title
    - `description: string` - Detailed explanation
    - `refinedQuery: string` - The refined query text
    - `type: 'intent_analysis' | 'disambiguation' | 'constraint_application' | 'sanitization'` - Refinement type
    - `confidence: number` - Confidence score (0-1)
    - `onSelect: () => void` - Selection callback
  - **Accessibility**: Button role, keyboard selectable, screen reader friendly

- **`ConstraintChip`** - Constraint selection chip
  - **Purpose**: Allow users to select query constraints
  - **Props**:
    - `id: string` - Constraint identifier
    - `label: string` - Display label
    - `type: 'time_range' | 'sources' | 'citations' | 'cost_ceiling' | 'depth'` - Constraint type
    - `options: string[]` - Available options for this constraint
    - `selected: boolean` - Whether constraint is selected
    - `onToggle: () => void` - Toggle selection callback
  - **Accessibility**: Toggle button role, keyboard accessible, clear selection state

#### 4.3 Modal Components (Legacy)
- **`Modal`** - Modal dialog
  - **Purpose**: Overlay dialog for focused content
  - **Props**: `isOpen`, `onClose`, `title`, `children`
  - **Accessibility**: Focus trap, escape key, ARIA dialog
  - **Usage**: Confirmations, forms, detailed views

- **`Dialog`** - Confirmation dialog
  - **Purpose**: User confirmation dialogs
  - **Props**: `isOpen`, `onConfirm`, `onCancel`, `title`, `message`
  - **Accessibility**: Focus management, keyboard navigation
  - **Usage**: Delete confirmations, action confirmations

- **`Drawer`** - Side drawer
  - **Purpose**: Side panel for additional content
  - **Props**: `isOpen`, `onClose`, `position`, `children`
  - **Accessibility**: Focus management, escape key
  - **Usage**: Filters, settings, additional information

#### 4.3 Menu Components
- **`Menu`** - Dropdown menu
  - **Purpose**: Contextual action menu
  - **Props**: `items`, `trigger`, `position`
  - **Accessibility**: Keyboard navigation, ARIA menu
  - **Usage**: Context menus, action menus

- **`MenuItem`** - Menu item
  - **Purpose**: Individual menu item
  - **Props**: `label`, `icon`, `onClick`, `disabled`
  - **Accessibility**: Keyboard activation, state indication
  - **Usage**: Within Menu component

- **`ContextMenu`** - Right-click context menu
  - **Purpose**: Contextual right-click menu
  - **Props**: `items`, `position`, `onClose`
  - **Accessibility**: Keyboard activation, position management
  - **Usage**: Table rows, list items, content areas

### 5. Feedback Components

#### 5.1 Status Components
- **`Alert`** - Alert message
  - **Purpose**: Display important messages
  - **Props**: `type`, `title`, `message`, `dismissible`
  - **Accessibility**: Alert role, dismissible controls
  - **Usage**: Success messages, warnings, errors

- **`Toast`** - Toast notification
  - **Purpose**: Temporary notification messages
  - **Props**: `type`, `message`, `duration`, `onClose`
  - **Accessibility**: Live region, auto-dismiss
  - **Usage**: Success confirmations, error notifications

- **`Badge`** - Status badge
  - **Purpose**: Display status or count
  - **Props**: `variant`, `size`, `children`
  - **Accessibility**: Status indication, count announcement
  - **Usage**: Status indicators, notification counts

- **`Progress`** - Progress indicator
  - **Purpose**: Show progress or loading state
  - **Props**: `value`, `max`, `indeterminate`, `label`
  - **Accessibility**: Progress role, value announcement
  - **Usage**: File uploads, query processing, loading states

#### 5.2 Loading Components
- **`Spinner`** - Loading spinner
  - **Purpose**: Indicate loading state
  - **Props**: `size`, `color`, `label`
  - **Accessibility**: Loading indication, screen reader support
  - **Usage**: Button loading, page loading, data loading

- **`Skeleton`** - Content skeleton
  - **Purpose**: Show content loading state
  - **Props**: `lines`, `width`, `height`
  - **Accessibility**: Loading indication, content structure
  - **Usage**: Content placeholders, data loading

- **`LoadingState`** - Loading state wrapper
  - **Purpose**: Wrap content with loading state
  - **Props**: `loading`, `children`, `fallback`
  - **Accessibility**: Loading indication, content management
  - **Usage**: Data fetching, async operations

### 6. Query Interface Components

#### 6.1 Query Input Components
- **`QueryInput`** - Main query input
  - **Purpose**: Primary query input interface
  - **Props**: `value`, `onChange`, `onSubmit`, `placeholder`
  - **Accessibility**: Label association, keyboard shortcuts
  - **Usage**: Main query interface

- **`QuerySuggestions`** - Query suggestions
  - **Purpose**: Show query suggestions and autocomplete
  - **Props**: `suggestions`, `onSelect`, `loading`
  - **Accessibility**: List navigation, selection announcements
  - **Usage**: Query input enhancement

- **`QueryHistory`** - Query history
  - **Purpose**: Display previous queries
  - **Props**: `queries`, `onSelect`, `onDelete`
  - **Accessibility**: List navigation, action buttons
  - **Usage**: Query input sidebar, history page

#### 6.2 Query Result Components
- **`QueryResults`** - Query results container
  - **Purpose**: Display query results
  - **Props**: `results`, `loading`, `error`
  - **Accessibility**: Results region, loading indication
  - **Usage**: Main results display

- **`ResultCard`** - Individual result card
  - **Purpose**: Display individual result
  - **Props**: `result`, `onSelect`, `onShare`
  - **Accessibility**: Card structure, action buttons
  - **Usage**: Within QueryResults component

- **`Citations`** - Source citations
  - **Purpose**: Display source citations
  - **Props**: `citations`, `onClick`
  - **Accessibility**: Link navigation, source information
  - **Usage**: Result cards, detailed views

- **`KnowledgeGraph`** - Knowledge graph visualization
  - **Purpose**: Display knowledge graph
  - **Props**: `nodes`, `edges`, `onNodeClick`
  - **Accessibility**: Graph navigation, node descriptions
  - **Usage**: Knowledge visualization, result exploration

### 7. Agent Interface Components

#### 7.1 Agent Dashboard Components
- **`AgentCard`** - Agent status card
  - **Purpose**: Display agent status and information
  - **Props**: `agent`, `status`, `onConfigure`
  - **Accessibility**: Status indication, configuration access
  - **Usage**: Agent dashboard, agent lists

- **`AgentStatus`** - Agent status indicator
  - **Purpose**: Show agent operational status
  - **Props**: `status`, `lastActivity`, `health`
  - **Accessibility**: Status announcement, health indication
  - **Usage**: Agent cards, status displays

- **`AgentMetrics`** - Agent performance metrics
  - **Purpose**: Display agent performance data
  - **Props**: `metrics`, `timeRange`, `onTimeRangeChange`
  - **Accessibility**: Data table, chart descriptions
  - **Usage**: Agent detail pages, performance monitoring

#### 7.2 Agent Interface Components
- **`DatabaseAgent`** - Database agent interface
  - **Purpose**: Database query and management interface
  - **Props**: `connection`, `onQuery`, `results`
  - **Accessibility**: SQL editor, result tables
  - **Usage**: Database agent page

- **`BrowserAgent`** - Browser agent interface
  - **Purpose**: Web browsing and information gathering
  - **Props**: `url`, `onNavigate`, `content`
  - **Accessibility**: Browser navigation, content extraction
  - **Usage**: Browser agent page

- **`PDFAgent`** - PDF processing interface
  - **Purpose**: PDF document processing and analysis
  - **Props**: `file`, `onUpload`, `analysis`
  - **Accessibility**: File upload, progress indication
  - **Usage**: PDF agent page

- **`CodeExecutor`** - Code execution interface
  - **Purpose**: Code execution and testing
  - **Props**: `code`, `language`, `onExecute`, `output`
  - **Accessibility**: Code editor, output formatting
  - **Usage**: Code executor agent page

### 8. Utility Components

#### 8.1 Layout Utilities
- **`Container`** - Content container
  - **Purpose**: Provide consistent content width
  - **Props**: `maxWidth`, `padding`, `children`
  - **Accessibility**: Content structure
  - **Usage**: Page content, section content

- **`Grid`** - Grid layout
  - **Purpose**: Responsive grid layout
  - **Props**: `columns`, `gap`, `children`
  - **Accessibility**: Layout structure
  - **Usage**: Card layouts, content grids

- **`Flex`** - Flexbox layout
  - **Purpose**: Flexible layout container
  - **Props**: `direction`, `justify`, `align`, `children`
  - **Accessibility**: Layout structure
  - **Usage**: Button groups, form rows, content alignment

#### 8.2 Content Utilities
- **`Divider`** - Content divider
  - **Purpose**: Separate content sections
  - **Props**: `orientation`, `spacing`
  - **Accessibility**: Content separation
  - **Usage**: Section separation, list separation

- **`Spacer`** - Spacing utility
  - **Purpose**: Add consistent spacing
  - **Props**: `size`, `axis`
  - **Accessibility**: Layout spacing
  - **Usage**: Component spacing, layout spacing

- **`Text`** - Text utility
  - **Purpose**: Consistent text styling
  - **Props**: `variant`, `size`, `color`, `children`
  - **Accessibility**: Text structure, semantic meaning
  - **Usage**: All text content

## Component Usage Guidelines

### 1. Accessibility Requirements

#### 1.1 Keyboard Navigation
- All interactive components must be keyboard accessible
- Tab order must be logical and predictable
- Focus indicators must be visible and consistent
- Keyboard shortcuts must be documented and consistent

#### 1.2 Screen Reader Support
- All components must have proper ARIA labels
- Form controls must be associated with labels
- Status changes must be announced
- Complex interactions must have clear instructions

#### 1.3 Color and Contrast
- All text must meet WCAG 2.1 AA contrast requirements
- Color must not be the only way to convey information
- Focus indicators must be visible in all color modes
- High contrast mode must be supported

### 2. Performance Requirements

#### 2.1 Loading Performance
- Components must load within 1 second
- Critical components must be prioritized
- Non-critical components must be lazy loaded
- Images must be optimized and responsive

#### 2.2 Runtime Performance
- Components must not cause layout shifts
- Animations must be smooth (60fps)
- Memory usage must be optimized
- Event handlers must be debounced where appropriate

### 3. Consistency Requirements

#### 3.1 Design System
- All components must follow Cosmic Pro design system
- Spacing, typography, and colors must be consistent
- Component variants must be clearly defined
- Documentation must be comprehensive

#### 3.2 Code Standards
- All components must be TypeScript
- Props must be properly typed
- Components must be properly tested
- Code must follow project conventions

## Component Testing

### 1. Unit Testing

#### 1.1 Component Tests
```typescript
describe('Button Component', () => {
  test('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });
  
  test('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  test('is accessible', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

#### 1.2 Integration Tests
```typescript
describe('Form Component Integration', () => {
  test('submits form with valid data', async () => {
    const handleSubmit = jest.fn();
    render(
      <Form onSubmit={handleSubmit}>
        <Input name="email" type="email" required />
        <Button type="submit">Submit</Button>
      </Form>
    );
    
    await user.type(screen.getByRole('textbox'), 'user@example.com');
    await user.click(screen.getByRole('button'));
    
    expect(handleSubmit).toHaveBeenCalledWith({
      email: 'user@example.com'
    });
  });
});
```

### 2. Visual Testing

#### 2.1 Storybook Stories
```typescript
export default {
  title: 'Components/Button',
  component: Button,
  parameters: {
    docs: {
      description: {
        component: 'Primary button component for user actions.'
      }
    }
  }
};

export const Primary = {
  args: {
    children: 'Primary Button',
    variant: 'primary'
  }
};

export const Secondary = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary'
  }
};

export const Loading = {
  args: {
    children: 'Loading Button',
    loading: true
  }
};
```

#### 2.2 Visual Regression Tests
```typescript
describe('Button Visual Tests', () => {
  test('matches snapshot', () => {
    const { container } = render(<Button>Test Button</Button>);
    expect(container.firstChild).toMatchSnapshot();
  });
  
  test('matches visual baseline', async () => {
    const { container } = render(<Button>Test Button</Button>);
    expect(await imageSnapshot(container)).toMatchImageSnapshot();
  });
});
```

---

## Appendix

### A. Component Library Structure
```
src/components/
├── layout/
│   ├── AppLayout.tsx
│   ├── DashboardLayout.tsx
│   └── AuthLayout.tsx
├── forms/
│   ├── Input.tsx
│   ├── Textarea.tsx
│   └── Select.tsx
├── data/
│   ├── Table.tsx
│   ├── List.tsx
│   └── Card.tsx
├── interactive/
│   ├── Button.tsx
│   ├── Modal.tsx
│   └── Menu.tsx
├── feedback/
│   ├── Alert.tsx
│   ├── Toast.tsx
│   └── Progress.tsx
├── query/
│   ├── QueryInput.tsx
│   ├── QueryResults.tsx
│   └── KnowledgeGraph.tsx
├── agents/
│   ├── AgentCard.tsx
│   ├── DatabaseAgent.tsx
│   └── BrowserAgent.tsx
└── utils/
    ├── Container.tsx
    ├── Grid.tsx
    └── Text.tsx
```

### B. Design System Tokens
- **Colors**: Primary, secondary, success, warning, error
- **Typography**: Headings, body text, captions, code
- **Spacing**: Consistent spacing scale
- **Shadows**: Elevation and depth
- **Borders**: Border radius and styles
- **Animations**: Transitions and micro-interactions

### C. Component Documentation
- **Storybook**: Interactive component documentation
- **Props**: TypeScript interfaces and JSDoc
- **Examples**: Usage examples and best practices
- **Accessibility**: Accessibility guidelines and testing
- **Performance**: Performance considerations and optimization
