# Guided Prompt UX Flow

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE DESIGN**  
**Purpose**: State machine, UX wires, and interaction patterns for Guided Prompt Confirmation

---

## 🔄 **State Machine**

### **Core States**
```
draft → refine_suggestions → user_confirm|edit|skip → final_query
```

### **Detailed State Flow**
```
User Input
    ↓
[draft] → Intent Analysis → Refinement Generation
    ↓
[refine_suggestions] → UI Display → User Interaction
    ↓
[user_confirm] → Execute Refined Query
    ↓
[user_edit] → Edit Interface → Confirm → Execute
    ↓
[user_skip] → Execute Original Query
    ↓
[final_query] → Main Processing
```

### **State Transitions**
| From State | To State | Trigger | Action |
|------------|----------|---------|--------|
| `draft` | `refine_suggestions` | Intent analysis complete | Show suggestions |
| `draft` | `final_query` | Skip refinement | Execute original |
| `refine_suggestions` | `user_confirm` | User clicks "Looks good" | Execute refined |
| `refine_suggestions` | `user_edit` | User clicks "Edit" | Show edit interface |
| `refine_suggestions` | `user_skip` | User clicks "Skip" | Execute original |
| `user_edit` | `final_query` | User confirms edit | Execute edited |
| `user_edit` | `refine_suggestions` | User cancels edit | Return to suggestions |

---

## 🎨 **UX Wireframes**

### **1. Modal Interface (Desktop)**
```
┌─────────────────────────────────────────────────────────────┐
│                    Guided Prompt Confirmation               │
├─────────────────────────────────────────────────────────────┤
│ Your query: "show me apple"                                 │
│                                                             │
│ 💡 I can help you be more specific:                        │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Do you mean:                                            │ │
│ │                                                         │ │
│ │ ○ Apple Inc. (company) stock performance               │ │
│ │ ○ Apple fruit nutritional information                  │ │
│ │ ○ Apple products and reviews                           │ │
│ │ ○ Apple ecosystem and services                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Add constraints:                                            │
│ [Time range] [Sources] [Depth] [Citations required]        │
│                                                             │
│ [Looks good → Run] [Edit] [Skip refinement]                │
└─────────────────────────────────────────────────────────────┘
```

### **2. Inline Compact Bar (Desktop)**
```
┌─────────────────────────────────────────────────────────────┐
│ Search: "show me apple"                    [Search]         │
├─────────────────────────────────────────────────────────────┤
│ 💡 More specific? Apple Inc. | Apple fruit | Apple products │
│    [Use this] [Edit] [Skip]                                 │
└─────────────────────────────────────────────────────────────┘
```

### **3. Mobile Sheet (Mobile)**
```
┌─────────────────────────────────────────────────────────────┐
│                    Guided Prompt                            │
├─────────────────────────────────────────────────────────────┤
│ Your query: "show me apple"                                 │
│                                                             │
│ 💡 I can help you be more specific:                        │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ○ Apple Inc. (company) stock performance               │ │
│ │ ○ Apple fruit nutritional information                  │ │
│ │ ○ Apple products and reviews                           │ │
│ │ ○ Apple ecosystem and services                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Time range] [Sources] [Depth]                              │
│                                                             │
│ [Looks good → Run]                                          │
│ [Edit] [Skip refinement]                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **Default Interactions**

### **Suggestion Display**
- **Tone**: Short, neutral, no hype
- **Count**: Up to 3 suggestions maximum
- **Format**: Clear options with brief descriptions
- **Visual**: Radio buttons for single selection

### **Diff Display**
- **Original**: Show user's draft query
- **Refined**: Show improved version
- **Changes**: Highlight additions/removals inline
- **Format**: Green for additions, red for removals

### **Constraint Chips**
| Chip | Purpose | Options | Default |
|------|---------|---------|---------|
| **Time range** | Limit temporal scope | Recent, 5 years, All time | Recent |
| **Sources** | Specify source types | Academic, News, Both | Both |
| **Citations required** | Force citations | Yes, No | Yes |
| **Cost ceiling** | Limit API costs | Low, Medium, High | Medium |
| **Depth** | Response complexity | Simple, Technical, Research | Simple |

### **Action Buttons**
| Button | Purpose | Style | Position |
|--------|---------|-------|----------|
| **Looks good → Run** | Accept suggestion | Primary (blue) | Left |
| **Edit** | Modify suggestion | Secondary (gray) | Center |
| **Skip refinement** | Use original | Tertiary (text) | Right |

---

## ♿ **Accessibility Notes**

### **Keyboard Navigation**
- **Tab Order**: Suggestions → Constraints → Action buttons
- **Arrow Keys**: Navigate between suggestions
- **Enter**: Select current suggestion
- **Escape**: Close modal/sheet
- **Space**: Toggle constraint chips

### **ARIA Roles**
```html
<!-- Example ARIA implementation -->
<div role="dialog" aria-labelledby="guided-prompt-title" aria-describedby="guided-prompt-description">
  <h2 id="guided-prompt-title">Guided Prompt Confirmation</h2>
  <p id="guided-prompt-description">I can help you be more specific with your query</p>
  
  <fieldset role="radiogroup" aria-labelledby="suggestions-label">
    <legend id="suggestions-label">Choose the most relevant option:</legend>
    <input type="radio" id="suggestion-1" name="suggestion" value="1" aria-describedby="suggestion-1-desc">
    <label for="suggestion-1">Apple Inc. (company) stock performance</label>
    <span id="suggestion-1-desc" class="sr-only">Financial information about Apple Inc. company</span>
  </fieldset>
  
  <div role="group" aria-labelledby="constraints-label">
    <h3 id="constraints-label">Add constraints (optional):</h3>
    <button type="button" role="checkbox" aria-checked="false" aria-describedby="time-range-desc">
      Time range
    </button>
    <span id="time-range-desc" class="sr-only">Limit results to specific time period</span>
  </div>
  
  <div role="group" aria-labelledby="actions-label">
    <h3 id="actions-label">Choose an action:</h3>
    <button type="button" aria-describedby="confirm-desc">Looks good → Run</button>
    <span id="confirm-desc" class="sr-only">Use the selected suggestion and run the query</span>
  </div>
</div>
```

### **Screen Reader Support**
- **Announcements**: "Guided prompt suggestions available"
- **Descriptions**: Clear descriptions for all interactive elements
- **State Changes**: Announce when suggestions are selected
- **Error Messages**: Clear error descriptions

### **Visual Accessibility**
- **Color Contrast**: WCAG AA compliant (4.5:1 ratio)
- **Focus Indicators**: Clear focus rings on all interactive elements
- **Text Size**: Minimum 16px font size
- **Spacing**: Adequate touch targets (44px minimum)

---

## 📱 **Responsive Design**

### **Breakpoints**
| Device | Width | Layout | Behavior |
|--------|-------|--------|----------|
| **Mobile** | < 768px | Full-screen sheet | Slide up from bottom |
| **Tablet** | 768px - 1024px | Modal with larger width | Center modal |
| **Desktop** | > 1024px | Modal or inline bar | Flexible positioning |

### **Mobile Optimizations**
- **Touch Targets**: 44px minimum touch targets
- **Swipe Gestures**: Swipe down to dismiss
- **Keyboard**: Optimized for mobile keyboards
- **Performance**: Reduced animations for better performance

### **Desktop Optimizations**
- **Keyboard Shortcuts**: Quick access keys
- **Mouse Interactions**: Hover states and tooltips
- **Multi-window**: Support for multiple browser tabs
- **Performance**: Full animations and transitions

---

## 🎭 **Interaction Patterns**

### **Suggestion Selection**
```javascript
// Example suggestion selection behavior
class SuggestionSelector {
  selectSuggestion(suggestionId) {
    // Update visual state
    this.highlightSuggestion(suggestionId);
    
    // Update form data
    this.updateFormData(suggestionId);
    
    // Enable action buttons
    this.enableActionButtons();
    
    // Announce to screen readers
    this.announceSelection(suggestionId);
  }
  
  announceSelection(suggestionId) {
    const suggestion = this.getSuggestion(suggestionId);
    const announcement = `Selected: ${suggestion.text}`;
    this.screenReaderAnnounce(announcement);
  }
}
```

### **Constraint Management**
```javascript
// Example constraint chip behavior
class ConstraintManager {
  toggleConstraint(constraintType) {
    const isActive = this.isConstraintActive(constraintType);
    
    if (isActive) {
      this.deactivateConstraint(constraintType);
    } else {
      this.activateConstraint(constraintType);
    }
    
    // Update suggestion based on constraints
    this.updateSuggestionsWithConstraints();
  }
  
  updateSuggestionsWithConstraints() {
    const activeConstraints = this.getActiveConstraints();
    const updatedSuggestions = this.applyConstraints(activeConstraints);
    this.displaySuggestions(updatedSuggestions);
  }
}
```

### **Edit Mode**
```javascript
// Example edit mode behavior
class EditMode {
  enterEditMode() {
    // Show edit interface
    this.showEditInterface();
    
    // Focus on editable text
    this.focusEditableText();
    
    // Enable save/cancel buttons
    this.enableEditActions();
  }
  
  saveEdit() {
    const editedText = this.getEditedText();
    
    // Validate edit
    if (this.validateEdit(editedText)) {
      this.applyEdit(editedText);
      this.exitEditMode();
    } else {
      this.showValidationError();
    }
  }
}
```

---

## 🎨 **Visual Design Tokens**

### **Colors**
| Token | Value | Usage |
|-------|-------|-------|
| `--guided-prompt-primary` | #2563eb | Primary action buttons |
| `--guided-prompt-secondary` | #6b7280 | Secondary action buttons |
| `--guided-prompt-success` | #10b981 | Success states |
| `--guided-prompt-warning` | #f59e0b | Warning states |
| `--guided-prompt-error` | #ef4444 | Error states |

### **Spacing**
| Token | Value | Usage |
|-------|-------|-------|
| `--guided-prompt-padding` | 1.5rem | Modal padding |
| `--guided-prompt-gap` | 1rem | Element spacing |
| `--guided-prompt-radius` | 0.5rem | Border radius |

### **Typography**
| Token | Value | Usage |
|-------|-------|-------|
| `--guided-prompt-title-size` | 1.25rem | Modal title |
| `--guided-prompt-text-size` | 1rem | Body text |
| `--guided-prompt-caption-size` | 0.875rem | Captions |

---

## 📚 **References**

- Overview: `docs/prompting/guided_prompt_overview.md`
- Policy: `docs/prompting/guided_prompt_policy.md`
- Toggle Contract: `docs/prompting/guided_prompt_toggle_contract.md`
- LLM Policy: `docs/prompting/guided_prompt_llm_policy.md`
- Metrics: `docs/prompting/guided_prompt_metrics.md`
- Experiments: `docs/prompting/guided_prompt_experiments.md`
- Test Cases: `docs/prompting/guided_prompt_test_cases.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This UX flow specification ensures consistent and accessible user experience across all Guided Prompt Confirmation interfaces.*
